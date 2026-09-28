r"""Figure 3 of the synthetic displacement replication.

Pre-registration: ``data/prereg/01-displacement-replication.md``. Reads the sealed replication run
(``output/replication/celulas.csv``) and recomputes NOTHING of the simulation: the analytic
prediction comes from ``displacement`` (Delta^2, AUC, saturation), the style from ``plot_style``
(DejaVu Serif, 300 dpi, PNG without timestamp).

(a) MIXED regime: cell T = 90, lambda = (0.1; 0.3; 3), d = (0.5; 0.15; .): dAUC of adding C as a
    function of d_C for A->AC, B->BC, AB->ABC, with the equilibrium point (brentq root of the
    analytic dAUC).
(b) P1b: context B->BC at T = 365, lambda_B = 0.6 (B alone already saturates): dAUC as a function
    of lambda_C for d_C in {0; 0.1; 0.2}; the sign does not change with lambda_C.

Empirical points: mean of 5 seeds (with C) minus mean of 5 seeds (without C), bar +/- 3 SE with
SE = sqrt(s2_with/5 + s2_without/5), s2 with ddof = 1: the operationalisation of Q2 in the
pre-registration. Points sit at the true x (d_C, lambda_C), with no offset. Hollow circle with the
+/- 3 SE bar drawn on top WITHOUT caps; the half-bar is smaller than the marker radius in all 24
points (measured by the test). Grey "x" = point below the 0.005 threshold (outside the sign test),
the same term as the sealed summary (``abaixo_limiar``).

The JSON sidecar keeps the keys of the frozen implementation (Portuguese names such as
``painel_a``, ``pontos``, ``media_com``); only the value of ``rodape`` is English. The sidecar is
compared number by number with the sealed one; the PNG is not part of that contract.

Run: ``python3 code/figure3.py`` (writes ``fig3_replication.png`` + ``fig3_values.json``).
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

import numpy as np
from matplotlib import patheffects
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, NullLocator
from scipy.optimize import brentq

import displacement as rd
from plot_style import DESTINO, META, RAIZ, plt

CSV_CELULAS = RAIZ / "output" / "replication" / "celulas.csv"
PNG_NOME = "fig3_replication.png"
SIDECAR_NOME = "fig3_values.json"
N_SEMENTES = 5
# Q2 of the pre-registration: outside the test if |dAUC_pred| < max(0.005; 3 SE). The sealed summary
# separates the two causes: < 0.005 = "abaixo_limiar"; otherwise < 3 SE = "empate". Here
# 3 SE <= 0.0025 in all 24 points, so only the first occurs.
LIMIAR_PREV = 0.005
ROTULO_FORA = "outside the sign test"  # legend label of the grey "x"

RODAPE = (
    "Illustrative (orders of magnitude); not a replication of nuFormer. N = 200,000 users per cell."
)
NOTA = (
    "Curve: approximate analytic prediction (expected counts). Point: mean of 5 seeds with C "
    "− mean of 5 without C;\n"
    "bar ± 3·SE, smaller than the marker. Dotted: equilibrium $d_C$* (analytic ΔAUC = 0). "
    "Grey ×: |predicted ΔAUC| < 0.005,\n"
    "outside the sign test. The pre-registered criterion (Q2) is the sign, not the fit."
)

# cell of panel (a): no context saturates WITHOUT C, all saturate WITH C
CEL_A = {"T": 90, "lam": {"A": 0.1, "B": 0.3, "C": 3}, "d": {"A": 0.5, "B": 0.15}}
CONTEXTOS_A = (("A", "AC"), ("B", "BC"), ("AB", "ABC"))
DC_EMP_A = (0, 0.025, 0.05, 0.1, 0.2)
# cell of panel (b): B alone already saturates (lambda_B T = 219 >= 146); lambda_A, d_A only pick
# the CSV row
CEL_B = {"T": 365, "lam": {"A": 0.1, "B": 0.6}, "d": {"A": 0.5, "B": 0.15}}
DC_B = (0, 0.1, 0.2)
LAMC_EMP_B = (1, 3, 6)
LAMC_FAIXA_B = (0.05, 7.0)

# AB->ABC in orange (Dark2), not green: green #5E8C4A against the red of B->BC gave dE = 1.2 under
# deuteranopia (Machado et al., 2009); the orange keeps dE >= 36 in normal vision, deuteranopia
# and protanopia (measured in test_cores_distinguiveis)
COR_A = {"A->AC": "#2F4F7F", "B->BC": "#C0504D", "AB->ABC": "#D95F02"}
# (b): every curve is B->BC, so shades of the SAME red as B->BC in (a), light -> dark with d_C;
# the light shade is >= 3:1 against white, and d_C = 0 is also dashed (a second cue besides colour)
COR_B = {0: "#D9716D", 0.1: "#C0504D", 0.2: "#6E1F1C"}
TRACO_B = {0: "--", 0.1: "-", 0.2: "-"}
COR_FORA = "#333333"  # "x" outside the test: neutral, distinct from the curves that cross it
# hollow circle (separates the point from the curve through it) with the +/- 3 SE bar drawn ON TOP;
# capsize = 0: the half-bar fits inside the circle radius
MARCADOR = {"mfc": "white", "elinewidth": 0.7, "capsize": 0}
# tested -> (shape, ms, mew, fixed colour or None = curve colour); the "x" gets a white halo
FORMA = {True: ("o", 2.8, 0.6, None), False: ("x", 4.2, 1.1, COR_FORA)}


def _chave(sem, com):
    """Return the context key ``"<without>-><with>"``."""
    return f"{sem}->{com}"


def _fmt_num(v, casas=None):
    """Format a number with a decimal point and a typographic minus sign (never ``-0``)."""
    if v == 0:
        v = 0.0  # -0.0 (round of -1e-9) would print "-0"
    txt = f"{v:g}" if casas is None else f"{v:.{casas}f}"
    return txt.replace("-", "−")


# --- analytic prediction (reuses displacement; no new formula here) ----------------------------


def delta_auc_analitica(sem, com, lam, d, T):
    """Return the predicted dAUC of adding C: AUC(with) - AUC(without), h = min(T, L/sum(lam))."""
    return rd.auc_analitica(com, lam, d, T) - rd.auc_analitica(sem, lam, d, T)


def equilibrio_a(sem, com):
    """Return d_C* of panel (a): root of the analytic dAUC in d_C in [0; 0.25] (brentq)."""
    lam, T = CEL_A["lam"], CEL_A["T"]
    # the closed form of the root only holds in this regime; guard against a wrong cell
    if rd.saturada(sem, lam, T) or not rd.saturada(com, lam, T):
        raise ValueError(f"{sem}->{com}: célula do painel (a) fora do regime misto")
    return brentq(
        lambda dc: delta_auc_analitica(sem, com, lam, {**CEL_A["d"], "C": dc}, T),
        0.0,
        0.25,
        xtol=1e-15,
        rtol=1e-15,
    )


def curva_a(sem, com, n=501):
    """Return (x, y) of the analytic dAUC curve of panel (a) over d_C in [0; 0.25]."""
    x = np.linspace(0.0, 0.25, n)
    y = np.array(
        [
            delta_auc_analitica(sem, com, CEL_A["lam"], {**CEL_A["d"], "C": dc}, CEL_A["T"])
            for dc in x
        ]
    )
    return x, y


def curva_b(d_c, n=400):
    """Return (x, y) of the analytic dAUC curve of panel (b) over lambda_C (log-spaced)."""
    x = np.geomspace(*LAMC_FAIXA_B, n)
    y = np.array(
        [
            delta_auc_analitica(
                "B", "BC", {**CEL_B["lam"], "C": lc}, {**CEL_B["d"], "C": d_c}, CEL_B["T"]
            )
            for lc in x
        ]
    )
    return x, y


# --- empirical data -----------------------------------------------------------------------------


def carregar(csv_path=CSV_CELULAS):
    """Load the sealed CSV as ``{(T, lam_A, lam_B, lam_C, d_A, d_B, d_C, combo): {seed: ...}}``.

    Each seed maps to ``(auc, i_celula)``.
    """
    tabela = {}
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            chave = tuple(
                float(r[c]) for c in ("T", "lam_A", "lam_B", "lam_C", "d_A", "d_B", "d_C")
            )
            tabela.setdefault(chave + (r["combo"],), {})[int(r["semente"])] = (
                float(r["auc"]),
                int(r["i_celula"]),
            )
    return tabela


def _sementes(tabela, T, lam, d, combo):
    """Return the AUCs of seeds 0..4 of one (cell, combination) and the cell index."""
    chave = (
        float(T),
        float(lam["A"]),
        float(lam["B"]),
        float(lam["C"]),
        float(d["A"]),
        float(d["B"]),
        float(d["C"]),
        combo,
    )
    linhas = tabela.get(chave, {})
    if sorted(linhas) != list(range(N_SEMENTES)):
        raise ValueError(
            f"{chave}: esperadas sementes 0..{N_SEMENTES - 1}, achadas {sorted(linhas)}"
        )
    aucs = [linhas[s][0] for s in range(N_SEMENTES)]
    return aucs, linhas[0][1]


def ponto_empirico(tabela, sem, com, lam, d, T):
    """Return one plotted point.

    Means, s2 (ddof = 1), SE of the difference, empirical and analytic dAUC, and whether the
    point enters the sign test.
    """
    a_sem, i_sem = _sementes(tabela, T, lam, d, sem)
    a_com, i_com = _sementes(tabela, T, lam, d, com)
    if i_sem != i_com:
        raise ValueError(f"combos {sem}/{com} vieram de células diferentes ({i_sem} × {i_com})")
    m_sem, m_com = statistics.mean(a_sem), statistics.mean(a_com)
    s2_sem, s2_com = statistics.variance(a_sem), statistics.variance(a_com)
    ep = math.sqrt(s2_com / N_SEMENTES + s2_sem / N_SEMENTES)
    prev = delta_auc_analitica(sem, com, lam, d, T)
    limiar = max(LIMIAR_PREV, 3 * ep)
    return {
        "contexto": _chave(sem, com),
        "i_celula": i_sem,
        "d_C": d["C"],
        "lam_C": lam["C"],
        "media_sem": m_sem,
        "media_com": m_com,
        "s2_sem": s2_sem,
        "s2_com": s2_com,
        "ep": ep,
        "delta_emp": m_com - m_sem,
        "delta_analitico": prev,
        "limiar_teste": limiar,
        "testado": abs(prev) >= limiar,
    }


def calcular_valores(csv_path=CSV_CELULAS):
    """Return everything the figure plots, as a JSON-serialisable dict (the sidecar)."""
    tabela = carregar(csv_path)
    pontos_a = []
    for sem, com in CONTEXTOS_A:
        for dc in DC_EMP_A:
            pontos_a.append(
                ponto_empirico(tabela, sem, com, CEL_A["lam"], {**CEL_A["d"], "C": dc}, CEL_A["T"])
            )
    pontos_b = []
    for dc in DC_B:
        for lc in LAMC_EMP_B:
            lam = {**CEL_B["lam"], "C": lc}
            if not rd.saturada("B", lam, CEL_B["T"]):
                raise ValueError("célula do painel (b): B sozinha não satura, P1b não se aplica")
            pontos_b.append(
                ponto_empirico(tabela, "B", "BC", lam, {**CEL_B["d"], "C": dc}, CEL_B["T"])
            )
    return {
        "rodape": RODAPE,
        "L": rd.L_JANELA,
        "n_sementes": N_SEMENTES,
        "painel_a": {
            "T": CEL_A["T"],
            "lam": CEL_A["lam"],
            "d": CEL_A["d"],
            "equilibrios": {_chave(s, c): equilibrio_a(s, c) for s, c in CONTEXTOS_A},
            "pontos": pontos_a,
        },
        "painel_b": {
            "T": CEL_B["T"],
            "lam": CEL_B["lam"],
            "d": CEL_B["d"],
            "contexto": "B->BC",
            "d_C_curvas": list(DC_B),
            "faixa_lam_C": list(LAMC_FAIXA_B),
            "pontos": pontos_b,
        },
    }


# --- figure -------------------------------------------------------------------------------------


def _eixo_estilo(ax):
    """Apply the shared axis style (zero line, light y grid, no top/right spines)."""
    ax.axhline(0, color="#555555", lw=0.6)
    ax.grid(axis="y", lw=0.4, color="#DDDDDD")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: _fmt_num(round(v, 6))))
    ax.set_ylabel("ΔAUC from adding C", fontsize=8)
    ax.tick_params(labelsize=7.5)


def _pontos(ax, pts, x, cor, obstaculos):
    """Draw the empirical points of one curve and register the artists the layout test measures.

    Tested points are hollow circles in the curve colour; points below the threshold (outside
    the sign test) are a grey "x" with a white halo, above the curve and the dotted line.
    """
    for testado, (fmt, ms, mew, cor_fixa) in FORMA.items():
        sel = [p for p in pts if p["testado"] is testado]
        if sel:
            c = cor_fixa or cor
            marca, pontas, barras = ax.errorbar(
                [p[x] for p in sel],
                [p["delta_emp"] for p in sel],
                yerr=[3 * p["ep"] for p in sel],
                fmt=fmt,
                ms=ms,
                mew=mew,
                color=c,
                **MARCADOR,
            ).lines
            z = 3 if testado else 4
            marca.set_zorder(z)
            for art in (*pontas, *barras):
                art.set_zorder(z + 0.5)
            if not testado:
                halo = [patheffects.withStroke(linewidth=2.2, foreground="white")]
                marca.set_path_effects(halo)
            obstaculos["marcadores"].append(marca)
            obstaculos["pontas"] += list(pontas)
            obstaculos["barras"] += list(barras)


def montar(valores):
    """Build the figure; return ``(fig, textos, obstaculos)``.

    ``textos`` are the named text artists the layout test measures; ``obstaculos`` are the curves,
    dotted lines and markers that no named text may cover.
    """
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(6.5, 4.1))
    va, vb = valores["painel_a"], valores["painel_b"]
    obstaculos = {"curvas": [], "pontilhados": [], "marcadores": [], "pontas": [], "barras": []}

    # (a) mixed regime, continuous d_C
    anot = []
    for sem, com in CONTEXTOS_A:
        k = _chave(sem, com)
        x, y = curva_a(sem, com)
        obstaculos["curvas"] += ax_a.plot(
            x, y, color=COR_A[k], lw=0.9, label=k.replace("->", " → ")
        )
        _pontos(ax_a, [p for p in va["pontos"] if p["contexto"] == k], "d_C", COR_A[k], obstaculos)
        obstaculos["pontilhados"].append(
            ax_a.axvline(va["equilibrios"][k], color=COR_A[k], lw=0.8, ls=":", zorder=1.5)
        )
    _eixo_estilo(ax_a)
    ax_a.set_xlim(-0.01, 0.26)
    ylo, yhi = ax_a.get_ylim()
    ax_a.set_ylim(ylo - 0.07, yhi)  # room for the legend below the curves (lower right)
    for (
        sem,
        com,
    ) in CONTEXTOS_A:  # labels at the top: the band d_C in [0.04; 0.12] has no curve there
        k = _chave(sem, com)
        eq = va["equilibrios"][k]
        anot.append(
            ax_a.text(
                eq + 0.002,
                yhi - 0.005,
                f"$d_C$* = {_fmt_num(eq, 4)}",
                rotation=90,
                fontsize=7,
                color=COR_A[k],
                ha="left",
                va="top",
            )
        )
    ax_a.xaxis.set_major_locator(FixedLocator([0, 0.05, 0.1, 0.15, 0.2, 0.25]))
    ax_a.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _fmt_num(round(v, 6))))
    ax_a.set_xlabel("mean attribute shift of C, $d_C$", fontsize=8)
    ax_a.set_title(
        "(a) Mixed regime: unsaturated without C,\nsaturated with C; "
        "$T$ = 90; $\\lambda_A$ = 0.1; $\\lambda_B$ = 0.3;\n"
        "$\\lambda_C$ = 3; $d_A$ = 0.5; $d_B$ = 0.15",
        fontsize=8,
    )
    fora = Line2D(
        [],
        [],
        ls="none",
        marker=FORMA[False][0],
        ms=FORMA[False][1],
        mew=FORMA[False][2],
        color=COR_FORA,
        label=ROTULO_FORA,
    )
    leg_a = ax_a.legend(
        handles=[*ax_a.get_legend_handles_labels()[0], fora],
        fontsize=7,
        frameon=False,
        loc="lower right",
        labelspacing=0.3,
        handlelength=1.5,
        borderaxespad=0.2,
    )

    # (b) P1b: continuous lambda_C, window saturated with and without C
    for dc in DC_B:
        x, y = curva_b(dc)
        rotulo = f"$d_C$ = {_fmt_num(dc)}"
        obstaculos["curvas"] += ax_b.plot(
            x, y, color=COR_B[dc], ls=TRACO_B[dc], lw=0.9, label=rotulo
        )
        _pontos(ax_b, [p for p in vb["pontos"] if p["d_C"] == dc], "lam_C", COR_B[dc], obstaculos)
    _eixo_estilo(ax_b)
    ax_b.set_xscale("log")
    ax_b.xaxis.set_major_locator(FixedLocator([0.05, 0.1, 0.3, 1, 3, 7]))
    ax_b.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _fmt_num(v)))
    ax_b.xaxis.set_minor_locator(NullLocator())
    ax_b.xaxis.set_minor_formatter(NullFormatter())
    ax_b.set_xlim(0.045, 8)
    ax_b.set_xlabel("event rate of C, $\\lambda_C$ (per day)", fontsize=8)
    ax_b.set_title(
        "(b) Saturated with and without C:\nB → BC; $T$ = 365; $\\lambda_B$ = 0.6;\n"
        "$d_B$ = 0.15 (equilibrium $d_C$* = 0.15)",
        fontsize=8,
    )
    leg_b = ax_b.legend(fontsize=7, frameon=False, loc="lower left")

    fig.tight_layout(rect=(0, 0.119, 1, 1), w_pad=1.5)
    nota = fig.text(0.5, 0.076, NOTA, ha="center", va="center", fontsize=7)
    rodape = fig.text(0.5, 0.016, RODAPE, ha="center", va="center", fontsize=7, style="italic")

    textos = {
        "titulo_a": ax_a.title,
        "titulo_b": ax_b.title,
        "xlabel_a": ax_a.xaxis.label,
        "xlabel_b": ax_b.xaxis.label,
        "ylabel_a": ax_a.yaxis.label,
        "ylabel_b": ax_b.yaxis.label,
        "legenda_a": leg_a,
        "legenda_b": leg_b,
        "nota": nota,
        "rodape": rodape,
        **{f"equilibrio_{i}": t for i, t in enumerate(anot)},
    }
    return fig, textos, obstaculos


def gerar(destino: Path = DESTINO, csv_path=CSV_CELULAS):
    """Write the PNG and the JSON sidecar (sorted keys, no date or time); return both paths."""
    valores = calcular_valores(csv_path)
    destino.mkdir(parents=True, exist_ok=True)
    fig, _, _ = montar(valores)
    png = destino / PNG_NOME
    fig.savefig(png, metadata=META)  # no bbox_inches: the PNG has exactly the measured area
    plt.close(fig)
    sidecar = destino / SIDECAR_NOME
    sidecar.write_text(
        json.dumps(valores, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return png, sidecar


if __name__ == "__main__":
    for f in gerar():
        print(f)
