"""TDD of the CMP family: fusion of events of the new source (Corollary 4(b)).

Specification frozen in ``data/prereg/07-fusion-addendum.md`` (grid ``data/fusion_grid.json``,
analytic table ``data/prereg/fusion_analytic_table.txt``). Test ids follow the pre-registration:
FU1 (identity with the sealed token-budget code), FU2 (fusion rule), FU3 (common random numbers),
FU4 (prediction = frozen analytic table) and FU5 (criterion and stream tag), plus the pins of the
frozen artifacts.
"""

import copy
import csv
import hashlib
import math
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pytest

import fusion as fu
import fusion_analytic_table as fat
import run_fusion as rf
import token_kat as kt

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/fusion_grid.json"
TABELA = RAIZ / "data/prereg/fusion_analytic_table.txt"
PREREG = RAIZ / "data/prereg/07-fusion-addendum.md"
SCRIPT_TABELA = RAIZ / "code/fusion_analytic_table.py"
KAT_CELULAS = RAIZ / "output/kat_token/celulas.csv"
SHA_GRADE = "869127a0cc6aa6e8bbc56840eb6b907ac354d5110521adc87dd69a5869951de6"
SHA_TABELA = "a4f55d6bbd3233c4edaa56c86652be1e8d43a5c62e9f0ff889361758146bcb2d"
SHA_PREREG = "e5b6cada9d320ed5880a4749ddaa9f9cc74fc05dad4920107e55515686ee53dc"


def _sha(p):
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _grade():
    """Return a fresh copy of the frozen grid."""
    return fu.carregar_grade()


def _celula(g, cid):
    """Return the cell ``cid`` of the grid ``g``."""
    return next(c for c in g["celulas"] if c["id"] == cid)


# --- pins: what was frozen before the run stays byte for byte ------------------------------------


def test_pinos_congelados():
    """Pin the sha256 of the frozen grid, analytic table and sanitized pre-registration."""
    assert _sha(GRADE) == SHA_GRADE, "grid changed after freezing"
    assert _sha(TABELA) == SHA_TABELA, "analytic table changed after freezing"
    assert _sha(PREREG) == SHA_PREREG, "sanitized pre-registration changed after freezing"


# --- FU1: identity with the sealed token-budget code ---------------------------------------------


@pytest.mark.parametrize("cid", ["CMP1", "CMP2", "CMP5"])
def test_fu1a_rs_identico_a_simular_literal_tokens(cid):
    """FU1(a): arm RS = ``simular_literal_tokens``, scores byte-identical with the same generator.

    Uses the real ``K`` in cells whose raw history saturates, so the window truncates.
    """
    g = _grade()
    cel = _celula(g, cid)
    N = 3000
    res, y = fu.simular_fusao(cel, np.random.default_rng([11, 5]), N, g["K"])
    fontes = kt.fontes_da_celula(cel, "RS")
    nomes = "".join(fontes)
    s_kat, y_kat, diag_kat = kt.simular_literal_tokens(
        nomes,
        {n: p["lam"] for n, p in fontes.items()},
        {n: p["d"] for n, p in fontes.items()},
        {n: p["k"] for n, p in fontes.items()},
        cel["T"],
        N,
        np.random.default_rng([11, 5]),
        g["K"],
    )
    escores, diag = res["RS"]
    assert diag_kat["n_saturados"] > 0, "cell must saturate for the identity to test truncation"
    assert y.tobytes() == y_kat.tobytes(), "labels differ from simular_literal_tokens"
    assert escores.tobytes() == s_kat.tobytes(), "RS scores differ from simular_literal_tokens"
    assert diag["n_saturados"] == diag_kat["n_saturados"]
    assert diag["soma_ociosos"] == diag_kat["soma_ociosos"]


@pytest.mark.parametrize("cid", ["CMP1", "CMP2"])
def test_fu1b_m1_e_custo_cru_identicos_a_rs(cid):
    """FU1(b): with ``m = 1`` and ``k' = k_S``, arms RF and RP are byte-identical to RS."""
    g = _grade()
    cel = copy.deepcopy(_celula(g, cid))
    ((_, S),) = cel["S"].items()
    cel["m"], cel["k_fund"] = 1, S["k"]
    res, _ = fu.simular_fusao(cel, np.random.default_rng([12, 7]), 3000, g["K"])
    s_rs, d_rs = res["RS"]
    assert d_rs["n_saturados"] > 0, "cell must saturate for the identity to test truncation"
    for braco in ("RF", "RP"):
        s_b, d_b = res[braco]
        assert s_b.tobytes() == s_rs.tobytes(), f"{braco} scores != RS with m = 1 and k' = k_S"
        assert d_b["n_saturados"] == d_rs["n_saturados"], f"{braco}: saturated users differ"
        assert d_b["soma_ociosos"] == d_rs["soma_ociosos"], f"{braco}: idle tokens differ"


def test_fu1c_rs_com_fluxo_do_kat_reproduz_linhas_seladas(tmp_path):
    """FU1(c): arm RS fed with the sealed KAT stream reproduces the sealed rows of S1b and S2b.

    ``[seed, 1, 1, 3, i_block]`` for S1b (= CMP1 R ∪ S) and ``[seed, 3, 1, 3, i_block]`` for S2b
    (= CMP4 R ∪ S); per seed, ``auc`` with equality of ``repr``, ``n_pos`` and ``n_neg`` equal.
    Written to a temporary directory; outside the verdict.
    """
    g = _grade()
    g_kat = {**g, "tag": 3}  # the sealed KAT stream (tag 3), for this identity check only
    pares = {"S1b": (1, _celula(g, "CMP1")), "S2b": (3, _celula(g, "CMP4"))}
    tarefas = [
        (i_kat, cel, 1, s, g_kat, ("RS",)) for i_kat, cel in pares.values() for s in g["sementes"]
    ]
    with ProcessPoolExecutor(max_workers=min(len(tarefas), os.cpu_count() or 1)) as ex:
        linhas = [row for rows in ex.map(rf._uma_tarefa, tarefas) for row in rows]
    rf.escrever_csv(linhas, tmp_path / "celulas.csv")
    with open(tmp_path / "celulas.csv", newline="", encoding="utf-8") as f:
        novas = list(csv.DictReader(f))
    with open(KAT_CELULAS, newline="", encoding="utf-8") as f:
        seladas = {
            (row["i_celula"], row["semente"]): row
            for row in csv.DictReader(f)
            if row["combo"] == "RS" and row["celula"] in pares
        }
    assert len(novas) == len(seladas) == 10
    for row in novas:
        sel = seladas[(row["i_celula"], row["semente"])]
        chave = f"{sel['celula']} seed {row['semente']}"
        assert row["auc"] == sel["auc"], f"{chave}: auc {row['auc']} != sealed {sel['auc']}"
        assert row["n_pos"] == sel["n_pos"] and row["n_neg"] == sel["n_neg"], chave


# --- FU2: fusion rule ----------------------------------------------------------------------------


def _eventos_s():
    """Return a hand-built set of S events: user 0 with 7 events, user 1 with 2 tied in time."""
    usuario = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1])
    tempos = np.array([5.0, 1.0, 3.0, 7.0, 2.0, 6.0, 4.0, 3.0, 3.0])
    ordem = np.arange(10, 19)
    contrib = 2.0 ** np.arange(9)  # powers of two: every block sum is exact
    return usuario, tempos, ordem, contrib


def test_fu2_blocos_ancorados_no_mais_recente():
    """FU2: block 0 = the ``m`` most recent; the incomplete block is the oldest.

    Also: time and input order of a block = those of its most recent member; RF sums the members;
    the representative is the most recent member (explicit index); a tie in time is resolved by the
    input order (later = more recent); a user with no event of S has no block.
    """
    usuario, tempos, ordem, contrib = _eventos_s()
    b = fu.fundir(usuario, tempos, ordem, contrib, 3, N=3)
    assert b["usuario"].tolist() == [0, 0, 0, 1]
    assert b["bloco"].tolist() == [0, 1, 2, 0], "blocks numbered from the most recent"
    assert b["representante"].tolist() == [3, 6, 1, 8], "representative = most recent member"
    assert b["tempo"].tolist() == [7.0, 4.0, 1.0, 3.0], "block time = most recent member's"
    assert b["ordem"].tolist() == [13, 16, 11, 18], "block order = most recent member's"
    assert b["membros"].tolist() == [3, 3, 1, 2]
    assert b["incompleto"].tolist() == [False, False, True, True], "incomplete block = the oldest"
    somas = [2.0**3 + 2.0**5 + 2.0**0, 2.0**6 + 2.0**2 + 2.0**4, 2.0**1, 2.0**7 + 2.0**8]
    assert b["soma"].tolist() == somas, "RF block = sum of the members' contributions"


def _eventos_rs():
    """Return a hand-built draw of R ∪ S for one user: 2 events of R (source 0), 7 of S (1)."""
    usuario, tempos_s, _, contrib_s = _eventos_s()
    so_0 = usuario == 0
    return {
        "usuario": np.zeros(9, dtype=np.int64),
        "fonte": np.array([0, 0] + [1] * 7),
        "tempos": np.concatenate([[0.5, 6.5], tempos_s[so_0]]),
        "ordem": np.arange(9),
        "custos": np.array([14, 14] + [55] * 7, dtype=np.int64),
        "contrib": np.concatenate([[1000.0, 3000.0], contrib_s[so_0]]),
    }


def test_fu2_lista_fundida_custo_e_contribuicoes():
    """FU2: every block costs ``k'`` (the incomplete one too); RF sums; RP keeps the most recent.

    Events of R pass through unchanged, and the incomplete block is kept, never dropped.
    """
    ev = _eventos_rs()
    lf = fu.lista_fundida(ev, i_S=1, m=3, k_fund=40, N=1)
    bloco = lf["e_bloco"]
    assert int(bloco.sum()) == 3, "ceil(7/3) = 3 blocks, the incomplete one included"
    assert lf["custos"][bloco].tolist() == [40, 40, 40], "block cost = k' (incomplete too)"
    assert lf["custos"][~bloco].tolist() == [14, 14], "events of R keep their cost"
    assert lf["contrib_RF"][~bloco].tolist() == [1000.0, 3000.0]
    assert lf["contrib_RP"][~bloco].tolist() == [1000.0, 3000.0]
    c = ev["contrib"]
    # members (positions in ``ev``): block 0 = {5, 7, 2}, block 1 = {8, 4, 6}, block 2 = {3}
    assert lf["contrib_RF"][bloco].tolist() == [c[5] + c[7] + c[2], c[8] + c[4] + c[6], c[3]]
    assert lf["contrib_RP"][bloco].tolist() == [c[5], c[8], c[3]], "RP = most recent member"
    assert lf["ordem"][bloco].tolist() == [5, 8, 3], "block order = most recent member's"
    assert lf["incompleto"][bloco].tolist() == [False, False, True]


def test_fu2_empate_R_bloco_no_mesmo_tempo():
    """FU2: a tie in time between an event of R and a block goes by the most recent member's order.

    The event of R enters before the events of S in the draw of a user, so the block (whose order
    is the one of its most recent member) is the more recent of the two and is the one kept.
    """
    ev = {
        "usuario": np.zeros(4, dtype=np.int64),
        "fonte": np.array([0, 1, 1, 1]),
        "tempos": np.array([5.0, 1.0, 2.0, 5.0]),
        "ordem": np.arange(4),
        "custos": np.array([14, 55, 55, 55], dtype=np.int64),
        "contrib": np.array([1.0, 2.0, 4.0, 8.0]),
    }
    lf = fu.lista_fundida(ev, i_S=1, m=3, k_fund=55, N=1)
    escores, visivel, _ = fu.janela_eventos(
        lf["usuario"], lf["tempos"], lf["ordem"], lf["custos"], lf["contrib_RF"], 1, 60
    )
    assert visivel.tolist() == [False, True], "the block (most recent member) must win the tie"
    assert escores.tolist() == [14.0], "only the block (2 + 4 + 8) fits in K = 60"


# --- FU3: common random numbers ------------------------------------------------------------------


def test_fu3_numeros_aleatorios_comuns():
    """FU3: with a huge ``K``, the scores of RF equal those of RS (atol 1e-12, rtol 0).

    Goes through the runner's block function, i.e. through the stream the run uses.
    """
    g = _grade()
    g_grande = {**g, "K": 10**9, "bloco_usuarios": 2000}
    res, _ = rf.escores_do_bloco(0, _celula(g, "CMP1"), 1, 0, 0, g_grande)
    s_rs, s_rf, s_rp = res["RS"][0], res["RF"][0], res["RP"][0]
    assert np.allclose(s_rf, s_rs, rtol=0, atol=1e-12), "RF != RS with every event visible"
    assert not np.allclose(s_rp, s_rs, rtol=0, atol=1e-12), "control: RP keeps one member only"
    res_k, _ = rf.escores_do_bloco(0, _celula(g, "CMP1"), 1, 0, 0, {**g, "bloco_usuarios": 2000})
    assert not np.allclose(res_k["RF"][0], res_k["RS"][0], rtol=0, atol=1e-12), (
        "control: with the real K the fused window differs"
    )


# --- FU4: prediction = frozen analytic table -----------------------------------------------------


def _tabela_celulas():
    """Return {cell: (regimes of R, RS, RF, RP; fluid AUCs; tolerances)} from the frozen table."""
    out = {}
    for linha in TABELA.read_text(encoding="utf-8").splitlines():
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cel) == 14 and cel[0].startswith("CMP"):
            out[cel[0]] = (cel[4].split(" · "), cel[12].split(" · "), cel[13].split(" · "))
    return out


def test_fu4a_forma_fechada_reproduz_a_tabela():
    """FU4(a): the closed form reproduces, per cell and arm, the AUC and regime of the table."""
    g = _grade()
    tab = _tabela_celulas()
    assert sorted(tab) == [c["id"] for c in g["celulas"]]
    for cel in g["celulas"]:
        regimes, aucs, _ = tab[cel["id"]]
        a = fat.analisar(cel, g)
        for i, braco in enumerate(fu.BRACOS):
            chave = f"{cel['id']}/{braco}"
            A = fu.auc_fluida_braco(cel, braco, g["K"])
            assert f"{A:.4f}" == aucs[i], f"{chave}: AUC {A:.4f} != table {aucs[i]}"
            assert abs(A - a["A"][braco]) <= 1e-12, f"{chave}: closed form != table generator"
            assert fu.regime_braco(cel, braco, g["K"]) == regimes[i], f"{chave}: regime"


def test_fu4b_tabela_portada_reproduz_o_arquivo_congelado():
    """FU4(b): stdout of the ported generator on the grid == the frozen table, byte for byte."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT_TABELA), "--grade", str(GRADE)],
        capture_output=True,
        env={**os.environ, "PYTHON_COLORS": "0", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert r.returncode == 0, f"design criterion failed: {r.stderr.decode().splitlines()[-1:]}"
    assert r.stdout == TABELA.read_bytes(), "ported analytic table != frozen file"


# --- FU5: criterion and stream tag ---------------------------------------------------------------


def test_fu5_tag_exclusiva_e_fluxo_do_runner():
    """FU5: ``grade["tag"] == 7``, 7 differs from 3, 5, 6 and 8, and the runner uses that stream."""
    g = _grade()
    assert "tag_r3" not in g
    assert g["tag"] == 7 and 7 not in {3, 5, 6, 8}
    assert fu.TAG_FAMILIA == 7 and fu.TAG_FAMILIA not in fu.TAGS_OUTRAS
    assert fu.TAGS_OUTRAS == {3, 5, 6, 8}
    assert rf.fluxo(4, 2, 1, 9, g) == [4, 2, 1, 7, 9], (
        "stream = [seed, i_cell, i_stream, 7, i_block]"
    )
    g_p = {**g, "bloco_usuarios": 1500}
    cel = _celula(g, "CMP2")
    res, y = rf.escores_do_bloco(1, cel, 1, 3, 2, g_p)
    ref, y_ref = fu.simular_fusao(cel, np.random.default_rng([3, 1, 1, 7, 2]), 1500, g["K"])
    assert y.tobytes() == y_ref.tobytes()
    for braco in ("RS", "RF", "RP"):
        assert res[braco][0].tobytes() == ref[braco][0].tobytes(), f"{braco}: stream != tag 7"
    res_r, y_r = rf.escores_do_bloco(1, cel, 0, 3, 2, g_p)
    fontes = kt.fontes_da_celula(cel, "R")
    s_r, y_r_ref, _ = kt.simular_literal_tokens(
        "".join(fontes),
        {n: p["lam"] for n, p in fontes.items()},
        {n: p["d"] for n, p in fontes.items()},
        {n: p["k"] for n, p in fontes.items()},
        cel["T"],
        1500,
        np.random.default_rng([3, 1, 0, 7, 2]),
        g["K"],
    )
    assert set(res_r) == {"R"}
    assert y_r.tobytes() == y_r_ref.tobytes() and res_r["R"][0].tobytes() == s_r.tobytes()


def test_fu5_papeis_lidos_da_tabela():
    """FU5: the role (criterion x report-only) is read from the frozen analytic table."""
    papeis = fu.papeis_da_tabela()
    assert len(papeis) == 30
    contagem = {}
    for p in papeis.values():
        contagem[p["papel"]] = contagem.get(p["papel"], 0) + 1
    assert contagem == {"critério": 28, "critério (nulo)": 1, "só reportado": 1}
    assert papeis[("CMP3", "RP-RS")]["papel"] == "só reportado"
    assert papeis[("CMP6", "RF-RS")]["papel"] == "critério (nulo)"
    assert papeis[("CMP1", "RS-R")]["sinal"] == "piora"
    assert papeis[("CMP5", "RF-R")]["sinal"] == "melhora"


def test_fu5_tolerancia_inclui_disc_bloco():
    """FU5: the level tolerance of an arm = the token KAT one + ``disc_bloco`` (= the table)."""
    g = _grade()
    tol = fu.tolerancias(g)
    tab = _tabela_celulas()
    for cel in g["celulas"]:
        for i, braco in enumerate(fu.BRACOS):
            t = tol[(cel["id"], braco)]
            assert t["tol"] == t["tol_sem_disc"] + t["disc_bloco"]
            assert f"{t['tol']:.4f}" == tab[cel["id"]][2][i], f"{cel['id']}/{braco}: tol"
            if braco in ("R", "RS"):
                assert t["disc_bloco"] == 0.0
    assert tol[("CMP3", "RP")]["disc_bloco"] > 0.002, "largest block bound (table: 0.0022)"


# --- FU5: the evaluator on synthetic rows --------------------------------------------------------

DESVIOS = (-2e-4, -1e-4, 0.0, 1e-4, 2e-4)  # per-seed offsets: variance (ddof = 1) = 2.5e-8


def _linhas(g, deslocar=None, desvios_de=None):
    """Return synthetic rows: per seed, AUC = fluid AUC + offset (+ a shift per cell and arm)."""
    deslocar = deslocar or {}
    desvios_de = desvios_de or {}
    linhas = []
    for cel in g["celulas"]:
        for braco in fu.BRACOS:
            base = fu.auc_fluida_braco(cel, braco, g["K"]) + deslocar.get((cel["id"], braco), 0.0)
            for s, dv in zip(
                g["sementes"], desvios_de.get((cel["id"], braco), DESVIOS), strict=True
            ):
                linhas.append({"celula": cel["id"], "braco": braco, "semente": s, "auc": base + dv})
    return linhas


def _avaliar(g, **kw):
    """Evaluate synthetic rows with the pre-registered tolerances and roles."""
    return fu.avaliar_fusao(_linhas(g, **kw), g, fu.tolerancias(g), fu.papeis_da_tabela())


def _contraste(av, cid, nome):
    """Return the contrast entry ``nome`` (e.g. ``"RF-R"``) of cell ``cid``."""
    return next(c for c in av["por_contraste"] if c["celula"] == cid and c["contraste"] == nome)


def _braco(av, cid, braco):
    """Return the arm entry of cell ``cid``."""
    return next(b for b in av["por_braco"] if b["celula"] == cid and b["braco"] == braco)


def test_fu5_avaliador_passa_na_forma_fechada_e_usa_ddof1():
    """FU5: rows at the closed form pass every criterion; the SE uses the seed mean and ddof = 1."""
    g = _grade()
    av = _avaliar(g)
    assert av["passou"] and av["veredito"] == "PASSA"
    assert av["CMP_S"] == {
        "passou": True,
        "contrastes": 28,
        "concordam": 28,
        "discordantes": 0,
        "empates": 0,
        "sem_significancia": 0,
    }
    assert av["CMP_0"]["passou"] and av["CMP_N"] == {"passou": True, "combos": 24, "estouros": 0}
    assert av["CMP_T"]["passou"] and av["CMP_T"]["no_veredito"] is False
    c = _contraste(av, "CMP1", "RF-R")
    var = float(np.var(DESVIOS, ddof=1))
    assert math.isclose(c["ep_dif"], math.sqrt(var / 5 + var / 5), rel_tol=1e-9)
    assert math.isclose(c["dif_empirica"], c["dif_prevista"], abs_tol=1e-12)


def test_fu5_empate_por_falta_de_poder_reprova():
    """FU5: ``|predicted| < 3 SE`` is a tie and fails for lack of power."""
    g = _grade()
    largos = (-0.05, -0.025, 0.0, 0.025, 0.05)
    av = _avaliar(g, desvios_de={("CMP2", "RS"): largos})
    assert _contraste(av, "CMP2", "RS-R")["estado"] == "empate"
    assert not av["CMP_S"]["passou"] and av["CMP_S"]["empates"] >= 1
    assert not av["passou"] and av["veredito"] == "REPROVA"


def test_fu5_sinal_certo_sem_3_ep_reprova():
    """FU5: the right sign with ``|difference| < 3 SE`` fails (``H_dia`` predicts zero)."""
    g = _grade()
    cel = _celula(g, "CMP1")
    alvo = fu.auc_fluida_braco(cel, "R", g["K"]) + 2e-4 - fu.auc_fluida_braco(cel, "RF", g["K"])
    av = _avaliar(g, deslocar={("CMP1", "RF"): alvo})
    assert _contraste(av, "CMP1", "RF-R")["estado"] == "sem_significancia"
    assert av["CMP_S"]["sem_significancia"] >= 1 and not av["passou"]


def test_fu5_discordancia_reprova():
    """FU5: one discordant sign fails CMP-S."""
    g = _grade()
    cel = _celula(g, "CMP1")
    alvo = fu.auc_fluida_braco(cel, "R", g["K"]) + 0.01 - fu.auc_fluida_braco(cel, "RS", g["K"])
    av = _avaliar(g, deslocar={("CMP1", "RS"): alvo})
    assert _contraste(av, "CMP1", "RS-R")["estado"] == "discorda"
    assert av["CMP_S"]["discordantes"] >= 1 and not av["passou"]


def test_fu5_nulo_usa_tol_0():
    """FU5: the null contrast (CMP6 RF - RS) passes within ``tol_0 = 0.0041``, fails beyond it."""
    g = _grade()
    dentro = _avaliar(g, deslocar={("CMP6", "RF"): 0.0039})
    assert dentro["CMP_0"]["passou"] and dentro["passou"]
    assert dentro["CMP_0"]["tol_0"] == 0.0041
    fora = _avaliar(g, deslocar={("CMP6", "RF"): 0.0043})
    assert not fora["CMP_0"]["passou"] and not fora["passou"]
    assert fora["CMP_S"]["passou"] and fora["CMP_N"]["passou"], "only the null fails here"


def test_fu5_nivel_usa_tolerancia_com_disc_bloco():
    """FU5: an arm inside ``tol`` only thanks to ``disc_bloco`` passes CMP-N; beyond it fails."""
    g = _grade()
    t = fu.tolerancias(g)[("CMP3", "RP")]
    meio = t["tol_sem_disc"] + t["disc_bloco"] / 2
    av = _avaliar(g, deslocar={("CMP3", "RP"): meio})
    b = _braco(av, "CMP3", "RP")
    assert abs(b["desvio"]) > t["tol_sem_disc"] and b["dentro"] and av["CMP_N"]["passou"]
    fora = _avaliar(g, deslocar={("CMP3", "RP"): t["tol"] + 5e-4})
    assert not _braco(fora, "CMP3", "RP")["dentro"] and not fora["CMP_N"]["passou"]
    assert not fora["passou"]


def test_fu5_so_reportado_fica_fora_do_veredito():
    """FU5: a report-only contrast (CMP3 RP - RS) that disagrees does not fail the verdict."""
    g = _grade()
    cel = _celula(g, "CMP3")
    alvo = fu.auc_fluida_braco(cel, "RS", g["K"]) - 0.005 - fu.auc_fluida_braco(cel, "RP", g["K"])
    av = _avaliar(g, deslocar={("CMP3", "RP"): alvo})
    c = _contraste(av, "CMP3", "RP-RS")
    assert c["papel"] == "só reportado" and c["estado"] == "discorda"
    assert av["passou"] and av["CMP_S"]["contrastes"] == 28


def test_fu5_teto_fora_do_veredito():
    """FU5: CMP-T (ceiling of the saturated RF) is reported but does not fail the verdict."""
    g = _grade()
    av = _avaliar(g, deslocar={("CMP1", "RF"): 0.004})
    assert not av["CMP_T"]["passou"] and av["CMP_T"]["estouros"] == 1
    assert av["CMP_N"]["passou"] and av["passou"]


def test_fu5_semente_faltando_levanta():
    """FU5: every (cell, arm) needs every seed; a missing row raises instead of passing."""
    g = _grade()
    linhas = _linhas(g)[1:]
    with pytest.raises(ValueError, match="seeds"):
        fu.avaliar_fusao(linhas, g, fu.tolerancias(g), fu.papeis_da_tabela())
