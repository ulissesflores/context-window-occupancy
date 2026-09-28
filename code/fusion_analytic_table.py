#!/usr/bin/env python3
"""Analytic table of the CMP addendum (event fusion, Corollary 4(b)): arithmetic, NO simulation.

Reads the pre-registered grid ``data/fusion_grid.json`` (optional ``--grade``) and, for each cell
and arm (``R``; ``RS`` = new source raw; ``RF`` = fused without loss, ``(lam/m, sqrt(m) d, k')``;
``RP`` = representative, ``d`` NOT preserved, ``(lam/m, d, k')``), computes the fluid closed form
of the token KAT (``W = sum(lam k)``, ``h = min(T, K / W)``, ``Delta^2 = h * sum(lam d^2)``,
``AUC = Phi(sqrt(Delta^2 / 2))``), the predictions of the rival rules, the level tolerance (the
token KAT one plus ``disc_bloco``) and the role of each contrast (criterion x report-only). It
checks the design criteria with named asserts (exit != 0 if any fails). First stdout line = sha256
of the bytes of the grid read.

Port of the frozen generator of the pre-registration ``data/prereg/07-fusion-addendum.md``: same
arithmetic, same asserts, same standard output, which is kept VERBATIM in Portuguese because it is
the frozen pre-registration artifact ``data/prereg/fusion_analytic_table.txt`` (reproduced byte
for byte by ``tests/test_fusion.py``, FU4(b)). It imports, without editing,
``token_kat_analytic_table`` (``W``, ``delta2``, ``auc``, ``z_saturacao``, ``tolerancia``,
``ep_hanley_mcneil``, ``inclinacao``). New here: ``z`` of the fused arm (mean with half an
incomplete block), ``disc_bloco``, rivals and criteria.

Usage: ``python3 code/fusion_analytic_table.py [--grade data/fusion_grid.json]``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parent.parent
GRADE = RAIZ / "data/fusion_grid.json"

BRACOS = ("R", "RS", "RF", "RP")
CONTRASTES = (("RS", "R"), ("RF", "R"), ("RP", "R"), ("RF", "RS"), ("RP", "RS"))
# regime (R, RS, RF, RP) required by each block label of the grid
REGIMES = {
    "saturado": ("sat", "sat", "sat", "sat"),
    "misto_para_nao_saturado": ("nao", "sat", "nao", "nao"),
    "nao_saturado": ("nao", "nao", "nao", "nao"),
}
RIVAIS = {"tok", "ideal", "dia", "m", "cor1_sem_saturacao", "monotonia", "p1", "nulo"}
TAG_FAMILIA, TAGS_OUTRAS = 7, {3, 5, 6, 8}
N_CRITERIO, N_NULO = 28, 1


def N_(fs):
    """Return the per-day separability ``sum(lam * d^2)`` of the sources."""
    return sum(f["lam"] * f["d"] ** 2 for f in fs)


def sinal(x):
    """Return the sign of ``x`` as -1, 0 or +1."""
    return (x > 0) - (x < 0)


def z_sat(fs, T, K, fundida=None):
    """Return (expected tokens - K) / standard deviation.

    Fused source: blocks = ceil(n/m) ~ n/m + (m-1)/(2m) (half an incomplete block in the mean);
    Poisson variance of the fused source (conservative).
    """
    if fundida is None:
        return tab.z_saturacao(fs, T, K)
    f, m = fundida
    media = T * tab.W(fs) + f["k"] * (m - 1) / (2 * m)
    return (media - K) / math.sqrt(T * sum(g["lam"] * g["k"] ** 2 for g in fs))


def bracos(cel):
    """Return ``(R, S, SF, SP, m)``: current sources, raw, lossless fused and representative."""
    R = [dict(nome=n, **p) for n, p in cel["R"].items()]
    ((nS, S),) = cel["S"].items()
    S = dict(nome=nS, **S)
    m, kl = cel["m"], cel["k_fund"]
    SF = dict(nome=nS + "f", lam=S["lam"] / m, d=math.sqrt(m) * S["d"], k=kl)  # lossless
    SP = dict(nome=nS + "p", lam=S["lam"] / m, d=S["d"], k=kl)  # representative
    return R, S, SF, SP, m


def pred_corolario(R, X, T, K):
    """Return the sign of R -> R ∪ X by the corollary of the regime (Corollary 1, theta, Cor. 3)."""
    rho_X, rho_bar = X["d"] ** 2 / X["k"], N_(R) / tab.W(R)
    if T * tab.W(R) >= K:
        return "saturado", sinal(rho_X - rho_bar), None
    if T * tab.W(R + [X]) >= K:
        Wl = tab.W(R) + X["lam"] * X["k"]
        th = tab.W(R) * (T * Wl - K) / (K * X["lam"] * X["k"])
        return "misto", sinal(rho_X - th * rho_bar), th
    return "nao_saturado", +1, None


def ep_ind(a1, a0, g):
    """Return the SE of a difference of seed means, independent arms, Hanley-McNeil.

    Upper bound for common random numbers.
    """
    npos = round(g["pi"] * g["N"])
    nneg = g["N"] - npos
    s1 = tab.ep_hanley_mcneil(a1, npos, nneg)
    s0 = tab.ep_hanley_mcneil(a0, npos, nneg)
    return math.sqrt(s1**2 + s0**2) / math.sqrt(len(g["sementes"]))


def analisar(cel, g):
    """Return every analytic quantity of one cell (arms, Delta^2, AUC, z, tol, rho, contrasts)."""
    K, T = g["K"], cel["T"]
    R, S, SF, SP, m = bracos(cel)
    fs = {"R": R, "RS": R + [S], "RF": R + [SF], "RP": R + [SP]}
    D2 = {b: tab.delta2(v, T, K) for b, v in fs.items()}
    A = {b: tab.auc(v) for b, v in D2.items()}
    Z = {
        "R": z_sat(R, T, K),
        "RS": z_sat(R + [S], T, K),
        "RF": z_sat(R + [SF], T, K, (SF, m)),
        "RP": z_sat(R + [SP], T, K, (SP, m)),
    }
    TOL = {b: tab.tolerancia(v, T, g) for b, v in fs.items()}
    rho = dict(S=S["d"] ** 2 / S["k"], SF=SF["d"] ** 2 / SF["k"], SP=SP["d"] ** 2 / SP["k"])
    rho_bar = N_(R) / tab.W(R)
    cor = {b: pred_corolario(R, X, T, K) for b, X in (("RS", S), ("RF", SF), ("RP", SP))}
    A_p1 = {b: tab.auc(K / tab.W(v) * N_(v)) for b, v in fs.items()}  # H_P1: h = K/W, unchecked
    contr = {}
    for a, b in CONTRASTES:
        contr[f"{a}-{b}"] = dict(
            prev=A[a] - A[b],
            tok=(A["RP"] if a == "RF" else A[a]) - (A["RP"] if b == "RF" else A[b]),  # RF as RP
            ideal=(A["RF"] if a == "RP" else A[a]) - (A["RF"] if b == "RP" else A[b]),  # RP as RF
            p1=A_p1[a] - A_p1[b],
            ep=ep_ind(A[a], A[b], g),
        )
    SM = dict(nome="Cm", lam=S["lam"] / m, d=math.sqrt(m) * S["d"], k=S["k"])  # H_m: ignores k'
    return dict(
        fs=fs,
        D2=D2,
        A=A,
        Z=Z,
        TOL=TOL,
        rho=rho,
        rho_bar=rho_bar,
        cor=cor,
        contr=contr,
        ev=T * (sum(f["lam"] for f in R) + S["lam"]),  # GENERATED events per user
        A_m=tab.auc(tab.delta2(R + [SM], T, K)),
        cor1_sem_sat_RF=sinal(rho["SF"] - rho_bar),
    )


def eceil(mu, m):
    """Return E[ceil(n/m)] with n ~ Poisson(mu), summed up to mu + 20 sqrt(mu) + 50."""
    s, p, n = 0.0, math.exp(-mu), 0
    while n < mu + 20 * math.sqrt(mu) + 50:
        s += p * math.ceil(n / m)
        n += 1
        p *= mu / n
    return s


def disc_bloco(cel, braco, a, K):
    """Return the analytic bound of the block effects (fused arms only).

    Anchoring on the most recent member (saturated) or the incomplete block of the representative
    (unsaturated); unsaturated RF = every member visible, exact sum.
    """
    if braco not in ("RF", "RP"):
        return 0.0
    R, S, SF, SP, m = bracos(cel)
    X = SF if braco == "RF" else SP
    if cel["T"] * tab.W(R + [X]) >= K:
        rho_X, rho_R = X["d"] ** 2 / X["k"], N_(R) / tab.W(R)
        dd = (m - 1) / (2 * m) * X["k"] * abs(rho_X - rho_R)
    elif braco == "RP":
        mu = S["lam"] * cel["T"]
        dd = (eceil(mu, m) - mu / m) * S["d"] ** 2
    else:
        dd = 0.0
    return tab.inclinacao(a["D2"][braco]) * dd


def previsao_rival(cod, v, a):
    """Return (label, prediction) of the rival declared for the contrast; None only for the null."""
    if cod == "tok":
        return "H_tok", v["tok"]
    if cod == "ideal":
        return "H_ideal", v["ideal"]
    if cod == "dia":
        return "H_dia", 0.0
    if cod == "p1":
        return "H_P1", v["p1"]
    if cod == "m":
        return "H_m", a["A_m"] - a["A"]["R"]
    if cod == "cor1_sem_saturacao":
        return "H_c1 (sinal)", a["cor1_sem_sat_RF"]
    if cod == "monotonia":
        return "H_mono (sinal)", +1
    return f"H_P1 {v['p1']:+.4f} · H_tok {v['tok']:+.4f}", None  # null


def conferir_grade(g):
    """Check the header criteria: tag exclusive to the family; tol_0 from the largest KAT ep_dif."""
    assert "tag_r3" not in g, "grade: chave 'tag_r3' proibida em grade nova (use 'tag')"
    assert g["tag"] == TAG_FAMILIA and g["tag"] not in TAGS_OUTRAS, (
        f"grade: tag {g['tag']} ≠ {TAG_FAMILIA} ou colide com {sorted(TAGS_OUTRAS)}"
    )
    assert g["tol_0"] == math.ceil(3 * g["ep_dif_max_kat"] * 1e4) / 1e4, (
        f"grade: tol_0 {g['tol_0']} ≠ ⌈3·ep_dif_max_kat·1e4⌉/1e4"
    )


def main(argv=None) -> int:
    """Print the analytic table of the grid; return 0 only if every design criterion passes."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grade", type=Path, default=GRADE)
    args = ap.parse_args(argv)
    bruto = args.grade.read_bytes()
    g = json.loads(bruto)
    conferir_grade(g)
    K, zmin, margem = g["K"], g["z_minimo_regime"], g["margem_minima_sobre_tol"]
    tol0 = g["tol_0"]
    n_crit = n_nulo = 0
    linhas_cel, linhas_con, linhas_disc, discs = [], [], [], []
    for cel in g["celulas"]:
        cid, T = cel["id"], cel["T"]
        a = analisar(cel, g)
        R, S, SF, SP, m = bracos(cel)
        disc = {b: disc_bloco(cel, b, a, K) for b in BRACOS}
        tol = {b: a["TOL"][b] + disc[b] for b in BRACOS}
        reg = {b: "sat" if T * tab.W(v) >= K else "nao" for b, v in a["fs"].items()}

        assert cel["bloco"] in REGIMES, f"{cid}: bloco '{cel['bloco']}' sem regime declarado"
        assert tuple(reg[b] for b in BRACOS) == REGIMES[cel["bloco"]], (
            f"{cid}: regime R·RS·RF·RP {tuple(reg[b] for b in BRACOS)} ≠ declarado "
            f"{REGIMES[cel['bloco']]}"
        )
        for b in BRACOS:
            z = a["Z"][b]
            assert (z >= zmin) if reg[b] == "sat" else (z <= -zmin), (
                f"{cid}/{b}: z = {z:.2f} a menos de {zmin} desvios do limiar (regime {reg[b]})"
            )
        assert a["ev"] <= g["eventos_max_por_usuario"], (
            f"{cid}: {a['ev']:.0f} eventos gerados por usuário"
        )
        for b in ("RS", "RF", "RP"):
            ff = sinal(a["D2"][b] - a["D2"]["R"])
            assert ff == a["cor"][b][1] != 0, (
                f"{cid}/{b}: sinal da forma fechada {ff} ≠ corolário do regime {a['cor'][b][1]}"
            )

        theta = a["cor"]["RS"][2]
        linhas_cel.append(
            f"| {cid} | {T} | {m} | {S['k']} -> {cel['k_fund']} | "
            + " · ".join(reg[b] for b in BRACOS)
            + " | "
            + " · ".join(f"{a['Z'][b]:+.2f}" for b in ("R", "RS", "RF"))
            + f" | {a['ev']:.0f} | "
            f"{a['rho']['S']:.6f} | {a['rho']['SF']:.6f} | {a['rho']['SP']:.6f} | "
            f"{a['rho_bar']:.6f} | "
            + ("—" if theta is None else f"{theta:.4f}")
            + " | "
            + " · ".join(f"{a['A'][b]:.4f}" for b in BRACOS)
            + " | "
            + " · ".join(f"{tol[b]:.4f}" for b in BRACOS)
            + " |"
        )
        for b in ("RF", "RP"):
            discs.append((disc[b], disc[b] / tol[b], cid, b))
        linhas_disc.append(
            f"| {cid} | {reg['RF']} · {reg['RP']} | {disc['RF']:.4f} | {disc['RP']:.4f} | "
            f"{100 * disc['RF'] / tol['RF']:.1f}% | {100 * disc['RP'] / tol['RP']:.1f}% |"
        )

        declarados = dict(cel["discrimina"])
        for cod in declarados.values():
            assert cod in RIVAIS, f"{cid}: rival '{cod}' desconhecido"
        for c, v in a["contr"].items():
            x, y = c.split("-")
            t = max(tol[x], tol[y])
            prev = v["prev"]
            cod = declarados.get(c)
            nulo = cod == "nulo"
            rival, prev_riv = ("—", None) if cod is None else previsao_rival(cod, v, a)
            if nulo:
                n_nulo += 1
                assert abs(prev) <= 1e-12, f"{cid} {c}: nulo com ΔAUC previsto {prev:+.2e} ≠ 0"
                for nome in ("p1", "tok"):
                    assert abs(v[nome]) >= margem * tol0, (
                        f"{cid} {c}: rival {nome} {v[nome]:+.4f} < {margem}·tol_0"
                    )
                papel, riv_txt = "critério (nulo)", rival
            else:
                entra = abs(prev) >= margem * t and abs(prev) >= 3 * v["ep"]
                n_crit += entra
                if cod is not None:
                    assert entra, (
                        f"{cid} {c}: contraste discriminante sem margem ({abs(prev) / t:.2f}·tol)"
                    )
                    assert sinal(prev_riv) != sinal(prev), (
                        f"{cid} {c}: rival {cod} não prevê o oposto"
                    )
                papel = "critério" if entra else "só reportado"
                if prev_riv is None:
                    riv_txt = rival
                elif "sinal" in rival:
                    riv_txt = f"{rival}: " + (
                        "melhora" if prev_riv > 0 else ("piora" if prev_riv < 0 else "zero")
                    )
                else:
                    riv_txt = f"{rival} {prev_riv:+.4f}"
            linhas_con.append(
                f"| {cid} | {c.replace('-', ' − ')} | {prev:+.4f} | "
                + ("**nulo**" if nulo else ("melhora" if prev > 0 else "piora"))
                + f" | {riv_txt} | {papel} | "
                + ("—" if nulo else f"{abs(prev) / t:.2f}")
                + " | "
                + ("—" if nulo else f"{abs(prev) / v['ep']:.0f}")
                + " |"
            )
    assert (n_crit, n_nulo) == (N_CRITERIO, N_NULO), (
        f"contagem: {n_crit} contrastes assinados no critério e {n_nulo} nulo "
        f"(declarado {N_CRITERIO} e {N_NULO})"
    )

    print(
        f"grade sha256 {hashlib.sha256(bruto).hexdigest()} · K = {K} · N = {g['N']} · "
        f"sementes = {len(g['sementes'])} · tag = {g['tag']} · tol_base_r1 = {g['tol_base_r1']} · "
        f"tol_0 = {tol0}"
    )
    print(
        "| célula | T | m | k_S -> k′ | regime R · RS · RF · RP | z (R · RS · RF) | "
        "eventos/usuário | ρ_S | ρ_S·m·k_S/k′ (RF) | ρ_S·k_S/k′ (RP) | ρ̄ | θ (RS) | "
        "AUC fluida R · RS · RF · RP | tol R · RS · RF · RP |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    print("\n".join(linhas_cel))
    print()
    print(
        "| célula | contraste | ΔAUC previsto | sinal | rival (previsão) | papel | "
        "\\|Δ\\|/tol | \\|Δ\\|/EP |"
    )
    print("|---|---|---|---|---|---|---|---|")
    print("\n".join(linhas_con))
    print()
    print(
        "| célula | regime RF · RP | disc_bloco RF | disc_bloco RP | disc_bloco/tol RF | "
        "disc_bloco/tol RP |"
    )
    print("|---|---|---|---|---|---|")
    print("\n".join(linhas_disc))
    v_max = max(discs)
    f_max = max(discs, key=lambda t: t[1])
    print(
        f"disc_bloco máximo em valor: {v_max[0]:.4f} ({v_max[2]}/{v_max[3]}; "
        f"{100 * v_max[1]:.1f}% da tol do braço)"
        f" · máximo em fração da tol: {f_max[2]}/{f_max[3]} ({f_max[0]:.4f}; "
        f"{100 * f_max[1]:.1f}%)"
    )
    print()
    print(
        "CRITÉRIOS DE DESENHO: todos passaram (tag exclusiva, tol_0 da grade, regime declarado "
        "por braço, |z| ≥ z_min do lado declarado, eventos ≤ máximo, forma fechada = corolário do "
        "regime, contraste discriminante no critério, rival com sinal oposto ou zero, nulo exato "
        "com rivais ≥ margem·tol_0) · "
        f"contrastes assinados no critério = {n_crit} · nulo = {n_nulo}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
