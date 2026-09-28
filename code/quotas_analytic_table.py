#!/usr/bin/env python3
"""Analytic table of the quota family (Corollary 5): pure arithmetic, NO random draw.

Reads the frozen grid of the family (``data/quotas_grid.json``) and prints, per cell, the EXACT
AUC of every policy under Poisson counts (``D`` deterministic in the counts;
``AUC = E[Phi(sqrt(D_1 + D_0) / 2)]`` with ``D_1, D_0`` iid; the recency cut with two sources
through the hypergeometric composition of the suffix, with the budget stopping rule), the fluid
form, the declared comparisons (type, tolerance, ratio, planned unpaired Hanley-McNeil standard
error), the Consequence sub-test of cell KNP1, the decay cell (fluid form, water filling) and the
sweeps of cell FIX1 (quota ``q_A``) and of cell DEC1 (``tau``). It checks the design criteria with
named asserts (exit != 0 if any fails). No ``x`` is drawn and no Mann-Whitney AUC is computed.

Port of the frozen private generator of the pre-registration
(``data/prereg/08-quotas-addendum.md``, section 8) with no change of result: identifiers, the
arithmetic and the standard output are verbatim; the closed-form primitives (``W``, ``delta2``,
``auc``, ``inclinacao``, ``z_saturacao``, ``ep_hanley_mcneil``) are imported, never edited, from
the frozen token-KAT table module ``token_kat_analytic_table``. The standard output is kept
VERBATIM in Portuguese, with fixed precision (no ``repr`` of floats): it is the frozen
pre-registration artifact ``data/prereg/quotas_analytic_table.txt``, reproduced byte for byte by
``tests/test_quotas.py``.

Usage: ``python3 code/quotas_analytic_table.py [--grade <json>] [--grade-kat <json>]``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/quotas_grid.json"
GRADE_KAT = RAIZ / "data/kat_token_grid.json"


# --- arithmetic ported from the draft (no change of result) -----------------------------------


def Phi_arr(x):
    """Return the standard normal CDF of every element of ``x`` (``math.erf``, float array)."""
    x = np.asarray(x, float)
    f = np.frompyfunc(lambda v: 0.5 * (1 + math.erf(v / math.sqrt(2))), 1, 1)
    return f(x).astype(float)


def pois_support(mu, sd_mult=9):
    """Return the truncated Poisson support ``(n, p)`` of mean ``mu`` (``sd_mult`` deviations)."""
    lo = max(0, int(mu - sd_mult * math.sqrt(mu) - 2))
    hi = int(mu + sd_mult * math.sqrt(mu) + 3)
    n = np.arange(lo, hi + 1)
    logp = n * math.log(mu) - mu - np.array([math.lgamma(v + 1) for v in n])
    return n, np.exp(logp)


def rho(f):
    """Return the separability per token ``rho = d^2 / k`` of a source."""
    return f["d"] ** 2 / f["k"]


def dd(f):
    """Return the separability per event ``d^2`` of a source."""
    return f["d"] ** 2


def d2_guloso_fluido(fs, T, K, chave):
    """Return the fluid ``Delta^2`` of the greedy fill by ``chave``, descending.

    Each source is filled up to ``lam_s T`` (Dantzig in the fluid form).
    """
    resto, tot = K, 0.0
    for f in sorted(fs, key=chave, reverse=True):
        n = min(f["lam"] * T, resto / f["k"])
        tot += n * f["d"] ** 2
        resto -= n * f["k"]
    return tot


def cotas_tax(fs, K):
    """Return the rate-proportional fixed quotas ``floor(lam_s K / W)``."""
    w = tab.W(fs)
    return [int(math.floor(f["lam"] * K / w)) for f in fs]


def D_politica(Ns, fs, K, pol):
    """Return the ``D`` of a user with integer counts ``Ns`` (grid order) under RHO, EVT or TAX."""
    idx = list(range(len(fs)))
    if pol in ("RHO", "EVT"):
        chave = rho if pol == "RHO" else dd
        ordem = sorted(idx, key=lambda i: chave(fs[i]), reverse=True)
        resto, D = K, 0.0
        for i in ordem:
            n = min(Ns[i], resto // fs[i]["k"])
            D += n * fs[i]["d"] ** 2
            resto -= n * fs[i]["k"]
        return D
    if pol == "TAX":
        q = cotas_tax(fs, K)
        return sum(min(Ns[i], q[i]) * fs[i]["d"] ** 2 for i in idx)
    raise ValueError(pol)


def auc_exata_contagens(fs, T, K, pol):
    """Return the exact pooled AUC ``sum_i sum_j p_i p_j Phi(sqrt(D_i + D_j) / 2)``.

    The sum runs over the Poisson support of the counts.
    """
    supp = [pois_support(f["lam"] * T) for f in fs]
    Dvals, probs = [], []
    for combo in itertools.product(*[range(len(s[0])) for s in supp]):
        Ns = tuple(int(supp[j][0][c]) for j, c in enumerate(combo))
        p = float(np.prod([supp[j][1][c] for j, c in enumerate(combo)]))
        if p < 1e-14:
            continue
        Dvals.append(D_politica(Ns, fs, K, pol))
        probs.append(p)
    Dvals = np.round(np.array(Dvals), 10)
    probs = np.array(probs)
    u, inv = np.unique(Dvals, return_inverse=True)
    pu = np.bincount(inv, weights=probs)
    pu /= pu.sum()
    if len(u) > 3000:
        # aggregate on a fine grid to fit in memory (error << 1e-6 in AUC)
        edges = np.linspace(u.min(), u.max(), 3001)
        b = np.clip(np.searchsorted(edges, u) - 1, 0, 2999)
        uu = np.bincount(b, weights=u * pu) / np.maximum(np.bincount(b, weights=pu), 1e-300)
        pp = np.bincount(b, weights=pu)
        m = pp > 0
        u, pu = uu[m], pp[m]
    S = u[:, None] + u[None, :]
    return float(np.sum(pu[:, None] * pu[None, :] * Phi_arr(np.sqrt(S) / 2)))


def cotas_fix(fs, T, K, arred):
    """Return the fixed quotas: greedy by rho over the EXPECTED counts.

    ``arred`` = ``"f"`` takes the floor of ``lam_s T``; ``"c"`` takes the ceiling.
    """
    ordem = sorted(range(len(fs)), key=lambda i: rho(fs[i]), reverse=True)
    resto, q = K, [0] * len(fs)
    for i in ordem:
        v = fs[i]["lam"] * T
        v = math.floor(v) if arred == "f" else math.ceil(v)
        q[i] = min(int(v), resto // fs[i]["k"])
        resto -= q[i] * fs[i]["k"]
    return q


def auc_exata_cotas(fs, T, q):
    """Return the exact AUC of fixed quotas ``q`` (two sources; leftover not reallocated)."""
    sA, pA = pois_support(fs[0]["lam"] * T)
    sC, pC = pois_support(fs[1]["lam"] * T)
    acc = {}
    for NA, a in zip(sA, pA, strict=True):
        for NC, c in zip(sC, pC, strict=True):
            D = round(
                min(int(NA), q[0]) * fs[0]["d"] ** 2 + min(int(NC), q[1]) * fs[1]["d"] ** 2, 10
            )
            acc[D] = acc.get(D, 0) + a * c
    u = np.array(sorted(acc))
    pu = np.array([acc[v] for v in u])
    pu /= pu.sum()
    return float(np.sum(pu[:, None] * pu[None, :] * Phi_arr(np.sqrt(u[:, None] + u[None, :]) / 2)))


def lchoose(n, k):
    """Return ``log C(n, k)`` through ``lgamma``."""
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def auc_exata_rec(fs, T, K):
    """Return the EXACT pooled AUC of the recency cut with 2 sources and heterogeneous cost.

    No simulation. Given ``(N_A, N_C)``, the time order is a uniform permutation; the most recent
    suffix has hypergeometric composition. The window is ``(a, c)`` if, and only if,
    ``cost(a, c) <= K`` and [``a + c = N`` or the next event overflows];
    ``P(next = A) = (N_A - a) / (N - a - c)``.
    """
    fa, fc = fs
    kA, kC = fa["k"], fc["k"]
    dA2, dC2 = fa["d"] ** 2, fc["d"] ** 2
    sA, pA = pois_support(fa["lam"] * T)
    sC, pC = pois_support(fc["lam"] * T)
    acc = {}
    for NA, qa in zip(sA, pA, strict=True):
        for NC, qc in zip(sC, pC, strict=True):
            w = qa * qc
            if w < 1e-13:
                continue
            NA_, NC_ = int(NA), int(NC)
            N = NA_ + NC_
            if NA_ * kA + NC_ * kC <= K:
                D = NA_ * dA2 + NC_ * dC2
                acc[round(D, 10)] = acc.get(round(D, 10), 0) + w
                continue
            for c in range(0, min(NC_, K // kC) + 1):
                amax = min(NA_, (K - c * kC) // kA)
                for a in range(max(0, amax - (kC // kA) - 1), amax + 1):
                    cost = a * kA + c * kC
                    if cost > K:
                        continue
                    rem = N - a - c
                    if rem == 0:
                        pstop = 1.0
                    else:
                        pnA = (NA_ - a) / rem
                        pnC = (NC_ - c) / rem
                        pstop = pnA * (cost + kA > K) + pnC * (cost + kC > K)
                    if pstop == 0:
                        continue
                    lh = lchoose(NA_, a) + lchoose(NC_, c) - lchoose(N, a + c)
                    pr = w * math.exp(lh) * pstop
                    if pr < 1e-16:
                        continue
                    D = round(a * dA2 + c * dC2, 10)
                    acc[D] = acc.get(D, 0) + pr
    u = np.array(sorted(acc))
    pu = np.array([acc[v] for v in u])
    pu /= pu.sum()
    S = u[:, None] + u[None, :]
    return float(np.sum(pu[:, None] * pu[None, :] * Phi_arr(np.sqrt(S) / 2)))


def V(lam, d2, a, tau):
    """Return the fluid value of a source covering ages ``[0, a]`` with ``d(a) = d e^(-a/tau)``."""
    return lam * d2 * (tau / 2) * (1 - math.exp(-2 * a / tau))


def dec_fluido(fs, T, K, tau):
    """Return the fluid ``Delta^2`` with age decay.

    Returns ``(rec, nom, otm, h, idades)``: recency (``a_s = h``), nominal RHO (no age) and the
    optimum with age (water filling), the recency horizon ``h`` and the optimal ages per source.
    """
    h = min(T, K / tab.W(fs))
    rec = sum(V(f["lam"], f["d"] ** 2, h, tau) for f in fs)
    resto, nom = K, 0.0
    for f in sorted(fs, key=rho, reverse=True):
        a = min(T, resto / (f["lam"] * f["k"]))
        nom += V(f["lam"], f["d"] ** 2, a, tau)
        resto -= a * f["lam"] * f["k"]

    def uso(mu):
        """Return the tokens used by the water level ``mu`` (ages clipped to ``[0, T]``)."""
        return sum(
            f["lam"] * f["k"] * min(T, max(0.0, tau / 2 * math.log(rho(f) / mu))) for f in fs
        )

    lo, hi = 1e-12, max(rho(f) for f in fs)
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if uso(mid) > K:
            lo = mid
        else:
            hi = mid
    mu = hi
    idades = [min(T, max(0.0, tau / 2 * math.log(rho(f) / mu))) for f in fs]
    otm = sum(V(f["lam"], f["d"] ** 2, a, tau) for f, a in zip(fs, idades, strict=True))
    return rec, nom, otm, h, idades


# --- table utilities -------------------------------------------------------------------------


def fontes(cel, qual="RS"):
    """Return the sources of ``R`` (``qual="R"``) or of ``R ∪ S`` (``"RS"``), in grid order."""
    fs = [dict(nome=n, **p) for n, p in cel["R"].items()]
    if qual == "RS":
        fs += [dict(nome=n, **p) for n, p in cel["S"].items()]
    return fs


def ep_dif(g, a1, a2):
    """Return the planned SE of a difference: unpaired Hanley-McNeil, mean of ``n`` seeds.

    Unpaired, hence an upper bound of the paired one.
    """
    n_pos = round(g["pi"] * g["N"])
    n_neg = g["N"] - n_pos
    ep = [tab.ep_hanley_mcneil(a, n_pos, n_neg) for a in (a1, a2)]
    return math.sqrt(ep[0] ** 2 + ep[1] ** 2) / math.sqrt(len(g["sementes"]))


def disc(fs, T, K, d2):
    """Return the whole-event bias in the saturated regime (up to ``k_max`` idle tokens).

    Same form as in the token-KAT table.
    """
    return tab.inclinacao(d2) * d2 * max(f["k"] for f in fs) / K if T * tab.W(fs) >= K else 0.0


def s(x, n=5):
    """Return ``x`` with sign and ``n`` decimals; a rounded zero is always ``+0.000...``.

    Stable across platforms.
    """
    t = f"{x:+.{n}f}"
    return "+" + t[1:] if float(t) == 0 else t


def sinal_rival(expr):
    """Return the sign a rival predicts (``-1``, ``+1``, or ``0`` for "about zero")."""
    return {"<=0": -1, "<0": -1, ">0": +1, "~0": 0}[expr]


def chaves(obj):
    """Yield every key of a nested JSON object (dicts and lists)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from chaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from chaves(v)


# --- table -----------------------------------------------------------------------------------


def main(argv=None) -> int:
    """Print the analytic table of the grid; return 0 only if every design criterion passes."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grade", type=Path, default=GRADE)
    ap.add_argument("--grade-kat", type=Path, default=GRADE_KAT)
    args = ap.parse_args(argv)
    bruto = args.grade.read_bytes()
    g = json.loads(bruto)
    gk = json.loads(args.grade_kat.read_bytes())
    K, tolX, margem, zmin = g["K"], g["tol_X"], g["margem_minima_sobre_tol"], g["z_minimo_regime"]
    cels = {c["id"]: c for c in g["celulas"]}

    # --- design criteria: tags, tolerance and streams (before any number) ---
    reservados = g["tags_reservados"]
    assert (
        g["tag"] == 8 and g["tag"] not in reservados.values() and len(set(reservados.values())) == 4
    ), f"tag: {g['tag']} colide com os reservados {reservados}"
    assert "tag_r3" not in set(chaves(g)), "tag: grade nova não pode ter a chave tag_r3"
    assert reservados["KAT"] == gk["tag_r3"], "tag: KAT reservado ≠ tag_r3 da grade do KAT"
    assert math.isclose(tolX, round(3 * g["ep_dif_kat_max"], 5), rel_tol=0, abs_tol=1e-12), (
        f"tol_X: {tolX} ≠ 3·ep_dif_kat_max"
    )
    idx_kat = {c["id"]: i for i, c in enumerate(gk["celulas"])}
    for i, c in enumerate(g["celulas"]):
        fl = c["fluxo"]
        if "fluxo_de" in c:
            ref = cels[c["fluxo_de"]]
            assert fl == ref["fluxo"], f"{c['id']}: fluxo ≠ o de {c['fluxo_de']}"
            mesmas_contagens = (
                c["R"] == ref["R"]
                and c["T"] == ref["T"]
                and all(
                    (c["S"][n]["lam"], c["S"][n]["k"]) == (p["lam"], p["k"])
                    for n, p in ref["S"].items()
                )
            )
            assert mesmas_contagens, (
                f"{c['id']}: λ, k ou T ≠ {c['fluxo_de']} "
                "(o fluxo partilhado não dá as mesmas contagens)"
            )
        elif "ancora" in c:
            ck = gk["celulas"][idx_kat[c["ancora"]["celula_kat"]]]
            assert (c["R"], c["S"]) == (ck["R"], ck["S"]) and c["T"] == ck["T"], (
                f"{c['id']}: fontes ≠ {ck['id']} R∪S do KAT"
            )
            assert fl == {"i_celula": idx_kat[ck["id"]], "i_combo": 1, "tag": reservados["KAT"]}, (
                f"{c['id']}: fluxo declarado ≠ o fluxo selado de {ck['id']} R∪S"
            )
            assert len(c["ancora"]["auc_rec_por_semente"]) == len(g["sementes"]), (
                f"{c['id']}: âncora incompleta"
            )
        else:
            assert fl == {"i_celula": i, "i_combo": 0, "tag": g["tag"]}, (
                f"{c['id']}: fluxo ≠ (índice, 0, tag 8)"
            )

    print(
        f"grade sha256 {hashlib.sha256(bruto).hexdigest()} · K = {K} · N = {g['N']} · "
        f"sementes = {len(g['sementes'])} · tag = {g['tag']} · tol_X = {tolX}"
    )
    print("Fluxos: default_rng([semente, i_celula, i_combo, tag, i_bloco])")
    for c in g["celulas"]:
        fl = c["fluxo"]
        extra = (
            f" · âncora = {c['ancora']['celula_kat']} R∪S do KAT "
            "(AUC da REC por semente = linhas seladas)"
            if "ancora" in c
            else (f" · mesmo fluxo de {c['fluxo_de']}" if "fluxo_de" in c else "")
        )
        print(
            f"- {c['id']}: [semente, {fl['i_celula']}, {fl['i_combo']}, {fl['tag']}, "
            f"i_bloco]{extra}"
        )

    # --- cells with an exact prediction ---
    A, comps, linhas_cel = {}, [], []
    for c in g["celulas"]:
        if c["id"] == "DEC1":
            continue
        fs, T = fontes(c), c["T"]
        fA, fC = fs
        z = tab.z_saturacao(fs, T, K)
        ev = T * sum(f["lam"] for f in fs)
        h = min(T, K / tab.W(fs))
        assert z >= zmin, f"{c['id']}: z = {z:.2f} < {zmin} (não saturada)"
        assert ev <= g["eventos_max_por_usuario"], f"{c['id']}: {ev:.0f} eventos por usuário"
        qf, qc = cotas_fix(fs, T, K, "f"), cotas_fix(fs, T, K, "c")
        a = {
            "REC": auc_exata_rec(fs, T, K),
            "RHO": auc_exata_contagens(fs, T, K, "RHO"),
            "EVT": auc_exata_contagens(fs, T, K, "EVT"),
            "TAX": auc_exata_contagens(fs, T, K, "TAX"),
            "FIXf": auc_exata_cotas(fs, T, qf),
            "FIXc": auc_exata_cotas(fs, T, qc),
        }
        fl = {
            "REC": tab.auc(tab.delta2(fs, T, K)),
            "RHO": tab.auc(d2_guloso_fluido(fs, T, K, rho)),
            "EVT": tab.auc(d2_guloso_fluido(fs, T, K, dd)),
        }
        A[c["id"]] = dict(auc=a, fluida=fl, fs=fs, T=T, z=z)
        linhas_cel.append((c, fs, T, z, ev, h, a, fl, qf, qc, cotas_tax(fs, K)))
        # declared structure of each cell
        if c["id"] in ("KNP1", "KNP3"):
            assert rho(fA) > rho(fC) and dd(fC) > dd(fA), (
                f"{c['id']}: ordem de ρ não oposta à de d²"
            )
        if c["id"] == "KNP2":
            assert rho(fC) > rho(fA) and dd(fA) > dd(fC), "KNP2: ordem de ρ não oposta à de d²"
        if c["id"] == "KNP3":
            assert fA["lam"] * T * fA["k"] < K, "KNP3: teto de A não liga (ótimo não é interior)"
        if c["id"] == "FIX1":
            assert qf != qc, "FIX1: piso e teto dão a mesma cota (fonte não é rara)"
        if c["id"] == "NUL1":
            assert math.isclose(rho(fA), rho(fC), rel_tol=1e-12), "NUL1: ρ_A ≠ ρ_C"
        for cp in c["comparacoes"]:
            x, y = cp["par"]
            prev = a[x] - a[y]
            prev_fl = fl[x] - fl[y] if x in fl and y in fl else None
            comps.append((c["id"], cp, prev, prev_fl, tolX, ep_dif(g, a[x], a[y])))

    # --- decay cell (fluid) ---
    cD = cels["DEC1"]
    fsD, TD, tau = fontes(cD), cD["T"], cD["tau"]
    zD = tab.z_saturacao(fsD, TD, K)
    evD = TD * sum(f["lam"] for f in fsD)
    assert zD >= zmin, f"DEC1: z = {zD:.2f} < {zmin}"
    assert evD <= g["eventos_max_por_usuario"], f"DEC1: {evD:.0f} eventos por usuário"
    recD, nomD, otmD, hD, idD = dec_fluido(fsD, TD, K, tau)
    aD = {"REC": tab.auc(recD), "RHO": tab.auc(nomD), "RHOidade": tab.auc(otmD)}
    tolF = g["tol_base_r1"] + disc(fsD, TD, K, recD) + tolX
    for cp in cD["comparacoes"]:
        x, y = cp["par"]
        comps.append(("DEC1", cp, aD[x] - aD[y], None, tolF, ep_dif(g, aD[x], aD[y])))
    # prediction of the rival H-(ii): the gain without decay (fluid form)
    ganho_sem_dec = tab.auc(d2_guloso_fluido(fsD, TD, K, rho)) - tab.auc(tab.delta2(fsD, TD, K))

    # --- design criteria on the comparisons ---
    for cid, cp, prev, _, tol, _ in comps:
        nome = f"{cid} {cp['par'][0]} − {cp['par'][1]}"
        if cp["tipo"] == "estrita":
            assert abs(prev) >= margem * tol, (
                f"{nome}: |previsto| {abs(prev):.5f} < {margem}·tol {tol:.5f}"
            )
            if cp["rival_preve"] is not None:
                sr = sinal_rival(cp["rival_preve"])
                assert sr == 0 or math.copysign(1, prev) == -sr, (
                    f"{nome}: rival {cp['rival']} não prevê o sinal oposto"
                )
        elif cp["tipo"] == "equivalencia":
            assert abs(prev) < tolX, f"{nome}: equivalência prevista fora de tol_X ({prev:+.5f})"
    assert ganho_sem_dec > 0 and aD["REC"] - aD["RHO"] > 0, (
        "DEC1: rival H-(ii) não prevê o sinal oposto"
    )

    # --- Consequence (KNP1): R = {A}, the history of R ∪ S without the events of C ---
    cq = g["consequencia"]
    cK = cels[cq["celula"]]
    fR = fontes(cK, "R")
    (fa,) = fR
    TK = cK["T"]
    zR = tab.z_saturacao(fR, TK, K)
    assert zR >= zmin, (
        f"Consequência: R sozinha a z = {zR:.2f} (a janela não satura antes da fonte nova)"
    )
    L = K // fa["k"]
    sA, pA = pois_support(fa["lam"] * TK)
    acc = {}
    for n, p in zip(sA, pA, strict=True):
        D = round(min(int(n), L) * fa["d"] ** 2, 10)
        acc[D] = acc.get(D, 0) + p
    u = np.array(sorted(acc))
    pu = np.array([acc[v] for v in u])
    pu /= pu.sum()
    aR = float(np.sum(pu[:, None] * pu[None, :] * Phi_arr(np.sqrt(u[:, None] + u[None, :]) / 2)))
    mu = fa["lam"] * TK
    p_menor = math.fsum(math.exp(n * math.log(mu) - mu - math.lgamma(n + 1)) for n in range(L))
    dRHO = A[cK["id"]]["auc"]["RHO"] - aR
    dREC = A[cK["id"]]["auc"]["REC"] - aR
    assert abs(dRHO) < tolX, f"Consequência: ΔRHO previsto {dRHO:+.5f} fora de tol_X"
    assert dREC < 0 and abs(dREC) >= margem * tolX, (
        f"Consequência: ΔREC previsto {dREC:+.5f} sem margem"
    )

    # --- printing ---
    print()
    print(
        "## Células (previsão exata sob contagens Poisson; eventos inteiros; orçamento de K tokens)"
    )
    print(
        "| célula | bloco | T | z | eventos/usuário | h | λ_A·T | λ_A·h | ρ_A | ρ_C | d_A² | "
        "d_C² | "
        "REC | RHO | EVT | "
        "TAX | FIXf | FIXc | cotas FIXf · FIXc · TAX |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c, fs, T, z, ev, h, a, _fl, qf, qc, qt in linhas_cel:
        fA, fC = fs
        print(
            f"| {c['id']} | {c['bloco']} | {T} | {z:.2f} | {ev:.0f} | {h:.2f} | "
            f"{fA['lam'] * T:.2f} | "
            f"{fA['lam'] * h:.2f} | {rho(fA):.6f} | {rho(fC):.6f} | {dd(fA):.6f} | {dd(fC):.6f} | "
            f"{a['REC']:.5f} | {a['RHO']:.5f} | {a['EVT']:.5f} | {a['TAX']:.5f} | "
            f"{a['FIXf']:.5f} | "
            f"{a['FIXc']:.5f} | {qf} · {qc} · {qt} |"
        )
    print(
        f"| DEC1 (fluida, τ = {tau}) | {cD['bloco']} | {TD} | {zD:.2f} | {evD:.0f} | {hD:.2f} | "
        "— | — | "
        f"{rho(fsD[0]):.6f} | {rho(fsD[1]):.6f} | {dd(fsD[0]):.6f} | {dd(fsD[1]):.6f} | "
        f"{aD['REC']:.5f} | "
        f"{aD['RHO']:.5f} (ρ nominal) | — | — | — | — | RHOidade {aD['RHOidade']:.5f} |"
    )
    print()
    print("## Forma fluida (referência; a previsão usada é a exata)")
    print("| célula | REC | RHO | EVT |")
    print("|---|---|---|---|")
    for c, *_ in linhas_cel:
        fl = A[c["id"]]["fluida"]
        print(f"| {c['id']} | {fl['REC']:.5f} | {fl['RHO']:.5f} | {fl['EVT']:.5f} |")
    print()
    print(
        "## Comparações declaradas (tol_X fixo; razão = previsto/tol; "
        "EP plan. = Hanley–McNeil NÃO pareado)"
    )
    print(
        "| célula | comparação | tipo | previsto (exata) | previsto (fluida) | tol | razão | "
        "EP plan. | rival | "
        "rival prevê | refuta o rival | critérios |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for cid, cp, prev, prev_fl, tol, ep in comps:
        razao = f"{prev / tol:+.2f}" if cp["tipo"] == "estrita" else "—"
        pfl = s(prev_fl) if prev_fl is not None else "—"
        print(
            f"| {cid} | {cp['par'][0]} − {cp['par'][1]} | {cp['tipo']} | {s(prev)} | {pfl} | "
            f"{tol:.5f} | {razao} | "
            f"{ep:.5f} | {cp['rival'] or '—'} | {cp['rival_preve'] or '—'} | "
            f"{cp['refuta_rival'] or '—'} | "
            f"{', '.join(cp['criterios']) or '—'} |"
        )
    print()
    print(
        f"DEC1: τ = {tau} dias (meia-vida de d = {tau * math.log(2):.1f} dias) · "
        f"tol_F = tol_base_r1 + disc + tol_X = "
        f"{g['tol_base_r1']} + {disc(fsD, TD, K, recD):.4f} + {tolX} = {tolF:.5f} "
        "(nível e RHOidade − REC: "
        f"report-only) · idades ótimas A, C = {idD[0]:.1f}, {idD[1]:.1f} dias · h = {hD:.2f} dias "
        "· rival H-(ii) "
        f"prevê RHO − REC = {s(ganho_sem_dec, 4)} (ganho fluido sem decaimento)"
    )
    print()
    print(f"## Consequência ({cK['id']}; R = {{A}}, a mesma história de R ∪ S sem os eventos de C)")
    print(
        f"z(R) = {zR:.2f} (a janela já satura antes da fonte nova) · janela de A = {L} eventos · "
        f"AUC(R) REC = RHO = {aR:.5f}"
    )
    print(
        f"ΔAUC_RHO(R -> R ∪ S) = {s(dRHO)} (equivalência; rival {cq['rival']} prevê < 0) · "
        f"ΔAUC_REC(R -> R ∪ S) = {s(dREC)} (estrita; razão {dREC / tolX:+.2f}) · tol_X = {tolX} · "
        f"EP plan. = {ep_dif(g, A[cK['id']]['auc']['RHO'], aR):.5f} · "
        f"{ep_dif(g, A[cK['id']]['auc']['REC'], aR):.5f}"
    )
    print(f"P(N_A < {L}) = {p_menor:.2e} para N_A ~ Poisson({mu:.0f})")
    print()
    cF = cels["FIX1"]
    fsF, TF = A["FIX1"]["fs"], A["FIX1"]["T"]
    print(
        "## Varredura do FIX1 (cota fixa q_A da fonte rara; C recebe ⌊(K − q_A·k_A)/k_C⌋; "
        "sem realocação) · "
        f"REC = {A['FIX1']['auc']['REC']:.5f} · RHO = {A['FIX1']['auc']['RHO']:.5f}"
    )
    print("| q_A | cotas | FIX | FIX − REC | RHO − FIX |")
    print("|---|---|---|---|---|")
    for qA in cF["varredura_qA"]["q_A"]:
        q = [qA, (K - qA * fsF[0]["k"]) // fsF[1]["k"]]
        f = auc_exata_cotas(fsF, TF, q)
        print(
            f"| {qA} | {q} | {f:.5f} | {s(f - A['FIX1']['auc']['REC'], 4)} | "
            f"{s(A['FIX1']['auc']['RHO'] - f)} |"
        )
    print()
    print(
        f"## Varredura do DEC1 (τ em dias; forma fluida; fontes do {cD['fluxo_de']}) · "
        "AUC exata do "
        f"{cD['fluxo_de']} sem decaimento: RHO − REC = "
        f"{s(A[cD['fluxo_de']]['auc']['RHO'] - A[cD['fluxo_de']]['auc']['REC'], 4)}"
    )
    print(
        "| τ | Δ² REC | Δ² RHO nominal | Δ² RHOidade | AUC REC | AUC RHO nominal | AUC RHOidade | "
        "REC − RHO | "
        "RHOidade − REC | idades ótimas A, C |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|")
    for t in cD["varredura_tau"]:
        if t is None:
            rec = tab.delta2(fsD, TD, K)
            nom = otm = d2_guloso_fluido(fsD, TD, K, rho)
            idades, rotulo = None, "∞ (sem decaimento)"
        else:
            rec, nom, otm, _, idades = dec_fluido(fsD, TD, K, t)
            rotulo = f"{t}"
        ar, an, ao = tab.auc(rec), tab.auc(nom), tab.auc(otm)
        ids = "—" if idades is None else f"{idades[0]:.1f}, {idades[1]:.1f}"
        print(
            f"| {rotulo} | {rec:.4f} | {nom:.4f} | {otm:.4f} | {ar:.4f} | {an:.4f} | {ao:.4f} | "
            f"{s(ar - an, 4)} | "
            f"{s(ao - ar)} | {ids} |"
        )
    print()
    print(
        "CRITÉRIOS DE DESENHO: todos passaram (tag 8 exclusivo e fora de {3, 5, 6, 7}; "
        "tol_X = 3·ep_dif_kat_max; "
        "fluxos declarados = fluxos selados do KAT nas âncoras; células saturadas a z ≥ z_min; "
        "eventos ≤ máximo; "
        "|previsto| ≥ 1,2·tol em toda comparação estrita; rival nomeado com sinal oposto; "
        "equivalências dentro de "
        "tol_X; Consequência com R já saturada)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
