"""Unit tests EX1-EX5 of the exponent family (``data/prereg/05-exponent-addendum.md``, 1.11).

EX1 pins the frozen grid (sha256, tag, regime, families, ids); EX2 checks the ported analytic
table (byte for byte against ``data/prereg/exponent_analytic_table.txt``) and its predictions
against ``token_kat.auc_fluida``; EX3 checks what the grid identifies (``d/sqrt(k)`` and
``d^2/k^2``); EX4 checks that the shared runner ``code/run_grid.py`` reuses the literal
simulation faithfully (tag 5, original cell index); EX5 checks the pre-registered criteria EXS and
EXN on fabricated rows. The rival values are recomputed here, independently of the port, so a
change in the port cannot pass by agreeing with itself.

EX1 is split in several functions on purpose: a mutated grid must die on the assert about its
CONTENT, not only on the sha256 pin.
"""

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import displacement as rd
import exponent_analytic_table as expo
import run_grid
import token_kat as kt
import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/exponent_grid.json"
TABELA = RAIZ / "data/prereg/exponent_analytic_table.txt"
ADENDO = RAIZ / "data/prereg/05-exponent-addendum.md"
SCRIPT_TABELA = RAIZ / "code/exponent_analytic_table.py"
PUBLICADO = RAIZ / "output/exponent"
# sha256 of the frozen grid and analytic table (recorded before any code of the family existed)
SHA_GRADE = "5a365aee2307ee2fb568f2221bbdf252ffe7c9e2c389b4082de8c9f928a04dda"
SHA_TABELA = "4cd78db2bd03b558d522053945e052827d2c529b377f8b3fdd5880cba107556a"

IDS = ("EXP-C1", "EXP-C2", "EXP-C3", "EXP-C4", "EXP-D1", "EXP-D2")
TAG = 5
TAGS_DAS_OUTRAS = {3, 6, 7, 8}
# sign of the theory per cell (section 1.7 of the addendum: "melhora" = +1, "piora" = -1)
SINAL_TEORIA = {"EXP-C1": 1, "EXP-C2": -1, "EXP-C3": -1, "EXP-C4": 1, "EXP-D1": -1, "EXP-D2": 1}
# exact sign-switch point of H(p, 1), 3 decimals (section 1.7; p/q in family C, p in family D)
TROCA = {
    "EXP-C1": 1.601,
    "EXP-C2": 1.604,
    "EXP-C3": 2.510,
    "EXP-C4": 2.498,
    "EXP-D1": 1.591,
    "EXP-D2": 2.510,
}
# short cell codes of one letter M or K plus one or two digits: the pattern the repository renames
# away (the mixed cells are MIX1 and MIX2); no id of this family may have that form
CODIGO_CURTO = re.compile(r"\b[MK]\d{1,2}\b", re.I)


def _sha(p):
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _grade():
    """Return the frozen grid of the family, loaded from disk."""
    return kt.carregar_grade(GRADE)


def _valor_rival(fs, T, K, p, q):
    """Return ``h * sum(lam k^(1-q) d^p)`` with ``h = min(T, K / sum(lam k))`` (not the port)."""
    ocupacao = sum(f["lam"] * f["k"] for f in fs)
    h = min(T, K / ocupacao)
    return h * sum(f["lam"] * f["k"] ** (1 - q) * f["d"] ** p for f in fs)


def _sinal_rival(cel, K, p, q):
    """Return the sign of the change of ``H(p, q)`` when ``S`` is added to ``R``."""
    R = tab.fontes(cel, "R")
    RS = R + tab.fontes(cel, "S")
    return int(np.sign(_valor_rival(RS, cel["T"], K, p, q) - _valor_rival(R, cel["T"], K, p, q)))


def _opostos(grade, p, q):
    """Return the ids where ``H(p, q)`` predicts the sign opposite to the theory."""
    return {
        cel["id"]
        for cel in grade["celulas"]
        if _sinal_rival(cel, grade["K"], p, q) == -SINAL_TEORIA[cel["id"]]
    }


def _tabela_1():
    """Return Table 1 of the frozen analytic table as ``{cell id: {column name: text}}``."""
    linhas = TABELA.read_text(encoding="utf-8").splitlines()
    i_cab = next(i for i, x in enumerate(linhas) if x.startswith("| célula | família | lado |"))
    cabecalho = [c.strip() for c in linhas[i_cab].strip("|").split("|")]
    out = {}
    for x in linhas[i_cab + 2 : i_cab + 2 + len(IDS)]:
        valores = [c.strip() for c in x.strip("|").split("|")]
        out[valores[0]] = dict(zip(cabecalho, valores, strict=True))
    return out


# --- EX1: pins of the grid -----------------------------------------------------------------------


def test_ex1_pino_sha256_da_grade():
    """Check that the grid is the frozen one, byte for byte."""
    assert _sha(GRADE) == SHA_GRADE


def test_ex1_tag_da_familia():
    """Check the stream tag: ``tag = 5``, no ``tag_r3`` key, and 5 not in {3, 6, 7, 8}."""
    grade = _grade()
    assert "tag_r3" not in grade, "the family grid must carry its tag only under 'tag'"
    assert grade.get("tag") == TAG, f"tag {grade.get('tag')!r} != {TAG}"
    assert grade["tag"] not in TAGS_DAS_OUTRAS, f"tag {grade['tag']} collides with another family"


def test_ex1_tag_difere_das_outras_grades_do_repositorio():
    """Check that the five grids of the repository draw with five distinct tags (5 is EXP's)."""
    tags = {}
    for p in sorted((RAIZ / "data").glob("*_grid.json")):
        g = kt.carregar_grade(p)
        tags[p.name] = g.get("tag", g.get("tag_r3"))
    assert tags["exponent_grid.json"] == TAG
    assert tags["kat_token_grid.json"] == 3
    assert len(set(tags.values())) == len(tags), f"repeated stream tags: {tags}"


def test_ex1_regime_saturado_e_eventos():
    """Check ``z >= 4`` in both combinations and at most 600 events per user, in every cell."""
    grade = _grade()
    assert grade["z_minimo_regime"] == 4.0
    assert grade["eventos_max_por_usuario"] == 600
    K = grade["K"]
    for cel in grade["celulas"]:
        R = tab.fontes(cel, "R")
        RS = R + tab.fontes(cel, "S")
        for rotulo, fs in (("R", R), ("R∪S", RS)):
            z = tab.z_saturacao(fs, cel["T"], K)
            assert z >= 4.0, f"{cel['id']}: {rotulo} at z = {z:.2f} < 4 from saturation"
            assert cel["T"] * tab.W(fs) >= K, f"{cel['id']}: {rotulo} not saturated"
        eventos = cel["T"] * sum(f["lam"] for f in RS)
        assert eventos <= 600, f"{cel['id']}: {eventos:.0f} events per user > 600"


def test_ex1_familia_c_fonte_unica_e_custo_diferente():
    """Check that family C has a single source in ``R`` and ``k_S != k_A``."""
    celulas = [c for c in _grade()["celulas"] if c["familia"] == "C"]
    assert [c["id"] for c in celulas] == ["EXP-C1", "EXP-C2", "EXP-C3", "EXP-C4"]
    for cel in celulas:
        R = tab.fontes(cel, "R")
        (S,) = tab.fontes(cel, "S")
        assert len(R) == 1, f"{cel['id']}: family C needs a single source in R"
        assert S["k"] != R[0]["k"], f"{cel['id']}: family C needs k_S != k_A"


def test_ex1_familia_d_custo_homogeneo_e_duas_fontes():
    """Check that family D has ``k = 14`` in every source and two sources of different ``d``."""
    celulas = [c for c in _grade()["celulas"] if c["familia"] == "D"]
    assert [c["id"] for c in celulas] == ["EXP-D1", "EXP-D2"]
    for cel in celulas:
        R = tab.fontes(cel, "R")
        fs = R + tab.fontes(cel, "S")
        assert all(f["k"] == 14 for f in fs), f"{cel['id']}: family D needs k = 14 everywhere"
        assert len(R) == 2 and R[0]["d"] != R[1]["d"], f"{cel['id']}: family D needs 2 sources"


def test_ex1_ids_exatos_e_sem_codigo_curto():
    """Check the six ids exactly, and that none has the short cell-code form renamed away."""
    ids = [c["id"] for c in _grade()["celulas"]]
    assert tuple(ids) == IDS
    for cid in ids:
        assert re.fullmatch(r"EXP-[CD][1-4]", cid), cid
        assert not CODIGO_CURTO.search(cid), cid


# --- EX2: prediction ------------------------------------------------------------------------------


def test_ex2_pino_sha256_da_tabela():
    """Check that the analytic table is the frozen one, byte for byte."""
    assert _sha(TABELA) == SHA_TABELA


def test_ex2_tabela_portada_reproduz_byte_a_byte():
    """Check that the ported generator passes its design criteria and prints the frozen table."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT_TABELA)],
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHON_COLORS": "0"},
    )
    assert r.returncode == 0, (
        "analytic table failed a design criterion: "
        f"{r.stderr.decode('utf-8', 'replace').strip().splitlines()[-1:]}"
    )
    assert r.stdout == TABELA.read_bytes(), "ported analytic table != frozen file"


def test_ex2_auc_fluidas_e_sinais_contra_token_kat():
    """Check the fluid AUCs of the port against ``token_kat.auc_fluida`` and the theory signs."""
    grade = _grade()
    K = grade["K"]
    for cel in grade["celulas"]:
        a = expo.analisar(cel, grade)
        aR = kt.auc_fluida(kt.fontes_da_celula(cel, "R"), cel["T"], K)
        aRS = kt.auc_fluida(kt.fontes_da_celula(cel, "RS"), cel["T"], K)
        assert a["aR"] == pytest.approx(aR, abs=1e-12), cel["id"]
        assert a["aRS"] == pytest.approx(aRS, abs=1e-12), cel["id"]
        assert int(np.sign(aRS - aR)) == SINAL_TEORIA[cel["id"]], cel["id"]
        assert a["teo"] == SINAL_TEORIA[cel["id"]], cel["id"]
        # Corollary 1: rho_S against the occupancy-weighted mean of R, recomputed here
        R = tab.fontes(cel, "R")
        (S,) = tab.fontes(cel, "S")
        rho_bar = sum(f["lam"] * f["d"] ** 2 for f in R) / sum(f["lam"] * f["k"] for f in R)
        assert int(np.sign(S["d"] ** 2 / S["k"] - rho_bar)) == SINAL_TEORIA[cel["id"]], cel["id"]


def test_ex2_regras_rivais_preveem_o_sinal_oposto():
    """Check ``d/k`` opposite in C1, C2, D1 and ``d^3/k`` opposite in C3, C4, D2."""
    grade = _grade()
    assert _opostos(grade, 1, 1.0) == {"EXP-C1", "EXP-C2", "EXP-D1"}
    assert _opostos(grade, 3, 1.0) == {"EXP-C3", "EXP-C4", "EXP-D2"}
    for cel in grade["celulas"]:
        a = expo.analisar(cel, grade)
        assert a["rivais"]["d/k"] == _sinal_rival(cel, grade["K"], 1, 1.0), cel["id"]
        assert a["rivais"]["d³/k"] == _sinal_rival(cel, grade["K"], 3, 1.0), cel["id"]


def test_ex2_ponto_de_troca_dentro_das_faixas():
    """Check the sign switch of ``H(p, 1)``: inside the pre-registered bands, at the frozen root."""
    grade = _grade()
    K = grade["K"]
    for cel in grade["celulas"]:
        faixa = grade["faixa_troca_baixo"] if cel["lado"] == "baixo" else grade["faixa_troca_alto"]
        # independent bracket: the rival changes sign between the two ends of the band
        assert _sinal_rival(cel, K, faixa[0], 1.0) == -_sinal_rival(cel, K, faixa[1], 1.0), cel[
            "id"
        ]
        a = expo.analisar(cel, grade)
        assert len(a["raiz_troca"]) == 1, cel["id"]
        assert faixa[0] <= a["raiz_troca"][0] <= faixa[1], cel["id"]
        assert round(a["raiz_troca"][0], 3) == TROCA[cel["id"]], cel["id"]


# --- EX3: identification --------------------------------------------------------------------------


def test_ex3_d_sobre_raiz_de_k_e_d2_sobre_k2():
    """Check ``d/sqrt(k)`` opposite only in D1 and ``d^2/k^2`` opposite only in C1 and C2.

    ``d/sqrt(k)`` keeps the sign of the theory in the four C cells (family C identifies only the
    ratio p/q = 2); ``d^2/k^2`` keeps it in the two D cells (family D identifies p alone).
    """
    grade = _grade()
    assert _opostos(grade, 1, 0.5) == {"EXP-D1"}
    assert _opostos(grade, 2, 2.0) == {"EXP-C1", "EXP-C2"}
    for cel in grade["celulas"]:
        a = expo.analisar(cel, grade)
        assert a["rivais"]["d/√k"] == _sinal_rival(cel, grade["K"], 1, 0.5), cel["id"]
        assert a["rivais"]["d²/k²"] == _sinal_rival(cel, grade["K"], 2, 2.0), cel["id"]


# --- EX4: faithful reuse of the shared runner -----------------------------------------------------


def test_ex4_runner_partilhado_reproduz_a_simulacao_a_mao(tmp_path):
    """Check that the runner's AUC equals the Mann-Whitney AUC of a hand call, tag 5, cell D1.

    Small cell: ``N = 2000`` in blocks of 1000 users, cell EXP-D1 filtered (original index 4).
    The hand call draws with ``default_rng([seed, 4, i_combo, 5, i_block])``, exactly as
    ``run_token_kat._uma_tarefa``. Writes only under ``tmp_path``.
    """
    grade = _grade()
    i_celula = [c["id"] for c in grade["celulas"]].index("EXP-D1")
    assert i_celula == 4
    cel = grade["celulas"][i_celula]
    N, bloco = 2000, 1000
    argv = ["--grid", str(GRADE), "--out", str(tmp_path / "out"), "--celulas", "EXP-D1"]
    argv += ["--N", str(N), "--bloco-usuarios", str(bloco), "--processos", "2"]
    assert run_grid.main(argv) == 0

    with open(tmp_path / "out/celulas.csv", newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 2 * len(grade["sementes"])
    esperado = {}
    for i_combo, combo in enumerate(("R", "RS")):
        fontes = kt.fontes_da_celula(cel, combo)
        nomes = "".join(fontes)
        lam = {n: p["lam"] for n, p in fontes.items()}
        d = {n: p["d"] for n, p in fontes.items()}
        k = {n: p["k"] for n, p in fontes.items()}
        for semente in grade["sementes"]:
            escores, rotulos = [], []
            for i_bloco in range(N // bloco):
                rng = np.random.default_rng([semente, i_celula, i_combo, TAG, i_bloco])
                s, y, _ = kt.simular_literal_tokens(
                    nomes, lam, d, k, cel["T"], bloco, rng, grade["K"]
                )
                escores.append(s)
                rotulos.append(y)
            auc = rd.auc_mann_whitney(np.concatenate(escores), np.concatenate(rotulos))
            esperado[(combo, str(semente))] = repr(float(auc))
    for row in linhas:
        assert row["i_celula"] == "4" and row["celula"] == "EXP-D1"
        assert row["auc"] == esperado[(row["combo"], row["semente"])], (
            row["combo"],
            row["semente"],
        )
    resumo = json.loads((tmp_path / "out/resumo.json").read_text(encoding="utf-8"))
    assert resumo["tag"] == TAG and resumo["celulas"] == ["EXP-D1"]


# --- EX5: criteria on fabricated rows -------------------------------------------------------------


def _linhas_fabricadas(grade, deslocamento=None, ruido=None):
    """Return rows whose mean AUCs sit on the fluid prediction, plus an optional shift per cell.

    ``deslocamento[id]`` is added to every ``R ∪ S`` AUC of that cell (so the empirical difference
    is the fluid one plus the shift); ``ruido[id]`` is the unit of a zero-mean between-seed spread
    (default 1e-4), whose standard error of the difference equals that unit.
    """
    deslocamento = deslocamento or {}
    ruido = ruido or {}
    passos = (-2, -1, 0, 1, 2)
    linhas = []
    for i_celula, cel in enumerate(grade["celulas"]):
        aR = kt.auc_fluida(kt.fontes_da_celula(cel, "R"), cel["T"], grade["K"])
        aRS = kt.auc_fluida(kt.fontes_da_celula(cel, "RS"), cel["T"], grade["K"])
        u = ruido.get(cel["id"], 1e-4)
        extra = deslocamento.get(cel["id"], 0.0)
        for j, semente in enumerate(grade["sementes"]):
            for combo, valor in (
                ("R", aR + u * passos[j]),
                ("RS", aRS + extra + u * passos[-1 - j]),
            ):
                linhas.append(
                    {
                        "i_celula": i_celula,
                        "celula": cel["id"],
                        "combo": combo,
                        "semente": semente,
                        "auc": valor,
                    }
                )
    return linhas


def _por_celula(v):
    """Return the per-cell block of a verdict as ``{cell id: entry}``."""
    return {x["celula"]: x for x in v["por_celula"]}


def test_ex5_linhas_na_previsao_passam():
    """Check that rows on the fluid prediction pass EXS and EXN, with the implied interval."""
    grade = _grade()
    v = expo.veredito(_linhas_fabricadas(grade), grade)
    assert v["EXS"]["passou"] and v["EXN"]["passou"] and v["passou"]
    assert v["desfecho"] == "passa"
    assert v["EXS"]["discordantes"] == 0 and v["EXS"]["empates"] == 0
    assert v["EXN"]["estouros"] == 0 and v["EXN"]["celulas"] == 6
    assert v["intervalo_implicado"] == {
        "C": {"p_sobre_q": [1.604, 2.498]},
        "D": {"p": [1.591, 2.51]},
    }


def test_ex5_discordancia_de_sinal_reprova():
    """Check that one cell with the sign opposite to the theory fails EXS."""
    grade = _grade()
    prev = {
        c["id"]: kt.auc_fluida(kt.fontes_da_celula(c, "RS"), c["T"], grade["K"])
        - kt.auc_fluida(kt.fontes_da_celula(c, "R"), c["T"], grade["K"])
        for c in grade["celulas"]
    }
    v = expo.veredito(_linhas_fabricadas(grade, {"EXP-C4": -2 * prev["EXP-C4"]}), grade)
    assert not v["EXS"]["passou"] and not v["passou"]
    assert v["EXS"]["discordantes"] == 1 and v["EXS"]["empates"] == 0
    assert _por_celula(v)["EXP-C4"]["EXS"] == "discorda"
    assert v["desfecho"] == "reprova_EXS"
    assert set(v["leitura_EXS"]) == {"EXP-C4"}
    assert v["leitura_EXS"] == {"EXP-C4": "the simulated pipeline behaves as an exponent above 2.5"}
    assert "intervalo_implicado" not in v


def test_ex5_empate_reprova_por_falta_de_poder():
    """Check that ``|predicted| < 3 SE_emp`` in one cell is a tie, and a tie fails EXS."""
    grade = _grade()
    v = expo.veredito(_linhas_fabricadas(grade, ruido={"EXP-D2": 0.02}), grade)
    c = _por_celula(v)["EXP-D2"]
    assert abs(c["dif_prevista"]) < 3 * c["ep_emp"]
    assert c["EXS"] == "empate"
    assert v["EXS"]["empates"] == 1 and v["EXS"]["discordantes"] == 0
    assert not v["EXS"]["passou"] and not v["passou"] and v["desfecho"] == "reprova_EXS"
    # section 1.10: "tie -> fails for lack of power", never the reading of a sign disagreement
    leitura = v["leitura_EXS"]
    assert leitura == {"EXP-D2": "tie: |predicted| < 3 SE_emp, fails for lack of power"}, leitura
    assert leitura["EXP-D2"] not in expo.LEITURA_EXS.values(), leitura


@pytest.mark.parametrize(("celula", "direcao"), [("EXP-C1", -1), ("EXP-D1", 1), ("EXP-C2", -1)])
def test_ex5_exn_usa_valor_absoluto(celula, direcao):
    """Check that a level deviation beyond tolDelta fails EXN on either side, with the right sign.

    The shift keeps the sign of the difference (EXS passes), so only EXN can catch it; a shift
    toward zero (``direcao`` opposite to the predicted sign) is what a signed test would miss.
    """
    grade = _grade()
    tolD = expo.analisar(next(c for c in grade["celulas"] if c["id"] == celula), grade)["tolD"]
    v = expo.veredito(_linhas_fabricadas(grade, {celula: direcao * (tolD + 0.001)}), grade)
    c = _por_celula(v)[celula]
    assert c["EXS"] == "concorda" and v["EXS"]["passou"]
    assert not c["EXN_dentro"] and abs(c["desvio"]) > c["tolD"], (
        f"{celula}: EXN must fail on |desvio| > tolD"
    )
    assert v["EXN"]["estouros"] == 1 and not v["EXN"]["passou"] and not v["passou"]
    assert v["desfecho"] == "reprova_so_EXN"


def test_ex5_exn_usa_a_tol_congelada_da_celula_e_nao_a_do_kat():
    """Check that EXN uses the frozen tolDelta of the cell, not the token KAT level tolerance.

    The tolDelta of every cell equals the frozen Table 1 (4 decimals); a shift of 0.008 in EXP-C1
    lies between its tolDelta (0.0052) and its KAT level tolerance (0.0132), so it must fail EXN.
    """
    grade = _grade()
    congelada = _tabela_1()
    v = expo.veredito(_linhas_fabricadas(grade), grade)
    for cid, c in _por_celula(v).items():
        assert f"{c['tolD']:.4f}" == congelada[cid]["tolΔ"], cid
    tolD = float(congelada["EXP-C1"]["tolΔ"])
    tol_nivel = float(congelada["EXP-C1"]["tol nível KAT"])
    assert tolD < 0.008 < tol_nivel
    v = expo.veredito(_linhas_fabricadas(grade, {"EXP-C1": 0.008}), grade)
    assert not _por_celula(v)["EXP-C1"]["EXN_dentro"] and not v["EXN"]["passou"]


def test_ex5_grade_incompleta_nao_passa():
    """Check that a verdict over fewer than the six cells never passes."""
    grade = _grade()
    parcial = {**grade, "celulas": grade["celulas"][:5]}
    v = expo.veredito(_linhas_fabricadas(parcial), parcial)
    assert v["EXS"]["passou"] and v["EXN"]["passou"]
    assert not v["completo"] and not v["passou"] and v["desfecho"] == "incompleto"


@pytest.mark.parametrize(
    ("chave", "valor"), [("N", 2000), ("bloco_usuarios", 1000), ("sementes", [0, 1, 2])]
)
def test_ex5_grade_fora_do_congelado_nao_passa(chave, valor):
    """Check that a run whose N, seeds or block size differ from the frozen grid never passes.

    A smoke run (``run_grid.py --N`` or ``--bloco-usuarios``) runs the six cells but recomputes
    ``tolDelta`` from its own N; its verdict must read ``incompleto``, never a real outcome.
    """
    grade = _grade()
    assert grade[chave] != valor
    alterada = {**grade, chave: valor}
    v = expo.veredito(_linhas_fabricadas(alterada), alterada)
    assert v["EXS"]["passou"] and v["EXN"]["passou"], (chave, v["EXS"], v["EXN"])
    assert not v["completo"], chave
    assert not v["passou"] and v["desfecho"] == "incompleto", (chave, v["desfecho"])
    assert "intervalo_implicado" not in v, chave


# --- the published run: its verdict is the one recomputed from its own rows -----------------------


def test_resumo_publicado_recomputa_do_csv():
    """Check that ``output/exponent/resumo.json`` is the pre-registered run and its verdict.

    Pins N, seeds, tag and the sha256 of grid, table and addendum, and recomputes the verdict from
    ``output/exponent/celulas.csv``. Whatever the outcome (pass or fail), it must be the one the
    rows imply.
    """
    resumo = json.loads((PUBLICADO / "resumo.json").read_text(encoding="utf-8"))
    grade = _grade()
    assert resumo["grade_sha256"] == SHA_GRADE and resumo["tabela_sha256"] == SHA_TABELA
    assert resumo["adendo_sha256"] == _sha(ADENDO)
    assert resumo["N"] == grade["N"] == 100000 and resumo["sementes"] == [0, 1, 2, 3, 4]
    assert resumo["tag"] == TAG and resumo["celulas"] == list(IDS)
    with open(PUBLICADO / "celulas.csv", newline="", encoding="utf-8") as f:
        linhas = [
            {**row, "semente": int(row["semente"]), "auc": float(row["auc"])}
            for row in csv.DictReader(f)
        ]
    assert len(linhas) == len(IDS) * 2 * len(grade["sementes"])
    assert expo.veredito(linhas, grade) == resumo["veredito"]
