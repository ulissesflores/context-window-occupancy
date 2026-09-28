"""Mutation locks, round 2 of the TDD of the displacement replication.

Inputs: ``data/prereg/01-displacement-replication.md`` (contract + operationalisation) and a
private two-reviewer report. Round 1 (``test_displacement.py``, 17 tests) let about 18 mutations
survive that changed publishable numbers or the falsification criterion without failing any test.
This file adds the locks; it does not edit ``test_displacement.py`` nor ``displacement.py``.

Each test kills one or more mutants, named by id (``X02`` ... ``X27``); the id is a label only.

Red/green classification BEFORE any mutation (run against the unmodified implementation):
  - PASS now (they lock behaviour that is already correct): every test of (a), (c), (d), (e), (f).
  - FAILED at the time, by design (they required API/contract that did not exist yet): (g) and (h);
    the implementation followed in a later step. (b) is the exception: instead of a new API it uses
    an RNG proxy that intercepts the draws of ``simular_literal`` and recomputes the reference per
    user with ``janela_ultimos``, so it passes against the correct implementation (the aggregate
    statistics are blind to the direction of the window under this generative model).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import displacement as rd

# --- construction helpers (not part of the API under test; they only build test inputs) ---------


def _cel(T, lam_a, lam_b, lam_c, d_a, d_b, d_c):
    """Build a cell dict from its seven parameters."""
    return {
        "T": T,
        "lam": {"A": lam_a, "B": lam_b, "C": lam_c},
        "d": {"A": d_a, "B": d_b, "C": d_c},
    }


def _linha(i_celula, cel, combo, semente, auc):
    """Build one result row as ``avaliar_quebra`` reads it."""
    return {
        "i_celula": i_celula,
        "T": cel["T"],
        "lam_A": cel["lam"]["A"],
        "lam_B": cel["lam"]["B"],
        "lam_C": cel["lam"]["C"],
        "d_A": cel["d"]["A"],
        "d_B": cel["d"]["B"],
        "d_C": cel["d"]["C"],
        "combo": combo,
        "semente": semente,
        "auc": auc,
    }


def _linhas_cel(i_celula, cel, overrides=None, n_sementes_default=5):
    """Build the rows of the 7 combinations of one cell.

    Combinations in ``overrides`` use the given AUC list (any length); the others repeat the
    analytic AUC ``n_sementes_default`` times (no noise between seeds), which isolates the effect
    of ONE combination or pair on the falsification criterion.
    """
    overrides = overrides or {}
    linhas = []
    for combo in rd.COMBOS:
        if combo in overrides:
            vals = overrides[combo]
        else:
            vals = [rd.auc_analitica(combo, cel["lam"], cel["d"], cel["T"])] * n_sementes_default
        for semente, v in enumerate(vals):
            linhas.append(_linha(i_celula, cel, combo, semente, v))
    return linhas


def _linhas_grid_exato():
    """Build the 720x7x5 rows of the pre-registered grid with auc = exact analytic AUC.

    Same construction as ``test_displacement.py::_linhas_grid_exato`` (duplicated on purpose: this
    file imports nothing from the other test module).
    """
    linhas = []
    for i_celula, cel in enumerate(rd.celulas()):
        for combo in rd.COMBOS:
            auc = rd.auc_analitica(combo, cel["lam"], cel["d"], cel["T"])
            for semente in range(5):
                linhas.append(_linha(i_celula, cel, combo, semente, auc))
    return linhas


def _cel_t90(lam_c):
    """Return the cell T=90, lam=(0.1, 0.3, lam_c), d=(0.5, 0.15, 0) used by several locks."""
    return {"T": 90, "lam": {"A": 0.1, "B": 0.3, "C": lam_c}, "d": {"A": 0.5, "B": 0.15, "C": 0}}


class _RNGTieProxy:
    """Wrap a real ``numpy.random.Generator``, record every draw and floor the uniform times.

    Flooring FORCES time ties inside each user, exercising the tie-break ("the event that enters
    later is more recent"), which has probability zero with continuous times. Used only to build
    the reference of test (b); not part of the production API.
    """

    def __init__(self, rng):
        """Wrap ``rng`` with an empty record of draws."""
        self._rng = rng
        self.gravado = {}

    def random(self, *a, **k):
        """Delegate ``random`` and record the draw as ``y``."""
        v = self._rng.random(*a, **k)
        self.gravado["y"] = v
        return v

    def poisson(self, *a, **k):
        """Delegate ``poisson`` and record the draw as ``contagens``."""
        v = self._rng.poisson(*a, **k)
        self.gravado["contagens"] = v
        return v

    def uniform(self, *a, **k):
        """Delegate ``uniform``, floor the times and record them as ``tempos``."""
        v = np.floor(self._rng.uniform(*a, **k))
        self.gravado["tempos"] = v
        return v

    def normal(self, *a, **k):
        """Delegate ``normal`` and record the draw as ``x``."""
        v = self._rng.normal(*a, **k)
        self.gravado["x"] = v
        return v


def _referencia_literal_por_usuario(combo, d, gravado, L):
    """Recompute the literal score user by user, calling ``janela_ultimos`` directly.

    A Python loop is acceptable in a test REFERENCE (forbidden in production). It uses the SAME
    draws that ``simular_literal`` consumed (via ``_RNGTieProxy.gravado``), so any divergence comes
    from the window selection or the score formula, never from chance.
    """
    y = gravado["y"] < rd.PI
    contagens = gravado["contagens"]
    N, k = contagens.shape
    d_combo = np.array([d[s] for s in combo])
    usuario_idx = np.repeat(np.repeat(np.arange(N)[:, None], k, axis=1).ravel(), contagens.ravel())
    fonte_idx = np.repeat(np.repeat(np.arange(k)[None, :], N, axis=0).ravel(), contagens.ravel())
    scores = np.zeros(N)
    for u in range(N):
        eventos_u = np.flatnonzero(usuario_idx == u)
        if len(eventos_u) == 0:
            continue
        visiveis = eventos_u[rd.janela_ultimos(gravado["tempos"][eventos_u], L)]
        f = fonte_idx[visiveis]
        scores[u] = np.sum(d_combo[f] * (gravado["x"][visiveis] - d_combo[f] / 2))
    return scores, y


def _momentos(scores, y, delta2):
    """Return the class sizes, means and variances with their standard errors, as a dict."""
    n_pos, n_neg = int(np.sum(y)), int(np.sum(~y))
    var_pos, var_neg = scores[y].var(ddof=1), scores[~y].var(ddof=1)
    return {
        "n_pos": n_pos,
        "n_neg": n_neg,
        "mean_pos": scores[y].mean(),
        "mean_neg": scores[~y].mean(),
        "var_pos": var_pos,
        "var_neg": var_neg,
        "se_mean_pos": math.sqrt(var_pos / n_pos),
        "se_mean_neg": math.sqrt(var_neg / n_neg),
        "se_var_pos": delta2 * math.sqrt(2 / (n_pos - 1)),
        "se_var_neg": delta2 * math.sqrt(2 / (n_neg - 1)),
    }


# === (a) centring of the log-ratio, reduction AND literal, saturated window and small L ==========


def test_a1_centragem_reducao_saturada_L_pequeno_mata_X26_e_centragem_reducao():
    """Lock the centring of the reduced score under a deterministically saturated window.

    Combo 'A' with lam_A*T = 100 >> L = 10: N_tot ~ Poisson(100) never falls below 10 (P ~ 1e-15,
    N = 200,000), so the window saturates DETERMINISTICALLY and Delta^2 = L*d_A^2 = 10 is a
    CONSTANT, which isolates the score formula from the variability of N_tot. Under the contract
    (exact reduction), score ~ Normal((y - 0.5) Delta^2, sqrt(Delta^2)): mean(y=1) = +5,
    mean(y=0) = -5, conditional variance = 10 (tolerance: 5 standard errors of the mean and 5 of the
    sample variance, sqrt(2/(n-1)) * Delta^2).

    Kills:
      - X26: reduction with min(N_tot, L-1), which gives Delta^2 = 9 (means +/-4.5), outside the
        tolerance of 5 SE around +/-5.
      - reduction without centring (mean y*Delta^2 instead of (y-0.5)*Delta^2), which gives
        mean(y=1) = +10 and mean(y=0) = 0.
    """
    lam = {"A": 100.0, "B": 0.0, "C": 0.0}
    d = {"A": 1.0, "B": 0.0, "C": 0.0}
    T, N, L = 1.0, 200_000, 10
    rng = rd.rng_para(11, 22, rd.COMBOS.index("A"))
    scores, y = rd.simular_reducao("A", lam, d, T, N, rng, L=L)

    delta2 = L * d["A"] ** 2  # = 10, constant under guaranteed saturation
    mo = _momentos(scores, y, delta2)
    assert mo["n_pos"] > 1000 and mo["n_neg"] > 1000  # makes the 5*SE tolerance meaningful

    assert abs(mo["mean_pos"] - delta2 / 2) <= 5 * mo["se_mean_pos"], mo
    assert abs(mo["mean_neg"] - (-delta2 / 2)) <= 5 * mo["se_mean_neg"], mo
    assert abs(mo["var_pos"] - delta2) <= 5 * mo["se_var_pos"], mo
    assert abs(mo["var_neg"] - delta2) <= 5 * mo["se_var_neg"], mo


def test_a2_centragem_literal_saturada_L_pequeno_mata_X25_e_X19():
    """Lock the centring of the literal score under a deterministically saturated window.

    Same logic as ``test_a1`` for ``simular_literal``: combo 'A' with lam_A*T = 50 >> L = 10
    (P(N_tot < 10) ~ 1e-9, N = 50,000: the literal simulation materialises events, so a smaller N
    for cost). Under the SAME recency rule, the number of visible events per user is EXACTLY
    L = 10, so Delta^2 = 10 is constant and the same 4 assertions of ``test_a1`` hold.

    Kills:
      - X25: literal window with L-1 events, which gives Delta^2 = 9, means +/-4.5, outside 5 SE.
      - X19: literal score d*x without the -d/2 term, which gives mean(y=1) = +10 (x ~ N(d, 1),
        d*x has mean d^2 = 1 per event * 10 events) and mean(y=0) = 0.
    """
    lam = {"A": 50.0, "B": 0.0, "C": 0.0}
    d = {"A": 1.0, "B": 0.0, "C": 0.0}
    T, N, L = 1.0, 50_000, 10
    rng = rd.rng_para(11, 22, rd.COMBOS.index("A"))
    scores, y = rd.simular_literal("A", lam, d, T, N, rng, L=L)

    delta2 = L * d["A"] ** 2  # = 10
    mo = _momentos(scores, y, delta2)
    assert mo["n_pos"] > 1000 and mo["n_neg"] > 1000

    assert abs(mo["mean_pos"] - delta2 / 2) <= 5 * mo["se_mean_pos"], mo
    assert abs(mo["mean_neg"] - (-delta2 / 2)) <= 5 * mo["se_mean_neg"], mo
    assert abs(mo["var_pos"] - delta2) <= 5 * mo["se_var_pos"], mo
    assert abs(mo["var_neg"] - delta2) <= 5 * mo["se_var_neg"], mo


# === (b) direction of the literal window ('most recent' != 'oldest') =============================


def test_b_literal_direcao_e_empate_batem_referencia_por_usuario():
    """Prove the DIRECTION of the literal window by exact equality, user by user.

    Under this generative model (i.i.d. times independent of x and y), 'keep the L most recent'
    and 'keep the L oldest' are equal IN DISTRIBUTION, so no test based on AUC, mean or variance
    sees the wrong direction (which is why KAT 4b, comparing AUCs only, let X02 survive). The
    right proof is EXACT EQUALITY against a reference that calls ``janela_ultimos`` directly
    (locked separately by KAT 4a).

    Technique: ``_RNGTieProxy`` intercepts the 4 draws of ``simular_literal`` and floors the times,
    which FORCES ties inside each user and also exercises the tie-break rule.
    ``_referencia_literal_por_usuario`` recomputes the score with the SAME draws, user by user; if
    ``simular_literal`` agrees to 1e-10 (floating-point error only), direction and tie-break are
    right. No API change was needed.

    Kills:
      - X02: ``simular_literal`` keeps the L OLDEST events (``visivel = rank_no_bloco < L``).
      - reversed time tie-break in the literal path (lexsort with ``-idx_original``): with
        deliberately tied times the order of the tie-break matters, and the reference uses the
        rule of ``janela_ultimos``.
    """
    combo, lam, d, T, L, N = (
        "ABC",
        {"A": 0.1, "B": 0.3, "C": 3},
        {"A": 0.5, "B": 0.15, "C": 0.05},
        20,
        15,
        300,
    )
    proxy = _RNGTieProxy(rd.rng_para(0, 0, 0))
    scores, y = rd.simular_literal(combo, lam, d, T, N, proxy, L=L)
    ref_scores, ref_y = _referencia_literal_por_usuario(combo, d, proxy.gravado, L)

    assert np.array_equal(y, ref_y)
    assert np.allclose(scores, ref_scores, atol=1e-10)


# === (c) order of draws and independence of the RNG streams ======================================


def test_c1_simular_reducao_sorteia_y_como_primeiro_draw_do_stream():
    """Check that ``y`` is the FIRST draw of the stream inside ``simular_reducao``.

    An independent generator with the same seed ``[s, i_celula, i_combo]`` calls
    ``.random(N) < PI`` as its first draw; the ``y`` returned by ``simular_reducao`` must be
    bit-identical.

    Kills X08: 'y drawn after the Poisson' (the stream would already have consumed the N Poisson
    numbers, so ``y`` would not match a fresh stream's first draw).
    """
    combo = "AB"
    lam = {"A": 0.2, "B": 0.5, "C": 0.0}
    d = {"A": 0.3, "B": 0.2, "C": 0.0}
    T, N = 100, 50_000
    s, i_celula, i_combo = 3, 9, rd.COMBOS.index(combo)

    rng_real = rd.rng_para(s, i_celula, i_combo)
    _, y = rd.simular_reducao(combo, lam, d, T, N, rng_real)

    rng_independente = np.random.default_rng([s, i_celula, i_combo])
    y_esperado = rng_independente.random(N) < rd.PI

    assert np.array_equal(y, y_esperado)


def test_c2_rng_para_respeita_ordem_semente_celula_combo():
    """Check that ``rng_para`` respects the order [seed, cell, combination].

    Uses 3 DISTINCT values (4, 17, 3), so that swapping positions cannot pass by accident.

    Kills X09: ``rng_para`` with the order [i_celula, semente, i_combo].
    """
    a = rd.rng_para(4, 17, 3).random(5)
    b = np.random.default_rng([4, 17, 3]).random(5)
    c = rd.rng_para(17, 4, 3).random(5)

    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_c3_streams_de_combos_diferentes_nao_colidem_tira_vacuo_do_kat2b():
    """Check that streams of different combinations do NOT give identical scores.

    KAT 2b (round 1) only checks that the AUCs of ABC (lam_C = 0) and AB AGREE within 3 SE; a
    mutant making ``rng_para`` ignore ``i_combo`` would give both simulations the SAME stream and
    identical y/scores, and the statistical test would pass by identity, not by agreement. This
    test checks the INEQUALITY on the real output of ``simular_reducao``.

    Kills the mutant ``rng_para`` ignoring ``i_combo``.
    """
    lam = {"A": 0.15, "B": 0.4, "C": 0.0}
    d = {"A": 0.4, "B": 0.2, "C": 0.0}
    T, N, semente, i_celula = 200, 20_000, 2, 777

    rng_abc = rd.rng_para(semente, i_celula, rd.COMBOS.index("ABC"))
    scores_abc, y_abc = rd.simular_reducao("ABC", lam, d, T, N, rng_abc)

    rng_ab = rd.rng_para(semente, i_celula, rd.COMBOS.index("AB"))
    scores_ab, y_ab = rd.simular_reducao("AB", lam, d, T, N, rng_ab)

    assert not np.array_equal(y_abc, y_ab)
    assert not np.array_equal(scores_abc, scores_ab)


# === (d) Q2 constants, boundaries built by hand ==================================================


def test_d1_q2_piso_0005_contagem_exata_no_grid_mata_ausencia_de_piso_e_X14():
    """Lock the 0.005 floor of Q2 (and its presence) by an exact count on the exact grid.

    On the EXACT grid (zero noise between seeds, so below/tested depends only on |prev| against the
    floor; 3 SE = 0 never yields a tie), ``abaixo_limiar`` must equal EXACTLY the count, computed
    here, of pairs with |prev| < 0.005. The grid must also have pairs in the band [0.005; 0.01),
    otherwise a wrong floor of 0.01 would be indistinguishable.

    Kills:
      - Q2 without a floor (``abs(prev) < 0.0`` is never true): ``abaixo_limiar`` would drop to 0.
      - X14: floor at 0.01, which would also count the band [0.005; 0.01).
    """
    linhas = _linhas_grid_exato()
    pares_q2 = (("A", "AC"), ("B", "BC"), ("AB", "ABC"))

    esperado_abaixo = 0
    n_na_banda_0005_001 = 0
    for cel in rd.celulas():
        for sem_combo, com_combo in pares_q2:
            prev = rd.auc_analitica(com_combo, cel["lam"], cel["d"], cel["T"]) - rd.auc_analitica(
                sem_combo, cel["lam"], cel["d"], cel["T"]
            )
            ap = abs(prev)
            if ap < 0.005:
                esperado_abaixo += 1
            elif ap < 0.01:
                n_na_banda_0005_001 += 1

    assert n_na_banda_0005_001 > 0  # 0.005 and 0.01 are distinguishable on this grid
    q2 = rd.avaliar_quebra(linhas)["Q2"]
    assert q2["abaixo_limiar"] == esperado_abaixo


def test_d2_q2_ddof1_decide_empate_na_fronteira_mata_X12():
    """Lock ddof = 1 in the Q2 standard error at the boundary where ddof decides the category.

    2 seeds in the 'with' combination (AC), 'without' (A) constant; the spread ``dx`` is chosen so
    that 3 SE(ddof=1) = 1.10 |prev| (tie) and 3 SE(ddof=0) = 0.78 |prev| (no tie).

    Kills X12: between-seed variance with ddof = 0.
    """
    cel = _cel_t90(3)
    a = {c: rd.auc_analitica(c, cel["lam"], cel["d"], cel["T"]) for c in rd.COMBOS}
    prev = a["AC"] - a["A"]
    dx = abs(prev) / 3 * 2 * 1.1  # 3*SE(ddof=1)=1.10*|prev| ; 3*SE(ddof=0)=0.78*|prev|

    linhas_rigged = _linhas_cel(
        0, cel, {"A": [a["A"]] * 2, "AC": [a["AC"] - dx / 2, a["AC"] + dx / 2]}
    )
    linhas_base = _linhas_cel(0, cel, {})

    empate_rigged = rd.avaliar_quebra(linhas_rigged)["Q2"]["empate"]
    empate_base = rd.avaliar_quebra(linhas_base)["Q2"]["empate"]
    assert empate_rigged == empate_base + 1


def test_d3_q2_zona_de_empate_3se_vs_2se_mata_X13():
    """Lock the 3 SE tie zone of Q2 (against 2 SE).

    5 seeds in AC with deviations [-2,-1,0,1,2]*e around the analytic value, A constant.
    ``e = |prev| / 1.75`` puts |prev| strictly BETWEEN 2 SE (0.808 |prev|) and 3 SE (1.212 |prev|):
    under the correct rule (3 SE) the pair is a tie; under 2 SE it would be tested.

    Kills X13: tie zone of Q2 with 2 SE.
    """
    cel = _cel_t90(3)
    a = {c: rd.auc_analitica(c, cel["lam"], cel["d"], cel["T"]) for c in rd.COMBOS}
    prev = a["AC"] - a["A"]
    e = abs(prev) / 1.75
    devs = np.array([-2, -1, 0, 1, 2]) * e
    com_vals = (a["AC"] + devs).tolist()

    # check the boundary arithmetic before using it
    se_ddof1 = math.sqrt(np.var(devs, ddof=1) / 5)
    assert 2 * se_ddof1 < abs(prev) < 3 * se_ddof1

    linhas_rigged = _linhas_cel(1, cel, {"AC": com_vals})
    linhas_base = _linhas_cel(1, cel, {})

    q2_rigged = rd.avaliar_quebra(linhas_rigged)["Q2"]
    q2_base = rd.avaliar_quebra(linhas_base)["Q2"]
    assert q2_rigged["empate"] == q2_base["empate"] + 1
    assert q2_rigged["testadas"] == q2_base["testadas"] - 1


def test_d4_q2_se_divide_por_k_mata_X21():
    """Lock the division by the number of seeds k in the Q2 standard error.

    Same construction as ``test_d3`` with ``e = |prev| / 3.0``: the CORRECT 3 SE (divided by k = 5)
    stays BELOW |prev| (tested), while 3 SE WITHOUT the division would be ABOVE (tie).

    Kills X21: SE of Q2 without dividing by k.
    """
    cel = _cel_t90(3)
    a = {c: rd.auc_analitica(c, cel["lam"], cel["d"], cel["T"]) for c in rd.COMBOS}
    prev = a["AC"] - a["A"]
    e = abs(prev) / 3.0
    devs = np.array([-2, -1, 0, 1, 2]) * e
    com_vals = (a["AC"] + devs).tolist()

    var_com = np.var(devs, ddof=1)
    se_com_k = math.sqrt(var_com / 5)  # correct (k = 5 seeds)
    se_sem_k = math.sqrt(var_com)  # mutant X21
    assert abs(prev) > 3 * se_com_k
    assert abs(prev) < 3 * se_sem_k

    linhas_rigged = _linhas_cel(2, cel, {"AC": com_vals})
    linhas_base = _linhas_cel(2, cel, {})

    q2_rigged = rd.avaliar_quebra(linhas_rigged)["Q2"]
    q2_base = rd.avaliar_quebra(linhas_base)["Q2"]
    assert q2_rigged["empate"] == q2_base["empate"]  # correct: still tested, not a tie
    assert q2_rigged["testadas"] == q2_base["testadas"]


def test_d5_q2_teto_5_por_cento_estrito_mata_X15():
    """Lock the strict 5% ceiling of Q2 (against 10%).

    A DETERMINISTIC subset of real grid cells (exact grid) whose tested comparisons
    (|prev| >= 0.005) add up to EXACTLY 19; inverting the empirical sign of ONE of them gives
    1/19 = 5.26% > 5% (correct ceiling) but < 10%. A second subset with 20 tested and 1 discordant
    (= 5.0% exactly) must NOT fail, which also locks the strict '>' of the ceiling.

    Kills X15: discordance ceiling of Q2 at 10%.
    """
    pares_q2 = (("A", "AC"), ("B", "BC"), ("AB", "ABC"))
    cels = rd.celulas()

    def selecionar(alvo):
        """Pick grid cells in order until their tested comparisons add up to ``alvo``."""
        selecionadas, total = [], 0
        for i, cel in enumerate(cels):
            testada_pairs = [
                (
                    sem_c,
                    com_c,
                    rd.auc_analitica(com_c, cel["lam"], cel["d"], cel["T"])
                    - rd.auc_analitica(sem_c, cel["lam"], cel["d"], cel["T"]),
                )
                for sem_c, com_c in pares_q2
            ]
            testada_pairs = [t for t in testada_pairs if abs(t[2]) >= 0.005]
            if not testada_pairs:
                continue
            if total + len(testada_pairs) <= alvo:
                selecionadas.append((i, testada_pairs))
                total += len(testada_pairs)
            if total == alvo:
                break
        assert total == alvo, f"grid did not yield exactly {alvo} testable comparisons"
        return selecionadas

    def montar_e_inverter(selecionadas):
        """Build the rows of the selected cells and invert the sign of the first comparison."""
        linhas = []
        for i, _ in selecionadas:
            linhas += _linhas_cel(i, cels[i], {})
        i0, pares0 = selecionadas[0]
        sem_c0, com_c0, prev0 = pares0[0]
        auc_sem0 = rd.auc_analitica(sem_c0, cels[i0]["lam"], cels[i0]["d"], cels[i0]["T"])
        novo_com = auc_sem0 - prev0  # inverts the sign of the difference, same magnitude
        for row in linhas:
            if row["i_celula"] == i0 and row["combo"] == com_c0:
                row["auc"] = novo_com
        return linhas

    sel19 = selecionar(19)
    q2_19 = rd.avaliar_quebra(montar_e_inverter(sel19))["Q2"]
    assert q2_19["testadas"] == 19
    assert q2_19["discordantes"] == 1
    assert abs(q2_19["frac_discordante"] - 1 / 19) < 1e-12
    assert q2_19["falhou"]  # 5.263...% > 5%

    sel20 = selecionar(20)
    q2_20 = rd.avaliar_quebra(montar_e_inverter(sel20))["Q2"]
    assert q2_20["testadas"] == 20
    assert q2_20["discordantes"] == 1
    assert q2_20["frac_discordante"] == 0.05
    assert not q2_20["falhou"]  # exactly 5% is not '> 5%'


# === (e) Q1: strict '<', saturation at BOTH ends, exact equality =================================


def test_e1_q1_medias_iguais_conta_como_violacao_mata_X16():
    """Lock the strict '<' of Q1: equal means count as a violation.

    Two consecutive saturated cells (lam_C = 3 -> 6, d_C = 0) with the SAME mean AUC (rigged) for
    AC: no strict drop, so a violation under the correct rule; under '<=' equal means would pass.

    Kills X16: non-strict Q1 (<=).
    """
    cel_3, cel_6 = _cel_t90(3), _cel_t90(6)
    assert rd.saturada("AC", cel_3["lam"], 90) and rd.saturada("AC", cel_6["lam"], 90)

    valor_empatado = rd.auc_analitica("AC", cel_3["lam"], cel_3["d"], 90)
    linhas = _linhas_cel(500, cel_3, {"AC": [valor_empatado] * 5}) + _linhas_cel(
        501, cel_6, {"AC": [valor_empatado] * 5}
    )
    q1 = rd.avaliar_quebra(linhas)["Q1"]
    assert q1["falhou"]
    assert len(q1["violacoes"]) == 1
    assert q1["violacoes"][0]["media_1"] == q1["violacoes"][0]["media_2"]


def test_e2_q1_par_com_uma_config_nao_saturada_nao_e_testado_mata_X17():
    """Lock that a pair whose smaller lam_C does NOT saturate is not tested by Q1.

    lam_C = 1 does not saturate AC (1.1*90 = 99 < 146), lam_C = 3 does (3.1*90 = 279 >= 146). The
    pair (1->3) must stay OUT of ``pares_testados``; testing it would create a spurious violation
    (AC rises from 0.5 to a much larger real value), so the test also checks ``not falhou``.

    Kills X17: Q1 requires saturation in only one of the two configurations (OR), and the variant
    that requires saturation only at the larger lam_C (same observable effect).
    """
    cel_1, cel_3 = _cel_t90(1), _cel_t90(3)
    assert not rd.saturada("AC", cel_1["lam"], 90)
    assert rd.saturada("AC", cel_3["lam"], 90)

    linhas = _linhas_cel(600, cel_1, {"AC": [0.5] * 5}) + _linhas_cel(601, cel_3, {})
    q1 = rd.avaliar_quebra(linhas)["Q1"]
    assert not q1["falhou"], q1["violacoes"]
    assert q1["pares_testados"] == 0


def test_e3_saturada_com_igualdade_exata_e_true_mata_X24():
    """Lock that ``saturada()`` with exact equality sum(lam)*T == L is True.

    Exact integers (lam_A = 2, T = 73, sum = 146 = L) avoid any floating-point rounding.

    Kills X24: ``saturada`` with a strict '>' (which would exclude the equality).
    """
    assert 2.0 * 73.0 == rd.L_JANELA
    assert rd.saturada("A", {"A": 2.0, "B": 0.0, "C": 0.0}, 73.0) is True


def test_e4_q1_pares_testados_contagem_exata_mata_X17_por_numero():
    """Lock the exact count of pairs tested by Q1 on the slice of the operationalisation.

    Slice T = 90, lam_A = 0.1, lam_B = 0.3, d_C = 0, lam_C in {1, 3, 6}: AC/BC/ABC only saturate
    from lam_C = 3 (99 < 146 at lam_C = 1; 279 and more at lam_C >= 3), so (1->3) is never tested
    and (3->6) always is: ``pares_testados == 3`` (one per combination). Under X17 the pair (1->3)
    would ALSO be tested, doubling it to 6; an exact count is more decisive than 'did not fail'.

    Kills X17 by the exact number (3, not 6).
    """
    cel_1, cel_3, cel_6 = _cel_t90(1), _cel_t90(3), _cel_t90(6)
    for combo in ("AC", "BC", "ABC"):
        assert not rd.saturada(combo, cel_1["lam"], 90)
        assert rd.saturada(combo, cel_3["lam"], 90) and rd.saturada(combo, cel_6["lam"], 90)

    linhas = _linhas_cel(700, cel_1, {}) + _linhas_cel(701, cel_3, {}) + _linhas_cel(702, cel_6, {})
    q1 = rd.avaliar_quebra(linhas)["Q1"]
    assert q1["pares_testados"] == 3
    assert not q1["falhou"]


# === (f) Q3: agreement by the SIGN PATTERN, not by the full order ================================


def test_f1_q3_concordancia_usa_padrao_de_sinais_nao_ordem_completa_mata_X22():
    """Lock that Q3 agreement compares the sign pattern, not the full order.

    The example cell of the pre-registration (T = 90, lam = (0.1; 0.3; 3), d = (0.5; 0.15; 0)): its
    ANALYTIC AUC satisfies both ``padrao_p3`` and ``ordem_completa``. An EMPIRICAL AUC that swaps
    the values of AC and ABC keeps the 6 signs of ``padrao_p3`` (none compares AC with ABC) but
    changes the full order: a case where the two criteria DIVERGE.

    Under the correct implementation (``padrao_p3(empirico) == padrao_p3(analitico)``) the
    agreement is 1. Kills X22: Q3 agreement computed by the full order (False against True).
    """
    lam = {"A": 0.1, "B": 0.3, "C": 3}
    d = {"A": 0.5, "B": 0.15, "C": 0}
    T = 90
    analitico = {c: rd.auc_analitica(c, lam, d, T) for c in rd.COMBOS}
    assert rd.padrao_p3(analitico) and rd.ordem_completa(analitico)  # precondition (test 2)

    empirico = dict(analitico)
    empirico["AC"], empirico["ABC"] = analitico["ABC"], analitico["AC"]  # swap AC <-> ABC
    assert rd.padrao_p3(empirico)  # the 6 signs survive the swap
    assert not rd.ordem_completa(empirico)  # but the full order does not

    cel = {"T": T, "lam": lam, "d": d}
    linhas = _linhas_cel(800, cel, {combo: [v, v] for combo, v in empirico.items()})
    q3 = rd.avaliar_quebra(linhas)["Q3"]
    assert q3["celulas_padrao"] == 1
    assert q3["celulas_ordem"] == 0
    assert q3["concordancia_padrao_com_analitico"] == 1


# === (g) shortfall ratio promised by the pre-registration ========================================


def test_g_resumo_shortfall_por_celula_e_padrao_t4():
    """Specify ``resumo_shortfall``: the shortfall ratio per cell and the T4 pattern count.

    Contract (written before the function existed):

        rd.resumo_shortfall(linhas) -> dict with
          - "shortfall_por_celula": {i_celula: {combo: ratio}} for the 6 combinations != 'ABC',
            ratio = (1 - mean_auc_combo) / (1 - mean_auc_ABC), where the mean over SEEDS comes
            first and the ratio is taken on the means (not the mean of per-seed ratios);
          - "shortfall_padrao_T4": integer count of cells in which, on the mean AUCs, the 3
            additions of C INCREASE the shortfall (AC<A, BC<B, ABC<AB) AND the 2 additions of B
            REDUCE it (AB>A, BC>C): ``padrao_p3`` WITHOUT the extra condition 'C < min(A, B)'.

        ``run_replication.main()`` copies both keys into ``resumo.json``.

    Small case (2 cells x 7 combinations x 2 identical seeds): cell 0 satisfies the full T4
    pattern; cell 1 is equal except AC > A, so ``shortfall_padrao_T4 == 1``.
    """
    cel = _cel_t90(3)
    valores = {"A": 0.80, "B": 0.70, "C": 0.50, "AB": 0.85, "BC": 0.62, "AC": 0.75, "ABC": 0.83}
    assert (
        valores["AC"] < valores["A"]
        and valores["BC"] < valores["B"]
        and valores["ABC"] < valores["AB"]
    )
    assert valores["AB"] > valores["A"] and valores["BC"] > valores["C"]  # cell 0: full T4

    valores_quebrados = dict(valores, AC=0.90)  # cell 1: breaks only AC<A (0.90 > 0.80)
    assert valores_quebrados["AC"] > valores_quebrados["A"]

    linhas = _linhas_cel(0, cel, {c: [v, v] for c, v in valores.items()}) + _linhas_cel(
        1, cel, {c: [v, v] for c, v in valores_quebrados.items()}
    )

    resumo = rd.resumo_shortfall(linhas)

    esperado_cel0 = {c: (1 - valores[c]) / (1 - valores["ABC"]) for c in rd.COMBOS if c != "ABC"}
    esperado_cel1 = {
        c: (1 - valores_quebrados[c]) / (1 - valores_quebrados["ABC"])
        for c in rd.COMBOS
        if c != "ABC"
    }

    assert resumo["shortfall_por_celula"][0] == pytest.approx(esperado_cel0)
    assert resumo["shortfall_por_celula"][1] == pytest.approx(esperado_cel1)
    assert resumo["shortfall_padrao_T4"] == 1


# === (h) avaliar_quebra with a missing combination or a lam_C subset =============================


def test_h_avaliar_quebra_combo_ausente_ou_lam_c_subconjunto_leva_a_valueerror():
    """Specify that incomplete data raises ``ValueError``, never a silent NaN.

    Before the fix, removing AC from the cell of the tested pair (3->6) produced ``media_1 = nan``
    with no error, and lam_C in {1, 6} only (the middle 3 missing) counted the non-consecutive
    pair (1->6) as consecutive. Contract: ``avaliar_quebra`` raises an explicit ``ValueError`` when
    (i) any of the 7 combinations is missing for a cell present in the rows, OR (ii) a d_C = 0
    cell appears with a subset of {1, 3, 6} for lam_C inside a group (T, lam_A, lam_B, d_A, d_B):
    the operationalised Q1 needs the full triad so that (1->3) and (3->6) are well defined.
    """
    # (i) missing combination: cells 20 (lam_C=3) and 40 (lam_C=6) of the real grid form the
    # tested pair (3->6); AC is removed from cell 20 only.
    cels = rd.celulas()
    i_20, i_40 = 20, 40
    assert cels[i_20]["lam"]["C"] == 3 and cels[i_40]["lam"]["C"] == 6 and cels[i_20]["d"]["C"] == 0
    linhas_combo_ausente = [
        row
        for row in (_linhas_cel(i_20, cels[i_20], {}) + _linhas_cel(i_40, cels[i_40], {}))
        if not (row["i_celula"] == i_20 and row["combo"] == "AC")
    ]
    with pytest.raises(ValueError):
        rd.avaliar_quebra(linhas_combo_ausente)

    # (ii) lam_C subset: {1, 6} only, the middle 3 missing.
    def base(lam_c):
        """Return the cell T=365, lam=(0.2, 0.3, lam_c), d=(0.5, 0.15, 0)."""
        return {
            "T": 365.0,
            "lam": {"A": 0.2, "B": 0.3, "C": lam_c},
            "d": {"A": 0.5, "B": 0.15, "C": 0.0},
        }

    cel_1, cel_6 = base(1.0), base(6.0)
    linhas_subset = _linhas_cel(900, cel_1, {}) + _linhas_cel(901, cel_6, {})
    with pytest.raises(ValueError):
        rd.avaliar_quebra(linhas_subset)
