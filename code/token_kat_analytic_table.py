#!/usr/bin/env python3
"""Analytic table of the token KAT: pure arithmetic, standard library only, NO simulation.

Reads the pre-registered grid ``data/kat_token_grid.json`` and, for each cell (current mixture
``R`` -> ``R ∪ S``), computes the prediction of the fluid closed form of the theory
(``docs/THEORY.md``): ``W = sum(lam_s k_s)``, ``h = min(T, K / W)``,
``Delta^2 = h * sum(lam_s d_s^2)``, ``AUC = Phi(sqrt(Delta^2 / 2))``. It classifies the regime
(saturated / mixed / unsaturated) and checks that the sign of the change in ``Delta^2`` is the one
of the applicable corollary: Corollary 1 (``rho_S`` against the occupancy-weighted ``rho_bar``),
the mixed-regime Observation (``rho_S`` against ``theta * rho_bar``) or Corollary 3 (always
improves). It also checks the design criteria of the addendum: regime at ``z >= z_min`` standard
deviations from the saturation threshold (tokens per user ~ compound Poisson), at most
``eventos_max`` events per user, ``|dAUC| >= margin * tol`` and the declared naive rule predicting
the OPPOSITE sign.

Level tolerance per combination (declared in the addendum, computed here before any simulation):
``tol = tol_base_r1 + disc + 3 * SE_mean``; ``tol_base_r1`` = largest |mean AUC - fluid AUC| of
the sealed replication run (0.007801 over the 5,040 cell x combination pairs, rounded UP);
``disc`` = whole-event bias in the saturated regime, up to ``k_max`` idle tokens:
``(dAUC/dDelta^2) * Delta^2 * k_max / K``; ``SE_mean`` = Hanley-McNeil with the ``N`` and the
prevalence of the grid, divided by ``sqrt(n_seeds)``. ``tolerancia`` uses ``statistics.NormalDist``
verbatim (never unified with scipy: the last float digit would change).

The standard output is kept VERBATIM in Portuguese: it is the frozen pre-registration artifact
``data/prereg/kat_token_analytic_table.txt`` (reproduced byte for byte by
``tests/test_token_kat.py``).

Usage: ``python3 code/token_kat_analytic_table.py [--grade data/kat_token_grid.json]``. Output:
table on stdout; exit 0 only if every design criterion passes (named assert otherwise).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

_N01 = NormalDist()
RAIZ = Path(__file__).resolve().parent.parent


def fontes(cel: dict, qual: str) -> list[dict]:
    """Return the sources of ``cel[qual]`` as a list of dicts with a ``nome`` key."""
    return [dict(nome=n, **p) for n, p in cel[qual].items()]


def W(fs):
    """Return the token occupancy rate ``sum(lam * k)``."""
    return sum(f["lam"] * f["k"] for f in fs)


def delta2(fs, T, K):
    """Return the fluid ``Delta^2 = min(T, K / W) * sum(lam * d^2)``."""
    h = min(T, K / W(fs))
    return h * sum(f["lam"] * f["d"] ** 2 for f in fs)


def auc(d2):
    """Return ``Phi(sqrt(d2 / 2))``."""
    return _N01.cdf(math.sqrt(d2 / 2))


def inclinacao(d2):
    """Return dAUC/dDelta^2 of ``Phi(sqrt(Delta^2 / 2))``."""
    x = math.sqrt(d2 / 2)
    return _N01.pdf(x) / (2 * math.sqrt(2 * d2))


def z_saturacao(fs, T, K):
    """Return (expected tokens - K) / standard deviation; tokens = sum(k_s * Poisson(lam_s T))."""
    media = T * W(fs)
    dp = math.sqrt(T * sum(f["lam"] * f["k"] ** 2 for f in fs))
    return (media - K) / dp


def ep_hanley_mcneil(A, n_pos, n_neg):
    """Return the Hanley-McNeil (1982) standard error of an AUC."""
    Q1 = A / (2 - A)
    Q2 = 2 * A**2 / (1 + A)
    return math.sqrt(
        (A * (1 - A) + (n_pos - 1) * (Q1 - A**2) + (n_neg - 1) * (Q2 - A**2)) / (n_pos * n_neg)
    )


def tolerancia(fs, T, g):
    """Return the pre-registered level tolerance of one combination of sources."""
    K = g["K"]
    d2 = delta2(fs, T, K)
    saturado = T * W(fs) >= K
    disc = inclinacao(d2) * d2 * max(f["k"] for f in fs) / K if saturado else 0.0
    n_pos = round(g["pi"] * g["N"])
    ep = ep_hanley_mcneil(auc(d2), n_pos, g["N"] - n_pos) / math.sqrt(len(g["sementes"]))
    return g["tol_base_r1"] + disc + 3 * ep


def sinal(x):
    """Return the sign of ``x`` as -1, 0 or +1."""
    return (x > 0) - (x < 0)


def analisar(cel: dict, g: dict) -> dict:
    """Return every analytic quantity of one cell (regime, z, rho, theta, AUCs, predicted signs)."""
    K, T = g["K"], cel["T"]
    R, (S,) = fontes(cel, "R"), fontes(cel, "S")
    RS = R + [S]
    WR, Wn = W(R), W(RS)
    sat_R, sat_RS = T * WR >= K, T * Wn >= K
    rho_S = S["d"] ** 2 / S["k"]
    rho_bar = sum(f["lam"] * f["d"] ** 2 for f in R) / WR  # occupancy-weighted
    rho_bar_taxa = sum(f["lam"] * f["d"] ** 2 / f["k"] for f in R) / sum(f["lam"] for f in R)
    media_d2_evento = sum(f["lam"] * f["d"] ** 2 for f in R) / sum(f["lam"] for f in R)
    lamk_S = S["lam"] * S["k"]
    theta = WR * (T * Wn - K) / (K * lamk_S) if (not sat_R and sat_RS) else None

    d2_R, d2_RS = delta2(R, T, K), delta2(RS, T, K)
    auc_R, auc_RS = auc(d2_R), auc(d2_RS)
    d_auc = auc_RS - auc_R
    tol = max(tolerancia(R, T, g), tolerancia(RS, T, g))

    if sat_R:
        regime, pred_corolario = "saturado", sinal(rho_S - rho_bar)  # Corollary 1
    elif sat_RS:
        regime, pred_corolario = "misto", sinal(rho_S - theta * rho_bar)  # mixed-regime Observation
    else:
        regime, pred_corolario = "nao_saturado", +1  # Corollary 3 (d_S > 0)

    ingenua = {
        "evento": sinal(S["d"] ** 2 - media_d2_evento),
        "taxa": sinal(rho_S - rho_bar_taxa),
        "cor1_fora_da_saturacao": sinal(rho_S - rho_bar),
        "monotonia": +1,
    }[cel["regra_ingenua"]]

    return dict(
        id=cel["id"],
        bloco=cel["bloco"],
        regime=regime,
        T=T,
        z_R=z_saturacao(R, T, K),
        z_RS=z_saturacao(RS, T, K),
        eventos=T * sum(f["lam"] for f in RS),
        rho_S=rho_S,
        rho_bar=rho_bar,
        rho_bar_taxa=rho_bar_taxa,
        theta=theta,
        d2_R=d2_R,
        d2_RS=d2_RS,
        auc_R=auc_R,
        auc_RS=auc_RS,
        d_auc=d_auc,
        tol=tol,
        pred_forma_fechada=sinal(d2_RS - d2_R),
        pred_corolario=pred_corolario,
        regra_ingenua=cel["regra_ingenua"],
        pred_ingenua=ingenua,
    )


def conferir(a: dict, g: dict) -> None:
    """Check the design criteria of the addendum; each assert names the cell and the criterion."""
    cid = a["id"]
    assert a["regime"] == a["bloco"], (
        f"{cid}: regime calculado {a['regime']} ≠ bloco declarado {a['bloco']}"
    )
    zmin = g["z_minimo_regime"]
    lado_R = a["z_R"] >= zmin if a["regime"] == "saturado" else a["z_R"] <= -zmin
    lado_RS = a["z_RS"] <= -zmin if a["regime"] == "nao_saturado" else a["z_RS"] >= zmin
    assert lado_R, f"{cid}: R a {a['z_R']:.2f} desvios do limiar de saturação (mínimo {zmin})"
    assert lado_RS, f"{cid}: R∪S a {a['z_RS']:.2f} desvios do limiar de saturação (mínimo {zmin})"
    assert a["eventos"] <= g["eventos_max_por_usuario"], (
        f"{cid}: {a['eventos']:.0f} eventos por usuário"
    )
    assert a["pred_forma_fechada"] == a["pred_corolario"] != 0, (
        f"{cid}: sinal da forma fechada {a['pred_forma_fechada']} ≠ corolário {a['pred_corolario']}"
    )
    assert abs(a["d_auc"]) >= g["margem_minima_sobre_tol"] * a["tol"], (
        f"{cid}: |ΔAUC| {abs(a['d_auc']):.4f} < {g['margem_minima_sobre_tol']}·tol {a['tol']:.4f}"
    )
    assert a["pred_ingenua"] == -a["pred_forma_fechada"], (
        f"{cid}: regra ingênua '{a['regra_ingenua']}' não prevê o sinal oposto"
    )


def main(argv=None) -> int:
    """Print the analytic table of the grid; return 0 only if every design criterion passes."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grade", type=Path, default=RAIZ / "data/kat_token_grid.json")
    args = ap.parse_args(argv)
    bruto = args.grade.read_bytes()
    g = json.loads(bruto)
    linhas = [analisar(c, g) for c in g["celulas"]]
    for a in linhas:
        conferir(a, g)
    # pairs with the same (R, S) and only lam_S different: constant sign when saturated,
    # inverted sign in the mixed regime
    por_id = {a["id"]: a for a in linhas}
    assert por_id["S1a"]["pred_forma_fechada"] == por_id["S1b"]["pred_forma_fechada"], (
        "S1: sinal muda com λ_S"
    )
    assert por_id["S2a"]["pred_forma_fechada"] == por_id["S2b"]["pred_forma_fechada"], (
        "S2: sinal muda com λ_S"
    )
    assert por_id["MIX1"]["pred_forma_fechada"] == -por_id["MIX2"]["pred_forma_fechada"], (
        "MIX: sinal não inverte com λ_S"
    )

    print(
        f"grade sha256 {hashlib.sha256(bruto).hexdigest()} · K = {g['K']} · N = {g['N']} · "
        f"sementes = {len(g['sementes'])} · tol_base_r1 = {g['tol_base_r1']}"
    )
    print(
        "| célula | regime | T | z(R) | z(R∪S) | eventos/usuário | ρ_S | ρ̄ (ocupação) | "
        "ρ̄ (taxa) | θ | AUC(R) | AUC(R∪S) | ΔAUC previsto | tol | ΔAUC/tol | forma fechada | "
        "regra ingênua |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for a in linhas:
        theta = "—" if a["theta"] is None else f"{a['theta']:.4f}"
        mf = "melhora" if a["pred_forma_fechada"] > 0 else "piora"
        mi = "melhora" if a["pred_ingenua"] > 0 else "piora"
        print(
            f"| {a['id']} | {a['regime']} | {a['T']} | {a['z_R']:.2f} | {a['z_RS']:.2f} | "
            f"{a['eventos']:.0f} | {a['rho_S']:.6f} | {a['rho_bar']:.6f} | "
            f"{a['rho_bar_taxa']:.6f} | {theta} | {a['auc_R']:.4f} | {a['auc_RS']:.4f} | "
            f"{a['d_auc']:+.4f} | {a['tol']:.4f} | {abs(a['d_auc']) / a['tol']:.2f} | {mf} | "
            f"{a['regra_ingenua']}: {mi} |"
        )
    print(
        "CRITÉRIOS DE DESENHO: todos passaram (regime a z ≥ z_min, eventos ≤ máximo, forma fechada "
        "= corolário, margem ≥ 1,2·tol, regra ingênua oposta; S1/S2 com sinal constante em λ_S; "
        "MIX1/MIX2 com sinal invertido)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
