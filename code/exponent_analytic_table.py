#!/usr/bin/env python3
"""Analytic table of the exponent family (EXP): arithmetic and exact enumeration, NO simulation.

Specification: ``data/prereg/05-exponent-addendum.md`` (sections 1.7, 1.8, 1.9 and 1.12). Reads
the frozen grid ``data/exponent_grid.json`` (``--grade`` optional) and, for each cell (mixture
``R`` -> ``R ∪ S``, both saturated), computes the prediction of the fluid closed form
(``W = sum(lam_s k_s)``, ``h = min(T, K / W)``, ``Delta^2 = h * sum(lam_s d_s^2)``,
``AUC = Phi(sqrt(Delta^2) / sqrt(2))``), the exact dAUC of the infinite population (enumeration
of the composition of the saturated window: iid marks of the Poisson superposition,
``AUC = E[Phi(sqrt(Delta^2_i + Delta^2_j) / 2)]``), ``SE_Delta`` of Hanley-McNeil (per
combination, in quadrature, ``/ sqrt(n_seeds)``), ``tolDelta = delta_kat_dif + 3 * SE_Delta``,
the level tolerance of the token KAT, the signs of the theory (``d^2 / k``), of the rival rules
``H(p, q)`` (value per token ``d^p / k^q`` with the SAME ``h``: ``d/k``, ``d^3/k``, ``d/sqrt(k)``,
``d^2/k^2``) and of the linear readers without weight and with weight ``d^2``, the sign-switch
point of ``H(p, 1)`` (grid of step 0.0005, literal port of the draft, and exact root by Brent),
the thresholds of the theory (family C: ``r`` against ``sqrt(kappa)``; family D: ``d_S`` against
the power means ``mu_p``) and where each reader mutant dies. It checks the design criteria with
named asserts (exit != 0 if one fails).

Port of the frozen private generator of the addendum: the arithmetic, the order of the
expressions and the standard output are verbatim; only the import of the analytic primitives
(``token_kat_analytic_table``, never edited), the default grid path, the comments and the
docstrings changed. The standard output and the assert messages stay in Portuguese: the output
is the frozen pre-registration artifact ``data/prereg/exponent_analytic_table.txt``, reproduced
byte for byte by ``tests/test_exponent.py``.

Family verdict hook. ``veredito(linhas, grade)`` is the function that ``code/run_grid.py`` calls
after the literal simulation; it applies the pre-registered criteria EXS and EXN (section 1.9)
to the result rows. The module has no side effect on import.

Usage: ``python3 code/exponent_analytic_table.py [--grade data/exponent_grid.json]``. Output:
tables on stdout (Portuguese, no path); the first line carries the sha256 of the grid read.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

import run_token_kat
import token_kat as kt
import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parent.parent
GRADE = RAIZ / "data/exponent_grid.json"

IDS = ("EXP-C1", "EXP-C2", "EXP-C3", "EXP-C4", "EXP-D1", "EXP-D2")
TAGS_DAS_OUTRAS = {3, 6, 7, 8}  # 3 = token KAT; 6, 7, 8 = the other three families of the batch
# token KAT run: generated events and wall time with 8 processes (base of the time estimate)
EVENTOS_KAT, SEGUNDOS_KAT = 1.476e9, 76


# --- rival rules and linear readers (fluid form) --------------------------------------------------


def V(fs, T, K, p, q=1.0):
    """Return the rival rule ``H(p, q)``: ``h * sum(lam_s k_s^(1-q) d_s^p)``, same ``h`` as theory.

    ``h = min(T, K / W)`` is the window of the theory, so ``H(2, 1)`` is the theory itself.
    """
    W = tab.W(fs)
    h = min(T, K / W)
    return h * sum(f["lam"] * f["k"] ** (1 - q) * f["d"] ** p for f in fs)


def sep_linear(fs, T, K, w):
    """Return the effective (fluid) ``Delta^2`` of a linear reader with weights ``w_s``.

    ``(sum(n w d))^2 / sum(n w^2)``, with ``n_s = h * lam_s``.
    """
    W = tab.W(fs)
    h = min(T, K / W)
    num = sum(h * f["lam"] * w(f) * f["d"] for f in fs) ** 2
    den = sum(h * f["lam"] * w(f) ** 2 for f in fs)
    return num / den


def pmean(ws, ds, p):
    """Return the weighted power mean ``(sum(w d^p))^(1/p)`` (weights and values of the same R)."""
    return (sum(w * d**p for w, d in zip(ws, ds, strict=True))) ** (1 / p)


def limiar(R, RS, T, K, q):
    """Return the sign switch of ``H(p, q)`` in ``p``.

    Returns
    -------
    tuple of list
        ``(grade, raizes)``: the first point after each switch on the grid of step 0.0005 over
        ``[0.5, 6]`` and the exact root of each switch (Brent, ``xtol = 1e-12``).
    """
    ps = np.round(np.arange(0.5, 6.0001, 0.0005), 4)
    s = np.sign([V(RS, T, K, p, q) - V(R, T, K, p, q) for p in ps])
    idx = np.nonzero(s[1:] != s[:-1])[0] + 1
    grade = [float(ps[i]) for i in idx]

    def f(p):
        """Return ``H(p, q)`` of ``R ∪ S`` minus that of ``R``."""
        return V(RS, T, K, p, q) - V(R, T, K, p, q)

    raizes = [float(brentq(f, float(ps[i - 1]), float(ps[i]), xtol=1e-12)) for i in idx]
    return grade, raizes


# --- exact AUC (infinite population) by enumeration of the saturated window -----------------------


def comp_final(fs, K):
    """Return the exact distribution of the composition of the saturated window.

    Marks are iid categorical (Poisson superposition), walked from the most recent backwards; the
    walk stops at the first event that would overflow ``K``. Assumes a saturated history.

    Returns
    -------
    list of tuple
        ``(counts per source, probability)``.
    """
    lam = np.array([f["lam"] for f in fs])
    pr = lam / lam.sum()
    k = np.array([f["k"] for f in fs])
    nf = len(fs)
    if nf == 1:
        n = K // k[0]
        return [((n,), 1.0)]
    out = []

    def rec(i, cur, custo):
        """Enumerate the counts of source ``i`` onwards, given the cost already used."""
        if i == nf:
            n = cur
            tot = sum(n)
            # probability that the first tot events have exactly the counts n (multinomial)
            logp = (
                math.lgamma(tot + 1)
                - sum(math.lgamma(x + 1) for x in n)
                + sum(x * math.log(pr[j]) for j, x in enumerate(n) if x)
            )
            # does the next mark overflow?
            stop = sum(pr[j] for j in range(nf) if custo + k[j] > K)
            if stop > 0:
                out.append((tuple(n), math.exp(logp) * stop))
            return
        for x in range(0, (K - custo) // k[i] + 1):
            rec(i + 1, cur + [x], custo + x * k[i])

    rec(0, [], 0)
    return out


def auc_exata(fs, K):
    """Return the exact AUC of the infinite population, ``E[Phi(sqrt(D2_i + D2_j) / 2)]``.

    Memoized by ``(lam, d, k)`` of each source and ``K``, the only inputs of the enumeration: a
    family-D mixture takes ~2 s to enumerate and the verdict hook needs the same six cells on
    every call. The arithmetic is the one of ``_auc_exata``, unchanged.
    """
    return _auc_exata(tuple((f["lam"], f["d"], f["k"]) for f in fs), K)


@functools.cache
def _auc_exata(chave, K):
    """Return the exact AUC of the sources ``chave`` (tuple of ``(lam, d, k)``); see auc_exata."""
    fs = [dict(lam=lam, d=d, k=k) for lam, d, k in chave]
    comp = comp_final(fs, K)
    d2 = np.array([f["d"] ** 2 for f in fs])
    vals = np.array([np.dot(n, d2) for n, _ in comp])
    w = np.array([p for _, p in comp])
    assert abs(w.sum() - 1) < 1e-9, f"enumeração: massa total {w.sum()} ≠ 1"
    u, inv = np.unique(np.round(vals, 12), return_inverse=True)
    wu = np.bincount(inv, weights=w)
    tot = 0.0
    for i0 in range(0, len(u), 400):
        a = u[i0 : i0 + 400, None]
        tot += float(
            np.sum(wu[i0 : i0 + 400, None] * wu[None, :] * norm.cdf(np.sqrt(a + u[None, :]) / 2))
        )
    return tot


def ep_dif(aR, aRS, g):
    """Return ``SE_Delta``: Hanley-McNeil per combination, in quadrature, over ``sqrt(n_seeds)``."""
    npos = round(g["pi"] * g["N"])
    nneg = g["N"] - npos
    return math.sqrt(
        tab.ep_hanley_mcneil(aR, npos, nneg) ** 2 + tab.ep_hanley_mcneil(aRS, npos, nneg) ** 2
    ) / math.sqrt(len(g["sementes"]))


def sgn(x):
    """Return the sign of ``x`` as a Python int (-1, 0 or +1)."""
    return int(np.sign(x))


# --- analysis per cell ----------------------------------------------------------------------------

LEITORES = (
    ("sem peso", lambda f: 1.0),
    ("peso d²", lambda f: f["d"] ** 2),
    ("peso √d", lambda f: f["d"] ** 0.5),
)
RIVAIS = (("d/k", 1, 1.0), ("d³/k", 3, 1.0), ("d/√k", 1, 0.5), ("d²/k²", 2, 2.0))


def analisar(c, g):
    """Return every analytic quantity of one cell (predictions, tolerances, rivals, mutants)."""
    K, T = g["K"], c["T"]
    R = tab.fontes(c, "R")
    (S,) = tab.fontes(c, "S")
    RS = R + [S]
    aR, aRS = tab.auc(tab.delta2(R, T, K)), tab.auc(tab.delta2(RS, T, K))
    dA = aRS - aR
    dE = auc_exata(RS, K) - auc_exata(R, K)
    ep = ep_dif(aR, aRS, g)
    tolD = g["delta_kat_dif"] + 3 * ep
    tolN = max(tab.tolerancia(R, T, g), tab.tolerancia(RS, T, g))
    WR = tab.W(R)
    rho_S = S["d"] ** 2 / S["k"]
    rho_bar = sum(f["lam"] * f["d"] ** 2 for f in R) / WR
    grade_troca, raiz_troca = limiar(R, RS, T, K, 1.0)
    a = dict(
        id=c["id"],
        familia=c["familia"],
        lado=c["lado"],
        bloco=c["bloco"],
        T=T,
        R=R,
        S=S,
        zR=tab.z_saturacao(R, T, K),
        zRS=tab.z_saturacao(RS, T, K),
        sat=(T * WR >= K, T * tab.W(RS) >= K),
        eventos=T * sum(f["lam"] for f in RS),
        phi=S["lam"] * S["k"] / tab.W(RS),
        rho_S=rho_S,
        rho_bar=rho_bar,
        aR=aR,
        aRS=aRS,
        dA=dA,
        dE=dE,
        ep=ep,
        tolD=tolD,
        tolN=tolN,
        teo=sgn(dA),
        cor1=sgn(rho_S - rho_bar),
        rivais={nome: sgn(V(RS, T, K, p, q) - V(R, T, K, p, q)) for nome, p, q in RIVAIS},
        grade_troca=grade_troca,
        raiz_troca=raiz_troca,
    )
    a["leitores"] = {}
    for nome, w in LEITORES:
        dm = tab.auc(sep_linear(RS, T, K, w)) - tab.auc(sep_linear(R, T, K, w))
        a["leitores"][nome] = dict(
            dm=dm,
            dif=abs(dm - dA),
            sinal=sgn(dm),
            morre=("sinal" if sgn(dm) != a["teo"] else ("EXN" if abs(dm - dA) > tolD else None)),
        )
    if c["familia"] == "C":
        (A,) = R
        a["r"], a["kappa"] = S["d"] / A["d"], S["k"] / A["k"]
        a["e_fechado"] = math.log(a["kappa"]) / math.log(a["r"])
        a["limiar_teo"] = sgn(a["r"] ** 2 - a["kappa"])
    else:
        ws = tuple(f["lam"] / sum(x["lam"] for x in R) for f in R)
        ds = tuple(f["d"] for f in R)
        a["pesos"] = ws
        a["mu"] = {p: pmean(ws, ds, p) for p in (1, 1.6, 2, 2.5, 3)}
        a["limiar_teo"] = sgn(S["d"] - a["mu"][2])
    return a


def conferir(linhas, g):
    """Check the design criteria (section 1.7), rival readings and mutants; named asserts."""
    assert g.get("tag") == 5, f"grade: tag {g.get('tag')!r} ≠ 5"
    assert "tag_r3" not in g, "grade: chave tag_r3 presente (grade nova usa só 'tag')"
    assert g["tag"] not in TAGS_DAS_OUTRAS, (
        f"grade: tag {g['tag']} colide com {sorted(TAGS_DAS_OUTRAS)}"
    )
    assert tuple(a["id"] for a in linhas) == IDS, (
        f"grade: ids {[a['id'] for a in linhas]} ≠ {list(IDS)}"
    )
    zmin = g["z_minimo_regime"]
    for a in linhas:
        cid = a["id"]
        assert a["bloco"] == "saturado" and all(a["sat"]), f"{cid}: R ou R∪S fora da saturação"
        assert a["zR"] >= zmin, (
            f"{cid}: R a {a['zR']:.2f} desvios do limiar de saturação (mínimo {zmin})"
        )
        assert a["zRS"] >= zmin, (
            f"{cid}: R∪S a {a['zRS']:.2f} desvios do limiar de saturação (mínimo {zmin})"
        )
        assert a["eventos"] <= g["eventos_max_por_usuario"], (
            f"{cid}: {a['eventos']:.0f} eventos por usuário"
        )
        assert a["teo"] == a["cor1"] != 0, (
            f"{cid}: sinal da forma fechada {a['teo']} ≠ Corolário 1 {a['cor1']}"
        )
        assert a["limiar_teo"] == a["teo"], (
            f"{cid}: limiar da família ({a['limiar_teo']}) ≠ forma fechada"
        )
        assert abs(a["dA"]) >= g["margem_tolD"] * a["tolD"], (
            f"{cid}: |ΔAUC| {abs(a['dA']):.4f} < {g['margem_tolD']}·tolΔ {a['tolD']:.4f}"
        )
        assert abs(a["dA"]) >= g["margem_tol_nivel"] * a["tolN"], (
            f"{cid}: |ΔAUC| {abs(a['dA']):.4f} < {g['margem_tol_nivel']}·tol de nível "
            f"{a['tolN']:.4f}"
        )
        assert abs(a["dE"] - a["dA"]) <= g["vies_max_sobre_tolD"] * a["tolD"], (
            f"{cid}: viés previsto {a['dE'] - a['dA']:+.5f} > {g['vies_max_sobre_tolD']}·tolΔ"
        )
        oposta = "d/k" if a["lado"] == "baixo" else "d³/k"
        assert a["rivais"][oposta] == -a["teo"], (
            f"{cid}: regra {oposta} não prevê o sinal oposto ({a['lado']})"
        )
        faixa = g["faixa_troca_baixo"] if a["lado"] == "baixo" else g["faixa_troca_alto"]
        assert len(a["grade_troca"]) == 1 and len(a["raiz_troca"]) == 1, (
            f"{cid}: {len(a['raiz_troca'])} trocas"
        )
        for rot, v in (("grade", a["grade_troca"][0]), ("raiz", a["raiz_troca"][0])):
            assert faixa[0] <= v <= faixa[1], (
                f"{cid}: ponto de troca ({rot}) {v:.4f} fora de {faixa}"
            )
        if a["familia"] == "C":
            assert len(a["R"]) == 1 and a["S"]["k"] != a["R"][0]["k"], (
                f"{cid}: família C exige R de fonte única e k_S ≠ k_A"
            )
            assert abs(a["raiz_troca"][0] - a["e_fechado"]) < 1e-6, (
                f"{cid}: raiz {a['raiz_troca'][0]:.6f} ≠ ln κ/ln r {a['e_fechado']:.6f}"
            )
        else:
            assert all(f["k"] == 14 for f in a["R"] + [a["S"]]), (
                f"{cid}: família D exige k = 14 em todas as fontes"
            )
            assert len(a["R"]) == 2 and a["R"][0]["d"] != a["R"][1]["d"], (
                f"{cid}: família D exige R com 2 fontes de d diferente"
            )
            mu_na_raiz = pmean(a["pesos"], tuple(f["d"] for f in a["R"]), a["raiz_troca"][0])
            assert abs(mu_na_raiz - a["S"]["d"]) < 1e-9, (
                f"{cid}: na raiz, μ_p = {mu_na_raiz:.6f} ≠ d_S"
            )
    teo = {a["id"]: a["teo"] for a in linhas}
    assert sorted(teo.values()) == [-1, -1, -1, 1, 1, 1], (
        f"direções: {teo} (esperado 3 melhora e 3 piora)"
    )

    def opostos(nome):
        """Return the ids of the cells where rival ``nome`` predicts the sign opposite to theory."""
        return {a["id"] for a in linhas if a["rivais"][nome] == -a["teo"]}

    for nome, esperado in (
        ("d/k", {"EXP-C1", "EXP-C2", "EXP-D1"}),
        ("d³/k", {"EXP-C3", "EXP-C4", "EXP-D2"}),
        ("d/√k", {"EXP-D1"}),
        ("d²/k²", {"EXP-C1", "EXP-C2"}),
    ):
        assert opostos(nome) == esperado, (
            f"rival {nome}: oposto em {sorted(opostos(nome))} ≠ {sorted(esperado)}"
        )
    # reader mutants (fluid prediction; the real verdict comes from mutation on the simulation)
    morte = {nome: {a["id"]: a["leitores"][nome]["morre"] for a in linhas} for nome, _ in LEITORES}
    assert morte["sem peso"] == {i: ("sinal" if i == "EXP-D1" else "EXN") for i in IDS}, (
        f"mutante leitor sem peso: {morte['sem peso']}"
    )
    assert all(a["leitores"]["peso d²"]["sinal"] == a["teo"] for a in linhas), (
        "mutante peso d²: sinal difere"
    )
    assert morte["peso d²"] == {i: "EXN" for i in IDS}, f"mutante peso d²: {morte['peso d²']}"
    assert morte["peso √d"] == {i: ("EXN" if i.startswith("EXP-D") else None) for i in IDS}, (
        f"mutante peso √d: {morte['peso √d']}"
    )


# --- pre-registered verdict (section 1.9), called by code/run_grid.py ----------------------------

# reading of an EXS failure, fixed before the data (section 1.10), by (family, side) of the cell
LEITURA_EXS = {
    ("C", "baixo"): "the simulated pipeline behaves as a ratio p/q <= 1.6",
    ("D", "baixo"): "the simulated pipeline behaves as p <= 1.6 (reader without the d weight)",
    ("C", "alto"): "the simulated pipeline behaves as an exponent above 2.5",
    ("D", "alto"): "the simulated pipeline behaves as an exponent above 2.5",
}
# reading of an EXS tie (section 1.10, "tie -> fails for lack of power"): no reading of the reader
LEITURA_EMPATE = "tie: |predicted| < 3 SE_emp, fails for lack of power"
# run parameters that must equal the frozen grid for the verdict to count (``run_grid.py`` can
# override N and the block size in a smoke run; the seeds fix the between-seed standard error)
PARAMETROS_DO_RUN = ("N", "sementes", "bloco_usuarios")


def _intervalo_implicado(analises, familia):
    """Return ``[max low-side switch, min high-side switch]`` of ``familia``, 3 decimals."""
    raizes = {
        lado: [
            a["raiz_troca"][0]
            for a in analises.values()
            if a["familia"] == familia and a["lado"] == lado
        ]
        for lado in ("baixo", "alto")
    }
    return [round(max(raizes["baixo"]), 3), round(min(raizes["alto"]), 3)]


def veredito(linhas, grade):
    """Apply the pre-registered criteria EXS and EXN (section 1.9) to the rows of a run.

    EXS is the ``KT_S`` of ``token_kat.avaliar_kat`` (section 1.13): the sign of
    ``mean(AUC(R ∪ S)) - mean(AUC(R))`` over the seeds equals the predicted sign in every cell;
    one disagreement fails, and ``|predicted| < 3 SE_emp`` (between-seed variance, ``ddof = 1``)
    is a tie that fails for lack of power. EXN: ``|dif_empirica - dif_prevista| <= tolDelta`` in
    every cell, with the FROZEN ``tolDelta = delta_kat_dif + 3 * SE_Delta`` of the cell
    (``analisar``, arithmetic of the analytic table; never recomputed from the data, never the
    level tolerance of the token KAT). The level per combination against the token KAT tolerance,
    the recovered ``Delta^2``, the idle tokens and the saturated fraction are report-only and live
    in the ``avaliar_kat`` and ``diagnostico`` blocks of ``resumo.json``.

    Parameters
    ----------
    linhas : list of dict
        Result rows (``celula``, ``combo``, ``semente``, ``auc``) of every cell of ``grade`` x
        (R, R ∪ S) x seed.
    grade : dict
        The loaded grid, possibly filtered to some cells by ``run_grid.py --celulas``.

    Returns
    -------
    dict
        JSON-serializable verdict: ``EXS``, ``EXN``, ``completo`` (the six pre-registered cells
        were run with the N, seeds and block size of the frozen grid on disk; a ``--celulas``
        filter or a smoke override makes it False), ``passou`` (EXS and EXN and completo),
        ``desfecho`` (``passa``, ``reprova_EXS``, ``reprova_so_EXN`` or ``incompleto``: the
        outcome rows of section 1.10), ``leitura_EXS`` (reading of each cell that failed EXS: the
        reading of its family and side for a sign disagreement, ``LEITURA_EMPATE`` for a tie),
        ``por_celula`` and, only when the run is complete and EXS passes, ``intervalo_implicado``
        (report-only, for the simulated pipeline, not for the world).

    Raises
    ------
    ValueError
        If a row is missing (from ``avaliar_kat``) or if the predicted sign of
        ``token_kat.auc_fluida`` differs from the sign of the analytic table.
    """
    aval = kt.avaliar_kat(linhas, grade, run_token_kat.tolerancias(grade))
    analises = {c["id"]: analisar(c, grade) for c in grade["celulas"]}
    por_celula, leitura, estouros = [], {}, 0
    for pc in aval["por_celula"]:
        a = analises[pc["celula"]]
        if sgn(pc["dif_prevista"]) != a["teo"]:
            raise ValueError(f"{pc['celula']}: predicted sign differs from the analytic table")
        desvio = pc["dif_empirica"] - pc["dif_prevista"]
        dentro = abs(desvio) <= a["tolD"]
        estouros += not dentro
        if pc["sinal"] == "discorda":
            leitura[pc["celula"]] = LEITURA_EXS[(a["familia"], a["lado"])]
        elif pc["sinal"] == "empate":
            leitura[pc["celula"]] = LEITURA_EMPATE
        por_celula.append(
            {
                "celula": pc["celula"],
                "familia": a["familia"],
                "lado": a["lado"],
                "sinal_teoria": a["teo"],
                "dif_prevista": pc["dif_prevista"],
                "dif_empirica": pc["dif_empirica"],
                "ep_emp": pc["ep_dif"],
                "EXS": pc["sinal"],
                "sinais_por_semente": pc["sinais_por_semente"],
                "desvio": desvio,
                "tolD": a["tolD"],
                "desvio_sobre_tolD": abs(desvio) / a["tolD"],
                "EXN_dentro": dentro,
                "dif_exata": a["dE"],
                "desvio_exato_em_ep": (
                    abs(pc["dif_empirica"] - a["dE"]) / pc["ep_dif"] if pc["ep_dif"] > 0 else None
                ),
            }
        )
    exs = dict(aval["KT_S"])
    exn = {"passou": estouros == 0, "celulas": len(por_celula), "estouros": estouros}
    congelada = kt.carregar_grade(GRADE)
    completo = tuple(c["id"] for c in grade["celulas"]) == IDS and all(
        grade[p] == congelada[p] for p in PARAMETROS_DO_RUN
    )
    if not completo:
        desfecho = "incompleto"
    elif exs["passou"] and exn["passou"]:
        desfecho = "passa"
    elif not exs["passou"]:
        desfecho = "reprova_EXS"
    else:
        desfecho = "reprova_so_EXN"
    out = {
        "EXS": exs,
        "EXN": exn,
        "completo": completo,
        "passou": desfecho == "passa",
        "desfecho": desfecho,
        "leitura_EXS": leitura,
        "por_celula": por_celula,
    }
    if completo and exs["passou"]:
        out["intervalo_implicado"] = {
            "C": {"p_sobre_q": _intervalo_implicado(analises, "C")},
            "D": {"p": _intervalo_implicado(analises, "D")},
        }
    return out


def main(argv=None) -> int:
    """Print the analytic tables of the grid; return 0 only if every design criterion passes."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grade", type=Path, default=GRADE)
    args = ap.parse_args(argv)
    bruto = args.grade.read_bytes()
    g = json.loads(bruto)
    linhas = [analisar(c, g) for c in g["celulas"]]
    conferir(linhas, g)

    def mv(s):
        """Return the Portuguese label of a sign ("melhora" if positive, else "piora")."""
        return "melhora" if s > 0 else "piora"

    print(
        f"grade sha256 {hashlib.sha256(bruto).hexdigest()} · K = {g['K']} · N = {g['N']} · "
        f"sementes = {len(g['sementes'])} · tag = {g['tag']} · tol_base_r1 = {g['tol_base_r1']} · "
        f"delta_kat_dif = {g['delta_kat_dif']}"
    )
    print(
        "Tabela 1 — previsões por célula (forma fechada fluida; exato = enumeração da janela "
        "saturada; sem sorteio)"
    )
    print(
        "| célula | família | lado | T | z(R) | z(R∪S) | eventos/usuário | φ′_S | ρ_S | "
        "ρ̄ (ocupação) | AUC(R) | "
        "AUC(R∪S) | ΔAUC fluido | ΔAUC exato | viés (exato − fluido) | EP_Δ | tolΔ | ΔAUC/tolΔ | "
        "tol nível KAT | "
        "ΔAUC/tol nível |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for a in linhas:
        print(
            f"| {a['id']} | {a['familia']} | {a['lado']} | {a['T']} | {a['zR']:.2f} | "
            f"{a['zRS']:.2f} | "
            f"{a['eventos']:.0f} | {a['phi']:.3f} | {a['rho_S']:.6f} | {a['rho_bar']:.6f} | "
            f"{a['aR']:.4f} | "
            f"{a['aRS']:.4f} | {a['dA']:+.4f} | {a['dE']:+.4f} | {a['dE'] - a['dA']:+.5f} | "
            f"{a['ep']:.5f} | "
            f"{a['tolD']:.4f} | {abs(a['dA']) / a['tolD']:.2f} | {a['tolN']:.4f} | "
            f"{abs(a['dA']) / a['tolN']:.2f} |"
        )
    print(
        "Tabela 2 — sinais previstos de ΔAUC: teoria (d²/k), regras rivais H(p, q) e leitores "
        "lineares"
    )
    print(
        "| célula | teoria (d²/k) | d/k | d³/k | d/√k | d²/k² | leitor sem peso | leitor peso d² |"
    )
    print("|---|---|---|---|---|---|---|---|")
    for a in linhas:
        rv = a["rivais"]
        print(
            f"| {a['id']} | {mv(a['teo'])} | {mv(rv['d/k'])} | {mv(rv['d³/k'])} | "
            f"{mv(rv['d/√k'])} | "
            f"{mv(rv['d²/k²'])} | {mv(a['leitores']['sem peso']['sinal'])} | "
            f"{mv(a['leitores']['peso d²']['sinal'])} |"
        )
    print(
        "Tabela 3 — limiar da teoria e ponto de troca de sinal da regra rival H(p, 1) (na família "
        "C, a razão p/q)"
    )
    print(
        "| célula | família | limiar da teoria | troca (grade de passo 0,0005) | "
        "troca (raiz exata) |"
    )
    print("|---|---|---|---|---|")
    for a in linhas:
        if a["familia"] == "C":
            lt = (
                f"r = {a['r']:.3f} {'>' if a['limiar_teo'] > 0 else '<'} "
                f"√κ = {math.sqrt(a['kappa']):.3f} "
                f"(κ = {a['kappa']:.4f}; ln κ/ln r = {a['e_fechado']:.4f}): {mv(a['limiar_teo'])}"
            )
        else:
            lt = (
                f"d_S = {a['S']['d']:.3f} {'>' if a['limiar_teo'] > 0 else '<'} "
                f"μ_2 = {a['mu'][2]:.4f}: "
                f"{mv(a['limiar_teo'])}"
            )
        print(
            f"| {a['id']} | {a['familia']} | {lt} | {a['grade_troca'][0]:.4f} | "
            f"{a['raiz_troca'][0]:.6f} |"
        )
    for a in linhas:
        if a["familia"] == "D":
            mu = a["mu"]
            print(
                f"{a['id']}: pesos de taxa em R = ({a['pesos'][0]:.2f}; {a['pesos'][1]:.2f}) · "
                f"μ_1 = {mu[1]:.4f} · μ_1,6 = {mu[1.6]:.4f} · μ_2 = {mu[2]:.4f} · "
                f"μ_2,5 = {mu[2.5]:.4f} · "
                f"μ_3 = {mu[3]:.4f}"
            )
    print(
        "Tabela 4 — mutantes de leitor: ΔAUC fluido que o leitor mutante produziria × teoria "
        "(onde morre)"
    )
    print(
        "| leitor | célula | ΔAUC teoria | ΔAUC mutante | desvio absoluto | tolΔ | desvio/tolΔ | "
        "desfecho previsto |"
    )
    print("|---|---|---|---|---|---|---|---|")
    rotulo = {
        "sinal": "morre por sinal (EXS)",
        "EXN": "morre por nível da diferença (EXN)",
        None: "sobrevive",
    }
    for nome, _ in LEITORES:
        for a in linhas:
            m = a["leitores"][nome]
            print(
                f"| {nome} | {a['id']} | {a['dA']:+.4f} | {m['dm']:+.4f} | {m['dif']:.4f} | "
                f"{a['tolD']:.4f} | "
                f"{m['dif'] / a['tolD']:.2f} | {rotulo[m['morre']]} |"
            )
    n_sim = len(linhas) * 2 * len(g["sementes"])
    ev = sum(
        g["N"]
        * a["T"]
        * (sum(f["lam"] for f in a["R"]) + sum(f["lam"] for f in a["R"] + [a["S"]]))
        * len(g["sementes"])
        for a in linhas
    )
    print(
        f"eventos gerados ({len(linhas)} células × 2 combos × {len(g['sementes'])} sementes = "
        f"{n_sim} simulações): "
        f"{ev:.3e}; razão ao run do KAT ({EVENTOS_KAT:.3e} eventos, {SEGUNDOS_KAT} s com 8 "
        f"processos) = "
        f"{ev / EVENTOS_KAT:.3f} -> ~{SEGUNDOS_KAT * ev / EVENTOS_KAT:.0f} s (escala linear; "
        f"estimativa, não medição)"
    )
    print(
        f"CRITÉRIOS DE DESENHO: todos passaram (tag = {g['tag']}, sem tag_r3; R e R∪S saturadas "
        f"a z ≥ "
        f"{g['z_minimo_regime']}; eventos ≤ {g['eventos_max_por_usuario']}; |ΔAUC fluido| ≥ "
        f"{g['margem_tolD']}·tolΔ "
        f"e ≥ {g['margem_tol_nivel']}·tol de nível; forma fechada = Corolário 1 = limiar da "
        f"família; d/k oposto no "
        f"lado baixo e d³/k no alto; troca em {g['faixa_troca_baixo']} (baixo) e "
        f"{g['faixa_troca_alto']} (alto); "
        f"|viés| ≤ {g['vies_max_sobre_tolD']}·tolΔ; família C com R de fonte única e k_S ≠ k_A; "
        f"família D com "
        f"k = 14 e duas fontes em R; 3 melhora e 3 piora; d/√k oposto só em D1; d²/k² oposto só "
        f"em C1 e C2; "
        f"mutantes de leitor onde a Tabela 4 diz)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
