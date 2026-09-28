"""Aggregate the published numbers into ``output/results.json``.

``results.json`` is the single source of the numbers that the README quotes and that
``tests/test_paper_numbers.py`` asserts. It is DERIVED: every value is read from the sealed outputs
(``replication/resumo.json``, ``kat_token/resumo.json``, ``estimativas.json``, ``tables/*.csv``,
and the ``resumo.json`` of the four workflow-B families under ``exponent/``, ``occupancy/``,
``fusion/`` and ``quotas/``, plus ``quotas/celulas.csv`` for the report-only decay row), never
typed by hand, so the file can be regenerated and compared byte for byte. The family blocks
record the SHA-256 of the frozen grid, analytic table and pre-registration each run used (read
from its summary), never the hash of an output, so they do not depend on the library versions.

Run: ``python3 code/results.py [--saida output]``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "output"

# estimates the paper quotes (keys of estimativas.json, kept verbatim)
CHAVES_ESTIMATIVAS = (
    "E1_txn_ctx_compacto",
    "E1_txn_ctx_texto",
    "E1_razao",
    "E2_usuarios_por_gpu_s",
    "E2_utilizacao_a100",
    "E2_utilizacao_l4_150",
    "E2_utilizacao_l4_300",
    "E3_utilizacao_6N",
    "E3_utilizacao_4N_lora",
    "E4_flops_pretreino",
    "E4_gpu_horas_h100",
    "E5_bytes_gradiente",
    "E5_t_computo_passo_s",
    "E6_vazao_media_gbps",
    "E7_latencia_min_computo_ms",
    "E7_fracao_sla_pix",
    "E7_a100_pico_pre_filtro",
    "E7_a100_pico_pos_filtro",
)


def _sha(p: Path) -> str:
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _json(p: Path) -> dict:
    """Load a UTF-8 JSON file."""
    return json.loads(p.read_text(encoding="utf-8"))


def _tabela(p: Path) -> list[dict]:
    """Load a CSV table as a list of row dicts (values kept as the printed strings)."""
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _sinal(x: float) -> int:
    """Return the sign of ``x`` as -1, 0 or +1."""
    return (x > 0) - (x < 0)


def _truncar3(x: float | None) -> float | None:
    """Truncate ``x`` to three decimals toward zero (a lower bound is never rounded up)."""
    if x is None:
        return None
    return float(Decimal(repr(x)).quantize(Decimal("0.001"), rounding=ROUND_DOWN))


def _bloco_exponent(saida: Path) -> dict:
    """Summarize the EXP family (exponent of ``d``) from ``exponent/resumo.json``.

    Parameters
    ----------
    saida : Path
        Directory holding ``exponent/resumo.json``.

    Returns
    -------
    dict
        Verdict, the EXS and EXN criteria, the report-only implied interval, one entry per cell
        and the SHA-256 of the frozen grid, analytic table and addendum the run used.
    """
    res = _json(saida / "exponent" / "resumo.json")
    v = res.get("veredito", {})
    exs, exn = v.get("EXS", {}), v.get("EXN", {})
    celulas = v.get("por_celula", [])
    intervalo = v.get("intervalo_implicado")
    return {
        "N": res["N"],
        "seeds": len(res["sementes"]),
        "tag": res["tag"],
        "outcome": v.get("desfecho"),
        "passed": v.get("passou"),
        "complete": v.get("completo"),
        "exs_passed": exs.get("passou"),
        "exs_cells": exs.get("celulas"),
        "exs_discordant": exs.get("discordantes"),
        "exs_ties": exs.get("empates"),
        "exs_agree": sum(c["EXS"] == "concorda" for c in celulas),
        "exs_seed_signs_agree": sum(
            s == c["sinal_teoria"] for c in celulas for s in c["sinais_por_semente"]
        ),
        "exs_seed_signs_total": sum(len(c["sinais_por_semente"]) for c in celulas),
        "exn_passed": exn.get("passou"),
        "exn_cells": exn.get("celulas"),
        "exn_exceedances": exn.get("estouros"),
        "exn_within": sum(bool(c["EXN_dentro"]) for c in celulas),
        "exn_max_dev_over_tol": max((c["desvio_sobre_tolD"] for c in celulas), default=None),
        "implied_interval": None
        if not intervalo
        else {
            "C_p_over_q": intervalo["C"]["p_sobre_q"],
            "D_p": intervalo["D"]["p"],
        },
        "cells": {
            c["celula"]: {
                "family": c["familia"],
                "side": c["lado"],
                "theory_sign": c["sinal_teoria"],
                "predicted": c["dif_prevista"],
                "empirical": c["dif_empirica"],
                "se": c["ep_emp"],
                "dev_over_tol": c["desvio_sobre_tolD"],
                "within": c["EXN_dentro"],
                "sign": c["EXS"],
            }
            for c in celulas
        },
        "sha256": {
            "grid": res["grade_sha256"],
            "analytic_table": res["tabela_sha256"],
            "preregistration": res["adendo_sha256"],
        },
    }


def _bloco_occupancy(saida: Path) -> dict:
    """Summarize the OCC family (occupancy against rate weighting) from ``occupancy/resumo.json``.

    Parameters
    ----------
    saida : Path
        Directory holding ``occupancy/resumo.json``.

    Returns
    -------
    dict
        Verdict, the OCC-S and OCC-N criteria, the threshold cells (OCC-L, outside the verdict),
        the report-only diagnostics (lower bounds of ``α`` truncated to three decimals, the
        per-event rule, the depth pairs) and the SHA-256 of the frozen inputs.
    """
    res = _json(saida / "occupancy" / "resumo.json")
    v = res.get("veredito", {})
    crit = v.get("criterios", {})
    occ_s, occ_n = crit.get("OCC_S", {}), crit.get("OCC_N", {})
    occ_l = v.get("fora_do_veredito", {}).get("OCC_L", {})
    principal = v.get("avaliar_kat_principal", {}).get("por_celula", [])
    rel = v.get("relatorio", {})
    alfa, evento = rel.get("alfa_minimo", {}), rel.get("regra_por_evento", {})
    pares = rel.get("invariancia_em_T", [])
    return {
        "N": res["N"],
        "seeds": len(res["sementes"]),
        "tag": res["tag"],
        "cells": len(res["celulas"]),
        "passed": v.get("passou"),
        "grid_complete": v.get("grade_completa"),
        "occ_s_passed": occ_s.get("passou"),
        "occ_s_cells": len(occ_s.get("celulas", [])),
        "occ_s_agree": len(occ_s.get("concorda", [])),
        "occ_s_ties": len(occ_s.get("empate", [])),
        "occ_s_discordant": len(occ_s.get("discorda", [])),
        "occ_s_improves": sum(c["dif_prevista"] > 0 for c in principal),
        "occ_s_worsens": sum(c["dif_prevista"] < 0 for c in principal),
        "occ_s_seed_signs_agree": sum(
            s == _sinal(c["dif_prevista"]) for c in principal for s in c["sinais_por_semente"]
        ),
        "occ_s_seed_signs_total": sum(len(c["sinais_por_semente"]) for c in principal),
        "occ_n_passed": occ_n.get("passou"),
        "occ_n_combos": occ_n.get("combos"),
        "occ_n_exceedances": len(occ_n.get("estouros", [])),
        "occ_n_within": occ_n.get("combos", 0) - len(occ_n.get("estouros", [])),
        "occ_n_max_abs_deviation": max(
            (abs(n["desvio"]) for c in principal for n in c["nivel"].values()), default=None
        ),
        "occ_l_cells": len(occ_l.get("celulas", [])),
        "occ_l_agree": len(occ_l.get("concorda", [])),
        "occ_l_ties": len(occ_l.get("empate", [])),
        "occ_l_discordant": len(occ_l.get("discorda", [])),
        "alpha_lower_bound_verdict": _truncar3(alfa.get("familia_principal")),
        "alpha_lower_bound_with_threshold": _truncar3(alfa.get("com_occ_l")),
        "per_event_rule_opposite_cells": len(evento.get("celulas_opostas", [])),
        "per_event_rule_refuted_cells": len(evento.get("refutada_em", [])),
        "per_event_rule_refuted": evento.get("refutada"),
        "depth_pairs": len(pares),
        "depth_pairs_within": sum(bool(x["dentro"]) for x in pares),
        "sha256": {
            "grid": res["grade_sha256"],
            "analytic_table": res["tabela_sha256"],
            "preregistration": res["adendo_sha256"],
        },
    }


def _bloco_fusion(saida: Path) -> dict:
    """Summarize the CMP family (event fusion, Corollary 4(b)) from ``fusion/resumo.json``.

    Parameters
    ----------
    saida : Path
        Directory holding ``fusion/resumo.json``.

    Returns
    -------
    dict
        Verdict, the CMP-S, CMP-0 and CMP-N criteria, the ceiling check CMP-T (outside the
        verdict) and the SHA-256 of the frozen inputs.
    """
    res = _json(saida / "fusion" / "resumo.json")
    av = res.get("avaliar_fusao", {})
    cs, c0 = av.get("CMP_S", {}), av.get("CMP_0", {})
    cn, ct = av.get("CMP_N", {}), av.get("CMP_T", {})
    criterio = [c for c in av.get("por_contraste", []) if c["papel"] == "critério"]
    reportado = [c for c in av.get("por_contraste", []) if c["papel"] == "só reportado"]
    return {
        "N": res["N"],
        "K": res["K"],
        "seeds": len(res["sementes"]),
        "tag": res["tag"],
        "verdict": res.get("veredito"),
        "passed": av.get("passou"),
        "cmp_s_passed": cs.get("passou"),
        "cmp_s_contrasts": cs.get("contrastes"),
        "cmp_s_agree": cs.get("concordam"),
        "cmp_s_ties": cs.get("empates"),
        "cmp_s_discordant": cs.get("discordantes"),
        "cmp_s_without_significance": cs.get("sem_significancia"),
        "cmp_s_seed_signs_agree": sum(
            s == _sinal(c["dif_prevista"]) for c in criterio for s in c["sinais_por_semente"]
        ),
        "cmp_s_seed_signs_total": sum(len(c["sinais_por_semente"]) for c in criterio),
        "cmp_0_passed": c0.get("passou"),
        "cmp_0_cell": c0.get("celula"),
        "cmp_0_contrast": c0.get("contraste"),
        "cmp_0_tol": c0.get("tol_0"),
        "cmp_0_abs_difference": None if c0.get("dif_empirica") is None else abs(c0["dif_empirica"]),
        "cmp_n_passed": cn.get("passou"),
        "cmp_n_combos": cn.get("combos"),
        "cmp_n_exceedances": cn.get("estouros"),
        "cmp_n_within": sum(bool(b["dentro"]) for b in av.get("por_braco", [])),
        "cmp_n_max_abs_deviation": max(
            (abs(b["desvio"]) for b in av.get("por_braco", [])), default=None
        ),
        "cmp_t_passed": ct.get("passou"),
        "cmp_t_arms": ct.get("bracos"),
        "cmp_t_exceedances": ct.get("estouros"),
        "cmp_t_in_verdict": ct.get("no_veredito"),
        "report_only_contrasts": len(reportado),
        "report_only_agree": sum(c["estado"] == "concorda" for c in reportado),
        "sha256": {
            "grid": res["grade_sha256"],
            "analytic_table": res["tabela_sha256"],
            "preregistration": res["preregistro_sha256"],
        },
    }


def _comparacao(c: dict) -> dict:
    """Reduce one C5 comparison of ``avaliar_c5.comparacoes`` to its published fields."""
    return {
        "kind": c["tipo"],
        "criteria": c["criterios"],
        "mean": c["media"],
        "predicted": c["previsto"],
        "se_pair": c["ep_par"],
        "within_tol": c["dentro_tol"],
        "sign": c.get("estado_sinal"),  # absent for equivalence and report-only comparisons
        "seed_signs": c["sinais_por_semente"],
        "rival": c["rival"],
        "rival_refuted": c["rival_refutado"],
    }


def _bloco_quotas(saida: Path) -> dict:
    """Summarize the C5 family (quotas against the recency cut) from ``quotas/``.

    Parameters
    ----------
    saida : Path
        Directory holding ``quotas/resumo.json`` and ``quotas/celulas.csv``.

    Returns
    -------
    dict
        Verdict and outcomes, the anchors, the C5-O, C5-G, C5-N, C5-C and C5-D criteria, every
        comparison (``"<cell> <a>-<b>"``), the exact prediction and mean AUC of each (cell,
        policy) level, the report-only decay row (fluid prediction and mean of the sealed CSV)
        and the SHA-256 of the frozen inputs.
    """
    res = _json(saida / "quotas" / "resumo.json")
    av = res.get("avaliar_c5", {})
    crit, ver = av.get("criterios", {}), av.get("veredito", {})
    ancoras = res.get("ancoras", {})
    linhas = ancoras.get("linhas", [])
    niveis = av.get("niveis", [])
    cons = av.get("consequencia", {})
    decai = res.get("previsoes", {}).get("decaimento", {})
    politicas_decai = [p for p in ("REC", "RHO", "RHOidade") if p in decai]
    aucs = {p: [] for p in politicas_decai}
    for row in _tabela(saida / "quotas" / "celulas.csv"):
        if row["celula"] == "DEC1" and row["historia"] == "RS" and row["politica"] in aucs:
            aucs[row["politica"]].append(float(row["auc"]))
    return {
        "N": res["N"],
        "K": res["K"],
        "seeds": len(res["sementes"]),
        "tag": res["tag"],
        "tol_X": res["tol_X"],
        "preregistered": res.get("preregistrado"),
        "passed": ver.get("passou"),
        "outcomes": ver.get("desfechos", []),
        "anchors_applicable": ancoras.get("aplicavel"),
        "anchors_passed": crit.get("ancoras", {}).get("passou"),
        "anchors_rows": len(linhas),
        "anchors_equal": sum(bool(x["igual"]) for x in linhas),
        "c5_o_passed": crit.get("C5-O", {}).get("passou"),
        "c5_o_comparisons": crit.get("C5-O", {}).get("comparacoes"),
        "c5_o_discordant": crit.get("C5-O", {}).get("discordantes"),
        "c5_o_ties": crit.get("C5-O", {}).get("empates"),
        "c5_g_passed": crit.get("C5-G", {}).get("passou"),
        "c5_g_comparisons": crit.get("C5-G", {}).get("comparacoes"),
        "c5_g_exceedances": crit.get("C5-G", {}).get("estouros"),
        "c5_g_without_power": crit.get("C5-G", {}).get("sem_poder"),
        "c5_n_passed": crit.get("C5-N", {}).get("passou"),
        "c5_n_levels": crit.get("C5-N", {}).get("niveis"),
        "c5_n_exceedances": crit.get("C5-N", {}).get("estouros"),
        "c5_n_max_abs_deviation": max((abs(n["desvio"]) for n in niveis), default=None),
        "c5_c_passed": crit.get("C5-C", {}).get("passou"),
        "c5_d_passed": crit.get("C5-D", {}).get("passou"),
        "c5_d_comparisons": crit.get("C5-D", {}).get("comparacoes"),
        "c5_d_discordant": crit.get("C5-D", {}).get("discordantes"),
        "c5_d_ties": crit.get("C5-D", {}).get("empates"),
        "consequence": {
            politica: {
                "mean": cons[politica]["media"],
                "predicted": cons[politica]["previsto"],
                "seed_changes": cons[politica]["difs_por_semente"],
            }
            for politica in ("REC", "RHO")
            if politica in cons
        },
        "consequence_rival_refuted": cons.get("rival_refutado"),
        "comparisons": {
            f"{c['celula']} {c['par'][0]}-{c['par'][1]}": _comparacao(c)
            for c in av.get("comparacoes", [])
        },
        "levels": {
            f"{n['celula']} {n['politica']}": {"exact": n["exata"], "mean": n["media"]}
            for n in niveis
        },
        "decay_report_only": {
            p: {"fluid": decai[p], "mean": sum(aucs[p]) / len(aucs[p]) if aucs[p] else None}
            for p in politicas_decai
        },
        "sha256": {
            "grid": res["grade_sha256"],
            "analytic_table": res["tabela_sha256"],
            "preregistration": res["preregistro_sha256"],
        },
    }


def construir(saida: Path = SAIDA) -> dict:
    """Build the aggregated results from the outputs under ``saida``.

    Parameters
    ----------
    saida : Path
        Directory holding ``replication/``, ``kat_token/``, ``estimativas.json``, ``tables/`` and
        the four workflow-B family directories (``exponent/``, ``occupancy/``, ``fusion/``,
        ``quotas/``).

    Returns
    -------
    dict
        ``{"replication": ..., "token_kat": ..., "estimates": ..., "tables": ...,
        "exponent": ..., "occupancy": ..., "fusion": ..., "quotas": ...}``.
    """
    rep = _json(saida / "replication" / "resumo.json")
    q1, q2, q3 = (rep["avaliar_quebra"][q] for q in ("Q1", "Q2", "Q3"))
    reg = rep["regiao_p3_analitica"]
    replication = {
        "N": rep["N"],
        "seeds": rep["sementes"],
        "cells": reg["n_celulas"],
        "q1_failed": q1["falhou"],
        "q1_pairs_tested": q1["pares_testados"],
        "q1_violations": len(q1["violacoes"]),
        "q2_failed": q2["falhou"],
        "q2_comparisons": q2["comparacoes"],
        "q2_below_threshold": q2["abaixo_limiar"],
        "q2_ties": q2["empate"],
        "q2_tested": q2["testadas"],
        "q2_discordant": q2["discordantes"],
        "q3_failed": q3["falhou"],
        "q3_sign_pattern_cells": q3["celulas_padrao"],
        "q3_full_order_cells": q3["celulas_ordem"],
        "q3_agreement_with_analytic": q3["concordancia_padrao_com_analitico"],
        "analytic_sign_pattern_cells": reg["n_padrao"],
        "analytic_full_order_cells": reg["n_ordem"],
        "shortfall_pattern_T4_cells": rep["shortfall_padrao_T4"],
        "sha256": {
            "celulas.csv": _sha(saida / "replication" / "celulas.csv"),
            "resumo.json": _sha(saida / "replication" / "resumo.json"),
        },
    }

    kat = _json(saida / "kat_token" / "resumo.json")
    av = kat["avaliar_kat"]
    celulas = av["por_celula"]
    sementes_concordam = sum(
        s == _sinal(c["dif_prevista"]) for c in celulas for s in c["sinais_por_semente"]
    )
    niveis = [n for c in celulas for n in c["nivel"].values()]
    token_kat = {
        "N": kat["N"],
        "seeds": len(kat["sementes"]),
        "passed": av["passou"],
        "kt_s_passed": av["KT_S"]["passou"],
        "kt_s_cells": av["KT_S"]["celulas"],
        "kt_s_agree": sum(c["sinal"] == "concorda" for c in celulas),
        "kt_s_discordant": av["KT_S"]["discordantes"],
        "kt_s_ties": av["KT_S"]["empates"],
        "kt_s_seed_signs_agree": sementes_concordam,
        "kt_s_seed_signs_total": sum(len(c["sinais_por_semente"]) for c in celulas),
        "kt_n_passed": av["KT_N"]["passou"],
        "kt_n_combos": av["KT_N"]["combos"],
        "kt_n_within": sum(n["dentro"] for n in niveis),
        "kt_n_exceedances": av["KT_N"]["estouros"],
        "kt_n_max_abs_deviation": max(abs(n["desvio"]) for n in niveis),
        "cells": {c["celula"]: {"regime": c["regime"], "sign": c["sinal"]} for c in celulas},
    }

    est = _json(saida / "estimativas.json")
    estimates = {k: est[k] for k in CHAVES_ESTIMATIVAS}

    tables = {
        "enlaces_allreduce": _tabela(saida / "tables" / "enlaces_allreduce.csv"),
        "fanout_cauda": _tabela(saida / "tables" / "fanout_cauda.csv"),
    }
    return {
        "replication": replication,
        "token_kat": token_kat,
        "estimates": estimates,
        "tables": tables,
        "exponent": _bloco_exponent(saida),
        "occupancy": _bloco_occupancy(saida),
        "fusion": _bloco_fusion(saida),
        "quotas": _bloco_quotas(saida),
    }


def escrever(r: dict, destino: Path) -> Path:
    """Write ``results.json`` (sorted keys, 2-space indent, trailing newline); return its path."""
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / "results.json"
    arquivo.write_text(
        json.dumps(r, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return arquivo


def main(argv=None) -> int:
    """Aggregate the outputs of ``--saida`` into ``<saida>/results.json``; return 0."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=SAIDA)
    args = ap.parse_args(argv)
    print(escrever(construir(args.saida), args.saida).name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
