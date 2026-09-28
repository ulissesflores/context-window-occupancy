"""Complementary token-KAT tests, written AFTER the run (private adversarial verification).

``test_token_kat.py`` was frozen with the run and is not edited; this file adds locks that do not
change the sealed verdict: they pin the estimator and the pre-registered constants of the evaluator
(mean, ddof = 1, 3 SE, tolerance per combination, level in both combinations) and boundary cases
of the vectorised path.
"""

import numpy as np
import pytest

import run_token_kat as rk
import token_kat as kt
from test_token_kat import _referencia_por_usuario


def _linhas(g, ruido=None):
    """Build rows with AUC = exact closed form; ``ruido[(cell, combo)]`` = 5 per-seed offsets."""
    linhas = []
    for cel in g["celulas"]:
        for combo in ("R", "RS"):
            a = kt.auc_fluida(kt.fontes_da_celula(cel, combo), cel["T"], g["K"])
            extra = (ruido or {}).get((cel["id"], combo), [0.0] * 5)
            for i, s in enumerate(g["sementes"]):
                linhas.append(
                    {"celula": cel["id"], "combo": combo, "semente": s, "auc": a + extra[i]}
                )
    return linhas


def _tol(g, valor):
    """Return the same tolerance for every (cell, combination)."""
    return {(c["id"], combo): valor for c in g["celulas"] for combo in ("R", "RS")}


def _prev(g, cid):
    """Return the predicted dAUC (fluid closed form) of cell ``cid``."""
    cel = next(c for c in g["celulas"] if c["id"] == cid)
    return kt.auc_fluida(kt.fontes_da_celula(cel, "RS"), cel["T"], g["K"]) - kt.auc_fluida(
        kt.fontes_da_celula(cel, "R"), cel["T"], g["K"]
    )


# --- evaluator: pre-registered constants and estimator -------------------------------------------


def test_limiar_de_empate_e_3_ep():
    """Check |predicted| = 2.5 SE: a tie under 3 SE (pre-registered), not under 2 SE."""
    g = kt.carregar_grade()
    prev = abs(_prev(g, "S1a"))
    a = prev / (2.5 * np.sqrt(0.5))  # noise a*(s-2) only in R ∪ S => SE = a * sqrt(0.5)
    r = kt.avaliar_kat(
        _linhas(g, {("S1a", "RS"): [a * (s - 2) for s in range(5)]}), g, _tol(g, 1.0)
    )
    assert r["KT_S"]["empates"] == 1, "tie threshold is not 3 SE (pre-registered)"


def test_variancia_entre_sementes_com_ddof_1():
    """Check noise [0,0,0,0,b], b = |predicted|/0.57: a tie with ddof = 1, not with ddof = 0."""
    g = kt.carregar_grade()
    b = abs(_prev(g, "S1a")) / 0.57
    r = kt.avaliar_kat(_linhas(g, {("S1a", "RS"): [0, 0, 0, 0, b]}), g, _tol(g, 1.0))
    assert r["KT_S"]["empates"] == 1, "SE does not use the between-seed variance with ddof = 1"


def test_nivel_usa_a_media_das_sementes():
    """Check noise [0; 0; 0; 0; 0.1] in N1/R: the mean moves 0.02 (> 0.0137), the median 0."""
    g = kt.carregar_grade()
    r = kt.avaliar_kat(_linhas(g, {("N1", "R"): [0, 0, 0, 0, 0.1]}), g, _tol(g, 0.0137))
    assert r["KT_N"]["estouros"] == 1, "level does not use the MEAN of the seeds"


def test_nivel_confere_o_combo_r_uniao_s():
    """Check that a level exceedance in R ∪ S fails KT-N."""
    g = kt.carregar_grade()
    r = kt.avaliar_kat(_linhas(g, {("N1", "RS"): [0.02] * 5}), g, _tol(g, 0.0137))
    assert r["KT_N"]["estouros"] == 1 and not r["KT_N"]["passou"], "exceedance in R ∪ S not failed"


# --- runner: tolerance per combination ------------------------------------------------------------


def test_tolerancias_por_combo_vem_da_tabela_congelada():
    """Check that the runner takes each tolerance from the frozen table with its own sources."""
    g = kt.carregar_grade()
    tab = rk._tabela_analitica()
    tol = rk.tolerancias(g)
    distintas = 0
    for cel in g["celulas"]:
        for combo in ("R", "RS"):
            fs = [dict(nome=n, **p) for n, p in kt.fontes_da_celula(cel, combo).items()]
            assert tol[(cel["id"], combo)] == tab.tolerancia(fs, cel["T"], g), (
                f"tolerance of {cel['id']}/{combo} does not use the sources of its own combination"
            )
        distintas += tol[(cel["id"], "R")] != tol[(cel["id"], "RS")]
    assert distintas >= 4, "the test needs cells whose tolerance differs between R and R ∪ S"


# --- vectorised path: boundaries ------------------------------------------------------------------


def test_saturacao_e_custo_estritamente_maior_que_K():
    """Check k = 1024, K = 2048: a user with exactly 2 events costs K and is NOT saturated."""
    N, lam, T = 4000, 2.0, 1
    _, _, diag = kt.simular_literal_tokens(
        "A", {"A": lam}, {"A": 0.1}, {"A": 1024}, T, N, np.random.default_rng(5), K=2048
    )
    rng = np.random.default_rng(5)
    rng.random(N)
    cont = rng.poisson(np.array([[lam * T]]), size=(N, 1))[:, 0]
    assert (cont == 2).sum() > 500, "the test needs users whose cost is exactly K"
    assert diag["n_saturados"] == int((cont * 1024 > 2048).sum()), "saturated must be cost > K"


class _RngTemposInteiros:
    """Delegate to the real generator, but floor the times: forces time ties inside a user."""

    def __init__(self, semente):
        """Create the real generator from ``semente``."""
        self._g = np.random.default_rng(semente)

    def uniform(self, *a, **kw):
        """Delegate ``uniform`` and floor the result."""
        return np.floor(self._g.uniform(*a, **kw))

    def __getattr__(self, nome):
        """Delegate every other attribute to the real generator."""
        return getattr(self._g, nome)


def test_desempate_fim_a_fim_com_tempos_empatados():
    """Check end to end, with tied times, that the vectorised path breaks ties by input order."""
    lam, d, k = (
        {"A": 0.3, "B": 0.4, "C": 1.0},
        {"A": 0.4, "B": 0.2, "C": 0.1},
        {"A": 14, "B": 70, "C": 28},
    )
    s_v, _, _ = kt.simular_literal_tokens("ABC", lam, d, k, 30, 300, _RngTemposInteiros(13), K=280)
    s_r, _, _ = _referencia_por_usuario("ABC", lam, d, k, 30, 300, _RngTemposInteiros(13), K=280)
    assert np.allclose(s_v, s_r, rtol=0, atol=1e-12), (
        "with tied times the vectorised path does not break ties by input order like janela_tokens"
    )


def test_custo_nao_positivo_e_valueerror():
    """Check that a non-positive cost per event raises ``ValueError``."""
    with pytest.raises(ValueError):
        kt.simular_literal_tokens(
            "A", {"A": 1.0}, {"A": 0.1}, {"A": 0}, 10, 10, np.random.default_rng(0), K=100
        )
