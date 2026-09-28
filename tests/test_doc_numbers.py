"""Lock the numbers that the documentation quotes against the files they come from.

``tests/test_paper_numbers.py`` asserts ``output/results.json``; this test asserts the prose around
it. Each scoped section of ``README.md``, ``docs/THEORY.md`` and ``REPRODUCIBILITY.md`` must contain
every expected phrase, rendered here from the sealed outputs, the token-KAT grid, the
pre-registration, the estimate inputs, ``env.json`` and the CI matrix; and every number in the
section must sit inside one of those phrases or inside a declared structural phrase (a table
number, a corollary number, a condition of a criterion). A number typed into a scoped section that
no source backs fails the suite. HTML tags, link targets and code spans that hold a path are
blanked before the count, so file names and image widths never count as numbers.

The core, :func:`divergencias`, is a pure function of the document texts: a mutation harness can
feed it edited copies without touching the files.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

import displacement

RAIZ = Path(__file__).resolve().parents[1]
DOCS = ("README.md", "docs/THEORY.md", "REPRODUCIBILITY.md")

# a number is a run of digits (with thousands commas and decimals) not glued to a word character:
# identifiers such as Q2, S3, MIX1, A100, p99, 4N or 10²⁰ are not numbers here
NUMERO = re.compile(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?(?!\w)")
SPAN_DE_CODIGO = re.compile(r"`[^`\n]*`")
PARECE_CAMINHO = re.compile(r"/|\.(?:md|json|py|csv|png|txt|lock|yml)\b")
ALVO_DE_LINK = re.compile(r"\]\([^)]*\)")
TAG_HTML = re.compile(r"<[^>\n]*>")
SOBRESCRITO = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
EXTENSO = {2: "two", 3: "three", 9: "nine"}
EXTENSO[17] = "seventeen"  # run_all.COMPARADOS with the four workflow-B families

# (section, expected phrase templates, declared structural phrases); templates use str.format
MODELOS = {
    "README callout": (
        [
            "({cells} cells, `N = {N}` users per cell, {seeds} seeds)",
            "**{disc} discordant out of {tested}** ({below} more fell below the pre-registered "
            "minimum effect and stayed outside the sign test; {ties} ties)",
            "**{s_agree} of {s_cells} cells ({s_sa} of {s_st} seed-level signs, {s_ties} ties)**",
            "**{n_within} of {n_combos} combinations** (largest deviation {n_dev} AUC)",
        ],
        [],
    ),
    "README at a glance": (
        [
            "| Displacement replication | {cells} cells, every combination of sources `A`, `B`, "
            "`C`, {seeds} seeds, `N = {N}` users per cell, uniform cost |",
            "| Token KAT | {k_cells} cells ({k_sat} saturated, {k_mix} mixed, {k_uns} "
            "unsaturated), `R` and `R ∪ S`, {k_seeds} seeds, `N = {k_N}` users, {k_costs_word} "
            "event costs |",
            "sealed on CPython {python}",
            "CI on Python {ci} |",
        ],
        ["RFC 6962"],
    ),
    "README results": (
        [
            "| {q1_pairs} pairs tested, {q1_viol} violations |",
            "| {disc} discordant out of {tested} tested; {below} of the {comp} comparisons below "
            "the minimum effect; {ties} ties |",
            "| {q3_pat} of {cells} cells (closed form: {an_pat}); cell-by-cell agreement with the "
            "closed form in {q3_agree} of {cells} |",
            "| {q3_ord} of {cells} cells (closed form: {an_ord}) |",
            "points are the means of {seeds} seeds",
            "| {s_agree} of {s_cells} cells agree; {s_sa} of {s_st} seed-level signs; {s_ties} "
            "ties; {s_disc} discordant |",
            "| {n_within} of {n_combos} combinations; {n_exc} exceedances; largest absolute "
            "deviation {n_dev} AUC |",
            "| ≈{e1c} vs ≈{e1t} (ratio {e1r}) |",
            "| {e2u}; {e2a} ({e2l300}–{e2l150} on the published range of L4 nodes) |",
            "| {e3lora} (LoRA-style, `4N` FLOPs per token) to {e36} (full, `6N`) |",
            "| {e4f} FLOPs; {e4h} GPU-hours |",
            "| {e5b} MB; {e5t} ms |",
            "| {e6} Gb/s |",
            "| ≈{e7lat} ms minimum compute latency ({e7sla}% of the payment SLA); ≈{e7pre} A100s "
            "at the published fraud-detection rate of {pre} transactions per second reaching the "
            "model before pre-policy filtering, ≈{e7pos} after ({pos} per second);",
            "{enlaces}",
            "| Services `n` | {fan_n} |",
            "| P(at least one above its p99) | {fan_p} |",
        ],
        [
            "`d_C = 0`",
            "`d_S > 0`",
            "Table 4 of Braithwaite et al. (2025)",
            "Figure 3.",
            "below the Corollary 1 threshold",
            "at 100% of dense BF16 peak",
        ],
    ),
    "THEORY testing status": (
        [
            "synthetic and illustrative, in orders of magnitude; not a replication of nuFormer",
            "window of `L = {L}` events",
            "over a grid of {cells} cells, with `N = {N}` users per cell and {seeds} seeds",
            "{below} of the {comp} comparisons fall below the pre-registered `|Δ| = {limiar}` and "
            "stay outside the sign test, there are {ties} ties, and {disc} of the {tested} tested "
            "comparisons are discordant",
            "agree in {q3_agree} of {cells} cells",
            "a budget of `K = {K}` tokens",
            "two costs `k ∈ {{{k_costs}}}`, `N = {k_N}` users per combination and {k_seeds} seeds, "
            "over {k_cells} cells ({k_sat} saturated, {k_mix} mixed and {k_uns} unsaturated)",
            "The sign criterion passes in {s_agree} of {s_cells} cells ({s_sa} of {s_st} "
            "seed-level signs, {s_ties} ties) and the level criterion in {n_within} of {n_combos} "
            "combinations",
            "improves in all {k_seeds} seeds",
            "worsens in all {k_seeds} seeds",
            "the {k_cells} cells do not discriminate the exponent",
            "give the same sign in all {k_cells}",
            "the worsening observed in all {k_seeds} seeds",
            "`λ_S ∈ ({lam_mix})`",
        ],
        ["items 4 and 5", *(f"Corollary {i}" for i in range(1, 6))],
    ),
    "REPRODUCIBILITY track 2": (
        [
            "(replication: `N = {N}` users per cell, {seeds} seeds, {cells} cells, {combos} source "
            "combinations; token KAT: `N = {k_N}` users per combination, {k_seeds} seeds, "
            "{k_cells} cells, {k_combos} combinations)",
            "compares {n_compared} outputs **byte for byte**",
            "The {n_images} PNG images are compared too",
        ],
        ["Figure 3"],
    ),
    "REPRODUCIBILITY dictionary E7": (
        ["share of the {sla} ms PIX SLA", "({pre} and {pos} per second)"],
        ["at 100% of dense BF16 peak"],
    ),
    "THEORY literal simulation checks": (
        [
            # EXP: exponent of d
            "costs `k ∈ {{{b_exp_costs}}}`",
            "the budget of `K = {b_exp_K}` tokens with a margin of at least `z = {b_exp_z}`; "
            "`N = {b_exp_N}` users per combination and {b_exp_seeds} seeds",
            "{b_exp_tabela}",
            "EXS (sign): {b_exs_agree} of {b_exs_cells} cells agree with the theory "
            "({b_exs_sa} of {b_exs_st} seed-level signs, {b_exs_ties} ties, {b_exs_disc} "
            "discordant). EXN (level of the difference): {b_exn_within} of {b_exn_cells} cells "
            "within the frozen per-cell `tolΔ`, with deviation `abs(Δ̄ − ΔAUC)`; largest ratio "
            "{b_exn_max}.",
            "ratio p/q outside [{b_c_lo}, {b_c_hi}] (family C) or exponent `p` outside "
            "[{b_d_lo}, {b_d_hi}] (family D)",
            # OCC: occupancy against rate weighting
            "checked by literal simulation on a {b_occ_main}-cell family in both directions",
            "Budget of `K = {b_occ_K}` tokens",
            "costs `k ∈ {{{b_occ_costs}}}`, `N = {b_occ_N}` users per combination and "
            "{b_occ_seeds} seeds, over {b_occ_cells} cells",
            "(`z(R) ≥ {b_occ_z}`)",
            "The verdict family has {b_occ_main} cells, {b_occ_up} in which adding `S` improves "
            "the AUC and {b_occ_down} in which it worsens it; {b_occ_l} threshold cells are "
            "reported apart",
            "| {b_occ_s_agree} of {b_occ_s_cells} cells agree with occupancy weighting; "
            "{b_occ_sa} of {b_occ_st} seed-level signs; {b_occ_ties} ties; {b_occ_disc} "
            "discordant |",
            "| {b_occ_n_within} of {b_occ_n_combos} combinations; largest absolute deviation "
            "{b_occ_n_dev} AUC |",
            "| {b_occ_l_agree} of {b_occ_l_cells} agree |",
            "agreement in the verdict family excludes `α < {b_a_main}`, and with the threshold "
            "cells `α < {b_a_all}` (truncated, not rounded)",
            "predicts the opposite of occupancy in {b_ev_opp} of the {b_occ_cells} cells and is "
            "refuted in all {b_ev_ref}",
            # CMP: event fusion
            "| CMP-S — sign and `3·SE` of the signed contrasts | {b_cmp_agree} of {b_cmp_total} "
            "agree; {b_cmp_sa} of {b_cmp_st} seed-level signs; {b_cmp_ties} ties; {b_cmp_disc} "
            "discordant; {b_cmp_nosig} without significance |",
            "| CMP-0 — exact null `RF − RS` in cell {b_cmp0_cell} | within "
            "`tol_0 = {b_cmp_tol0}` |",
            "| CMP-N — level within the tolerance of the fluid form | {b_cmp_n_within} of "
            "{b_cmp_n_total} combinations; largest absolute deviation {b_cmp_n_dev} AUC |",
            "| CMP-T — ceiling of the fused arms (outside the verdict) | {b_cmp_t_ok} of "
            "{b_cmp_t_total} |",
            # C5: quotas
            "Budget of `K = {b_c5_K}` tokens, whole events, costs `k ∈ {{{b_c5_costs}}}`, "
            "`N = {b_c5_N}` users per cell and {b_c5_seeds} seeds, {b_c5_cells} cells",
            "seed by seed ({b_c5_anc_eq} of {b_c5_anc_rows})",
            "Sign (C5-O): {b_c5_o} of {b_c5_o} strict comparisons, {b_c5_o_ties} ties. Size "
            "(C5-G): {b_c5_g} of {b_c5_g} within `tol_X = {b_c5_tolx}`, {b_c5_g_nopower} without "
            "power. Level (C5-N): {b_c5_n} of {b_c5_n} (cell, policy) pairs, largest deviation "
            "{b_c5_n_dev} AUC.",
            "(RHO − FIXc = {b_c5_fix_mean}, predicted {b_c5_fix_pred})",
            "(change in AUC exactly {b_c5_rho_change} in {b_c5_rho_zero} of {b_c5_seeds} seeds), "
            "while the recency cut loses {b_c5_rec_loss} AUC (predicted {b_c5_rec_pred}, the harm "
            "of Corollary 1)",
            "`τ = {b_c5_tau}`",
            "Recency minus nominal-`ρ` quotas: {b_c5_dec1_mean} (fluid prediction "
            "{b_c5_dec1_pred}); age-aware minus nominal-`ρ` quotas: {b_c5_dec2_mean} (fluid "
            "prediction {b_c5_dec2_pred}); same sign in {b_c5_dec_seeds} of {b_c5_seeds} seeds",
            "is RHO − REC in KNP1 ({b_c5_knp1_mean} against {b_c5_knp1_pred}) and in NUL1 "
            "({b_c5_nul1_mean} against {b_c5_nul1_pred}), about four paired standard errors "
            "estimated from {b_c5_seeds} seeds",
            "{b_c5_tabela}",
        ],
        [
            "(exponent 2 analytic",
            "`α = 1` is occupancy, `α = 0` is rate",
            "`α > 1` is not tested",
            "(Dantzig, 1957)",
            "`k_max − 1`",
            "unit test UT-2",
            *(f"Corollary {i}" for i in range(1, 6)),
        ],
    ),
    "README workflow B": (
        [
            "| EXP — exponent of d in the per-token separability | {b_exs_agree} of {b_exs_cells} "
            "cells agree in sign ({b_exs_sa} of {b_exs_st} seed-level signs, {b_exs_ties} ties, "
            "{b_exs_disc} discordant); level of the difference within the frozen tolerance in "
            "{b_exn_within} of {b_exn_cells} |",
            "| OCC — occupancy against rate weighting | {b_occ_s_agree} of {b_occ_s_cells} verdict "
            "cells agree ({b_occ_sa} of {b_occ_st} seed-level signs, {b_occ_ties} ties, "
            "{b_occ_disc} discordant); level within tolerance in {b_occ_n_within} of "
            "{b_occ_n_combos} combinations; threshold cells {b_occ_l_agree} of {b_occ_l_cells} "
            "agree, outside the verdict |",
            "| CMP — event fusion | {b_cmp_agree} of {b_cmp_total} signed contrasts agree "
            "({b_cmp_sa} of {b_cmp_st} seed-level signs, {b_cmp_ties} ties, {b_cmp_disc} "
            "discordant); exact null within its tolerance; level within tolerance in "
            "{b_cmp_n_within} of {b_cmp_n_total} combinations |",
            "| C5 — quotas against the recency cut | anchors {b_c5_anc_eq} of {b_c5_anc_rows}; "
            "sign {b_c5_o} of {b_c5_o} strict comparisons, {b_c5_o_ties} ties; size {b_c5_g} of "
            "{b_c5_g} within the frozen tolerance, {b_c5_g_nopower} without power; level "
            "{b_c5_n} of {b_c5_n}; Consequence sub-test and decay boundary pass |",
        ],
        [*(f"Corollary {i}" for i in range(1, 6))],
    ),
}


def _plano(texto: str) -> str:
    """Drop blockquote markers, blank HTML, link targets and path code spans; collapse spaces."""

    def em_branco(m: re.Match) -> str:
        """Blank the match, keeping its length."""
        return " " * len(m.group(0))

    texto = re.sub(r"^> ?", "", texto, flags=re.M)
    texto = TAG_HTML.sub(em_branco, texto)
    texto = ALVO_DE_LINK.sub(em_branco, texto)
    texto = SPAN_DE_CODIGO.sub(
        lambda m: em_branco(m) if PARECE_CAMINHO.search(m.group(0)) else m.group(0), texto
    )
    return " ".join(texto.split())


def _entre(texto: str, inicio: str, fim: str) -> str:
    """Return the text from ``inicio`` up to, not including, ``fim``; empty if one is missing."""
    i = texto.find(inicio)
    j = texto.find(fim, i + 1) if i >= 0 else -1
    return texto[i:j] if 0 <= i < j else ""


def _potencia(x: float) -> str:
    """Render ``9.9e20`` as ``9.9 × 10²⁰``."""
    mantissa, expoente = f"{x:.1e}".split("e")
    return f"{mantissa} × 10{str(int(expoente)).translate(SOBRESCRITO)}"


def _json(rel: str) -> dict:
    """Load a JSON file of the repository."""
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


def _run_all():
    """Import ``run_all.py`` from the repository root (the root is not on ``sys.path``)."""
    spec = importlib.util.spec_from_file_location("run_all", RAIZ / "run_all.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _valores() -> dict:
    """Render every value the documents quote, read from the file that holds it."""
    run_all = _run_all()
    r = _json("output/results.json")
    rep, kat, e = r["replication"], r["token_kat"], r["estimates"]
    grade = _json("data/kat_token_grid.json")
    entradas = _json("configs/estimates_inputs.json")
    prereg = (RAIZ / "data/prereg/01-displacement-replication.md").read_text(encoding="utf-8")
    ci = (RAIZ / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    with (RAIZ / "output/kat_token/celulas.csv").open(encoding="utf-8", newline="") as f:
        combos_kat = {row["combo"] for row in csv.DictReader(f)}
    limiar = re.search(r"max\((\d+),(\d+); 3·SE\)", prereg)
    celulas = grade["celulas"]
    regimes = [c["bloco"] for c in celulas]
    custos = sorted({s["k"] for c in celulas for g in ("R", "S") for s in c[g].values()})
    lam_misto = [c["S"][s]["lam"] for c in celulas if c["bloco"] == "misto" for s in c["S"]]
    tabelas = r["tables"]
    enlaces = "\n".join(
        f"| {x['enlace'].replace('intra-no', 'intra-node')} | {x['t_allreduce_ddp_ms']} "
        f"| {x['t_allreduce_fsdp_ms']} | {x['razao_ddp_sobre_computo']} |"
        for x in tabelas["enlaces_allreduce"]
    )
    return {
        "cells": rep["cells"],
        "N": f"{rep['N']:,}",
        "seeds": rep["seeds"],
        "disc": rep["q2_discordant"],
        "tested": f"{rep['q2_tested']:,}",
        "comp": f"{rep['q2_comparisons']:,}",
        "below": rep["q2_below_threshold"],
        "ties": rep["q2_ties"],
        "q1_pairs": rep["q1_pairs_tested"],
        "q1_viol": rep["q1_violations"],
        "q3_pat": rep["q3_sign_pattern_cells"],
        "an_pat": rep["analytic_sign_pattern_cells"],
        "q3_ord": rep["q3_full_order_cells"],
        "an_ord": rep["analytic_full_order_cells"],
        "q3_agree": rep["q3_agreement_with_analytic"],
        "combos": len(displacement.COMBOS),
        "L": displacement.L_JANELA,
        "limiar": f"{limiar.group(1)}.{limiar.group(2)}" if limiar else "?",
        "s_agree": kat["kt_s_agree"],
        "s_cells": kat["kt_s_cells"],
        "s_sa": kat["kt_s_seed_signs_agree"],
        "s_st": kat["kt_s_seed_signs_total"],
        "s_ties": kat["kt_s_ties"],
        "s_disc": kat["kt_s_discordant"],
        "n_within": kat["kt_n_within"],
        "n_combos": kat["kt_n_combos"],
        "n_exc": kat["kt_n_exceedances"],
        "n_dev": f"{kat['kt_n_max_abs_deviation']:.4f}",
        "k_N": f"{kat['N']:,}",
        "k_seeds": kat["seeds"],
        "k_cells": len(celulas),
        "k_sat": regimes.count("saturado"),
        "k_mix": regimes.count("misto"),
        "k_uns": regimes.count("nao_saturado"),
        "k_costs": ", ".join(str(k) for k in custos),
        "k_costs_word": EXTENSO[len(custos)],
        "k_combos": len(combos_kat),
        "K": grade["K"],
        "lam_mix": ", ".join(str(x) for x in lam_misto),
        "e1c": f"{e['E1_txn_ctx_compacto']:.0f}",
        "e1t": int(e["E1_txn_ctx_texto"]),
        "e1r": f"{e['E1_razao']:.1f}",
        "e2u": f"{e['E2_usuarios_por_gpu_s']:.1f}",
        "e2a": f"{e['E2_utilizacao_a100']:.3f}",
        "e2l300": f"{e['E2_utilizacao_l4_300']:.2f}",
        "e2l150": f"{e['E2_utilizacao_l4_150']:.2f}",
        "e3lora": f"{e['E3_utilizacao_4N_lora']:.3f}",
        "e36": f"{e['E3_utilizacao_6N']:.3f}",
        "e4f": _potencia(e["E4_flops_pretreino"]),
        "e4h": f"{e['E4_gpu_horas_h100']:.1f}",
        "e5b": f"{e['E5_bytes_gradiente'] / 1e6:.0f}",
        "e5t": f"{e['E5_t_computo_passo_s'] * 1000:.0f}",
        "e6": f"{e['E6_vazao_media_gbps']:.2f}",
        "e7lat": f"{e['E7_latencia_min_computo_ms']:.0f}",
        "e7sla": f"{100 * e['E7_fracao_sla_pix']:.1f}",
        "e7pre": f"{e['E7_a100_pico_pre_filtro']:.0f}",
        "e7pos": f"{e['E7_a100_pico_pos_filtro']:.1f}",
        "pre": f"{entradas['eventos_pre_filtro_tps']['value']:,}",
        "pos": entradas["eventos_pos_filtro_tps"]["value"],
        "sla": entradas["sla_pix_ms"]["value"],
        "enlaces": enlaces,
        "fan_n": " | ".join(x["servicos"] for x in tabelas["fanout_cauda"]),
        "fan_p": " | ".join(x["prob_ao_menos_um_acima_do_p99"] for x in tabelas["fanout_cauda"]),
        "python": _json("env.json")["python"]["version"],
        "ci": " and ".join(
            re.findall(r'"(\d+\.\d+)"', re.search(r"python-version: \[(.*)\]", ci)[1])
        ),
        "n_compared": EXTENSO[len(run_all.COMPARADOS)],
        "n_images": EXTENSO[len(run_all.IMAGENS)],
        "_limiar_achado": limiar is not None,
        **_valores_workflow_b(r),
    }


def _custos(grade: dict) -> str:
    """Return the distinct event costs of a grid as ``"14, 55"``."""
    return ", ".join(
        str(k)
        for k in sorted(
            {s["k"] for c in grade["celulas"] for g in ("R", "S") for s in c[g].values()}
        )
    )


def _sinal(x: float) -> int:
    """Return the sign of ``x`` as -1, 0 or +1."""
    return (x > 0) - (x < 0)


def _valores_workflow_b(r: dict) -> dict:
    """Render the values quoted by the workflow-B sections of ``README.md`` and ``docs/THEORY.md``.

    Every value comes from a family block of ``output/results.json`` (itself derived from the
    sealed ``resumo.json`` of the family) or from the frozen grid of the family.

    Parameters
    ----------
    r : dict
        Content of ``output/results.json``.

    Returns
    -------
    dict
        Values keyed by the ``b_`` placeholders of the workflow-B templates of ``MODELOS``.
    """
    exp, occ, cmp_, c5 = r["exponent"], r["occupancy"], r["fusion"], r["quotas"]
    g_exp = _json("data/exponent_grid.json")
    g_occ = _json("data/occupancy_grid.json")
    g_c5 = _json("data/quotas_grid.json")
    rival = {"baixo": "d/k", "alto": "d³/k"}
    lado = {"baixo": "low", "alto": "high"}
    efeito = {1: "improves", -1: "worsens"}
    tabela_exp = "\n".join(
        f"| `{cel['id']}` | {c['family']}, {lado[c['side']]} | {rival[c['side']]} | "
        f"{efeito[c['theory_sign']]} | {c['predicted']:+.4f} | {c['empirical']:+.4f} "
        f"({c['se']:.4f}) | {c['dev_over_tol']:.2f} |"
        for cel in g_exp["celulas"]
        for c in [exp["cells"][cel["id"]]]
    )
    ivl = exp["implied_interval"]
    cmp_c = {k: c5["comparisons"][k] for k in ("DEC1 REC-RHO", "DEC1 RHOidade-RHO")}
    politicas = g_c5["politicas"]
    linhas_c5 = [
        "| "
        + cel["id"]
        + " | "
        + " | ".join(
            "{exact:.5f} / {mean:.5f}".format(**c5["levels"][f"{cel['id']} {p}"]) for p in politicas
        )
        + " | — |"
        for cel in g_c5["celulas"]
        if "tau" not in cel
    ]
    dec = c5["decay_report_only"]
    linhas_c5.append(
        "| DEC1 (fluid) | "
        + " | ".join(
            "{fluid:.5f} / {mean:.5f}".format(**dec[p]) if p in dec else "—"
            for p in (*politicas, "RHOidade")
        )
        + " |"
    )
    rho = c5["consequence"]["RHO"]["seed_changes"]
    rec = c5["consequence"]["REC"]
    return {
        "b_exp_costs": _custos(g_exp),
        "b_exp_K": g_exp["K"],
        "b_exp_z": f"{g_exp['z_minimo_regime']:g}",
        "b_exp_N": f"{exp['N']:,}",
        "b_exp_seeds": exp["seeds"],
        "b_exp_tabela": tabela_exp,
        "b_exs_agree": exp["exs_agree"],
        "b_exs_cells": exp["exs_cells"],
        "b_exs_sa": exp["exs_seed_signs_agree"],
        "b_exs_st": exp["exs_seed_signs_total"],
        "b_exs_ties": exp["exs_ties"],
        "b_exs_disc": exp["exs_discordant"],
        "b_exn_within": exp["exn_within"],
        "b_exn_cells": exp["exn_cells"],
        "b_exn_max": f"{exp['exn_max_dev_over_tol']:.2f}",
        "b_c_lo": f"{ivl['C_p_over_q'][0]:.3f}",
        "b_c_hi": f"{ivl['C_p_over_q'][1]:.3f}",
        "b_d_lo": f"{ivl['D_p'][0]:.3f}",
        "b_d_hi": f"{ivl['D_p'][1]:.3f}",
        "b_occ_main": occ["occ_s_cells"],
        "b_occ_K": g_occ["K"],
        "b_occ_costs": _custos(g_occ),
        "b_occ_N": f"{occ['N']:,}",
        "b_occ_seeds": occ["seeds"],
        "b_occ_cells": occ["cells"],
        "b_occ_z": f"{g_occ['z_minimo_regime']:g}",
        "b_occ_up": occ["occ_s_improves"],
        "b_occ_down": occ["occ_s_worsens"],
        "b_occ_l": occ["occ_l_cells"],
        "b_occ_s_agree": occ["occ_s_agree"],
        "b_occ_s_cells": occ["occ_s_cells"],
        "b_occ_sa": occ["occ_s_seed_signs_agree"],
        "b_occ_st": occ["occ_s_seed_signs_total"],
        "b_occ_ties": occ["occ_s_ties"],
        "b_occ_disc": occ["occ_s_discordant"],
        "b_occ_n_within": occ["occ_n_within"],
        "b_occ_n_combos": occ["occ_n_combos"],
        "b_occ_n_dev": f"{occ['occ_n_max_abs_deviation']:.4f}",
        "b_occ_l_agree": occ["occ_l_agree"],
        "b_occ_l_cells": occ["occ_l_cells"],
        "b_a_main": f"{occ['alpha_lower_bound_verdict']:.3f}",
        "b_a_all": f"{occ['alpha_lower_bound_with_threshold']:.3f}",
        "b_ev_opp": occ["per_event_rule_opposite_cells"],
        "b_ev_ref": occ["per_event_rule_refuted_cells"],
        "b_cmp_agree": cmp_["cmp_s_agree"],
        "b_cmp_total": cmp_["cmp_s_contrasts"],
        "b_cmp_sa": cmp_["cmp_s_seed_signs_agree"],
        "b_cmp_st": cmp_["cmp_s_seed_signs_total"],
        "b_cmp_ties": cmp_["cmp_s_ties"],
        "b_cmp_disc": cmp_["cmp_s_discordant"],
        "b_cmp_nosig": cmp_["cmp_s_without_significance"],
        "b_cmp0_cell": cmp_["cmp_0_cell"],
        "b_cmp_tol0": cmp_["cmp_0_tol"],
        "b_cmp_n_within": cmp_["cmp_n_within"],
        "b_cmp_n_total": cmp_["cmp_n_combos"],
        "b_cmp_n_dev": f"{cmp_['cmp_n_max_abs_deviation']:.4f}",
        "b_cmp_t_ok": cmp_["cmp_t_arms"] - cmp_["cmp_t_exceedances"],
        "b_cmp_t_total": cmp_["cmp_t_arms"],
        "b_c5_K": c5["K"],
        "b_c5_costs": _custos(g_c5),
        "b_c5_N": f"{c5['N']:,}",
        "b_c5_seeds": c5["seeds"],
        "b_c5_cells": len(g_c5["celulas"]),
        "b_c5_anc_eq": c5["anchors_equal"],
        "b_c5_anc_rows": c5["anchors_rows"],
        "b_c5_o": c5["c5_o_comparisons"],
        "b_c5_o_ties": c5["c5_o_ties"],
        "b_c5_g": c5["c5_g_comparisons"],
        "b_c5_tolx": c5["tol_X"],
        "b_c5_g_nopower": c5["c5_g_without_power"],
        "b_c5_n": c5["c5_n_levels"],
        "b_c5_n_dev": f"{c5['c5_n_max_abs_deviation']:.5f}",
        "b_c5_fix_mean": f"{c5['comparisons']['FIX1 RHO-FIXc']['mean']:+.4f}",
        "b_c5_fix_pred": f"{c5['comparisons']['FIX1 RHO-FIXc']['predicted']:+.4f}",
        "b_c5_rho_change": f"{max(abs(x) for x in rho):g}",
        "b_c5_rho_zero": sum(x == 0 for x in rho),
        "b_c5_rec_loss": f"{-rec['mean']:.4f}",
        "b_c5_rec_pred": f"{-rec['predicted']:.4f}",
        "b_c5_tau": next(cel["tau"] for cel in g_c5["celulas"] if "tau" in cel),
        "b_c5_dec1_mean": f"{cmp_c['DEC1 REC-RHO']['mean']:+.4f}",
        "b_c5_dec1_pred": f"{cmp_c['DEC1 REC-RHO']['predicted']:+.4f}",
        "b_c5_dec2_mean": f"{cmp_c['DEC1 RHOidade-RHO']['mean']:+.4f}",
        "b_c5_dec2_pred": f"{cmp_c['DEC1 RHOidade-RHO']['predicted']:+.4f}",
        "b_c5_dec_seeds": min(
            sum(s == _sinal(c["predicted"]) for s in c["seed_signs"]) for c in cmp_c.values()
        ),
        "b_c5_knp1_mean": f"{c5['comparisons']['KNP1 RHO-REC']['mean']:+.4f}",
        "b_c5_knp1_pred": f"{c5['comparisons']['KNP1 RHO-REC']['predicted']:+.4f}",
        "b_c5_nul1_mean": f"{c5['comparisons']['NUL1 RHO-REC']['mean']:+.4f}",
        "b_c5_nul1_pred": f"{c5['comparisons']['NUL1 RHO-REC']['predicted']:+.4f}",
        "b_c5_tabela": "\n".join(linhas_c5),
    }


def _secoes(textos: dict[str, str]) -> dict[str, str]:
    """Cut the scoped sections out of the flattened documents."""
    readme = _plano(textos["README.md"])
    theory = _plano(textos["docs/THEORY.md"])
    repro = _plano(textos["REPRODUCIBILITY.md"])
    glance = _entre(readme, "| Displacement replication |", "| Estimates |")
    return {
        "README callout": _entre(readme, "**Finding.**", "This repository is the companion"),
        "README at a glance": glance + " " + _entre(readme, "| Environment |", "## Quick start"),
        "README results": _entre(readme, "## Results", "### Case-study figures"),
        "THEORY testing status": _entre(theory, "## What is tested by", "- **Analytic only.**"),
        "REPRODUCIBILITY track 2": _entre(repro, "Regenerates every output", "Expected tail"),
        "REPRODUCIBILITY dictionary E7": _entre(repro, "`fracao_sla_pix`:", "| `enlace`"),
        "THEORY literal simulation checks": _entre(
            theory, "## Checked by literal simulation (workflow B)", "## Novelty"
        ),
        "README workflow B": _entre(
            readme, "### Pre-registered simulation checks (workflow B)", "## What is and isn't"
        ),
    }


def divergencias(textos: dict[str, str]) -> list[str]:
    """Return every problem of the scoped sections: a missing phrase or an unbacked number.

    Parameters
    ----------
    textos : dict of str to str
        Full text of each document of ``DOCS``, keyed by its path relative to the repository.

    Returns
    -------
    list of str
        Human-readable problems; empty when every quoted number is backed by its source.
    """
    valores = _valores()
    problemas = []
    if not valores["_limiar_achado"]:
        problemas.append("pre-registration 01: threshold `max(0,005; 3·SE)` not found")
    secoes = _secoes(textos)
    for nome, (modelos, estruturais) in MODELOS.items():
        secao = secoes[nome]
        if not secao:
            problemas.append(f"{nome}: section markers not found")
            continue
        cobertos = []
        frases = [linha for m in modelos for linha in m.format(**valores).split("\n")]
        for frase in frases:
            achados = [m.span() for m in re.finditer(re.escape(frase), secao)]
            if not achados:
                problemas.append(f"{nome}: expected phrase missing: {frase!r}")
            cobertos += achados
        for frase in estruturais:
            cobertos += [m.span() for m in re.finditer(re.escape(frase), secao)]
        for m in NUMERO.finditer(secao):
            if not any(a <= m.start() and m.end() <= b for a, b in cobertos):
                contexto = secao[max(0, m.start() - 40) : m.end() + 40]
                problemas.append(
                    f"{nome}: number not backed by a source: {m.group(0)!r} in {contexto!r}"
                )
    return problemas


def _textos() -> dict[str, str]:
    """Read the three documents."""
    return {d: (RAIZ / d).read_text(encoding="utf-8") for d in DOCS}


def test_numeros_citados_nos_documentos_batem_com_as_fontes():
    """Check every scoped section of the documentation against the files its numbers come from."""
    assert divergencias(_textos()) == []


def test_sinais_das_celulas_mistas_citados_na_teoria():
    """Check that MIX1 improves and MIX2 worsens in every sealed seed, as the theory quotes."""
    kat = _json("output/kat_token/resumo.json")
    sinais = {c["celula"]: c["sinais_por_semente"] for c in kat["avaliar_kat"]["por_celula"]}
    n = len(kat["sementes"])
    assert sinais["MIX1"] == [1] * n
    assert sinais["MIX2"] == [-1] * n


def test_credito_da_figura_1_bate_com_o_ledger():
    """Check the Figure 1 capture hashes and Wayback snapshot in the README against the ledger."""
    with (RAIZ / "data/claims-ledger.csv").open(encoding="utf-8", newline="") as f:
        linhas = {row["id"]: row for row in csv.DictReader(f)}
    readme = _plano((RAIZ / "README.md").read_text(encoding="utf-8"))
    for rotulo, id_linha in (
        ("adoption", "case-fig-adocao"),
        ("sequence-data sources", "case-fig-fontes"),
    ):
        locator = linhas[id_linha]["locator"]
        captura = re.search(r"captura sha256:([0-9a-f]{64})", locator)
        instantaneo = re.search(r"web\.archive\.org/web/(\d{14})", locator)
        assert captura and instantaneo, id_linha
        assert f"{rotulo}, `{captura.group(1)}`" in readme, id_linha
        assert f"snapshot {instantaneo.group(1)}" in readme, id_linha


# --- numbers added to the documentation outside the scoped sections (2026-09-27) -----------------

# Date of the preprint version pinned in ``configs/estimates_inputs.json``: arXiv submission history
# of arXiv:2507.23267, "[v2] Mon, 10 Aug 2026 08:33:06 UTC". The version number and the year are
# read from the sealed input below; the day is declared here, with that source.
DATA_DA_VERSAO_DO_PREPRINT = "2026-08-10"

# statement anchor of docs/THEORY.md -> how the README "Claimed" paragraph names it
NOMES_NO_README = {
    "proposition-1": "Proposition 1",
    "corollary-1": "Corollary 1",
    "mixed-regime": "the mixed-regime Observation",
    "corollary-3": "Corollary 3",
}


def _achatado(rel: str) -> str:
    """Read a document with every run of whitespace collapsed to one space."""
    return " ".join((RAIZ / rel).read_text(encoding="utf-8").split())


def test_theta_definido_no_readme_como_na_teoria():
    """Check that the README defines θ where it first uses it, with the formula of the theory."""
    theory = (RAIZ / "docs/THEORY.md").read_text(encoding="utf-8")
    achada = re.findall(r"^(θ = .+?)\.?$", theory, flags=re.M)
    assert len(achada) == 1, f"docs/THEORY.md: the formula of θ is not stated once: {achada}"
    formula = achada[0]
    readme = _achatado("README.md")
    definicao = readme.find(f"`{formula}`")
    assert definicao >= 0, (
        f"README.md: θ is not defined with the formula of the theory, {formula!r}"
    )
    assert 0 <= definicao - readme.index("θ") < 200, "README.md: θ is used before its definition"


def test_versao_do_preprint_declarada_nos_documentos():
    """Check the version of the nuFormer preprint that README and THEORY declare as read.

    Every declaration is read, not just one: each must name the pinned version and its date, and
    each document keeps its number of declarations (the introduction and the anchor references of
    the README, the reference list of THEORY), so a declaration reworded out of the pattern fails.
    """
    fonte = _json("configs/estimates_inputs.json")["fonte_nuformer"]
    fixada = re.search(r"arXiv:(\d{4}\.\d{5})v(\d+) \((\d{4})\)", fonte)
    assert fixada, f"configs/estimates_inputs.json: no pinned preprint version in {fonte!r}"
    ident, versao, ano = fixada.groups()
    assert DATA_DA_VERSAO_DO_PREPRINT.startswith(ano), (DATA_DA_VERSAO_DO_PREPRINT, ano)
    for doc, vezes in (("README.md", 2), ("docs/THEORY.md", 1)):
        texto = _achatado(doc)
        achadas = re.findall(r"read in version (\d+), submitted on (\d{4}-\d{2}-\d{2})", texto)
        assert len(achadas) == vezes, f"{doc}: {len(achadas)} declarations of the version read"
        assert set(achadas) == {(versao, DATA_DA_VERSAO_DO_PREPRINT)}, (
            f"{doc}: declares {sorted(set(achadas))}, "
            f"the pinned version is {(versao, DATA_DA_VERSAO_DO_PREPRINT)}"
        )
        assert f"arXiv:{ident}v{versao}" in texto, f"{doc}: missing arXiv:{ident}v{versao}"
        outras = set(re.findall(rf"arXiv:{re.escape(ident)}v(\d+)", texto)) - {versao}
        assert not outras, f"{doc}: cites another version of the preprint: {sorted(outras)}"


def test_paragrafo_claimed_do_readme_nomeia_as_provas_da_teoria():
    """Check the README "Claimed" paragraph: it names as proved exactly the statements with a proof.

    Every number in the paragraph must sit inside a structural phrase (a statement label or the
    Dantzig citation), and the list of proved statements must match the sections of
    ``docs/THEORY.md`` that carry a ``*Proof.*``.
    """
    theory = (RAIZ / "docs/THEORY.md").read_text(encoding="utf-8")
    partes = re.split(r'^<a id="([^"]+)"></a>$', theory, flags=re.M)
    provadas = [
        a for a, corpo in zip(partes[1::2], partes[2::2], strict=True) if "*Proof.*" in corpo
    ]
    assert sorted(provadas) == sorted(NOMES_NO_README), f"docs/THEORY.md: proofs in {provadas}"
    lista = (
        ", ".join(NOMES_NO_README[a] for a in provadas[:-1])
        + f" and {NOMES_NO_README[provadas[-1]]}"
    )
    secao = _entre(
        _plano((RAIZ / "README.md").read_text(encoding="utf-8")), "**Claimed.**", "**Not claimed.**"
    )
    assert secao, "README.md: 'Claimed' paragraph markers not found"
    assert f"{lista}, each with the proof given there" in secao, (
        f"README.md: proved list is not {lista!r}"
    )
    estruturais = [
        *NOMES_NO_README.values(),
        *(f"Corollary {i}" for i in range(1, 6)),
        "(Dantzig, 1957)",
    ]
    cobertos = [m.span() for f in estruturais for m in re.finditer(re.escape(f), secao)]
    soltos = [
        m.group(0)
        for m in NUMERO.finditer(secao)
        if not any(a <= m.start() and m.end() <= b for a, b in cobertos)
    ]
    assert soltos == [], f"README.md 'Claimed': number not backed by a structural phrase: {soltos}"


# --- the seal quoted by the changelog (2026-09-27) ------------------------------------------------

RESELO = re.compile(
    r"re-sealed in place[^`]*\(staging\): root `[0-9a-f]+…` → `([0-9a-f]{64})` \((\d+) sealed files"
)


def test_changelog_cita_o_selo_atual():
    """Check that the newest re-seal entry of the changelog quotes the committed seal.

    The root and the number of sealed files are read from ``runs/v0.1.0/manifest.json``. After a
    re-seal this test fails until the changelog entry quotes the new root, so the changelog never
    points to a seal that is no longer committed.
    """
    manifest = _json("runs/v0.1.0/manifest.json")
    folhas = sum(s["nfiles"] for s in manifest["stages"])
    entrada = RESELO.search(_achatado("CHANGELOG.md"))
    assert entrada, "CHANGELOG.md: no re-seal entry with a full root and a count of sealed files"
    raiz, n = entrada.group(1), int(entrada.group(2))
    assert raiz == manifest["root"], (
        f"CHANGELOG.md quotes root {raiz}, the seal is {manifest['root']}"
    )
    assert n == folhas, f"CHANGELOG.md quotes {n} sealed files, the manifest seals {folhas}"


def test_licenca_e_zenodo_concordam_com_o_notice():
    """Lock the licence summaries to ``NOTICE``: no third-party material is redistributed.

    ``NOTICE`` lists third-party material only under the heading "Third-party material — NOT
    redistributed here": no heading lists redistributed third-party files and no file is left to
    "its own terms". Every summary of the licence (the README ``## License`` section and the
    ``notes`` of ``.zenodo.json``) must say that third-party sources are "not redistributed", in a
    sentence with no exception. A ``NOTICE`` that lists redistributed files again, or a summary
    that names an exception, fails here until ``NOTICE`` and both summaries are rewritten together.
    """
    notice = _achatado("NOTICE")
    assert "Third-party material — NOT redistributed here" in notice, (
        "NOTICE: the heading of the third-party material that is not redistributed is missing"
    )
    for proibido in ("Third-party material redistributed here", "own terms"):
        assert proibido not in notice, (
            f"NOTICE: {proibido!r}, but the licence summaries say that no third-party material is "
            "redistributed"
        )
    resumos = {
        "README.md ## License": _entre(
            _achatado("README.md"), "## License", "## Anchor references"
        ),
        ".zenodo.json notes": _json(".zenodo.json")["notes"],
    }
    excecao = re.compile(r"\b(?:except|but|apart from|other than|own terms)\b", re.I)
    for onde, texto in resumos.items():
        assert texto, f"{onde}: not found"
        frases = [f for f in re.split(r"(?<=[.!?])\s+", texto) if "not redistributed" in f]
        assert frases, f"{onde}: no sentence says that third-party sources are not redistributed"
        for frase in frases:
            achado = excecao.search(frase)
            assert not achado, (
                f"{onde}: exception {achado.group(0)!r} in {frase!r}, but NOTICE redistributes no "
                "third-party material"
            )
