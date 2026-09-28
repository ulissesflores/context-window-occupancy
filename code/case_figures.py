"""Case-study figures (English labels): adoption over time and the architecture synthesis.

``fig1_adoption.png``: adoption funnel and sequence-data sources over the first eight months.
The counts in ``configs/adoption_counts.csv`` were read from the bar charts of Udagawa (2025),
recovered from the Wayback Machine snapshot 20250613214328; the bars sit on integer gridlines, so
the reading is exact.

``fig2_architecture.png``: the author's synthesis of the architecture as a flow, with the three
network planes named by function (training, batch, synchronous). Every drawn line has a source,
listed in ``tests/test_case_figures.py``: a label read from a diagram of the case, the wording of
a text source, an input of ``configs/estimates_inputs.json`` or the author's synthesis. Dashed
links and the dashed box are not described in the sources: the precomputed-score link is inferred
by the author, the Kafka (CDC) -> Model Server link joins two posts, neither of which connects the
two components, and the customer app -> API entry is the author's reconstruction. The tools box
lists the two tool panels of the case diagram without giving any tool a role, as the diagram does.

Deterministic: fixed sizes, no timestamp in the PNG metadata (``plot_style.META``).
"""

from __future__ import annotations

import csv
from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from plot_style import DESTINO, META, RAIZ, plt

CSV_ADOCAO = RAIZ / "configs" / "adoption_counts.csv"
COR = {
    "dado": "#E8EEF7",
    "gpu": "#FBE9D8",
    "gov": "#E6F2E6",
    "serv": "#F3E6F3",
    "rt": "#F2F2F2",
    "ferr": "#FFFFFF",
}

# Figure 2 geometry, in inches: the axes span the whole canvas, so one data unit is one inch
LARGURA, ALTURA = 5.55, 5.35
TITULO_PT, CORPO_PT = 7.6, 6.4
COLUNAS = {1: (0.05, 1.30), 2: (1.55, 1.15), 3: (2.90, 1.30), 4: (4.40, 1.10)}  # (x, width)
LINHAS = {1: (4.05, 1.20), 2: (2.45, 1.25), 3: (1.00, 1.05)}  # (y of the bottom edge, height)

# box -> (column, row, title, body lines, colour, dashed border)
CAIXAS = {
    "fontes": (
        1,
        1,
        "Data sources",
        (
            "card transactions",
            "transfers",
            "loans",
            "Bureau Data",
            "Open Finance",
            "app events (planned)",
        ),
        "dado",
        False,
    ),
    "sequencias": (
        2,
        1,
        "Sequences",
        (
            "Raw Data Store",
            "compact tokenisation",
            "(~14 tokens per",
            "transaction)",
            "validation; data as",
            "of the score date",
        ),
        "dado",
        False,
    ),
    "gpu": (
        3,
        1,
        "GPU cluster (Ray)",
        (
            "causal pre-training (NTP)",
            "~500 B tokens",
            "330 M parameters",
            "Joint Fusion: DCNv2 +",
            "PLR + LoRA (r = 64)",
            "DDP/FSDP on H100/H200",
        ),
        "gpu",
        False,
    ),
    "governanca": (
        4,
        1,
        "Governance",
        ("challenger × baseline", "LightGBM, same", "data; approval"),
        "gov",
        False,
    ),
    "ferramentas": (
        1,
        2,
        "Tools (case diagram)",
        (
            "Internal Tools:",
            "Model Catalog",
            "Reporting Tool",
            "OSS Tools:",
            "Ray · vLLM",
            "PyTorch Lightning",
            "MLflow · Dagster",
        ),
        "ferr",
        False,
    ),
    "monitoramento": (
        2,
        2,
        "Monitoring",
        ("field and behavioural", "drift; records vs.", "historical snapshots"),
        "dado",
        False,
    ),
    "inferencia": (
        3,
        2,
        "Daily inference",
        (
            "batch over the whole",
            "customer base",
            "100 M+ customers",
            "~5 h on 60 A100",
            "(or 150–300 L4 nodes)",
        ),
        "serv",
        False,
    ),
    "motores": (
        4,
        2,
        "Decision engines",
        ("credit limit,", "loans, income,", "spending (Table 2 of", "Braithwaite et al.)"),
        "serv",
        False,
    ),
    "app": (
        1,
        3,
        "Customer app → API",
        ("PIX or card", "transaction (author's", "reconstruction)"),
        "rt",
        True,
    ),
    "eventos": (
        2,
        3,
        "Real-time events",
        ("Kafka (CDC)", "pre-policy filter:", "2,800 → 20 events/s"),
        "rt",
        False,
    ),
    "model_server": (
        3,
        3,
        "Model Server",
        ("Clojure + Python", "short features (hot", "store) + long (batch)", "PIX SLA: 700 ms"),
        "rt",
        False,
    ),
}
# network plane -> (box it marks, colour, legend text)
PLANOS = (
    (
        "training",
        "gpu",
        "gpu",
        "NVLink intra-node; InfiniBand/RoCE across nodes (gradient all-reduce)",
    ),
    ("batch", "sequencias", "dado", "storage → preprocessing → GPUs (bulk data transfer)"),
    ("synchronous", "model_server", "rt", "fan-out to services, latency tail, 700 ms budget"),
)
# arrow: (from box, side, fraction along the side), (to box, side, fraction), line style
SETAS = (
    (("fontes", "r", 0.5), ("sequencias", "l", 0.5), "-"),
    (("sequencias", "r", 0.5), ("gpu", "l", 0.5), "-"),
    (("gpu", "r", 0.5), ("governanca", "l", 0.5), "-"),
    (("governanca", "b", 0.35), ("inferencia", "t", 0.75), "-"),
    (("sequencias", "b", 0.5), ("monitoramento", "t", 0.5), "-"),
    (("inferencia", "r", 0.5), ("motores", "l", 0.5), "-"),
    (("inferencia", "b", 0.5), ("model_server", "t", 0.5), "--"),
    (("app", "r", 0.5), ("eventos", "l", 0.5), "--"),
    (("eventos", "r", 0.5), ("model_server", "l", 0.5), "--"),
)
# free text: (x, y, text, horizontal alignment, size, style)
ROTULOS = (
    (4.45, 3.87, "approved model", "left", 6.8, "italic"),
    (3.65, 2.25, "precomputed score\n(link inferred by the author)", "left", 6.8, "italic"),
    (5.50, 0.76, "dashed = link or component not described in the sources", "right", 6.6, "italic"),
)


def _retangulo(nome: str) -> tuple[float, float, float, float]:
    """Return ``(x, y, width, height)`` of a Figure 2 box, in inches."""
    coluna, linha = CAIXAS[nome][:2]
    (x, w), (y, h) = COLUNAS[coluna], LINHAS[linha]
    return x, y, w, h


def _ponto(nome: str, lado: str, frac: float) -> tuple[float, float]:
    """Return the point at ``frac`` along side ``lado`` (l, r, t, b) of a box."""
    x, y, w, h = _retangulo(nome)
    return {
        "l": (x, y + frac * h),
        "r": (x + w, y + frac * h),
        "t": (x + frac * w, y + h),
        "b": (x + frac * w, y),
    }[lado]


def desenhar_arquitetura(ax) -> dict[str, list]:
    """Draw Figure 2 on ``ax`` (inch coordinates); return ``{box: [patch, title, body, tag?]}``.

    Every text of the figure is an element of ``ax.texts``; the returned mapping says which of
    them belong to which box, so that a test can measure the layout.
    """
    ax.set_xlim(0, LARGURA)
    ax.set_ylim(0, ALTURA)
    ax.axis("off")
    caixas = {}
    for nome, (_, _, titulo, corpo, cor, tracejada) in CAIXAS.items():
        x, y, w, h = _retangulo(nome)
        caixa = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            fc=COR[cor],
            ec="#333333",
            lw=0.9,
            ls="--" if tracejada else "-",
        )
        ax.add_patch(caixa)
        texto_titulo = ax.text(
            x + w / 2,
            y + h - 0.08,
            titulo,
            ha="center",
            va="top",
            fontsize=TITULO_PT,
            fontweight="bold",
        )
        texto_corpo = ax.text(
            x + w / 2,
            y + h - 0.27,
            "\n".join(corpo),
            ha="center",
            va="top",
            fontsize=CORPO_PT,
            linespacing=1.25,
        )
        caixas[nome] = [caixa, texto_titulo, texto_corpo]
    for plano, nome, cor, _ in PLANOS:
        x, y, w, _h = _retangulo(nome)
        caixas[nome].append(
            ax.text(
                x + w - 0.08,
                y + 0.11,
                plano,
                ha="right",
                va="center",
                fontsize=7,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc=COR[cor], ec="#333333", lw=0.7),
            )
        )
    for origem, destino, estilo in SETAS:
        ax.add_patch(
            FancyArrowPatch(
                _ponto(*origem),
                _ponto(*destino),
                arrowstyle="-|>",
                mutation_scale=9,
                lw=0.9,
                ls=estilo,
                color="#333333",
            )
        )
    for x, y, texto, alinhamento, tamanho, estilo in ROTULOS:
        ax.text(x, y, texto, ha=alinhamento, va="center", fontsize=tamanho, style=estilo)

    # legend of the network planes, named by function
    ax.text(0.05, 0.76, "Network planes", fontsize=8.4, fontweight="bold", va="center")
    for i, (plano, _, cor, legenda) in enumerate(PLANOS):
        y = 0.52 - i * 0.20
        ax.add_patch(
            FancyBboxPatch(
                (0.05, y - 0.07),
                0.14,
                0.14,
                boxstyle="round,pad=0.01",
                fc=COR[cor],
                ec="#333333",
                lw=0.6,
            )
        )
        ax.text(0.27, y, f"{plano}: {legenda}", fontsize=7, va="center")
    return caixas


def figura_2():
    """Return ``(figure, boxes)`` with Figure 2 drawn at the resolution of the saved PNG."""
    fig = plt.figure(figsize=(LARGURA, ALTURA), dpi=plt.rcParams["savefig.dpi"])
    return fig, desenhar_arquitetura(fig.add_axes((0, 0, 1, 1)))


def fig_architecture(destino: Path = DESTINO) -> Path:
    """Draw the architecture synthesis with the three network planes; return the PNG path."""
    fig, _ = figura_2()
    destino.mkdir(parents=True, exist_ok=True)
    caminho = destino / "fig2_architecture.png"
    fig.savefig(caminho, bbox_inches="tight", metadata=META)
    plt.close(fig)
    return caminho


def fig_adoption(destino: Path = DESTINO, csv_path: Path = CSV_ADOCAO) -> Path:
    """Draw the adoption funnel and the sequence-data sources per month; return the PNG path."""
    with open(csv_path, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    meses = [f"{row['month'][5:]}/{row['month'][2:4]}" for row in linhas]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.9), sharey=True)
    series1 = [
        ("problems_integrated", "problems integrated", "#9EB3D1"),
        ("baselines_replicated", "baselines replicated", "#5D7FAE"),
        ("challengers_built", "challengers built", "#2F4F7F"),
        ("models_in_production", "models in production", "#C0504D"),
    ]
    series2 = [
        ("sources_ingested", "ingested", "#A9C79B"),
        ("sources_modeled", "modeled", "#5E8C4A"),
        ("sources_productized", "productized", "#2E5220"),
    ]
    for ax, series, titulo in (
        (a1, series1, "(a) Adoption by use case"),
        (a2, series2, "(b) Sequence data sources"),
    ):
        largura = 0.8 / len(series)
        for j, (col, rot, cor) in enumerate(series):
            xs = [i + (j - (len(series) - 1) / 2) * largura for i in range(len(meses))]
            ax.bar(
                xs,
                [int(row[col]) for row in linhas],
                width=largura,
                color=cor,
                label=rot,
                edgecolor="none",
            )
        ax.set_title(titulo, fontsize=9)
        ax.set_xticks(range(len(meses)))
        ax.set_xticklabels(meses, fontsize=7)
        ax.set_yticks(range(0, 11, 2))
        ax.grid(axis="y", lw=0.4, color="#BBBBBB")
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(fontsize=6.6, frameon=False, loc="upper left")
    a1.set_ylabel("count")
    a1.set_xlabel("month/year", fontsize=7.5)
    a2.set_xlabel("month/year", fontsize=7.5)
    fig.tight_layout()
    destino.mkdir(parents=True, exist_ok=True)
    caminho = destino / "fig1_adoption.png"
    fig.savefig(caminho, bbox_inches="tight", metadata=META)
    plt.close(fig)
    return caminho
