"""Mutation locks, round 3 (5 real survivors) of the displacement replication.

Input: a private mutation report (only the 5 items that survived, none equivalent). This file does
not edit ``test_displacement_locks.py``, ``test_displacement.py`` nor any module of ``code/``; it
runs against the real source (correct at these 5 points) and must PASS with no production change.

Each function kills one mutant:
  1. X27: ``rodar_grade`` without the final sort (survives when ``celulas_idx``/``sementes`` already
     arrive sorted, as in ``test_rodar_grade_determinismo_e_chaves_da_linha``).
  2. N04: ``resumo_shortfall`` as the MEAN OF PER-SEED RATIOS instead of the RATIO OF MEANS
     (survives when the seeds of a combination and of ABC are identical).
  3. N05: ``shortfall_padrao_T4`` with the extra condition ``C < min(A,B)`` (= the whole
     ``padrao_p3``), which survives when the test cell always has C below min(A,B).
  4. N06: ``shortfall_padrao_T4`` without the condition ``BC > C``.
  5. N09: ``run_replication.main`` not copying ``shortfall_por_celula``/``shortfall_padrao_T4``
     into ``resumo.json`` (survives because no test calls ``main()``).
"""

from __future__ import annotations

import json

import pytest

import displacement as rd
import run_replication

# --- construction helpers (minimal, duplicated on purpose: this file imports nothing from another
#     test module, same convention as ``test_displacement_locks.py``) -----------------------------


def _linha(i_celula, cel, combo, semente, auc):
    """Build one result row as ``avaliar_quebra`` and ``resumo_shortfall`` read it."""
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


def _linhas_de_valores(i_celula, cel, valores):
    """Build rows from ``valores`` (combination -> list of AUCs, one row per seed from 0).

    It must cover the 7 combinations: ``resumo_shortfall`` reads the mean of each one, and a
    missing combination would become the mean of an empty list (silent NaN), which is not what
    these tests exercise.
    """
    linhas = []
    for combo, vals in valores.items():
        for semente, v in enumerate(vals):
            linhas.append(_linha(i_celula, cel, combo, semente, v))
    return linhas


_CEL_PADRAO = {"T": 90, "lam": {"A": 0.1, "B": 0.3, "C": 3}, "d": {"A": 0.5, "B": 0.15, "C": 0}}


# === 1. rodar_grade: final sort, independent of the submission order ============================


def test_1_rodar_grade_ordena_por_celula_combo_semente_fora_de_ordem_mata_X27():
    """Check that ``rodar_grade`` sorts its output even when the inputs arrive out of order.

    The docstring promises output sorted by (i_celula, i_combo, semente) regardless of the number
    of processes. The round-1 test uses ``celulas_idx=[0, 1]`` and ``sementes=range(2)``, both
    already sorted, so an implementation without the final sort (``ex.map`` keeps the SUBMISSION
    order) passes by accident. Here both are OUT of order.

    Kills X27: remove the final sort of ``rodar_grade`` (the first row would have ``i_celula=1``).
    """
    kwargs = dict(N=300, sementes=[1, 0], celulas_idx=[1, 0])
    r1 = rd.rodar_grade(processos=1, **kwargs)
    r2 = rd.rodar_grade(processos=2, **kwargs)

    assert len(r1) == len(r2) == 2 * 7 * 2  # 2 cells x 7 combos x 2 seeds
    assert r1 == r2  # determinism independent of the number of processes (round 1)

    chaves = [(row["i_celula"], rd.COMBOS.index(row["combo"]), row["semente"]) for row in r1]
    assert chaves == sorted(chaves), "output not sorted by (i_celula, i_combo, semente)"
    assert r1[0]["i_celula"] == 0  # without the final sort (X27) the first row would be cell 1


# === 2. resumo_shortfall: ratio OF MEANS, not mean OF RATIOS ======================================


def test_2_resumo_shortfall_e_razao_das_medias_nao_media_das_razoes_mata_N04():
    """Check that the shortfall is the ratio of the seed means, not the mean of per-seed ratios.

    Test (g) of round 2 uses IDENTICAL seeds, where both conventions coincide algebraically. Here
    'A' has seeds 0.2 and 0.8 (mean 0.5) and 'ABC' 0.4 and 0.6 (mean 0.5), chosen so that the two
    conventions diverge (checked below before using the boundary).

    Kills N04: ``resumo_shortfall`` as the mean of per-seed ratios.
    """
    valores = {
        "A": [0.2, 0.8],
        "ABC": [0.4, 0.6],
        "B": [0.5, 0.5],
        "C": [0.5, 0.5],
        "AB": [0.5, 0.5],
        "BC": [0.5, 0.5],
        "AC": [0.5, 0.5],
    }
    razao_das_medias = (1 - 0.5) / (1 - 0.5)  # the means of A and of ABC are both 0.5
    media_das_razoes_errada = ((1 - 0.2) / (1 - 0.4) + (1 - 0.8) / (1 - 0.6)) / 2
    assert abs(media_das_razoes_errada - razao_das_medias) > 0.05  # the conventions diverge

    linhas = _linhas_de_valores(0, _CEL_PADRAO, valores)
    resumo = rd.resumo_shortfall(linhas)

    assert resumo["shortfall_por_celula"][0]["A"] == pytest.approx(razao_das_medias)


# === 3. shortfall_padrao_T4: without the extra condition 'C < min(A,B)' of padrao_p3 ==============


def test_3_shortfall_padrao_t4_conta_celula_com_c_maior_que_min_a_b_mata_N05():
    """Check that the T4 count includes a cell with C >= min(A, B).

    The cell satisfies T4 (AC<A, BC<B, ABC<AB, AB>A, BC>C) but has ``C >= min(A, B)``: it breaks
    only the extra condition of ``padrao_p3`` (the absolute position of C, not the effect of adding
    B or C to a context).

    Kills N05: ``shortfall_padrao_T4`` with the extra condition C < min(A, B), which would give 0.
    """
    valores = {
        "A": [0.60],
        "B": [0.90],
        "C": [0.65],
        "AB": [0.80],
        "BC": [0.75],
        "AC": [0.55],
        "ABC": [0.78],
    }
    v = {c: vals[0] for c, vals in valores.items()}
    assert v["AC"] < v["A"] and v["BC"] < v["B"] and v["ABC"] < v["AB"]
    assert v["AB"] > v["A"] and v["BC"] > v["C"]  # full T4 pattern
    assert v["C"] >= min(v["A"], v["B"])  # and STILL not the extra condition of padrao_p3
    assert not rd.padrao_p3(v)  # distinct from padrao_p3

    linhas = _linhas_de_valores(0, _CEL_PADRAO, valores)
    resumo = rd.resumo_shortfall(linhas)

    assert resumo["shortfall_padrao_T4"] == 1


# === 4. shortfall_padrao_T4: requires BC > C (mutant N06 omits it) ================================


def test_4_shortfall_padrao_t4_nao_conta_celula_sem_bc_maior_que_c_mata_N06():
    """Check that the T4 count excludes a cell with BC <= C.

    The cell satisfies AC<A, BC<B, ABC<AB, AB>A (the 4 remaining conditions) but ``BC <= C``.

    Kills N06: ``shortfall_padrao_T4`` without the condition BC > C, which would give 1.
    """
    valores = {
        "A": [0.80],
        "B": [0.70],
        "C": [0.50],
        "AB": [0.85],
        "BC": [0.45],
        "AC": [0.75],
        "ABC": [0.82],
    }
    v = {c: vals[0] for c, vals in valores.items()}
    assert v["AC"] < v["A"] and v["BC"] < v["B"] and v["ABC"] < v["AB"] and v["AB"] > v["A"]
    assert v["BC"] <= v["C"]  # breaks only this condition

    linhas = _linhas_de_valores(0, _CEL_PADRAO, valores)
    resumo = rd.resumo_shortfall(linhas)

    assert resumo["shortfall_padrao_T4"] == 0


# === 5. run_replication.main: writes the shortfall keys into resumo.json ==========================


def test_5_rodar_replica_main_grava_chaves_de_shortfall_no_resumo_json_mata_N09(
    tmp_path, monkeypatch
):
    """Check that ``run_replication.main`` writes both shortfall keys into ``resumo.json``.

    ``main()`` takes neither ``celulas_idx`` nor a reduced grid, and the real grid has 720 cells x
    7 combinations; to run fast, ``celulas()`` (called by ``rd.rodar_grade`` inside ``main``) is
    replaced by a synthetic grid of 2 cells with ``d_C != 0`` (keeps both out of the Q1 grouping,
    which only looks at ``d_C == 0``) and a small ``d`` (avoids an exact AUC of 1.0, which would
    make ``resumo_shortfall`` divide by zero). N and seeds are minimal (N=200, 1 seed, 1 process),
    output in ``tmp_path``.

    Kills N09: ``run_replication.main`` does not copy the shortfall keys into ``resumo.json``.
    """
    celula_sintetica_1 = {
        "T": 10,
        "lam": {"A": 0.02, "B": 0.02, "C": 0.02},
        "d": {"A": 0.1, "B": 0.1, "C": 0.1},
    }
    celula_sintetica_2 = {
        "T": 10,
        "lam": {"A": 0.03, "B": 0.03, "C": 0.03},
        "d": {"A": 0.08, "B": 0.08, "C": 0.08},
    }
    monkeypatch.setattr(rd, "celulas", lambda: [celula_sintetica_1, celula_sintetica_2])

    rc = run_replication.main(
        [
            "--N",
            "200",
            "--sementes",
            "1",
            "--saida",
            str(tmp_path),
            "--processos",
            "1",
        ]
    )
    assert rc == 0

    with open(tmp_path / "resumo.json", encoding="utf-8") as f:
        resumo = json.load(f)

    assert "shortfall_por_celula" in resumo
    assert "shortfall_padrao_T4" in resumo
    assert set(resumo["shortfall_por_celula"].keys()) == {"0", "1"}
    assert isinstance(resumo["shortfall_padrao_T4"], int)
