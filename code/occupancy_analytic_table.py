#!/usr/bin/env python3
"""Analytic table of the occupancy family (open limit (b): token occupancy vs event rate).

Pure arithmetic, standard library only, NO simulation. Reads the frozen grid of the family
(``--grade``, default ``data/occupancy_grid.json``) and the token KAT grid (``--grade-kat``,
default ``data/kat_token_grid.json``: only the cell S3, the total of generated events and the
largest number of events per user are read). For each cell it computes, with the frozen functions
of ``token_kat_analytic_table`` (imported, never edited), the fluid closed-form prediction of
Corollary 1 (``rho_S`` against the occupancy-weighted ``rho_bar``) and the one of the rival rule
(event-rate-weighted ``rho_bar``), the position ``t`` and the ``alpha*`` of the family
``w ~ lam * k**alpha``; it checks the design criteria of the addendum with named asserts (exit != 0
if one fails) and prints design diagnostics outside the criterion (Jensen bias, idle tokens, power,
time). Deterministic; the first line of stdout carries the sha256 of the grid read.

The standard output is kept VERBATIM in Portuguese: it is the frozen pre-registration artifact
``data/prereg/occupancy_analytic_table.txt`` (reproduced byte for byte by
``tests/test_occupancy.py``). Specification: ``data/prereg/06-occupancy-addendum.md``.

Family verdict. ``veredito(linhas, grade)`` is the hook of the shared runner ``code/run_grid.py``:
it computes the pre-registered criteria of section 2.8 of the addendum (OCC-S sign and OCC-N level
on the main family, OCC-L threshold sub-block reported outside the verdict) from the result rows,
with ``token_kat.avaliar_kat`` called twice, as section 2.11 fixes. It imports the simulation
modules lazily, so the table generator itself stays standard-library only.

Usage: ``python3 code/occupancy_analytic_table.py [--grade <json>] [--grade-kat <json>]``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parent.parent
_N01 = NormalDist()

TAG = 6  # stream tag of this family (tag table of the addendum)
TAGS_RESERVADOS = {3, 5, 7, 8}  # token KAT 3 · exponent 5 · fusion 7 · quotas 8
Z_MINIMO = 4.0  # minimum z(R) and z(R ∪ S) (the token KAT used 2.5; S3 had 2.87)
MARGEM_MINIMA = 1.5  # |predicted dAUC| >= 1.5 * tol (the token KAT used 1.2)
VIES_MAX_KAT = (
    0.00191  # largest |empirical - predicted dAUC| of the sealed token KAT run, rounded up
)
PISO_VIES = 10  # criterion outside ``conferir``: |predicted dAUC| >= 10 * VIES_MAX_KAT
FATOR_JENSEN = 1.5  # the Jensen model underestimates ~20% at the worst cell of the replication
FATOR_EP = 1.3  # true SE assumed = 1.3 * SE_HM (sealed token KAT: SE_emp / SE_HM <= 1.15, 4 df)
SEGUNDOS_KAT = 76  # measured wall time of the sealed token KAT run, 8 processes
VEREDITO = ("nucleo", "tres_fontes")  # sub-blocks of the main family (OCC-S and OCC-N)
LIMIAR = ("limiar",)  # OCC-L: outside the verdict


def rho_bar_alfa(fs, alfa):
    """Return the mean of ``rho = d^2 / k`` weighted by ``lam * k**alfa``.

    ``alfa = 1`` is the occupancy weighting; ``alfa = 0`` is the event-rate weighting.
    """
    w = [f["lam"] * f["k"] ** alfa for f in fs]
    return sum(wi * f["d"] ** 2 / f["k"] for wi, f in zip(w, fs, strict=True)) / sum(w)


def alfa_bissecao(fs, rho_S, lo=-6.0, hi=12.0):
    """Return ``alpha*`` with ``rho_bar_alpha* = rho_S`` by bisection (None if outside [lo, hi]).

    Monotone in ``alpha`` with two cost classes.
    """

    def f(a):
        """Return ``rho_bar_alfa(fs, a) - rho_S``."""
        return rho_bar_alfa(fs, a) - rho_S

    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        meio = (lo + hi) / 2
        if f(lo) * f(meio) <= 0:
            hi = meio
        else:
            lo = meio
    return (lo + hi) / 2


def alfa_fechado(fs, rho_S):
    """Return ``alpha*`` in closed form with two cost classes.

    ``ln[L_b (rho_S - rho_b) / (L_c (rho_c - rho_S))] / ln(k_c / k_b)``, where ``L`` is the summed
    rate and ``rho`` the rate-weighted mean of the cheap (``b``) and costly (``c``) classes.
    """
    custos = sorted({f["k"] for f in fs})
    assert len(custos) == 2, f"α* fechado exige duas classes de custo, há {custos}"
    k_b, k_c = custos
    lam_b = sum(f["lam"] for f in fs if f["k"] == k_b)
    lam_c = sum(f["lam"] for f in fs if f["k"] == k_c)
    rho_b = sum(f["lam"] * f["d"] ** 2 / f["k"] for f in fs if f["k"] == k_b) / lam_b
    rho_c = sum(f["lam"] * f["d"] ** 2 / f["k"] for f in fs if f["k"] == k_c) / lam_c
    return math.log(lam_b * (rho_S - rho_b) / (lam_c * (rho_c - rho_S))) / math.log(k_c / k_b)


def _g2(u):
    """Return ``g''(u)`` of ``g(u) = Phi(sqrt(u) / 2)``."""
    z = math.sqrt(u) / 2
    return -_N01.pdf(z) / (16 * u) * (z + 2 / math.sqrt(u))


def vies_jensen(fs, T, K):
    """Return the Jensen bias of the literal AUC (delta method): ``g''(2 mu) * Var(D)``.

    ``D = sum(n_s d_s^2)`` with ``n_s ~ Poisson(lam_s h)``.
    """
    h = min(T, K / tab.W(fs))
    mu = h * sum(f["lam"] * f["d"] ** 2 for f in fs)
    var = h * sum(f["lam"] * f["d"] ** 4 for f in fs)
    return _g2(2 * mu) * var


def vies_ocioso(fs, T, K, ociosos):
    """Return the idle-token bias (whole events) when saturated: ``-(dAUC/dD2) * D2 * idle / K``."""
    if T * tab.W(fs) < K:
        return 0.0
    d2 = tab.delta2(fs, T, K)
    return -tab.inclinacao(d2) * d2 * ociosos / K


def cauda_qui2_4(x):
    """Return ``P(chi2_4 > x) = exp(-x / 2) * (1 + x / 2)``."""
    return math.exp(-x / 2) * (1 + x / 2)


def cauda_normal(z):
    """Return ``P(N(0, 1) > z)``, stable in the tail."""
    return math.erfc(z / math.sqrt(2)) / 2


def gerados(g, cel):
    """Return the events generated for one cell (R and R ∪ S, all seeds, N users)."""
    lam_R = sum(p["lam"] for p in cel["R"].values())
    lam_S = sum(p["lam"] for p in cel["S"].values())
    return len(g["sementes"]) * g["N"] * cel["T"] * (lam_R + (lam_R + lam_S))


def analisar_occ(cel, g):
    """Return one row of the table.

    The frozen ``analisar`` of the token KAT plus ``t``, ``alpha*``, SE_HM, the Jensen and idle
    biases and the window of ``R ∪ S``.
    """
    a = tab.analisar(cel, g)
    K, T = g["K"], cel["T"]
    R, (S,) = tab.fontes(cel, "R"), tab.fontes(cel, "S")
    RS = R + [S]
    a["t"] = (a["rho_S"] - a["rho_bar"]) / (a["rho_bar_taxa"] - a["rho_bar"])
    a["alfa_bis"] = alfa_bissecao(R, a["rho_S"])
    a["alfa_fechado"] = alfa_fechado(R, a["rho_S"])
    n_pos = round(g["pi"] * g["N"])

    def ep(A):
        """Return the Hanley-McNeil SE of the AUC ``A`` with the grid N and prevalence."""
        return tab.ep_hanley_mcneil(A, n_pos, g["N"] - n_pos)

    a["ep_hm"] = math.sqrt(ep(a["auc_R"]) ** 2 + ep(a["auc_RS"]) ** 2) / math.sqrt(
        len(g["sementes"])
    )
    a["jensen_R"], a["jensen_RS"] = vies_jensen(R, T, K), vies_jensen(RS, T, K)
    a["vies_dif"] = a["jensen_RS"] - a["jensen_R"]
    a["ocioso_R"] = vies_ocioso(R, T, K, max(f["k"] for f in R))
    a["ocioso_RS"] = vies_ocioso(RS, T, K, max(f["k"] for f in RS))
    a["tol_R"], a["tol_RS"] = tab.tolerancia(R, T, g), tab.tolerancia(RS, T, g)
    h_RS = min(T, K / tab.W(RS))
    a["janela_RS"] = {f["nome"]: f["lam"] * h_RS for f in RS}
    a["k_S"] = S["k"]
    a["pred_evento"] = tab.analisar({**cel, "regra_ingenua": "evento"}, g)["pred_ingenua"]
    return a


def conferir_grade(g):
    """Check the grid pins: own tag, thresholds of the addendum, rival rule and regime per cell."""
    assert "tag_r3" not in g, (
        "grade nova com a chave 'tag_r3' (o tag desta família vai na chave 'tag')"
    )
    assert g["tag"] == TAG, f"tag {g['tag']} ≠ {TAG}"
    assert g["tag"] not in TAGS_RESERVADOS, (
        f"tag {g['tag']} colide com os reservados {sorted(TAGS_RESERVADOS)}"
    )
    assert g["z_minimo_regime"] == Z_MINIMO, f"z_minimo_regime {g['z_minimo_regime']} ≠ {Z_MINIMO}"
    assert g["margem_minima_sobre_tol"] == MARGEM_MINIMA, (
        f"margem_minima_sobre_tol {g['margem_minima_sobre_tol']} ≠ {MARGEM_MINIMA}"
    )
    assert g["eventos_max_por_usuario"] == 600, (
        f"eventos_max_por_usuario {g['eventos_max_por_usuario']} ≠ 600"
    )
    for c in g["celulas"]:
        assert c["bloco"] == "saturado", f"{c['id']}: bloco {c['bloco']} ≠ saturado"
        assert c["regra_ingenua"] == "taxa", f"{c['id']}: regra rival {c['regra_ingenua']} ≠ taxa"
        assert c["subbloco"] in VEREDITO + LIMIAR, (
            f"{c['id']}: subbloco {c['subbloco']} desconhecido"
        )
        assert c["direcao"] in ("sobe", "desce"), f"{c['id']}: direção {c['direcao']} desconhecida"
    n_ver = sum(c["subbloco"] in VEREDITO for c in g["celulas"])
    n_lim = sum(c["subbloco"] in LIMIAR for c in g["celulas"])
    assert (n_ver, n_lim) == (10, 2), f"veredito {n_ver} + limiar {n_lim} ≠ 10 + 2"


def conferir_celula(a, cel):
    """Check the design criteria outside the frozen ``conferir``, cell by cell."""
    cid = a["id"]
    assert abs(a["d_auc"]) >= PISO_VIES * VIES_MAX_KAT, (
        f"{cid}: |ΔAUC| {abs(a['d_auc']):.4f} < {PISO_VIES} × {VIES_MAX_KAT}"
    )
    if cel["direcao"] == "sobe":
        assert a["rho_bar"] < a["rho_S"] < a["rho_bar_taxa"] and a["d_auc"] > 0, (
            f"{cid}: direção 'sobe' exige ρ̄_ocup < ρ_S < ρ̄_taxa e ΔAUC > 0"
        )
    else:
        assert a["rho_bar_taxa"] < a["rho_S"] < a["rho_bar"] and a["d_auc"] < 0, (
            f"{cid}: direção 'desce' exige ρ̄_taxa < ρ_S < ρ̄_ocup e ΔAUC < 0"
        )
    assert a["alfa_bis"] is not None, f"{cid}: α* fora de [−6, 12]"
    assert abs(a["alfa_bis"] - a["alfa_fechado"]) < 1e-6, (
        f"{cid}: α* bissecção {a['alfa_bis']:.8f} ≠ forma fechada {a['alfa_fechado']:.8f}"
    )


def conferir_pares(g, por_id):
    """Check the core design and return its depth pairs.

    Core = 2 directions x 2 ``k_S`` x 2 depths: each (R, S) at two T with identical fluid
    prediction; 8 distinct (R, S) configurations.
    """

    def chave(c):
        """Return the (R, S) configuration of the cell ``c`` as a canonical string."""
        return json.dumps([c["R"], c["S"]], sort_keys=True)

    grupos = {}
    for c in g["celulas"]:
        grupos.setdefault(chave(c), []).append(c)
    assert len(grupos) == 8, f"{len(grupos)} configurações (R, S) distintas ≠ 8"
    nucleo = [v for v in grupos.values() if v[0]["subbloco"] == "nucleo"]
    assert len(nucleo) == 4, f"núcleo com {len(nucleo)} configurações (R, S) ≠ 4"
    fatores = set()
    pares = []
    for par in nucleo:
        assert len(par) == 2 and par[0]["T"] != par[1]["T"], (
            f"par {[c['id'] for c in par]}: não são dois T distintos"
        )
        assert all(c["subbloco"] == "nucleo" for c in par), (
            f"par {[c['id'] for c in par]} mistura subblocos"
        )
        x, y = (por_id[c["id"]] for c in sorted(par, key=lambda c: c["T"]))
        for campo in ("auc_R", "auc_RS", "d_auc"):
            assert abs(x[campo] - y[campo]) < 1e-12, f"par {x['id']}/{y['id']}: {campo} muda com T"
        fatores.add((par[0]["direcao"], x["k_S"]))
        pares.append((x["id"], y["id"]))
    assert len(fatores) == 4, f"núcleo não cobre 2 direções × 2 k_S: {sorted(fatores)}"
    return sorted(pares)


# --- family verdict (section 2.8 of the addendum), hook of code/run_grid.py ----------------------


def _estados(avaliacao):
    """Return the ids of the cells of an ``avaliar_kat`` result by sign state."""
    out = {"concorda": [], "discorda": [], "empate": []}
    for c in avaliacao["por_celula"]:
        out[c["sinal"]].append(c["celula"])
    return out


def _leitura(completa, estados, occ_s, occ_n):
    """Return the pre-registered reading of the outcome (section 2.9 of the addendum)."""
    if not completa:
        return "incomplete grid: a subset of cells was run; no family verdict"
    discorda, empate = estados["discorda"], estados["empate"]
    if discorda and len(discorda) == len(estados["concorda"] + discorda + empate):
        return (
            "every cell of the main family disagrees: the event-rate weighting is supported and "
            "the occupancy weighting is contradicted by the literal simulation"
        )
    if discorda:
        texto = (
            f"the occupancy weighting is contradicted by the literal simulation at "
            f"{', '.join(discorda)}; the event-rate weighting is not vindicated (mixed pattern, "
            f"read through alpha* of each cell)"
        )
        if discorda == ["OCC10"]:
            texto += "; reads as hypothesis (iii) failing with a sparse window (E[n] < 3)"
        return texto
    if empate:
        return f"fails for lack of power (tie at {', '.join(empate)}); nothing changes in the text"
    if occ_s and occ_n:
        return "event-rate weighting refuted in the 10 cells; sign and level checked"
    return "sign checked (event-rate weighting refuted in the 10 cells), level not"


def veredito(linhas, grade):
    """Return the pre-registered verdict of the family from the result rows of the runner.

    Parameters
    ----------
    linhas : list of dict
        Rows of ``run_token_kat._uma_tarefa`` (keys ``celula``, ``combo``, ``semente``, ``auc``).
    grade : dict
        The loaded grid (not adapted), possibly filtered to a subset of cells by the runner.

    Returns
    -------
    dict
        JSON-serializable: ``criterios`` (OCC-S: 10/10 ``concorda`` with a tie at
        ``|predicted dAUC| < 3 SE_emp``; OCC-N: ``|mean AUC - fluid AUC| <= tol`` in the 20
        combinations, frozen token KAT tolerance), ``passou`` (both, on the complete grid),
        ``leitura`` (section 2.9), ``fora_do_veredito`` (OCC-L), the two ``avaliar_kat`` results
        and the report-only items of section 2.8. The unit tests OCCT1-OCCT3 are a precondition
        checked by ``tests/test_occupancy.py`` before the run, not re-run here.
    """
    import run_token_kat  # lazy: keeps the table generator standard-library only
    import token_kat as kt

    celulas = grade["celulas"]
    principal = [c for c in celulas if c["subbloco"] in VEREDITO]
    limiar = [c for c in celulas if c["subbloco"] in LIMIAR]
    completa = len(principal) == 10 and len(limiar) == 2
    tol = run_token_kat.tolerancias(grade)
    av_principal = kt.avaliar_kat(linhas, {**grade, "celulas": principal}, tol)
    av_limiar = kt.avaliar_kat(linhas, {**grade, "celulas": limiar}, tol)
    est_p, est_l = _estados(av_principal), _estados(av_limiar)
    estouros = [
        f"{c['celula']}/{combo}"
        for c in av_principal["por_celula"]
        for combo in ("R", "RS")
        if not c["nivel"][combo]["dentro"]
    ]
    occ_s = completa and len(est_p["concorda"]) == len(principal) == 10
    occ_n = completa and not estouros

    analise = {c["id"]: analisar_occ(c, grade) for c in celulas}
    por_celula = {c["celula"]: c for c in av_principal["por_celula"] + av_limiar["por_celula"]}

    concordantes_p = est_p["concorda"]
    alfa_p = max((analise[cid]["alfa_bis"] for cid in concordantes_p), default=None)
    limiar_concorda = len(limiar) == 2 and len(est_l["concorda"]) == 2
    alfa_l = (
        max(analise[cid]["alfa_bis"] for cid in concordantes_p + est_l["concorda"])
        if limiar_concorda and concordantes_p
        else None
    )

    grupos = {}
    for c in principal:
        if c["subbloco"] == "nucleo":
            grupos.setdefault(json.dumps([c["R"], c["S"]], sort_keys=True), []).append(c)
    invariancia = []
    for par in grupos.values():
        if len(par) != 2:
            continue
        x, y = (por_celula[c["id"]] for c in sorted(par, key=lambda c: c["T"]))
        diferenca = abs(x["dif_empirica"] - y["dif_empirica"])
        limite = 3 * math.sqrt(x["ep_dif"] ** 2 + y["ep_dif"] ** 2)
        invariancia.append(
            {
                "par": f"{x['celula']}/{y['celula']}",
                "diferenca": diferenca,
                "limite": limite,
                "dentro": diferenca <= limite,
            }
        )
    invariancia.sort(key=lambda p: p["par"])

    vies = {
        cid: {
            "observado": c["dif_empirica"] - c["dif_prevista"],
            "previsto": analise[cid]["vies_dif"],
        }
        for cid, c in sorted(por_celula.items())
    }
    opostas = [
        c["id"]
        for c in celulas
        if analise[c["id"]]["pred_evento"] == -analise[c["id"]]["pred_forma_fechada"]
    ]
    refutada_em = [cid for cid in opostas if por_celula[cid]["sinal"] == "concorda"]

    return {
        "familia": "OCC",
        "grade_completa": completa,
        "criterios": {
            "OCC_S": {
                "regra": (
                    "main family (core + three sources): tie if |predicted dAUC| < 3 SE_emp; "
                    "disagree if the empirical sign differs; passes with 10/10 agree"
                ),
                "celulas": [c["id"] for c in principal],
                **est_p,
                "passou": occ_s,
            },
            "OCC_N": {
                "regra": (
                    "level: |mean(AUC) - fluid AUC| <= tol of the combination (frozen token KAT "
                    "tolerance) in the 20 combinations of the main family"
                ),
                "combos": 2 * len(principal),
                "estouros": estouros,
                "passou": occ_n,
            },
        },
        "testes_unidade": {
            "ids": ["OCCT1", "OCCT2", "OCCT3"],
            "arquivo": "tests/test_occupancy.py",
            "verificados_neste_run": False,
            "nota": "precondition of the verdict, checked by pytest before the run",
        },
        "passou": occ_s and occ_n,
        "leitura": _leitura(completa, est_p, occ_s, occ_n),
        "fora_do_veredito": {
            "OCC_L": {
                "regra": "threshold sub-block: same sign rule, reported apart, outside the verdict",
                "celulas": [c["id"] for c in limiar],
                **est_l,
            }
        },
        "avaliar_kat_principal": av_principal,
        "avaliar_kat_limiar": av_limiar,
        "relatorio": {
            "alfa_minimo": {
                "familia_principal": alfa_p,
                "com_occ_l": alfa_l,
                "alfa_por_celula": {cid: analise[cid]["alfa_bis"] for cid in sorted(analise)},
            },
            "invariancia_em_T": invariancia,
            "vies_observado_vs_previsto": vies,
            "regra_por_evento": {
                "celulas_opostas": opostas,
                "refutada_em": refutada_em,
                "refutada": bool(opostas) and refutada_em == opostas,
            },
        },
    }


def main(argv=None) -> int:
    """Print the analytic table of the grid; return 0 only if every design criterion passes."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grade", type=Path, default=RAIZ / "data/occupancy_grid.json")
    ap.add_argument("--grade-kat", type=Path, default=RAIZ / "data/kat_token_grid.json")
    args = ap.parse_args(argv)
    bruto = args.grade.read_bytes()
    g = json.loads(bruto)
    gk = json.loads(args.grade_kat.read_bytes())

    conferir_grade(g)
    linhas = [analisar_occ(c, g) for c in g["celulas"]]
    por_id = {a["id"]: a for a in linhas}
    for c, a in zip(g["celulas"], linhas, strict=True):
        # frozen: regime, z >= z_min, events <= max, Corollary 1, margin * tol, rate rule opposite
        tab.conferir(a, g)
        conferir_celula(a, c)
    pares = conferir_pares(g, por_id)
    ver = [a for c, a in zip(g["celulas"], linhas, strict=True) if c["subbloco"] in VEREDITO]
    lim = [a for c, a in zip(g["celulas"], linhas, strict=True) if c["subbloco"] in LIMIAR]

    # S3 of the token KAT by the same routine: passes the KAT criteria, fails those of this grid
    (cel_s3,) = [c for c in gk["celulas"] if c["id"] == "S3"]
    s3 = analisar_occ(cel_s3, gk)
    tab.conferir(s3, gk)
    try:
        tab.conferir(s3, g)
    except AssertionError as erro:
        motivo_s3 = str(erro)
    else:
        raise AssertionError("S3: passou nos critérios desta grade; a família não a supera")
    assert "desvios do limiar de saturação" in motivo_s3 and s3["z_R"] < Z_MINIMO, (
        f"S3 reprovou por outro motivo: {motivo_s3}"
    )

    print(
        f"grade sha256 {hashlib.sha256(bruto).hexdigest()} · K = {g['K']} · N = {g['N']} · "
        f"sementes = {len(g['sementes'])} · tol_base_r1 = {g['tol_base_r1']} · tag = {g['tag']} · "
        f"z_minimo_regime = {g['z_minimo_regime']} · "
        f"margem_minima_sobre_tol = {g['margem_minima_sobre_tol']}"
    )
    print(
        "| célula | subbloco | direção | T | z(R) | z(R∪S) | eventos/usuário | ρ_S | ρ̄ ocupação | "
        "ρ̄ taxa | t | α* | AUC(R) | AUC(R∪S) | ΔAUC previsto | tol | ΔAUC/tol | ΔAUC/EP_HM | "
        "viés dif. previsto | ocupação | taxa |"
    )
    print("|" + "---|" * 21)
    for c, a in zip(g["celulas"], linhas, strict=True):
        mo = "melhora" if a["pred_forma_fechada"] > 0 else "piora"
        mt = "melhora" if a["pred_ingenua"] > 0 else "piora"
        print(
            f"| {a['id']} | {c['subbloco']} | {c['direcao']} | {a['T']} | {a['z_R']:.2f} | "
            f"{a['z_RS']:.2f} | {a['eventos']:.0f} | {a['rho_S']:.6f} | {a['rho_bar']:.6f} | "
            f"{a['rho_bar_taxa']:.6f} | {a['t']:.2f} | {a['alfa_bis']:.2f} | {a['auc_R']:.4f} | "
            f"{a['auc_RS']:.4f} | {a['d_auc']:+.4f} | {a['tol']:.4f} | "
            f"{abs(a['d_auc']) / a['tol']:.2f} | {abs(a['d_auc']) / a['ep_hm']:.1f} | "
            f"{a['vies_dif']:+.4f} | {mo} | {mt} |"
        )
    print(
        f"conferência S3 (grade do KAT, mesma rotina): z(R) = {s3['z_R']:.2f} · "
        f"ρ_S = {s3['rho_S']:.6f} · ρ̄ = {s3['rho_bar']:.6f} (ocupação) / "
        f"{s3['rho_bar_taxa']:.6f} (taxa) · ΔAUC = {s3['d_auc']:+.4f} · tol = {s3['tol']:.4f} · "
        f"t = {s3['t']:.2f} · α* = {s3['alfa_bis']:.2f} · critérios do KAT: passa · "
        f"critérios desta grade: reprova (z(R) = {s3['z_R']:.2f} < {Z_MINIMO})"
    )

    print("diagnósticos de desenho (fora do critério):")
    a_ver = max(ver, key=lambda a: a["alfa_bis"])
    a_tod = max(linhas, key=lambda a: a["alfa_bis"])
    print(
        f"- α* máximo: {a_ver['alfa_bis']:.2f} ({a_ver['id']}) nas 10 do veredito; "
        f"{a_tod['alfa_bis']:.2f} ({a_tod['id']}) com OCC-L; S3 sozinha {s3['alfa_bis']:.2f}"
    )
    r_rel = math.sqrt(55 / 14)
    afast = r_rel / (1 + r_rel) - 14 * r_rel / (14 * r_rel + 55)
    for r in (r_rel * 0.999, r_rel * 1.001):
        assert afast > r / (1 + r) - 14 * r / (14 * r + 55), (
            "w − φ não é máximo em λ_barata/λ_cara = √(55/14)"
        )
    print(
        f"- duas classes (k = 14 e 55): ρ̄_taxa − ρ̄_ocup = (w − φ)·(ρ_barata − ρ_cara); "
        f"w − φ máximo = {afast:.4f} em λ_barata/λ_cara = √(55/14) = {r_rel:.2f}"
    )
    contra = [a["id"] for a in linhas if a["vies_dif"] * a["d_auc"] < 0]
    j_max = max(linhas, key=lambda a: abs(a["vies_dif"]))
    print(
        f"- viés de Jensen da diferença: máximo |·| = {abs(j_max['vies_dif']):.4f} "
        f"({j_max['id']}); contra o sinal da teoria em {len(contra)}/{len(linhas)}; menor "
        f"|ΔAUC|/|viés| = {min(abs(a['d_auc']) / abs(a['vies_dif']) for a in linhas):.1f}"
    )
    combos = [
        (
            a["id"],
            nome,
            (FATOR_JENSEN * abs(a[f"jensen_{nome}"]) + abs(a[f"ocioso_{nome}"])) / a[f"tol_{nome}"],
        )
        for a in linhas
        for nome in ("R", "RS")
    ]
    pior_nivel = max(combos, key=lambda x: x[2])
    print(
        f"- nível, pior caso somado ({FATOR_JENSEN}·|Jensen| + |ocioso com k_max tokens|)/tol "
        f"do combo: {100 * pior_nivel[2]:.0f}% ({pior_nivel[0]}/{pior_nivel[1]}); ocioso máximo "
        f"|·| = {max(max(abs(a['ocioso_R']), abs(a['ocioso_RS'])) for a in linhas):.5f}"
    )
    razao_dif = {
        a["id"]: abs(a["d_auc"])
        / (FATOR_JENSEN * abs(a["vies_dif"]) + max(abs(a["ocioso_R"]), abs(a["ocioso_RS"])))
        for a in linhas
    }
    menor = min(razao_dif[a["id"]] for a in ver)
    onde = [a["id"] for a in ver if round(razao_dif[a["id"]], 1) == round(menor, 1)]
    print(
        f"- diferença, |ΔAUC previsto| / ({FATOR_JENSEN}·|viés dif.| + "
        f"max(|ocioso R|, |ocioso R∪S|)): mínimo {menor:.1f} nas 10 do veredito "
        f"({', '.join(onde)}); OCC-L: "
        + "; ".join(f"{a['id']} {razao_dif[a['id']]:.1f}" for a in lim)
    )
    k_alto = {
        d: [c["id"] for c in g["celulas"] if c["direcao"] == d and por_id[c["id"]]["k_S"] == 55]
        for d in ("sobe", "desce")
    }
    print(
        f"- células com k_S = 55 (ociosos maiores em R∪S): 'sobe' {', '.join(k_alto['sobe'])}; "
        f"'desce' {', '.join(k_alto['desce'])}"
    )
    esparsas = [
        f"{a['id']} (" + "; ".join(f"{n} {v:.2f}" for n, v in a["janela_RS"].items() if v < 3) + ")"
        for a in linhas
        if any(v < 3 for v in a["janela_RS"].values())
    ]
    print(f"- fonte com E[n] < 3 na janela de R∪S: {', '.join(esparsas)}")
    evento_oposto = [a["id"] for a in linhas if a["pred_evento"] == -a["pred_forma_fechada"]]
    print(
        f"- regra 'por evento' (ignora k) prevê o oposto da ocupação em "
        f"{len(evento_oposto)}/{len(linhas)}: {', '.join(evento_oposto)}"
    )
    razoes_ep = [abs(a["d_auc"]) / a["ep_hm"] for a in linhas]
    p_empate = sum(cauda_qui2_4(4 * (r / (3 * FATOR_EP)) ** 2) for r in razoes_ep)
    p_troca = sum(cauda_normal(r / FATOR_EP) for r in razoes_ep)
    print(
        f"- poder (EP verdadeiro = {FATOR_EP}·EP_HM; limite da união nas 12; 4 g.l. por combo): "
        f"P(algum empate) ≤ {p_empate:.1e}; P(algum sinal trocado por ruído) ≤ {p_troca:.0e}; "
        f"menor ΔAUC/EP_HM = {min(razoes_ep):.1f}; menor ΔAUC/tol = "
        f"{min(abs(a['d_auc']) / a['tol'] for a in linhas):.2f}"
    )
    ger = sum(gerados(g, c) for c in g["celulas"])
    ger_kat = sum(gerados(gk, c) for c in gk["celulas"])
    ev_max = max(linhas, key=lambda a: a["eventos"])
    ev_kat = max(
        c["T"] * (sum(p["lam"] for p in c["R"].values()) + sum(p["lam"] for p in c["S"].values()))
        for c in gk["celulas"]
    )
    print(
        f"- tempo: {len(linhas)} células × 2 combos × {len(g['sementes'])} sementes = "
        f"{2 * len(linhas) * len(g['sementes'])} simulações; eventos gerados {ger:.3e} contra "
        f"{ger_kat:.3e} do KAT (razão {ger / ger_kat:.2f}) -> "
        f"~{SEGUNDOS_KAT * ger / ger_kat:.0f} s com 8 processos (KAT = "
        f"{SEGUNDOS_KAT} s; estimativa linear, não medição)"
    )
    print(
        f"- memória: máximo {ev_max['eventos']:.0f} eventos/usuário ({ev_max['id']}) contra "
        f"{ev_kat:.0f} no KAT (+{100 * (ev_max['eventos'] / ev_kat - 1):.1f}%); teto "
        f"{g['eventos_max_por_usuario']}"
    )
    print(
        f"- pares de profundidade com previsão fluida idêntica: "
        f"{', '.join(f'{x}/{y}' for x, y in pares)}"
    )
    print(
        f"CRITÉRIOS DE DESENHO: todos passaram (tag = {TAG} fora de {sorted(TAGS_RESERVADOS)}, "
        f"sem 'tag_r3'; regime saturado a z ≥ {Z_MINIMO}; eventos ≤ "
        f"{g['eventos_max_por_usuario']}; forma fechada = Corolário 1; margem ≥ "
        f"{MARGEM_MINIMA}·tol; taxa oposta nas {len(linhas)}; |ΔAUC| ≥ {PISO_VIES} × "
        f"{VIES_MAX_KAT}; direção coerente com a ordem de ρ; α* bissecção = forma fechada "
        f"(< 1e-6); 8 configurações (R, S); 4 pares de profundidade; S3 reprovada sob z ≥ "
        f"{Z_MINIMO})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
