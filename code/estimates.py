"""Order-of-magnitude estimates for the Nubank foundation-model case study.

Every number the paper prints about compute, network or latency that is NOT copied from a source is
produced here, from the inputs in ``configs/estimates_inputs.json`` (each tagged FACT, SPEC or
ASSUMPTION). Nothing is simulated: these are closed-form engineering estimates whose formulas are
cited in the docstrings, so a reader can recompute every figure by hand.

Run: ``python3 code/estimates.py [--saida output]`` -> writes ``output/estimativas.json`` and
``output/tables/*.csv``.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTRADAS = RAIZ / "configs" / "estimates_inputs.json"
SAIDA = RAIZ / "output"


def carregar(caminho: Path = ENTRADAS) -> dict:
    """Load inputs, returning {name: value}; the provenance tags stay in the JSON file."""
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    v = {k: e["value"] for k, e in bruto.items() if isinstance(e, dict) and "value" in e}
    v["enlaces"] = {nome: e["value"] for nome, e in bruto["enlaces"].items()}
    return v


# --- formulas (each one is the whole method; no hidden constants) -------------------------------


def txn_por_contexto(contexto: int, tokens_por_txn: float) -> float:
    """Return the transactions that fit in one context window: n = L / tokens-per-transaction."""
    return contexto / tokens_por_txn


def flops_forward_por_token(n_params: float, n_camadas: int, n_ctx: int, d_modelo: int) -> float:
    """Return forward FLOPs per token, C_fwd ~ 2N + 2 n_layer n_ctx d_attn (Kaplan et al., 2020).

    The second term (Table 1 of Kaplan et al.) is attention over the full context; using n_ctx
    (not n_ctx/2) makes it an upper bound for a causal model.
    """
    return 2 * n_params + 2 * n_camadas * n_ctx * d_modelo


def trafego_ring_allreduce(bytes_mensagem: float, p: int) -> float:
    """Return the bytes each GPU sends in a ring all-reduce, 2 (p-1)/p S (Patarasuk & Yuan, 2009).

    Bandwidth-optimal: independent of p for large p, which is why the per-GPU link, not the cluster
    size, sets the cost of synchronising gradients.
    """
    return 2 * (p - 1) / p * bytes_mensagem


def prob_ao_menos_um_lento(n_servicos: int, p_lento: float) -> float:
    """Return P(at least one of n independent dependencies is slow) = 1 - (1 - p)^n.

    Tail-at-scale argument of Dean & Barroso (2013).
    """
    return 1 - (1 - p_lento) ** n_servicos


# --- estimates ----------------------------------------------------------------------------------


def calcular(v: dict) -> dict:
    """Compute every estimate E1-E7 from the loaded inputs.

    Parameters
    ----------
    v : dict
        Output of :func:`carregar`.

    Returns
    -------
    dict
        Estimates keyed ``E1_*`` ... ``E7_*`` (insertion order is the order of
        ``output/estimativas.json``).
    """
    N, L = v["params_modelo"], int(v["contexto_tokens"])
    fwd_tok = flops_forward_por_token(N, int(v["n_camadas"]), L, int(v["d_modelo"]))
    fwd_seq = fwd_tok * L  # one user, full context, one forward pass
    r: dict = {}

    # E1 -- context budget: how much behavioural history one window holds
    r["E1_txn_ctx_compacto"] = txn_por_contexto(L, v["tokens_por_txn_compacto"])
    r["E1_txn_ctx_texto"] = txn_por_contexto(L, v["tokens_por_txn_texto"])
    r["E1_razao"] = r["E1_txn_ctx_compacto"] / r["E1_txn_ctx_texto"]

    # E2 -- daily batch inference, as published: throughput and implied utilisation
    seg = v["horas_inferencia"] * 3600
    r["E2_fwd_flops_por_usuario"] = fwd_seq
    r["E2_usuarios_por_gpu_s"] = v["usuarios_inferencia"] / (seg * v["gpus_inferencia_a100"])
    r["E2_tokens_por_gpu_s"] = r["E2_usuarios_por_gpu_s"] * L
    r["E2_flops_s_por_gpu"] = r["E2_usuarios_por_gpu_s"] * fwd_seq
    r["E2_utilizacao_a100"] = r["E2_flops_s_por_gpu"] / v["a100_bf16_denso_flops"]
    flops_s_total = r["E2_flops_s_por_gpu"] * v["gpus_inferencia_a100"]
    r["E2_utilizacao_l4_150"] = flops_s_total / (
        v["nos_inferencia_l4_min"] * v["l4_bf16_denso_flops"]
    )
    r["E2_utilizacao_l4_300"] = flops_s_total / (
        v["nos_inferencia_l4_max"] * v["l4_bf16_denso_flops"]
    )
    r["E2_gpu_horas_dia"] = v["horas_inferencia"] * v["gpus_inferencia_a100"]

    # E3 -- fine-tuning run as published (7 days on 8 A100): implied utilisation
    tokens_ft = v["linhas_finetune"] * L  # upper bound: every row fills the window
    seg_ft = v["dias_finetune"] * 86400 * v["gpus_finetune_a100"]
    r["E3_tokens_finetune"] = tokens_ft
    r["E3_utilizacao_6N"] = 6 * N * tokens_ft / seg_ft / v["a100_bf16_denso_flops"]
    r["E3_utilizacao_4N_lora"] = 4 * N * tokens_ft / seg_ft / v["a100_bf16_denso_flops"]

    # E4 -- pre-training compute (C ~ 6ND, Kaplan et al., 2020) under stated assumptions
    r["E4_flops_pretreino"] = 6 * N * v["tokens_pretreino"]
    r["E4_gpu_horas_h100"] = (
        r["E4_flops_pretreino"] / (v["mfu_pretreino"] * v["h100_bf16_denso_flops"]) / 3600
    )

    # E5 -- the network of distributed training: gradient all-reduce per optimiser step (DDP)
    S = N * v["bytes_gradiente"]
    p = int(v["gpus_pretreino"])
    tokens_passo = v["batch_pretreino_seq"] * L
    flops_passo_gpu = 6 * N * tokens_passo / p  # dense part only; attention adds ~10%
    t_computo = flops_passo_gpu / (v["mfu_pretreino"] * v["h100_bf16_denso_flops"])
    r["E5_bytes_gradiente"] = S
    r["E5_trafego_por_gpu_ddp"] = trafego_ring_allreduce(S, p)
    # ZeRO-3/FSDP: +50% volume (Zhao et al., 2023)
    r["E5_trafego_por_gpu_fsdp"] = 1.5 * r["E5_trafego_por_gpu_ddp"]
    r["E5_t_computo_passo_s"] = t_computo
    r["E5_enlaces"] = {}
    for nome, bw in v["enlaces"].items():
        t_ddp = r["E5_trafego_por_gpu_ddp"] / bw
        r["E5_enlaces"][nome] = {
            "t_allreduce_ddp_ms": 1000 * t_ddp,
            "t_allreduce_fsdp_ms": 1000 * 1.5 * t_ddp,
            "razao_ddp_sobre_computo": t_ddp / t_computo,
        }

    # E6 -- data the daily batch has to move into the GPUs (token ids only)
    bytes_tokens = v["usuarios_inferencia"] * L * v["bytes_por_token_id"]
    r["E6_bytes_tokens_dia"] = bytes_tokens
    r["E6_vazao_media_gbps"] = bytes_tokens * 8 / seg / 1e9

    # E7 -- the online counterfactual: what if the transformer sat on the synchronous PIX path?
    r["E7_latencia_min_computo_ms"] = 1000 * fwd_seq / v["a100_bf16_denso_flops"]
    # read BF16 weights once
    r["E7_latencia_min_memoria_ms"] = 1000 * N * 2 / v["a100_hbm_bytes_s"]
    r["E7_fracao_sla_pix"] = (
        max(r["E7_latencia_min_computo_ms"], r["E7_latencia_min_memoria_ms"]) / v["sla_pix_ms"]
    )
    r["E7_a100_pico_pre_filtro"] = (
        v["eventos_pre_filtro_tps"] * fwd_seq / v["a100_bf16_denso_flops"]
    )
    r["E7_a100_pico_pos_filtro"] = (
        v["eventos_pos_filtro_tps"] * fwd_seq / v["a100_bf16_denso_flops"]
    )
    r["E7_fanout"] = {
        str(n): prob_ao_menos_um_lento(n, v["p_lento_por_servico"]) for n in v["servicos_fanout"]
    }
    return r


def escrever(r: dict, destino: Path = SAIDA) -> None:
    """Persist results: full JSON plus the two CSV tables the paper reproduces."""
    (destino / "tables").mkdir(parents=True, exist_ok=True)
    (destino / "estimativas.json").write_text(
        json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with open(destino / "tables" / "enlaces_allreduce.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["enlace", "t_allreduce_ddp_ms", "t_allreduce_fsdp_ms", "razao_ddp_sobre_computo"]
        )
        for nome, e in r["E5_enlaces"].items():
            w.writerow(
                [
                    nome,
                    f"{e['t_allreduce_ddp_ms']:.1f}",
                    f"{e['t_allreduce_fsdp_ms']:.1f}",
                    f"{e['razao_ddp_sobre_computo']:.3f}",
                ]
            )
    with open(destino / "tables" / "fanout_cauda.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["servicos", "prob_ao_menos_um_acima_do_p99"])
        for n, pr in r["E7_fanout"].items():
            w.writerow([n, f"{pr:.4f}"])


def main(argv=None) -> int:
    """Compute the estimates, write them under ``--saida`` and print a summary; return 0."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=SAIDA)
    args = ap.parse_args(argv)
    res = calcular(carregar())
    escrever(res, args.saida)
    for k, val in res.items():
        if not isinstance(val, dict):
            print(f"{k:32s} {val:,.4g}")
    for nome, e in res["E5_enlaces"].items():
        print(
            f"  {nome:30s} DDP {e['t_allreduce_ddp_ms']:8.1f} ms  "
            f"FSDP {e['t_allreduce_fsdp_ms']:8.1f} ms  "
            f"comm/compute {e['razao_ddp_sobre_computo']:.3f}"
        )
    print("  fan-out:", {n: round(x, 4) for n, x in res["E7_fanout"].items()})
    print(f"  (sanity) {math.floor(res['E1_txn_ctx_texto'])} txn text-only vs source 37")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
