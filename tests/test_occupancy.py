"""TDD of the occupancy family (OCC): token occupancy vs event rate in the window mean of rho.

Specification frozen in ``data/prereg/06-occupancy-addendum.md``, section 2.12: OCCT1 (the shared
runner ``code/run_grid.py`` reproduces the sealed token KAT rows of cell S3 byte for byte), OCCT2
(analytic table: alpha*, design criteria, own tag, S3 rejected under this grid, stdout equal to the
frozen table) and OCCT3 (the fluid closed form reproduces the AUCs and signs of the table; the four
depth pairs have identical predictions). OCCT2 and OCCT3 are parametrized by cell, so a mutant that
breaks the prediction fails once per cell.

Supporting tests: the declared stream ``default_rng([semente, i_celula, i_combo, 6, i_bloco])``
through the runner and its tag adapter, and the family verdict ``occupancy_analytic_table.veredito``
(section 2.8: OCC-S sign, OCC-N level, OCC-L threshold sub-block outside the verdict) on synthetic
rows. The family module is imported inside each test (``_occ``), so that a missing or broken module
fails those tests one by one instead of breaking the collection of the whole file.
"""

import csv
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import displacement as rd
import run_grid
import run_token_kat
import token_kat as kt
import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/occupancy_grid.json"
TABELA = RAIZ / "data/prereg/occupancy_analytic_table.txt"
ADENDO = RAIZ / "data/prereg/06-occupancy-addendum.md"
SCRIPT_TABELA = RAIZ / "code/occupancy_analytic_table.py"
SCRIPT_RUNNER = RAIZ / "code/run_grid.py"
GRADE_KAT = RAIZ / "data/kat_token_grid.json"
TABELA_KAT = RAIZ / "data/prereg/kat_token_analytic_table.txt"
CSV_KAT = RAIZ / "output/kat_token/celulas.csv"
# sha256 of the frozen artifacts of this family (grid and table byte-identical to the private
# frozen originals; the addendum is the sanitized public copy)
SHA_GRADE = "64ae62f966e22e7de03960a6ca11af70cfa553e3892c0b29d7d15e40a3524b0e"
SHA_TABELA = "40d922b5f3119c32e9ef3990aea312772074d70f87e2ce72663cea79f1d622a3"
SHA_ADENDO = "14061945a837d79c291d7a2f077621472bd6ee13b2a793802464024c6856d241"

G_OCC = json.loads(GRADE.read_text(encoding="utf-8"))
IDS = [c["id"] for c in G_OCC["celulas"]]
PARES = [("OCC01", "OCC02"), ("OCC03", "OCC04"), ("OCC05", "OCC06"), ("OCC07", "OCC08")]


def _occ():
    """Import the family module ``occupancy_analytic_table`` (lazily; see the module docstring)."""
    return importlib.import_module("occupancy_analytic_table")


def _sha(p):
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _celula(g, cid):
    """Return the cell ``cid`` of the grid ``g``."""
    (cel,) = [c for c in g["celulas"] if c["id"] == cid]
    return cel


def _linhas_tabela():
    """Parse the rows of the frozen analytic table of this family, keyed by cell id."""
    out = {}
    for row in TABELA.read_text(encoding="utf-8").splitlines():
        if row.startswith("| OCC"):
            c = [x.strip() for x in row.strip("|").split("|")]
            out[c[0]] = {
                "T": int(c[3]),
                "alfa": c[11],
                "auc_R": float(c[12]),
                "auc_RS": float(c[13]),
                "d_auc": float(c[14]),
                "ocupacao": c[19],
                "taxa": c[20],
            }
    return out


# --- pins: what was frozen before any code of the family stays byte for byte ---------------------


def test_pinos_congelados():
    """Pin the sha256 of the frozen grid, analytic table and sanitized addendum of this family."""
    assert _sha(GRADE) == SHA_GRADE, "occupancy grid changed after freezing"
    assert _sha(TABELA) == SHA_TABELA, "occupancy analytic table changed after freezing"
    assert _sha(ADENDO) == SHA_ADENDO, "sanitized occupancy addendum changed after freezing"


# --- OCCT1: identity of the shared runner with the sealed token KAT rows --------------------------


def test_occt1_runner_reproduz_byte_a_byte_as_linhas_seladas_da_s3(tmp_path):
    """Check OCCT1: the runner CLI on the token KAT grid, filtered to S3, rewrites its sealed rows.

    Runs the command line of the shared runner (``--grid``/``--out``, the frozen form of the
    addendum) with the token KAT grid of this repository (only ``tag_r3 = 3``) and the cell S3
    (original ``i_celula`` = 4), and compares the header and the 10 lines ``4,S3,...`` (CRLF
    terminator included) with ``output/kat_token/celulas.csv``. Writes only under ``tmp_path``.
    """
    saida = tmp_path / "occt1"
    r = subprocess.run(
        [sys.executable, str(SCRIPT_RUNNER), "--grid", str(GRADE_KAT), "--out", str(saida)]
        + ["--processos", "4", "--celulas", "S3"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHON_COLORS": "0"},
    )
    assert r.returncode == 0, f"OCCT1: runner failed: {r.stderr.strip().splitlines()[-1:]}"
    selado = CSV_KAT.read_bytes().split(b"\r\n")
    novo = (saida / "celulas.csv").read_bytes()
    s3_selado = [x for x in selado if x.startswith(b"4,S3,")]
    assert len(s3_selado) == 10, "OCCT1: the sealed token KAT CSV does not hold 10 rows of S3"
    esperado = selado[0] + b"\r\n" + b"\r\n".join(s3_selado) + b"\r\n"
    assert novo == esperado, "OCCT1: runner rows of S3 != sealed token KAT rows (byte for byte)"


# --- OCCT2: analytic table -----------------------------------------------------------------------


def test_occt2_tag_proprio_sem_tag_r3():
    """Check OCCT2 (stream tag): the grid tag is 6, outside {3, 5, 7, 8}, with no ``tag_r3`` key."""
    occ = _occ()
    assert G_OCC["tag"] == 6 and occ.TAG == 6, "OCCT2: the tag of the family is not 6"
    assert occ.TAGS_RESERVADOS == {3, 5, 7, 8}, "OCCT2: reserved tags are not {3, 5, 7, 8}"
    assert G_OCC["tag"] not in occ.TAGS_RESERVADOS, "OCCT2: tag collides with a reserved tag"
    assert "tag_r3" not in G_OCC, "OCCT2: the new grid carries the key 'tag_r3'"
    occ.conferir_grade(G_OCC)


@pytest.mark.parametrize("cid", IDS)
def test_occt2_alfa_bissecao_igual_forma_fechada(cid):
    """Check OCCT2 (alpha*): bisection = two-class closed form (< 1e-6), as printed in the table."""
    occ = _occ()
    a = occ.analisar_occ(_celula(G_OCC, cid), G_OCC)
    assert a["alfa_bis"] is not None, f"OCCT2: alpha* of {cid} outside the bisection bracket"
    assert abs(a["alfa_bis"] - a["alfa_fechado"]) < 1e-6, (
        f"OCCT2: alpha* of {cid}: bisection {a['alfa_bis']:.8f} != closed form "
        f"{a['alfa_fechado']:.8f}"
    )
    assert f"{a['alfa_bis']:.2f}" == _linhas_tabela()[cid]["alfa"], (
        f"OCCT2: alpha* of {cid} != frozen table"
    )


@pytest.mark.parametrize("cid", IDS)
def test_occt2_conferir_passa_na_celula(cid):
    """Check OCCT2 (design criteria): the frozen ``conferir`` and the family checks pass."""
    occ = _occ()
    cel = _celula(G_OCC, cid)
    a = occ.analisar_occ(cel, G_OCC)
    tab.conferir(a, G_OCC)
    occ.conferir_celula(a, cel)


def test_occt2_s3_reproduz_a_linha_congelada_do_kat_e_reprova_nesta_grade():
    """Check OCCT2 (S3): same routine = frozen token KAT row; KAT criteria pass, these fail.

    S3 has ``z(R) = 2.87``: it passes under the token KAT grid (``z_minimo_regime`` 2.5) and
    fails under this grid (4.0) with the saturation-threshold message of ``conferir``.
    """
    occ = _occ()
    g_kat = json.loads(GRADE_KAT.read_text(encoding="utf-8"))
    s3 = occ.analisar_occ(_celula(g_kat, "S3"), g_kat)
    (linha,) = [
        x for x in TABELA_KAT.read_text(encoding="utf-8").splitlines() if x.startswith("| S3 ")
    ]
    c = [x.strip() for x in linha.strip("|").split("|")]
    obtido = [
        f"{s3['z_R']:.2f}",
        f"{s3['z_RS']:.2f}",
        f"{s3['eventos']:.0f}",
        f"{s3['rho_S']:.6f}",
        f"{s3['rho_bar']:.6f}",
        f"{s3['rho_bar_taxa']:.6f}",
        f"{s3['auc_R']:.4f}",
        f"{s3['auc_RS']:.4f}",
        f"{s3['d_auc']:+.4f}",
        f"{s3['tol']:.4f}",
    ]
    assert obtido == [c[i] for i in (3, 4, 5, 6, 7, 8, 10, 11, 12, 13)], (
        f"OCCT2: S3 by the family routine != frozen token KAT row: {obtido}"
    )
    tab.conferir(s3, g_kat)
    with pytest.raises(AssertionError, match="desvios do limiar de saturação"):
        tab.conferir(s3, G_OCC)
    assert s3["z_R"] < G_OCC["z_minimo_regime"], "OCCT2: S3 is not below z_min of this grid"


def test_occt2_stdout_igual_a_tabela_congelada():
    """Check OCCT2 (table): the ported generator exits 0 and prints the frozen table bytes."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT_TABELA)],
        capture_output=True,
        env={**os.environ, "PYTHON_COLORS": "0"},
    )
    assert r.returncode == 0, (
        f"OCCT2: generator failed a design criterion: "
        f"{r.stderr.decode('utf-8', 'replace').strip().splitlines()[-1:]}"
    )
    assert r.stdout == TABELA.read_bytes(), "OCCT2: generator stdout != frozen table (bytes)"


# --- OCCT3: closed-form prediction ---------------------------------------------------------------


@pytest.mark.parametrize("cid", IDS)
def test_occt3_forma_fechada_reproduz_a_tabela(cid):
    """Check OCCT3: the module closed form reproduces AUC(R), AUC(R ∪ S) and the table signs.

    ``token_kat.auc_fluida`` (scipy) is independent of the table (``statistics.NormalDist``). The
    Corollary 1 prediction ``sign(rho_S - rho_bar_occupancy)`` must equal the closed-form sign
    and the "ocupação" column; the event-rate rule must predict the opposite ("taxa" column).
    """
    occ = _occ()
    cel = _celula(G_OCC, cid)
    t = _linhas_tabela()[cid]
    a_r = kt.auc_fluida(kt.fontes_da_celula(cel, "R"), cel["T"], G_OCC["K"])
    a_rs = kt.auc_fluida(kt.fontes_da_celula(cel, "RS"), cel["T"], G_OCC["K"])
    assert abs(a_r - t["auc_R"]) <= 5e-5 and abs(a_rs - t["auc_RS"]) <= 5e-5, (
        f"OCCT3: closed form of the module != table AUCs at {cid}"
    )
    assert abs((a_rs - a_r) - t["d_auc"]) <= 5e-5, f"OCCT3: predicted dAUC != table at {cid}"
    sinal = "melhora" if a_rs > a_r else "piora"
    assert sinal == t["ocupacao"], f"OCCT3: closed-form sign != table 'ocupação' at {cid}"
    a = occ.analisar_occ(cel, G_OCC)
    assert a["pred_corolario"] == a["pred_forma_fechada"] == (1 if a_rs > a_r else -1), (
        f"OCCT3: Corollary 1 prediction (occupancy-weighted mean) != closed form at {cid}"
    )
    assert ("melhora" if a["pred_ingenua"] > 0 else "piora") == t["taxa"] != sinal, (
        f"OCCT3: event-rate rule does not predict the opposite at {cid}"
    )


def test_occt3_pares_de_profundidade_com_previsao_identica():
    """Check OCCT3 (pairs): same (R, S) at two distinct depths T, identical fluid prediction."""
    occ = _occ()
    por_id = {c["id"]: occ.analisar_occ(c, G_OCC) for c in G_OCC["celulas"]}
    assert occ.conferir_pares(G_OCC, por_id) == PARES, "OCCT3: depth pairs != the frozen four"
    for x, y in PARES:
        cx, cy = _celula(G_OCC, x), _celula(G_OCC, y)
        assert (cx["R"], cx["S"]) == (cy["R"], cy["S"]), f"OCCT3: {x}/{y} differ in (R, S)"
        assert cx["T"] != cy["T"], f"OCCT3: {x}/{y} have the same depth T"
        for combo in ("R", "RS"):
            px = kt.auc_fluida(kt.fontes_da_celula(cx, combo), cx["T"], G_OCC["K"])
            py = kt.auc_fluida(kt.fontes_da_celula(cy, combo), cy["T"], G_OCC["K"])
            assert abs(px - py) < 1e-12, f"OCCT3: {x}/{y} {combo} prediction changes with T"


# --- declared stream (tag 6) through the runner and its adapter ----------------------------------


def test_runner_usa_o_fluxo_declarado_com_tag_6(tmp_path):
    """Check that the runner draws ``default_rng([semente, i_celula, i_combo, 6, i_bloco])``.

    Tiny run (``--N 20 --bloco-usuarios 10``) of cell OCC03 (original index 2) through
    ``run_grid.main``; every row must equal the direct literal simulation with tag 6.
    """
    g = dict(G_OCC)
    g["N"], g["bloco_usuarios"] = 20, 10
    assert run_grid.adaptar_grade(g)["tag_r3"] == 6, "adapter does not pass tag 6 on"
    saida = tmp_path / "fluxo"
    argv = ["--grid", str(GRADE), "--out", str(saida), "--processos", "2"]
    argv += ["--N", "20", "--bloco-usuarios", "10", "--celulas", "OCC03"]
    assert run_grid.main(argv) == 0
    with open(saida / "celulas.csv", newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 10 and {x["i_celula"] for x in linhas} == {"2"}
    cel = _celula(G_OCC, "OCC03")
    for x in linhas:
        i_combo = ("R", "RS").index(x["combo"])
        fontes = kt.fontes_da_celula(cel, x["combo"])
        lam = {n: p["lam"] for n, p in fontes.items()}
        d = {n: p["d"] for n, p in fontes.items()}
        k = {n: p["k"] for n, p in fontes.items()}
        semente = int(x["semente"])
        partes = [
            kt.simular_literal_tokens(
                "".join(fontes),
                lam,
                d,
                k,
                cel["T"],
                10,
                np.random.default_rng([semente, 2, i_combo, 6, b]),
                G_OCC["K"],
            )
            for b in range(2)
        ]
        s = np.concatenate([p[0] for p in partes])
        y = np.concatenate([p[1] for p in partes])
        assert x["auc"] == repr(float(rd.auc_mann_whitney(s, y))), (
            f"runner does not use default_rng([seed, cell, combination, 6, block]) "
            f"({x['combo']}, seed {semente})"
        )
    resumo = json.loads((saida / "resumo.json").read_text(encoding="utf-8"))
    assert resumo["tag"] == 6, "resumo.json does not record tag 6"


def test_adaptador_leva_o_tag_6_da_grade_da_familia_ate_a_simulacao(tmp_path):
    """Check the tag adapter end to end with the family grid, which has no ``tag_r3`` key.

    Guards against an absent adapter (mutant X06 of the addendum, section 2.13), both inside
    ``run_grid.adaptar_grade`` and in ``run_grid.main``: without it, the grid of this family cannot
    reach ``run_token_kat._uma_tarefa``, which reads ``tag_r3``, and the run stops with an
    exception. That failure is reported here as a named assertion. Tiny run of cell OCC01
    (``--N 20 --bloco-usuarios 10``).
    """
    try:
        tag = run_grid.adaptar_grade(dict(G_OCC)).get("tag_r3")
    except Exception as erro:
        tag = f"{type(erro).__name__}: {erro}"
    assert tag == 6, f"tag adapter does not map the family 'tag' to 'tag_r3': {tag!r}"
    saida = tmp_path / "adaptador"
    argv = ["--grid", str(GRADE), "--out", str(saida), "--processos", "2"]
    argv += ["--N", "20", "--bloco-usuarios", "10", "--celulas", "OCC01"]
    try:
        rc = run_grid.main(argv)
    except Exception as erro:
        rc = f"{type(erro).__name__}: {erro}"
    assert rc == 0, f"runner does not pass the family grid through the tag adapter: {rc!r}"
    resumo = json.loads((saida / "resumo.json").read_text(encoding="utf-8"))
    assert resumo["tag"] == 6, f"resumo.json records tag {resumo['tag']!r}, not 6"


# --- family verdict (section 2.8) on synthetic rows ---------------------------------------------


def _linhas_sinteticas(ajuste=None):
    """Return result rows at the fluid AUC plus a small symmetric seed pattern (no simulation).

    ``ajuste(cid, combo, semente)`` adds a shift to one row; the seed pattern gives a standard
    error of the difference of 1e-4, far below every predicted dAUC of the grid.
    """
    padrao = dict(zip(G_OCC["sementes"], (-2e-4, -1e-4, 0.0, 1e-4, 2e-4), strict=True))
    linhas = []
    for i, cel in enumerate(G_OCC["celulas"]):
        for combo in ("R", "RS"):
            base = kt.auc_fluida(kt.fontes_da_celula(cel, combo), cel["T"], G_OCC["K"])
            for s in G_OCC["sementes"]:
                extra = ajuste(cel["id"], combo, s) if ajuste else 0.0
                linhas.append(
                    {
                        "i_celula": i,
                        "celula": cel["id"],
                        "regime": cel["bloco"],
                        "combo": combo,
                        "semente": s,
                        "auc": base + padrao[s] + extra,
                    }
                )
    return linhas


def _ajuste(cid, combo, deslocamento):
    """Return an ``ajuste`` that shifts every seed of ``(cid, combo)`` by a per-seed amount."""

    def f(c, cb, s):
        """Shift of row ``(c, cb, s)``."""
        return deslocamento(s) if (c, cb) == (cid, combo) else 0.0

    return f


def test_veredito_passa_quando_tudo_bate():
    """All 12 cells agree and every level is inside: OCC-S 10/10, OCC-N 20/20, the family passes."""
    v = _occ().veredito(_linhas_sinteticas(), G_OCC)
    assert v["grade_completa"] is True
    assert (
        v["criterios"]["OCC_S"]["passou"] is True and len(v["criterios"]["OCC_S"]["concorda"]) == 10
    )
    assert v["criterios"]["OCC_N"]["passou"] is True and v["criterios"]["OCC_N"]["combos"] == 20
    assert v["passou"] is True
    assert v["fora_do_veredito"]["OCC_L"]["celulas"] == ["OCC11", "OCC12"]
    alfa = v["relatorio"]["alfa_minimo"]
    assert f"{alfa['familia_principal']:.2f}" == "0.52" and f"{alfa['com_occ_l']:.2f}" == "0.75"
    evento = v["relatorio"]["regra_por_evento"]
    assert evento["celulas_opostas"] == [
        "OCC03",
        "OCC04",
        "OCC05",
        "OCC06",
        "OCC09",
        "OCC10",
        "OCC12",
    ]
    assert evento["refutada"] is True
    assert all(p["dentro"] for p in v["relatorio"]["invariancia_em_T"])
    assert [p["par"] for p in v["relatorio"]["invariancia_em_T"]] == [f"{x}/{y}" for x, y in PARES]
    json.dumps(v, sort_keys=True)  # serializable as the runner writes it


def test_veredito_uma_discordancia_reprova():
    """One disagreeing cell of the main family fails OCC-S and falsifies the occupancy there."""
    v = _occ().veredito(_linhas_sinteticas(_ajuste("OCC05", "RS", lambda s: 0.1)), G_OCC)
    assert v["criterios"]["OCC_S"]["discorda"] == ["OCC05"]
    assert v["criterios"]["OCC_S"]["passou"] is False and v["passou"] is False
    assert "OCC05" in v["leitura"]


def test_veredito_empate_reprova_por_poder():
    """A tie (``|predicted dAUC| < 3 SE``) fails OCC-S for lack of power, with the level inside."""
    passo = {0: 0.03, 1: -0.03, 2: 0.015, 3: -0.015, 4: 0.0}
    v = _occ().veredito(_linhas_sinteticas(_ajuste("OCC03", "RS", passo.__getitem__)), G_OCC)
    assert v["criterios"]["OCC_S"]["empate"] == ["OCC03"]
    assert v["criterios"]["OCC_S"]["discorda"] == []
    assert v["criterios"]["OCC_S"]["passou"] is False and v["passou"] is False
    assert v["criterios"]["OCC_N"]["passou"] is True


def test_veredito_limiar_fica_fora():
    """A disagreement only in the threshold sub-block (OCC-L) is reported and does not fail."""
    v = _occ().veredito(_linhas_sinteticas(_ajuste("OCC12", "RS", lambda s: 0.05)), G_OCC)
    assert v["fora_do_veredito"]["OCC_L"]["discorda"] == ["OCC12"]
    assert (
        v["criterios"]["OCC_S"]["passou"] is True and len(v["criterios"]["OCC_S"]["celulas"]) == 10
    )
    assert v["criterios"]["OCC_N"]["passou"] is True and v["passou"] is True
    assert f"{v['relatorio']['alfa_minimo']['familia_principal']:.2f}" == "0.52"
    assert v["relatorio"]["alfa_minimo"]["com_occ_l"] is None


def test_veredito_estouro_de_nivel_reprova():
    """A level overflow in the main family fails OCC-N while the sign still agrees."""
    v = _occ().veredito(_linhas_sinteticas(_ajuste("OCC03", "R", lambda s: 0.015)), G_OCC)
    assert v["criterios"]["OCC_S"]["passou"] is True
    assert v["criterios"]["OCC_N"]["estouros"] == ["OCC03/R"]
    assert v["criterios"]["OCC_N"]["passou"] is False and v["passou"] is False


def test_veredito_grade_parcial_nao_passa():
    """A run of a subset of cells records an incomplete grid and never passes."""
    grade = {**G_OCC, "celulas": [_celula(G_OCC, "OCC01")]}
    linhas = [x for x in _linhas_sinteticas() if x["celula"] == "OCC01"]
    v = _occ().veredito(linhas, grade)
    assert v["grade_completa"] is False and v["passou"] is False
    assert v["criterios"]["OCC_S"]["concorda"] == ["OCC01"]
    json.dumps(v, sort_keys=True)


def test_tolerancias_do_veredito_sao_as_do_kat():
    """The level tolerance of the verdict is the frozen one of the token KAT, per combination."""
    v = _occ().veredito(_linhas_sinteticas(), G_OCC)
    tol = run_token_kat.tolerancias(G_OCC)
    por_celula = v["avaliar_kat_principal"]["por_celula"]
    for c in por_celula:
        for combo in ("R", "RS"):
            assert c["nivel"][combo]["tol"] == tol[(c["celula"], combo)]
