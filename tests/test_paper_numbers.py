"""Lock every number the paper publishes, read from ``output/results.json``.

``results.json`` is derived from the sealed outputs by ``code/results.py``; the first test checks
that it is exactly what that code derives today (so no value in it was typed by hand). The other
tests assert the published numbers at the precision the paper prints them.
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

import results

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "output"
PREREG = RAIZ / "data" / "prereg" / "01-displacement-replication.md"


@pytest.fixture(scope="module")
def r():
    """Load ``output/results.json``."""
    return json.loads((SAIDA / "results.json").read_text(encoding="utf-8"))


def test_results_json_e_derivado_das_saidas_seladas(r):
    """Check that results.json equals what ``results.construir`` derives from the sealed outputs."""
    assert r == results.construir(SAIDA)
    texto = (SAIDA / "results.json").read_text(encoding="utf-8")
    assert texto == json.dumps(r, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# --- displacement replication -------------------------------------------------------------------


def test_replica_parametros_do_run(r):
    """Check the run parameters: N = 200,000 users, 5 seeds, 720 cells."""
    rep = r["replication"]
    assert (rep["N"], rep["seeds"], rep["cells"]) == (200_000, 5, 720)


def test_replica_q3_padrao_e_ordem(r):
    """Check 410/720 cells with the sign pattern (analytic 407) and 55/720 in full order (50)."""
    rep = r["replication"]
    assert rep["q3_sign_pattern_cells"] == 410
    assert rep["analytic_sign_pattern_cells"] == 407
    assert rep["q3_full_order_cells"] == 55
    assert rep["analytic_full_order_cells"] == 50
    assert rep["q3_agreement_with_analytic"] == 717
    assert rep["shortfall_pattern_T4_cells"] == 410
    assert rep["q3_failed"] is False


def test_replica_q2_zero_discordancias_em_2011(r):
    """Check 0 discordant out of 2,011 tested comparisons (2,160 = 2,011 + 149 below 0.005 + 0)."""
    rep = r["replication"]
    assert rep["q2_discordant"] == 0
    assert rep["q2_tested"] == 2011
    assert rep["q2_comparisons"] == 2160
    assert rep["q2_below_threshold"] == 149
    assert rep["q2_ties"] == 0
    assert rep["q2_failed"] is False


def test_replica_q1_monotonicidade(r):
    """Check Q1: 248 pairs tested, 0 violations."""
    rep = r["replication"]
    assert (rep["q1_pairs_tested"], rep["q1_violations"], rep["q1_failed"]) == (248, 0, False)


def test_replica_bate_os_sha256_registrados_no_pre_registro(r):
    """Check that the replication outputs have the sha256 recorded in the pre-registration."""
    registrados = dict(
        (m.group(2), m.group(1))
        for m in re.finditer(
            r"^([0-9a-f]{64})  output/replication/(celulas\.csv|resumo\.json)$",
            PREREG.read_text(encoding="utf-8"),
            flags=re.M,
        )
    )
    assert set(registrados) == {"celulas.csv", "resumo.json"}
    assert r["replication"]["sha256"] == registrados


# --- token KAT ----------------------------------------------------------------------------------


def test_kat_token_kt_s(r):
    """Check KT-S 8/8 cells, 40/40 per-seed signs, 0 ties, 0 discordant."""
    kat = r["token_kat"]
    assert (kat["kt_s_agree"], kat["kt_s_cells"]) == (8, 8)
    assert (kat["kt_s_seed_signs_agree"], kat["kt_s_seed_signs_total"]) == (40, 40)
    assert (kat["kt_s_ties"], kat["kt_s_discordant"]) == (0, 0)
    assert kat["kt_s_passed"] is True


def test_kat_token_kt_n(r):
    """Check KT-N 16/16 combinations within tolerance; largest |deviation| 0.0019 AUC."""
    kat = r["token_kat"]
    assert (kat["kt_n_within"], kat["kt_n_combos"], kat["kt_n_exceedances"]) == (16, 16, 0)
    assert kat["kt_n_passed"] is True
    assert round(kat["kt_n_max_abs_deviation"], 4) == 0.0019


def test_kat_token_parametros_e_veredito(r):
    """Check N = 100,000 users, 5 seeds, the global verdict and the regime of each cell."""
    kat = r["token_kat"]
    assert (kat["N"], kat["seeds"], kat["passed"]) == (100_000, 5, True)
    regimes = {c: v["regime"] for c, v in kat["cells"].items()}
    assert regimes == {
        "S1a": "saturado",
        "S1b": "saturado",
        "S2a": "saturado",
        "S2b": "saturado",
        "S3": "saturado",
        "MIX1": "misto",
        "MIX2": "misto",
        "N1": "nao_saturado",
    }


# --- order-of-magnitude estimates ---------------------------------------------------------------


def test_estimativas_publicadas(r):
    """Check E2 0.462, E3 0.364/0.545, E4 695.1 GPU-hours and the other printed estimates."""
    e = r["estimates"]
    assert round(e["E2_utilizacao_a100"], 3) == 0.462
    assert (round(e["E3_utilizacao_4N_lora"], 3), round(e["E3_utilizacao_6N"], 3)) == (0.364, 0.545)
    assert round(e["E4_gpu_horas_h100"], 1) == 695.1
    assert e["E4_flops_pretreino"] == 9.9e20
    assert round(e["E1_txn_ctx_compacto"]) == 146 and int(e["E1_txn_ctx_texto"]) == 37
    assert round(e["E1_razao"], 1) == 3.9
    assert round(e["E2_usuarios_por_gpu_s"], 1) == 92.6
    assert (round(e["E2_utilizacao_l4_300"], 2), round(e["E2_utilizacao_l4_150"], 2)) == (
        0.24,
        0.48,
    )
    assert round(e["E5_bytes_gradiente"] / 1e6) == 660
    assert round(e["E5_t_computo_passo_s"] * 1000) == 328
    assert round(e["E6_vazao_media_gbps"], 2) == 0.36
    assert round(e["E7_latencia_min_computo_ms"]) == 5
    assert round(100 * e["E7_fracao_sla_pix"], 1) == 0.7
    assert (round(e["E7_a100_pico_pre_filtro"]), round(e["E7_a100_pico_pos_filtro"], 1)) == (
        14,
        0.1,
    )


def test_tabela_enlaces_allreduce(r):
    """Check every row of the all-reduce table (DDP ms, FSDP ms, communication/compute ratio)."""
    linhas = {
        row["enlace"]: (
            row["t_allreduce_ddp_ms"],
            row["t_allreduce_fsdp_ms"],
            row["razao_ddp_sobre_computo"],
        )
        for row in r["tables"]["enlaces_allreduce"]
    }
    assert linhas == {
        "NVLink 3 (A100, intra-no)": ("4.3", "6.5", "0.013"),
        "NVLink 4 (H100, intra-no)": ("2.9", "4.3", "0.009"),
        "InfiniBand NDR 400 Gb/s": ("26.0", "39.0", "0.079"),
        "Ethernet RoCE 200 Gb/s": ("52.0", "78.0", "0.158"),
        "Ethernet 100 Gb/s": ("104.0", "155.9", "0.317"),
        "Ethernet 25 Gb/s": ("415.8", "623.7", "1.268"),
    }


def test_tabela_fanout_cauda(r):
    """Check the fan-out tail table: P(at least one of n services above its p99)."""
    linhas = {
        row["servicos"]: row["prob_ao_menos_um_acima_do_p99"] for row in r["tables"]["fanout_cauda"]
    }
    assert linhas == {"1": "0.0100", "5": "0.0490", "10": "0.0956", "20": "0.1821"}


def test_kat_token_resumo_aponta_para_o_adendo_e_a_grade_congelados():
    """Check that the KAT summary records the sha256 of the committed addendum and grid.

    This makes "frozen before the run" checkable inside the repository: editing the addendum or
    the grid after the run breaks this test (and the seal).
    """
    kat = json.loads((SAIDA / "kat_token" / "resumo.json").read_text(encoding="utf-8"))
    adendo = RAIZ / "data" / "prereg" / "02-token-kat-addendum.md"
    grade = RAIZ / "data" / "kat_token_grid.json"
    assert kat["adendo_sha256"] == hashlib.sha256(adendo.read_bytes()).hexdigest()
    assert kat["grade_sha256"] == hashlib.sha256(grade.read_bytes()).hexdigest()


# --- workflow B: pre-registered families (data/prereg/05 to 08) ---------------------------------


def test_exp_expoente_de_d_passa(r):
    """Check EXP: EXS 6/6 (30/30 seed-level signs, 0 ties, 0 discordant) and EXN 6/6."""
    e = r["exponent"]
    assert (e["N"], e["seeds"], e["tag"]) == (100_000, 5, 5)
    assert (e["exs_agree"], e["exs_cells"]) == (6, 6)
    assert (e["exs_seed_signs_agree"], e["exs_seed_signs_total"]) == (30, 30)
    assert (e["exs_ties"], e["exs_discordant"], e["exs_passed"]) == (0, 0, True)
    assert (e["exn_within"], e["exn_cells"], e["exn_exceedances"], e["exn_passed"]) == (
        6,
        6,
        0,
        True,
    )
    assert round(e["exn_max_dev_over_tol"], 2) == 0.25
    assert (e["outcome"], e["passed"], e["complete"]) == ("passa", True, True)
    assert e["implied_interval"] == {"C_p_over_q": [1.604, 2.498], "D_p": [1.591, 2.51]}
    assert all(c["sign"] == "concorda" and c["within"] for c in e["cells"].values())


def test_occ_ocupacao_contra_taxa_passa(r):
    """Check OCC: OCC-S 10/10 (5 up, 5 down; 50/50 seed signs), OCC-N 20/20, OCC-L 2/2 apart."""
    o = r["occupancy"]
    assert (o["N"], o["seeds"], o["tag"], o["cells"]) == (100_000, 5, 6, 12)
    assert (o["occ_s_agree"], o["occ_s_cells"], o["occ_s_passed"]) == (10, 10, True)
    assert (o["occ_s_improves"], o["occ_s_worsens"]) == (5, 5)
    assert (o["occ_s_seed_signs_agree"], o["occ_s_seed_signs_total"]) == (50, 50)
    assert (o["occ_s_ties"], o["occ_s_discordant"]) == (0, 0)
    assert (o["occ_n_within"], o["occ_n_combos"], o["occ_n_exceedances"]) == (20, 20, 0)
    assert round(o["occ_n_max_abs_deviation"], 4) == 0.0039
    assert (o["occ_l_agree"], o["occ_l_cells"], o["occ_l_ties"], o["occ_l_discordant"]) == (
        2,
        2,
        0,
        0,
    )
    # lower bounds of alpha are truncated, never rounded up (0.74890 must not read 0.749)
    assert (o["alpha_lower_bound_verdict"], o["alpha_lower_bound_with_threshold"]) == (
        0.515,
        0.748,
    )
    assert (o["per_event_rule_opposite_cells"], o["per_event_rule_refuted_cells"]) == (7, 7)
    assert (o["depth_pairs_within"], o["depth_pairs"]) == (4, 4)
    assert (o["passed"], o["grid_complete"]) == (True, True)


def test_cmp_fusao_de_eventos_passa(r):
    """Check CMP: CMP-S 28/28 (140/140 seed signs), exact null within tol_0, CMP-N 24/24."""
    f = r["fusion"]
    assert (f["N"], f["K"], f["seeds"], f["tag"]) == (100_000, 2048, 5, 7)
    assert (f["cmp_s_agree"], f["cmp_s_contrasts"], f["cmp_s_passed"]) == (28, 28, True)
    assert (f["cmp_s_seed_signs_agree"], f["cmp_s_seed_signs_total"]) == (140, 140)
    assert (f["cmp_s_ties"], f["cmp_s_discordant"], f["cmp_s_without_significance"]) == (0, 0, 0)
    assert (f["cmp_0_cell"], f["cmp_0_contrast"], f["cmp_0_tol"]) == ("CMP6", "RF-RS", 0.0041)
    assert f["cmp_0_passed"] is True and f["cmp_0_abs_difference"] <= f["cmp_0_tol"]
    assert (f["cmp_n_within"], f["cmp_n_combos"], f["cmp_n_exceedances"]) == (24, 24, 0)
    assert round(f["cmp_n_max_abs_deviation"], 4) == 0.0026
    assert (f["cmp_t_passed"], f["cmp_t_arms"], f["cmp_t_exceedances"]) == (True, 4, 0)
    assert f["cmp_t_in_verdict"] is False
    assert (f["verdict"], f["passed"]) == ("PASSA", True)


def test_c5_cotas_contra_recencia_passa(r):
    """Check C5: anchors 10/10, C5-O 13/13, C5-G 19/19, C5-N 30/30, C5-C and C5-D pass."""
    q = r["quotas"]
    assert (q["N"], q["K"], q["seeds"], q["tag"], q["tol_X"]) == (100_000, 2048, 5, 8, 0.00405)
    assert (q["preregistered"], q["passed"]) == (True, True)
    assert q["outcomes"] == ["Tudo passa", "C5-D passa (com o acima)"]
    assert (q["anchors_applicable"], q["anchors_equal"], q["anchors_rows"]) == (True, 10, 10)
    assert q["anchors_passed"] is True
    assert (q["c5_o_comparisons"], q["c5_o_discordant"], q["c5_o_ties"]) == (13, 0, 0)
    assert (q["c5_g_comparisons"], q["c5_g_exceedances"], q["c5_g_without_power"]) == (19, 0, 0)
    assert (q["c5_n_levels"], q["c5_n_exceedances"]) == (30, 0)
    assert round(q["c5_n_max_abs_deviation"], 5) == 0.00142
    assert all(q[k] is True for k in ("c5_o_passed", "c5_g_passed", "c5_n_passed", "c5_c_passed"))
    assert (q["c5_d_passed"], q["c5_d_comparisons"], q["c5_d_discordant"], q["c5_d_ties"]) == (
        True,
        2,
        0,
        0,
    )
    rec, rho = q["consequence"]["REC"], q["consequence"]["RHO"]
    assert (round(rec["mean"], 4), round(rec["predicted"], 4)) == (-0.0459, -0.0441)
    assert rho["seed_changes"] == [0.0] * 5 and q["consequence_rival_refuted"] is True
    fix = q["comparisons"]["FIX1 RHO-FIXc"]
    assert (round(fix["mean"], 4), round(fix["predicted"], 4)) == (0.0154, 0.0159)


@pytest.mark.parametrize(
    "bloco, grade, tabela, prereg",
    [
        (
            "exponent",
            "exponent_grid.json",
            "exponent_analytic_table.txt",
            "05-exponent-addendum.md",
        ),
        (
            "occupancy",
            "occupancy_grid.json",
            "occupancy_analytic_table.txt",
            "06-occupancy-addendum.md",
        ),
        ("fusion", "fusion_grid.json", "fusion_analytic_table.txt", "07-fusion-addendum.md"),
        ("quotas", "quotas_grid.json", "quotas_analytic_table.txt", "08-quotas-addendum.md"),
    ],
)
def test_familias_apontam_para_a_grade_tabela_e_pre_registro_congelados(
    r, bloco, grade, tabela, prereg
):
    """Check that each family summary records the SHA-256 of the committed frozen inputs.

    Editing a grid, an analytic table or a pre-registration after its run breaks this test.
    """

    def sha(p: Path) -> str:
        """Return the sha256 hex digest of the bytes of ``p``."""
        return hashlib.sha256(p.read_bytes()).hexdigest()

    assert r[bloco]["sha256"] == {
        "grid": sha(RAIZ / "data" / grade),
        "analytic_table": sha(RAIZ / "data" / "prereg" / tabela),
        "preregistration": sha(RAIZ / "data" / "prereg" / prereg),
    }


def test_familias_tem_fluxos_aleatorios_proprios(r):
    """Check that the families draw from their own streams: tags 5 to 8, never the KAT tag 3."""
    tags = [r[b]["tag"] for b in ("exponent", "occupancy", "fusion", "quotas")]
    assert tags == [5, 6, 7, 8]
