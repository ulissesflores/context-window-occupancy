"""Known-answer tests for the formulas and locks on every estimate the paper prints.

If an input in ``configs/estimates_inputs.json`` changes, the locked values below fail on purpose:
the paper text must be updated in the same change.
"""

import math

import estimates as e

R = e.calcular(e.carregar())


# --- formulas against hand-worked cases ---------------------------------------------------------


def test_ring_allreduce_kat():
    """Check the ring all-reduce volume: p=2 sends S; p -> inf tends to 2S."""
    # p=2: each GPU sends S (reduce-scatter half + all-gather half); p->inf: 2S
    assert e.trafego_ring_allreduce(100.0, 2) == 100.0
    assert math.isclose(e.trafego_ring_allreduce(100.0, 10_000), 2 * 100.0 * 9_999 / 10_000)


def test_tail_kat():
    """Check the fan-out tail probability on hand-worked cases."""
    assert math.isclose(e.prob_ao_menos_um_lento(1, 0.01), 0.01)
    assert math.isclose(e.prob_ao_menos_um_lento(2, 0.5), 0.75)


def test_flops_kat():
    """Check that the attention term vanishes with zero layers: only 2N remains."""
    assert e.flops_forward_por_token(10, 0, 2048, 1024) == 20


# --- consistency with the source ----------------------------------------------------------------


def test_text_only_window_matches_source():
    """Check the ~37 transactions of a text-only serialisation in 2048 tokens (source value)."""
    assert math.floor(R["E1_txn_ctx_texto"]) == 37


def test_published_throughput_is_physically_possible():
    """Check that implied utilisation is strictly below the hardware peak."""
    # otherwise the published inputs would be mutually inconsistent
    assert 0 < R["E2_utilizacao_a100"] < 1
    assert 0 < R["E2_utilizacao_l4_300"] < R["E2_utilizacao_l4_150"] < 1
    assert 0 < R["E3_utilizacao_4N_lora"] < R["E3_utilizacao_6N"] < 1


# --- locks on printed numbers -------------------------------------------------------------------


def test_locked_values():
    """Lock every estimate the paper prints, at the precision it prints."""
    assert round(R["E1_txn_ctx_compacto"]) == 146
    assert round(R["E1_razao"], 1) == 3.9
    assert round(R["E2_usuarios_por_gpu_s"], 1) == 92.6
    assert round(100 * R["E2_utilizacao_a100"]) == 46
    assert (round(100 * R["E2_utilizacao_l4_300"]), round(100 * R["E2_utilizacao_l4_150"])) == (
        24,
        48,
    )
    assert (round(100 * R["E3_utilizacao_4N_lora"]), round(100 * R["E3_utilizacao_6N"])) == (
        36,
        55,
    )
    assert round(R["E4_gpu_horas_h100"], -1) == 700
    assert round(R["E5_bytes_gradiente"] / 1e6) == 660
    assert round(R["E5_t_computo_passo_s"] * 1000) == 328
    enl = R["E5_enlaces"]
    assert round(enl["InfiniBand NDR 400 Gb/s"]["t_allreduce_ddp_ms"]) == 26
    assert round(100 * enl["InfiniBand NDR 400 Gb/s"]["razao_ddp_sobre_computo"]) == 8
    assert round(100 * enl["Ethernet 25 Gb/s"]["razao_ddp_sobre_computo"]) == 127
    assert round(R["E6_vazao_media_gbps"], 2) == 0.36
    assert round(R["E7_latencia_min_computo_ms"]) == 5
    assert round(R["E7_a100_pico_pre_filtro"]) == 14
    assert round(R["E7_fanout"]["10"], 3) == 0.096
