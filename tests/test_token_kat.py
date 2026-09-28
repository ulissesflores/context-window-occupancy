"""TDD of the token KAT: a token-budget window with heterogeneous per-event cost.

Specification frozen in ``data/prereg/02-token-kat-addendum.md``: KT1 (identity with the
displacement replication code), KT2 (truncation), KT3 (prediction = analytic table) and the
evaluator of the KT-S / KT-N criterion.
"""

import hashlib
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import displacement as rd
import token_kat as kt

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/kat_token_grid.json"
TABELA = RAIZ / "data/prereg/kat_token_analytic_table.txt"
SCRIPT_TABELA = RAIZ / "code/token_kat_analytic_table.py"
# sha256 of the frozen grid and analytic table of this repository (the private originals differ
# only by the declared renaming of the mixed-regime cells and by the grid sha in the first line)
SHA_GRADE = "2cd4cd1218f0822df03a61e163406cb043014dd99e8ce210e740725a494d0b22"
SHA_TABELA = "d08c24752a1527a976b6e12dd57522e42139f08b0309bd8f076b0eb8d0940784"


def _sha(p):
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- pins: what was frozen before the run stays byte for byte ------------------------------------


def test_pinos_congelados():
    """Pin the sha256 of the frozen grid and of the frozen analytic table of this repository.

    The integrity of the code is guarded by the provenance chain (``make_provenance.py --verify``),
    not by a pin here.
    """
    assert _sha(GRADE) == SHA_GRADE, "grid changed after freezing"
    assert _sha(TABELA) == SHA_TABELA, "analytic table changed after freezing"


def test_tabela_analitica_reproduz_e_passa_os_criterios():
    """Check that the analytic-table script passes its design criteria and reproduces the file."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT_TABELA)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHON_COLORS": "0"},  # traceback without ANSI in the assert message
    )
    assert r.returncode == 0, (
        f"analytic table failed a design criterion: {r.stderr.strip().splitlines()[-1:]}"
    )
    assert r.stdout == TABELA.read_text(encoding="utf-8"), "analytic table != frozen file"


def test_constantes_batem_com_a_grade():
    """Check K = 2048, the prevalence of the replication, and floor(K/14) = L of the replication."""
    g = kt.carregar_grade()
    assert g["K"] == 2048 and g["pi"] == rd.PI
    assert math.floor(g["K"] / 14) == rd.L_JANELA, "identity KT1 needs floor(K/14) = L"


# --- KT2: truncation by budget -------------------------------------------------------------------


def _visiveis(tempos, custos, K):
    """Return the visible indices of the token window as a list."""
    return kt.janela_tokens(
        np.asarray(tempos, dtype=float), np.asarray(custos, dtype=np.int64), K
    ).tolist()


def test_truncamento_sufixo_maximo():
    """Check the longest suffix with cost <= K."""
    assert _visiveis([1, 2, 3], [5, 5, 5], 10) == [1, 2], "longest suffix with cost <= K"


def test_truncamento_custo_exatamente_K_cabe():
    """Check that a summed cost of exactly K fits (<=, not <)."""
    assert _visiveis([1, 2], [4, 6], 10) == [0, 1], "cost exactly K must fit (<=, not <)"


def test_truncamento_evento_que_estoura_cai_sem_pular():
    """Check that the overflowing event drops with every older one (no partial, no skipping)."""
    # suffix: 2 (fits) + 9 = 11 > 10 -> stop; event 0 (cost 3) would fit by skipping 1, but it does
    # NOT enter
    assert _visiveis([1, 2, 3], [3, 9, 2], 10) == [2], "overflowing event drops with the older ones"


def test_truncamento_empate_por_ordem_de_entrada():
    """Check the tie-break: the event that appears LATER in the input is more recent."""
    assert _visiveis([1.0, 1.0, 1.0], [4, 4, 4], 8) == [1, 2], "tie: later in the input is newer"


def test_truncamento_historico_que_cabe_fica_inteiro_e_ordenado():
    """Check that a history with cost <= K stays whole, in order of recency."""
    assert _visiveis([3, 1, 2], [2, 2, 2], 100) == [1, 2, 0], "history <= K stays whole, ordered"


def test_truncamento_vazio():
    """Check that an empty history gives an empty window."""
    assert _visiveis([], [], 10) == [], "empty history gives an empty window"


def test_truncamento_ordena_por_tempo_antes_de_cortar():
    """Check that the window cuts by time, not by position in the input."""
    # the newest is index 0 (t=9); a budget of 5 only fits it
    assert _visiveis([9, 1, 5], [5, 5, 5], 5) == [0], "the window cuts by time, not by position"


# --- KT1: identity with the replication code (k = 14, K = 2048 => L = 146) ----------------------


def test_kt1a_indices_identicos_a_janela_ultimos_do_r1():
    """Check KT1a: with k = 14 and K = 2048 the token window equals ``janela_ultimos(L=146)``."""
    rng = np.random.default_rng(20260926)
    for _ in range(400):
        n = int(rng.integers(0, 400))
        tempos = np.round(rng.uniform(0, 30, n), 0)  # rounding forces ties
        esperado = rd.janela_ultimos(tempos, rd.L_JANELA).tolist()
        obtido = kt.janela_tokens(tempos, np.full(n, 14, dtype=np.int64), 2048).tolist()
        assert obtido == esperado, "KT1a: token window (k=14, K=2048) != janela_ultimos(L=146)"


@pytest.mark.parametrize(
    "T,lam",
    [
        (90, {"A": 0.2, "B": 0.6, "C": 3.0}),  # saturated
        (90, {"A": 0.1, "B": 0.3, "C": 1.0}),  # unsaturated
    ],
)
def test_kt1b_escores_byte_identicos_ao_simular_literal_do_r1(T, lam):
    """Check KT1b: with k = 14 the token simulation is byte-identical to ``simular_literal``."""
    d = {"A": 0.5, "B": 0.15, "C": 0.05}
    k = {"A": 14, "B": 14, "C": 14}
    s_r1, y_r1 = rd.simular_literal("ABC", lam, d, T, 3000, np.random.default_rng(7), L=rd.L_JANELA)
    s_tk, y_tk, _ = kt.simular_literal_tokens(
        "ABC", lam, d, k, T, 3000, np.random.default_rng(7), K=2048
    )
    assert np.array_equal(y_r1, y_tk), "KT1b: labels differ (order of draws != replication)"
    assert s_r1.tobytes() == s_tk.tobytes(), "KT1b: scores not byte-identical to simular_literal"


def test_diagnostico_de_ociosidade():
    """Check the idle-token diagnostic: 1 source, k = 55, K = 2048 leaves 13 idle tokens."""
    # saturated: 2048 - 55*37 = 13 idle tokens (37 events fit)
    s, y, diag = kt.simular_literal_tokens(
        "A", {"A": 5.0}, {"A": 0.1}, {"A": 55}, 90, 2000, np.random.default_rng(3), K=2048
    )
    assert diag["n_saturados"] == 2000, "every user with ~450 events of 55 tokens saturates"
    assert diag["soma_ociosos"] == 13 * 2000, "idle = K - 55*floor(K/55) per saturated user"


# --- KT3: prediction of the module = frozen analytic table --------------------------------------


def _linhas_tabela():
    """Parse the rows of the frozen analytic table (AUCs, dAUC and closed-form sign per cell)."""
    out = {}
    for row in TABELA.read_text(encoding="utf-8").splitlines():
        if row.startswith("| ") and not row.startswith("| célula"):
            c = [x.strip() for x in row.strip("|").split("|")]
            out[c[0]] = {
                "auc_R": float(c[10]),
                "auc_RS": float(c[11]),
                "d_auc": float(c[12]),
                "sinal": c[15],
            }
    return out


def test_kt3_forma_fechada_do_modulo_reproduz_a_tabela():
    """Check KT3: the closed form of the module reproduces the AUCs and signs of the table."""
    g = kt.carregar_grade()
    tab = _linhas_tabela()
    assert set(tab) == {c["id"] for c in g["celulas"]}
    for cel in g["celulas"]:
        a_r = kt.auc_fluida(kt.fontes_da_celula(cel, "R"), cel["T"], g["K"])
        a_rs = kt.auc_fluida(kt.fontes_da_celula(cel, "RS"), cel["T"], g["K"])
        t = tab[cel["id"]]
        assert abs(a_r - t["auc_R"]) <= 5e-5 and abs(a_rs - t["auc_RS"]) <= 5e-5, (
            f"KT3: closed form of the module != table at cell {cel['id']}"
        )
        assert ("melhora" if a_rs > a_r else "piora") == t["sinal"], (
            f"KT3: sign != table at cell {cel['id']}"
        )


def test_fontes_da_celula_ordem_e_uniao():
    """Check the order of the sources of R and of R ∪ S."""
    g = kt.carregar_grade()
    s3 = next(c for c in g["celulas"] if c["id"] == "S3")
    assert list(kt.fontes_da_celula(s3, "R")) == ["A", "B"]
    assert list(kt.fontes_da_celula(s3, "RS")) == ["A", "B", "C"]


# --- evaluator of the KT-S / KT-N criterion ------------------------------------------------------


def _linhas_sinteticas(g, deslocamento=None):
    """Build rows with AUC = exact closed form + small deterministic noise per seed.

    ``deslocamento`` shifts one (cell, combination).
    """
    linhas = []
    for cel in g["celulas"]:
        for combo in ("R", "RS"):
            a = kt.auc_fluida(kt.fontes_da_celula(cel, combo), cel["T"], g["K"])
            for s in g["sementes"]:
                extra = deslocamento.get((cel["id"], combo), 0.0) if deslocamento else 0.0
                linhas.append(
                    {
                        "celula": cel["id"],
                        "combo": combo,
                        "semente": s,
                        "auc": a + extra + 1e-4 * (s - 2),
                    }
                )
    return linhas


def _tol(g, valor=0.0137):
    """Return the same tolerance for every (cell, combination)."""
    return {(c["id"], combo): valor for c in g["celulas"] for combo in ("R", "RS")}


def test_avaliador_aprova_quando_tudo_bate():
    """Check that the evaluator passes exact data."""
    g = kt.carregar_grade()
    r = kt.avaliar_kat(_linhas_sinteticas(g), g, _tol(g))
    assert r["passou"] and r["KT_S"]["passou"] and r["KT_N"]["passou"], (
        "evaluator failed exact data"
    )
    assert r["KT_S"]["discordantes"] == 0 and r["KT_S"]["empates"] == 0
    assert r["KT_N"]["estouros"] == 0


def test_avaliador_reprova_discordancia_de_sinal():
    """Check that a sign discordance fails KT-S (and the global verdict)."""
    g = kt.carregar_grade()
    # S2a predicts +0.0237: pushing R ∪ S down by 0.05 inverts the sign (and exceeds the level)
    r = kt.avaliar_kat(_linhas_sinteticas(g, {("S2a", "RS"): -0.05}), g, _tol(g, 1.0))
    assert not r["KT_S"]["passou"] and r["KT_S"]["discordantes"] == 1, "KT-S did not fail"
    assert r["KT_N"]["passou"], "with tol = 1 the level cannot fail"
    assert not r["passou"]


def test_avaliador_reprova_empate_por_falta_de_poder():
    """Check that a tie (3 SE > |predicted|) fails KT-S for lack of power."""
    g = kt.carregar_grade()
    linhas = _linhas_sinteticas(g)
    for row in linhas:  # huge between-seed noise only in S1a/R ∪ S => 3 SE > |predicted dAUC|
        if row["celula"] == "S1a" and row["combo"] == "RS":
            row["auc"] += 0.2 * (row["semente"] - 2)
    r = kt.avaliar_kat(linhas, g, _tol(g, 1.0))
    assert r["KT_S"]["empates"] == 1 and not r["KT_S"]["passou"], "KT-S tie did not fail"


def test_avaliador_reprova_estouro_de_nivel():
    """Check that a level exceedance fails KT-N and the global verdict, not KT-S."""
    g = kt.carregar_grade()
    r = kt.avaliar_kat(_linhas_sinteticas(g, {("N1", "R"): 0.02}), g, _tol(g, 0.0137))
    assert not r["KT_N"]["passou"] and r["KT_N"]["estouros"] == 1, "KT-N exceedance did not fail"
    assert r["KT_S"]["passou"], "the shift of N1/R does not invert the sign of N1"
    assert not r["passou"], "global verdict passed with KT-N failed"


def test_avaliador_nivel_na_fronteira_passa():
    """Check that a deviation within the tolerance (<=) passes KT-N."""
    g = kt.carregar_grade()
    r = kt.avaliar_kat(_linhas_sinteticas(g, {("N1", "R"): 0.0100}), g, _tol(g, 0.0103))
    assert r["KT_N"]["passou"], "a deviation within the tolerance (<=) cannot fail"


def test_avaliador_dado_incompleto_e_valueerror():
    """Check that a missing seed raises ``ValueError``."""
    g = kt.carregar_grade()
    linhas = [
        row
        for row in _linhas_sinteticas(g)
        if not (row["celula"] == "MIX2" and row["semente"] == 4)
    ]
    with pytest.raises(ValueError):
        kt.avaliar_kat(linhas, g, _tol(g))


# --- vectorised path x per-user reference (heterogeneous cost) ----------------------------------


def _referencia_por_usuario(combo, lam, d, k, T, N, rng, K):
    """Recompute the scores with the same draws, applying ``janela_tokens`` user by user.

    Costs that are multiples of 14 and K = 280 make windows with cost exactly K appear.
    """
    y = rng.random(N) < rd.PI
    lams = np.array([lam[s] for s in combo])
    d_c = np.array([d[s] for s in combo])
    k_c = np.array([k[s] for s in combo], dtype=np.int64)
    cont = rng.poisson(lams[None, :] * T, size=(N, len(combo)))
    u_idx = np.repeat(np.repeat(np.arange(N), len(combo)), cont.ravel())
    f_idx = np.repeat(np.tile(np.arange(len(combo)), N), cont.ravel())
    tempos = rng.uniform(0.0, T, size=len(u_idx))
    x = rng.normal(d_c[f_idx] * y[u_idx].astype(float), 1.0, size=len(u_idx))
    contrib = d_c[f_idx] * (x - d_c[f_idx] / 2)
    escores, exatos = np.zeros(N), 0
    for u in range(N):
        ev = np.flatnonzero(u_idx == u)
        vis = kt.janela_tokens(tempos[ev], k_c[f_idx[ev]], K)
        escores[u] = contrib[ev][vis].sum()
        exatos += int(k_c[f_idx[ev]][vis].sum() == K)
    return escores, y, exatos


def test_vetorizado_igual_a_referencia_por_usuario():
    """Check the vectorised path against ``janela_tokens`` applied user by user."""
    lam, d, k = (
        {"A": 0.3, "B": 0.4, "C": 1.0},
        {"A": 0.4, "B": 0.2, "C": 0.1},
        {"A": 14, "B": 70, "C": 28},
    )
    s_v, y_v, _ = kt.simular_literal_tokens(
        "ABC", lam, d, k, 30, 400, np.random.default_rng(11), K=280
    )
    s_r, y_r, exatos = _referencia_por_usuario(
        "ABC", lam, d, k, 30, 400, np.random.default_rng(11), K=280
    )
    assert exatos >= 20, f"the test needs windows with cost exactly K (found {exatos})"
    assert np.array_equal(y_v, y_r)
    assert np.allclose(s_v, s_r, rtol=0, atol=1e-12), (
        "vectorised path != janela_tokens applied user by user (heterogeneous cost)"
    )


# --- runner: stream declared in the addendum ------------------------------------------------------


def test_runner_usa_o_fluxo_declarado():
    """Check that the runner uses ``default_rng([seed, cell, combination, 3, block])``."""
    import run_token_kat as rk

    g = dict(kt.carregar_grade())
    g["N"], g["bloco_usuarios"] = 2000, 1000
    cel = g["celulas"][0]
    out = rk._uma_tarefa((0, cel, 1, "RS", 2, g))
    fontes = kt.fontes_da_celula(cel, "RS")
    lam = {n: p["lam"] for n, p in fontes.items()}
    d = {n: p["d"] for n, p in fontes.items()}
    k = {n: p["k"] for n, p in fontes.items()}
    partes = [
        kt.simular_literal_tokens(
            "".join(fontes),
            lam,
            d,
            k,
            cel["T"],
            1000,
            np.random.default_rng([2, 0, 1, 3, b]),
            g["K"],
        )
        for b in range(2)
    ]
    s = np.concatenate([p[0] for p in partes])
    y = np.concatenate([p[1] for p in partes])
    assert out["auc"] == rd.auc_mann_whitney(s, y), (
        "runner does not use default_rng([seed, cell, combination, 3, block]) of the addendum"
    )
