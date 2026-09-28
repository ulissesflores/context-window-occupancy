"""TDD round 1 of the synthetic displacement replication.

Specification: ``data/prereg/01-displacement-replication.md`` (KATs 1-4, falsification criterion
Q1/Q2/Q3, operationalisation of 2026-09-24). These tests were written before the implementation
(``code/displacement.py``) existed.

Note on item KAT 2(c) of the contract (deliberately OMITTED, not forgotten): with Poisson counts,
Delta^2 is a random variable per user (a function of the multinomial draw), and positives and
negatives draw Delta^2 independently; the pooled AUC is the expectation over the independent pair
(Delta^2_+, Delta^2_-) of the effective Phi per pair, not Phi(sqrt(E[Delta^2]) / sqrt(2)). Since
Phi(sqrt(x) / sqrt(2)) is not linear in x, by Jensen that mean departs systematically from
"plugging the expected Delta^2 into the formula", with no guarantee of fitting in 3 SE. Writing
that test would lock a number the mathematics of the model does not promise. Tests 6a/6b below
cover what the reduction DOES guarantee (L=None equals a very large L; equivalent combinations on
independent streams agree), without that third leg.
"""

import copy
import itertools
import math

import numpy as np
from scipy.stats import norm

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


def _linhas_grid_exato():
    """Build the 720x7x5 rows of the pre-registered grid with auc = exact analytic AUC."""
    linhas = []
    for i_celula, cel in enumerate(rd.celulas()):
        for combo in rd.COMBOS:
            auc = rd.auc_analitica(combo, cel["lam"], cel["d"], cel["T"])
            for semente in range(5):
                linhas.append(_linha(i_celula, cel, combo, semente, auc))
    return linhas


def _se_diff(se1, se2):
    """Return the standard error of a difference of two independent estimates."""
    return math.sqrt(se1**2 + se2**2)


# --- 1. celulas() -------------------------------------------------------------------------------


def test_celulas_720_e_extremos_conforme_o_contrato():
    """Check the full grid: 720 cells in itertools.product order, first and last as contracted."""
    cels = rd.celulas()
    assert len(cels) == 720
    assert cels[0] == _cel(90, 0.1, 0.3, 1, 0.3, 0.15, 0)
    # last tuple of the product: the last index of every axis of the grid
    assert cels[-1] == _cel(365, 0.2, 0.6, 6, 0.5, 0.25, 0.2)


# --- 2. regiao_p3_analitica + example cell of the contract -------------------------------------


def test_regiao_p3_analitica_e_auc_da_celula_exemplo():
    """Check the pre-computed P3 region and the analytic AUC of the example cell to 4 decimals."""
    assert rd.regiao_p3_analitica() == (720, 407, 50)

    lam = {"A": 0.1, "B": 0.3, "C": 3}
    d = {"A": 0.5, "B": 0.15, "C": 0}
    T = 90
    esperado = {
        "A": 0.8556,
        "B": 0.7092,
        "C": 0.5,
        "AB": 0.884,
        "BC": 0.6504,
        "AC": 0.7785,
        "ABC": 0.7955,
    }
    for combo, auc_esperado in esperado.items():
        auc = rd.auc_analitica(combo, lam, d, T)
        assert round(auc, 4) == auc_esperado, combo

    # the example cell itself satisfies the sign pattern AND the full order of P3 (direct coverage
    # of padrao_p3/ordem_completa, which would otherwise only show through the counts 407/50)
    empirico = {c: rd.auc_analitica(c, lam, d, T) for c in rd.COMBOS}
    assert rd.padrao_p3(empirico)
    assert rd.ordem_completa(empirico)


# --- 3. analytic properties P1 / P1b / P2 -------------------------------------------------------


def test_propriedade_p1_p1b_regime_saturado_sinal_independe_de_lam_s():
    """Check P1 and P1b: in the saturated regime the sign of adding S does not depend on lam_S.

    P1: the sign of AUC(with S) - AUC(without S) equals the sign of d_S^2 minus the rate-weighted
    mean of d^2 of the current mixture. P1b: that sign does NOT depend on lam_S (only the magnitude
    and the onset do).
    """
    lam_a, d_a, T = 1.0, 0.1, 365.0  # combo "A" already saturates alone: 1.0*365=365 >= 146
    limiar = d_a**2  # weighted mean of the mixture "A" alone = d_a^2 (a single term)
    auc_sem = rd.auc_analitica(
        "A", {"A": lam_a, "B": 0.0, "C": 0.0}, {"A": d_a, "B": 0.0, "C": 0.0}, T
    )

    for lam_s in (0.5, 2.0, 5.0, 10.0):
        lam = {"A": lam_a, "B": lam_s, "C": 0.0}
        assert rd.saturada("A", lam, T) and rd.saturada("AB", lam, T)

        d_abaixo = {"A": d_a, "B": 0.05, "C": 0.0}  # 0.05^2 = 0.0025 < threshold (0.01)
        assert d_abaixo["B"] ** 2 < limiar
        auc_com_abaixo = rd.auc_analitica("AB", lam, d_abaixo, T)
        assert auc_com_abaixo < auc_sem, f"lam_s={lam_s}"

        d_acima = {"A": d_a, "B": 0.2, "C": 0.0}  # 0.2^2 = 0.04 > threshold
        assert d_acima["B"] ** 2 > limiar
        auc_com_acima = rd.auc_analitica("AB", lam, d_acima, T)
        assert auc_com_acima > auc_sem, f"lam_s={lam_s}"


def test_propriedade_p2_regime_nao_saturado_fonte_nova_nunca_piora():
    """Check P2: if the window stays unsaturated with the new source, adding d_S > 0 never hurts."""
    lam_a, d_a, T = 0.05, 0.2, 50.0  # (0.05+0.1)*50 = 7.5 << 146: never saturates below
    auc_sem = rd.auc_analitica(
        "A", {"A": lam_a, "B": 0.0, "C": 0.0}, {"A": d_a, "B": 0.0, "C": 0.0}, T
    )

    for lam_s, d_s in ((0.01, 0.05), (0.05, 0.3), (0.1, 0.9)):
        lam = {"A": lam_a, "B": lam_s, "C": 0.0}
        assert not rd.saturada("AB", lam, T)
        d = {"A": d_a, "B": d_s, "C": 0.0}
        auc_com = rd.auc_analitica("AB", lam, d, T)
        assert auc_com > auc_sem, f"lam_s={lam_s} d_s={d_s}"


# --- 4. auc_mann_whitney + se_hanley_mcneil -----------------------------------------------------


def test_auc_mann_whitney_casos_a_mao():
    """Check the Mann-Whitney AUC on hand-worked cases.

    Perfect separation = 1.0; inverted = 0.0; all tied = 0.5; small case with a tie = 0.875
    (mid-ranks [1, 2.5, 2.5, 4]; R_pos = 6.5; AUC = (6.5 - 3) / 4 = 0.875, checked by hand).
    """
    y = np.array([0, 1, 1, 0])
    scores_perfeita = np.array([0.0, 1.0, 2.0, -1.0])  # y=1 always above y=0
    assert rd.auc_mann_whitney(scores_perfeita, y) == 1.0

    scores_invertida = np.array([0.0, -1.0, -2.0, 1.0])  # y=1 always below y=0
    assert rd.auc_mann_whitney(scores_invertida, y) == 0.0

    scores_empate = np.array([5.0, 5.0, 5.0, 5.0])
    assert rd.auc_mann_whitney(scores_empate, y) == 0.5

    scores_pequeno = np.array([1.0, 2.0, 2.0, 3.0])
    y_pequeno = np.array([0, 1, 0, 1])
    assert math.isclose(rd.auc_mann_whitney(scores_pequeno, y_pequeno), 0.875)


def test_se_hanley_mcneil_valor_a_mao():
    """Check A=0.8, n_pos=10, n_neg=20: se = 0.093571125650788 (Hanley & McNeil, by hand)."""
    se = rd.se_hanley_mcneil(0.8, 10, 20)
    assert abs(se - 0.093571125650788) < 1e-9


# --- 5. KAT 1: closed form with fixed counts ----------------------------------------------------


def test_kat1_forma_fechada_contagens_fixas():
    """Check KAT 1: with fixed counts the empirical oracle AUC is within 3 SE of the closed form.

    Three signal magnitudes (~0.65 / ~0.80 / ~0.95), N = 200,000.
    """
    N = 200_000
    configs = [
        {"A": 30, "B": 0, "C": 0},
        {"A": 35, "B": 0, "C": 0},
        {"A": 60, "B": 0, "C": 0},
    ]
    ds = [
        {"A": 0.1, "B": 0.0, "C": 0.0},
        {"A": 0.2, "B": 0.0, "C": 0.0},
        {"A": 0.3, "B": 0.0, "C": 0.0},
    ]
    for semente, (n, d) in enumerate(zip(configs, ds, strict=True)):
        rng = rd.rng_para(semente, 0, 0)
        scores, y = rd.escores_contagens_fixas(n, d, N, rng)
        delta2 = sum(n[s] * d[s] ** 2 for s in n)
        teorica = norm.cdf(math.sqrt(delta2) / math.sqrt(2))
        auc_emp = rd.auc_mann_whitney(scores, y)
        n_pos = int(np.sum(y))
        n_neg = N - n_pos
        se = rd.se_hanley_mcneil(auc_emp, n_pos, n_neg)
        assert abs(auc_emp - teorica) <= 3 * se, (
            f"config {n} {d}: emp={auc_emp} teorica={teorica} se={se}"
        )


# --- 6. KAT 2: exact reduction ------------------------------------------------------------------


def test_kat2a_L_none_e_L_muito_grande_dao_scores_identicos():
    """Check KAT 2: L=None and L=10**9 never truncate, so the scores are bit-identical."""
    combo = "AB"
    lam = {"A": 0.1, "B": 0.2, "C": 0.05}
    d = {"A": 0.3, "B": 0.2, "C": 0.1}
    T, N = 250, 200_000

    rng1 = rd.rng_para(1, 42, rd.COMBOS.index(combo))
    scores1, y1 = rd.simular_reducao(combo, lam, d, T, N, rng1, L=None)

    rng2 = rd.rng_para(1, 42, rd.COMBOS.index(combo))
    scores2, y2 = rd.simular_reducao(combo, lam, d, T, N, rng2, L=10**9)

    assert np.array_equal(y1, y2)
    assert np.array_equal(scores1, scores2)


def test_kat2b_combos_equivalentes_por_streams_independentes_concordam():
    """Check that ABC with lam_C=0 and AB agree within 3 SE on independent streams.

    Poisson(0) never generates an event, so ABC with lam_C = 0 is statistically AB, but it uses
    a DIFFERENT random stream (distinct i_combo); both empirical AUCs must agree within
    3 * sqrt(se1^2 + se2^2).
    """
    lam = {"A": 0.15, "B": 0.4, "C": 0.0}
    d = {"A": 0.4, "B": 0.2, "C": 0.0}
    T, N, semente, i_celula = 200, 200_000, 2, 777

    rng_abc = rd.rng_para(semente, i_celula, rd.COMBOS.index("ABC"))
    scores_abc, y_abc = rd.simular_reducao("ABC", lam, d, T, N, rng_abc)
    auc_abc = rd.auc_mann_whitney(scores_abc, y_abc)
    n_pos_abc = int(np.sum(y_abc))
    se_abc = rd.se_hanley_mcneil(auc_abc, n_pos_abc, N - n_pos_abc)

    rng_ab = rd.rng_para(semente, i_celula, rd.COMBOS.index("AB"))
    scores_ab, y_ab = rd.simular_reducao("AB", lam, d, T, N, rng_ab)
    auc_ab = rd.auc_mann_whitney(scores_ab, y_ab)
    n_pos_ab = int(np.sum(y_ab))
    se_ab = rd.se_hanley_mcneil(auc_ab, n_pos_ab, N - n_pos_ab)

    assert abs(auc_abc - auc_ab) <= 3 * _se_diff(se_abc, se_ab)


# --- 7. KAT 3: pure noise does not help ---------------------------------------------------------


def test_kat3_ruido_puro_nao_ajuda_em_todas_as_sementes():
    """Check KAT 3: with d_C = 0 and a saturated window, AUC(with C) < AUC(without C) always.

    lam = (0.2, 0.6, 6), T = 365, d_A = 0.5, d_B = 0.25: saturated for A->AC, B->BC, AB->ABC, in
    all 5 seeds (large effect, no tolerance).
    """
    lam = {"A": 0.2, "B": 0.6, "C": 6.0}
    d = {"A": 0.5, "B": 0.25, "C": 0.0}
    T, N, i_celula = 365, 200_000, 8001

    pares = [("A", "AC"), ("B", "BC"), ("AB", "ABC")]
    for sem_combo, com_combo in pares:
        assert rd.saturada(com_combo, lam, T)
        for semente in range(5):
            rng_sem = rd.rng_para(semente, i_celula, rd.COMBOS.index(sem_combo))
            scores_sem, y_sem = rd.simular_reducao(sem_combo, lam, d, T, N, rng_sem)
            auc_sem = rd.auc_mann_whitney(scores_sem, y_sem)

            rng_com = rd.rng_para(semente, i_celula, rd.COMBOS.index(com_combo))
            scores_com, y_com = rd.simular_reducao(com_combo, lam, d, T, N, rng_com)
            auc_com = rd.auc_mann_whitney(scores_com, y_com)

            assert auc_com < auc_sem, f"{sem_combo}->{com_combo} semente={semente}"


# --- 8. KAT 4a: janela_ultimos by hand ----------------------------------------------------------


def test_kat4a_janela_ultimos_casos_a_mao():
    """Check that the window keeps exactly the L most recent events, ties broken by input order.

    The event that comes later is more recent; len <= L returns everything, in increasing order of
    recency.
    """
    # no tie: the last 3 of [1,2,3,4,5] are indices 2,3,4 (times 3,4,5)
    idx = rd.janela_ultimos(np.array([1, 2, 3, 4, 5]), 3)
    assert np.array_equal(idx, np.array([2, 3, 4]))

    # tie: times [5,3,3,1] -> increasing recency = [3 (t1), 1 (t3, older of the tie),
    # 2 (t3, newer of the tie), 0 (t5)]; L=2 most recent = [2, 0]
    idx = rd.janela_ultimos(np.array([5, 3, 3, 1]), 2)
    assert np.array_equal(idx, np.array([2, 0]))

    # len <= L: everything, in increasing order of recency
    idx = rd.janela_ultimos(np.array([1, 2]), 5)
    assert np.array_equal(idx, np.array([0, 1]))


# --- 9. KAT 4b: literal vs reduction ------------------------------------------------------------


def test_kat4b_literal_e_reducao_concordam_nas_seis_celulas_da_operacionalizacao():
    """Check KAT 4b: literal and reduced AUCs agree within 3 SE in the 6 cells of KAT 4.

    T=90, lam_A=0.1, lam_B=0.3, lam_C in {1,3}, d_A=0.5, d_B=0.15, d_C in {0,0.05,0.2}, combo ABC,
    N=50,000, independent streams (i_combo 100 vs 200).
    """
    T, lam_a, d_a, lam_b, d_b, N = 90, 0.1, 0.5, 0.3, 0.15, 50_000
    combo = "ABC"

    for idx, (lam_c, d_c) in enumerate(itertools.product((1, 3), (0, 0.05, 0.2))):
        i_celula = 9100 + idx
        lam = {"A": lam_a, "B": lam_b, "C": lam_c}
        d = {"A": d_a, "B": d_b, "C": d_c}

        rng_lit = rd.rng_para(0, i_celula, 100)
        scores_lit, y_lit = rd.simular_literal(combo, lam, d, T, N, rng_lit)
        auc_lit = rd.auc_mann_whitney(scores_lit, y_lit)
        n_pos_lit = int(np.sum(y_lit))
        se_lit = rd.se_hanley_mcneil(auc_lit, n_pos_lit, N - n_pos_lit)

        rng_red = rd.rng_para(0, i_celula, 200)
        scores_red, y_red = rd.simular_reducao(combo, lam, d, T, N, rng_red)
        auc_red = rd.auc_mann_whitney(scores_red, y_red)
        n_pos_red = int(np.sum(y_red))
        se_red = rd.se_hanley_mcneil(auc_red, n_pos_red, N - n_pos_red)

        assert abs(auc_lit - auc_red) <= 3 * _se_diff(se_lit, se_red), f"lam_C={lam_c} d_C={d_c}"


# --- 10. avaliar_quebra -------------------------------------------------------------------------


def test_avaliar_quebra_grid_exato_sem_ruido_nao_falha_q1_e_bate_q3():
    """Check the exact grid (zero noise): Q1 passes, Q2 has no discordance, Q3 gives 407/50."""
    linhas = _linhas_grid_exato()
    r = rd.avaliar_quebra(linhas)

    assert not r["Q1"]["falhou"]
    assert r["Q1"]["violacoes"] == []

    assert r["Q2"]["discordantes"] == 0

    assert r["Q3"]["celulas_padrao"] == 407
    assert r["Q3"]["celulas_ordem"] == 50
    assert not r["Q3"]["falhou"]


def test_avaliar_quebra_q2_detecta_uma_discordancia_invertida():
    """Check that inverting the empirical sign of ONE tested comparison gives discordantes == 1.

    The inverted comparison has a large |prev| and d_C != 0, so that Q1 is not affected.
    """
    linhas = _linhas_grid_exato()
    por_chave = {(row["i_celula"], row["combo"], row["semente"]): row for row in linhas}
    cels = rd.celulas()

    alvo = None
    for limiar in (0.05, 0.02, 0.01, 0.005):
        for i_celula, cel in enumerate(cels):
            if cel["d"]["C"] == 0:
                continue  # stay away from Q1 (which only looks at cells with d_C == 0)
            for base, com in (("A", "AC"), ("B", "BC"), ("AB", "ABC")):
                prev = rd.auc_analitica(com, cel["lam"], cel["d"], cel["T"]) - rd.auc_analitica(
                    base, cel["lam"], cel["d"], cel["T"]
                )
                if abs(prev) >= limiar:
                    alvo = (i_celula, base, com, prev)
                    break
            if alvo:
                break
        if alvo:
            break
    assert alvo is not None, "grid produced no testable pair to invert (unexpected)"
    i_celula, base, com, prev = alvo

    linhas_mod = copy.deepcopy(linhas)
    auc_base = rd.auc_analitica(
        base, cels[i_celula]["lam"], cels[i_celula]["d"], cels[i_celula]["T"]
    )
    novo_com = auc_base - prev  # inverts the sign of the empirical difference, same magnitude
    for semente in range(5):
        linha = por_chave[(i_celula, com, semente)]
        idx = linhas_mod.index(linha)
        linhas_mod[idx] = dict(linha, auc=novo_com)

    r = rd.avaliar_quebra(linhas_mod)
    assert r["Q2"]["discordantes"] == 1, r["Q2"]


def test_avaliar_quebra_q1_detecta_violacao_de_monotonicidade():
    """Check that Q1 fails when the AUC of AC RISES from lam_C=1 to lam_C=3 (d_C=0, saturated).

    The three cells (lam_C = 1, 3, 6) close BOTH consecutive pairs (1->3, 3->6) that the contract
    asks for; the rows are complete (7 combinations) so that the Q2 pairing does not break.
    """
    base_params = dict(T=365.0, lam_a=0.2, lam_b=0.3, d_a=0.5, d_b=0.15, d_c=0.0)
    cel1 = _cel(
        base_params["T"],
        base_params["lam_a"],
        base_params["lam_b"],
        1.0,
        base_params["d_a"],
        base_params["d_b"],
        base_params["d_c"],
    )
    cel3 = _cel(
        base_params["T"],
        base_params["lam_a"],
        base_params["lam_b"],
        3.0,
        base_params["d_a"],
        base_params["d_b"],
        base_params["d_c"],
    )
    cel6 = _cel(
        base_params["T"],
        base_params["lam_a"],
        base_params["lam_b"],
        6.0,
        base_params["d_a"],
        base_params["d_b"],
        base_params["d_c"],
    )
    for cel in (cel1, cel3, cel6):
        assert rd.saturada("AC", cel["lam"], cel["T"])

    linhas = []
    for i_celula, cel in ((9001, cel1), (9002, cel3), (9003, cel6)):
        for combo in rd.COMBOS:
            if combo == "AC":
                continue  # rigged below
            auc = rd.auc_analitica(combo, cel["lam"], cel["d"], cel["T"])
            for semente in range(5):
                linhas.append(_linha(i_celula, cel, combo, semente, auc))
    # rigging: AC rises from 0.5 (lam_C=1) to 0.9 (lam_C=3), violating the required drop in (1->3);
    # the pair (3->6) uses the correct analytic value (a drop), so the violation stays in (1->3)
    auc_ac_6 = rd.auc_analitica("AC", cel6["lam"], cel6["d"], cel6["T"])
    for semente in range(5):
        linhas.append(_linha(9001, cel1, "AC", semente, 0.5))
        linhas.append(_linha(9002, cel3, "AC", semente, 0.9))
        linhas.append(_linha(9003, cel6, "AC", semente, auc_ac_6))

    r = rd.avaliar_quebra(linhas)
    assert r["Q1"]["falhou"]


def test_avaliar_quebra_contagem_de_comparacoes_q2():
    """Check 720 cells x 3 pairs = 2,160 comparisons, each in exactly one category."""
    linhas = _linhas_grid_exato()
    r = rd.avaliar_quebra(linhas)
    q2 = r["Q2"]
    assert q2["comparacoes"] == 2160
    assert q2["abaixo_limiar"] + q2["empate"] + q2["testadas"] == q2["comparacoes"]


# --- 11. rodar_grade: determinism independent of parallelism -----------------------------------


def test_rodar_grade_determinismo_e_chaves_da_linha():
    """Check that 1 and 2 processes give identical rows, with the complete set of keys."""
    kwargs = dict(N=2000, sementes=range(2), celulas_idx=[0, 1])
    r1 = rd.rodar_grade(processos=1, **kwargs)
    r2 = rd.rodar_grade(processos=2, **kwargs)

    assert len(r1) == len(r2) == 2 * 7 * 2  # 2 cells x 7 combos x 2 seeds
    assert r1 == r2

    chaves_esperadas = {
        "i_celula",
        "T",
        "lam_A",
        "lam_B",
        "lam_C",
        "d_A",
        "d_B",
        "d_C",
        "combo",
        "semente",
        "auc",
        "auc_analitica",
        "saturada",
        "n_pos",
        "n_neg",
    }
    for linha in r1:
        assert set(linha.keys()) == chaves_esperadas
