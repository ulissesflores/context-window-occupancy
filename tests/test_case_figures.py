"""Lock the counts behind Figure 1 and every drawn text of Figure 2.

Figure 1 (``configs/adoption_counts.csv``): the counts were read from the two bar charts of
Udagawa (2025) in the Wayback Machine snapshot 20250613214328 (credit and capture hashes in
``README.md``). Two independent records must agree: the sealed CSV that the figure plots, and the
ledger rows that record the April 2025 values with the SHA-256 of each chart capture
(``case-fig-adocao``, ``case-fig-fontes``).

Figure 2 (``code/case_figures.py``): every text drawn in the figure (box titles and bodies, the
network-plane tags, arrow labels, legend and footnote) must be a key of ``FONTES_DA_FIGURA_2``
below, and every key must be drawn: a text added or reworded without a source, or a source left
without its text, fails. Each key lists where its content comes from:

- ``("diagram", row)``: a label that appears in no text of the sources, only in a diagram of the
  case; every item of the ledger row's value must be drawn in that text, and the row's locator
  carries the capture hash of the diagram;
- ``("ledger", row, token)``: the token is drawn and is part of the value of that ledger row;
- ``("inputs", ((token, key, scale), ...))``: each quantity is an input of
  ``configs/estimates_inputs.json`` (value divided by scale, written as drawn);
- ``("text", locator)``: wording of a text source that the repository does not redistribute;
- ``("author", reason)``: the author's heading, synthesis or reconstruction; reconstructed links
  and the reconstructed box are drawn dashed, and the footnote says so.

Labels retracted because no source supports them must not come back, in any letter case, in the
drawing or in the module source: a role given to a tool that the case diagram lists without one, a
GPU model that the training section does not name, a registry that the case does not name, the
product "Caixinhas" / "Money Boxes", and the letter markers of the network planes, now named by
function. The layout is measured on the drawn figure: each text inside its box with a margin, the
title clear of the top border, no two texts overlapping, no free text over a box, titles at
7.6 pt or more.
"""

import csv
import json
import re
from itertools import combinations
from pathlib import Path

import case_figures
from plot_style import plt

RAIZ = Path(__file__).resolve().parents[1]
CSV_ADOCAO = RAIZ / "configs" / "adoption_counts.csv"
ENTRADAS = RAIZ / "configs" / "estimates_inputs.json"
LEDGER = RAIZ / "data" / "claims-ledger.csv"
MODULO_DA_FIGURA_2 = RAIZ / "code" / "case_figures.py"

ADOCAO = (
    "problems_integrated",
    "baselines_replicated",
    "challengers_built",
    "models_in_production",
)
FONTES = ("sources_ingested", "sources_modeled", "sources_productized")

# month -> adoption funnel (4 series) + sequence-data sources (3 series), as plotted
ESPERADO = {
    "2024-09": (3, 0, 0, 0, 1, 0, 0),
    "2024-10": (4, 2, 1, 0, 2, 1, 0),
    "2024-11": (4, 3, 2, 0, 3, 2, 0),
    "2024-12": (5, 4, 4, 0, 5, 5, 0),
    "2025-01": (5, 4, 4, 0, 8, 5, 2),
    "2025-02": (6, 5, 5, 1, 8, 5, 5),
    "2025-03": (9, 7, 7, 2, 9, 5, 5),
    "2025-04": (9, 8, 7, 3, 9, 5, 5),
}

NUFORMER = "Braithwaite et al. (2025)"
CASE = "Udagawa (2025)"
MLOPS = "Nubank Editorial (2025), real-time ML post"
FRAUDE = "Nubank Editorial (2024), sequential fraud models Q&A"

# every text drawn in Figure 2, lines joined by a space -> where its content comes from
FONTES_DA_FIGURA_2 = {
    "Data sources": (("author", "heading; the case diagram is titled 'Nubank Data Sources'"),),
    "card transactions transfers loans Bureau Data Open Finance app events (planned)": (
        ("text", f"{NUFORMER}, Appendix A: 'credit card, debit card', 'transfer activity'"),
        ("text", "Foust (2025): 'loan-related transactions'"),
        ("diagram", "case-fig-fontes-bureau"),
        ("diagram", "case-fig-fontes-open-finance"),
        ("text", f"{CASE}: 'we plan to experiment soon with incorporating app event' signals"),
    ),
    "Sequences": (("text", f"{CASE}: 'Sequence Data Preprocessing'"),),
    "Raw Data Store compact tokenisation (~14 tokens per transaction) validation; data as of "
    "the score date": (
        ("diagram", "case-fig-plataforma-raw-data-store"),
        ("inputs", (("14", "tokens_por_txn_compacto", 1),)),
        ("text", f"{CASE}: workflows 'to transform, validate, and monitor sequence data'"),
        ("text", f"{NUFORMER}, Section 4.3: 'presented as they existed at the score date'"),
    ),
    "GPU cluster (Ray)": (
        ("ledger", "case-pilha-ray", "Ray"),
        ("text", f"{CASE}: 'GPU/Heterogeneous Clusters'"),
    ),
    "causal pre-training (NTP) ~500 B tokens 330 M parameters Joint Fusion: DCNv2 + PLR + LoRA "
    "(r = 64) DDP/FSDP on H100/H200": (
        ("inputs", (("500", "tokens_pretreino", 1e9), ("330", "params_modelo", 1e6))),
        ("ledger", "ARX-lora_rank", "64"),
        (
            "text",
            f"{NUFORMER}, Section 3.1: 'clusters of H100 or H200 GPUs using distributed data "
            "parallel or fully sharded training'",
        ),
    ),
    "Governance": (("author", "heading of the challenger-baseline comparison and approval"),),
    "challenger × baseline LightGBM, same data; approval": (
        ("text", f"{CASE}: 'Baselines Replicated', 'Challengers Built', 'Get model approval'"),
        ("text", f"{NUFORMER}, Section 4.1: LightGBM is the production baseline"),
    ),
    "Tools (case diagram)": (("author", "heading of the two tool panels of the case diagram"),),
    "Internal Tools: Model Catalog Reporting Tool OSS Tools: Ray · vLLM PyTorch Lightning MLflow "
    "· Dagster": (
        ("diagram", "case-fig-ferramenta-catalogo"),
        ("diagram", "case-fig-ferramenta-relatorios"),
        ("diagram", "case-pilha-figura-ocr"),
        ("ledger", "case-pilha-ray", "Ray"),
    ),
    "Monitoring": (("text", f"{NUFORMER}, Section 4.3: 'Drift Monitoring'"),),
    "field and behavioural drift; records vs. historical snapshots": (
        (
            "text",
            f"{NUFORMER}, Section 4.3: 'field-level drift', 'behavioral drift', "
            "'historical snapshots'",
        ),
    ),
    "Daily inference": (("text", f"{NUFORMER}, Section 4.3: 'a daily batch job'"),),
    "batch over the whole customer base 100 M+ customers ~5 h on 60 A100 (or 150–300 L4 nodes)": (
        (
            "inputs",
            (
                ("100", "usuarios_inferencia", 1e6),
                ("5", "horas_inferencia", 1),
                ("60", "gpus_inferencia_a100", 1),
                ("150", "nos_inferencia_l4_min", 1),
                ("300", "nos_inferencia_l4_max", 1),
            ),
        ),
    ),
    "Decision engines": (("text", f"{NUFORMER}, Section 4.3: 'serving credit decisions'"),),
    "credit limit, loans, income, spending (Table 2 of Braithwaite et al.)": (
        ("text", f"{NUFORMER}, Table 2: the downstream tasks"),
    ),
    "Customer app → API": (("author", "reconstruction: no source names the entry point"),),
    "PIX or card transaction (author's reconstruction)": (
        ("text", f"{MLOPS}: SLA '700ms for PIX transactions'; a stolen credit card purchase"),
    ),
    "Real-time events": (("text", f"{FRAUDE}: events on a Kafka topic"),),
    "Kafka (CDC) pre-policy filter: 2,800 → 20 events/s": (
        ("text", f"{FRAUDE}: 'a Kafka topic which has all the Change Data Capture (CDC)'"),
        (
            "inputs",
            (("2,800", "eventos_pre_filtro_tps", 1), ("20", "eventos_pos_filtro_tps", 1)),
        ),
    ),
    "Model Server": (("text", f"{MLOPS}: 'Model Server'"),),
    "Clojure + Python short features (hot store) + long (batch) PIX SLA: 700 ms": (
        ("text", f"{MLOPS}: Clojure and Python; short-term 'hot' and long-term batch features"),
        ("inputs", (("700", "sla_pix_ms", 1),)),
    ),
    "training": (("author", "network plane named by function"),),
    "batch": (("author", "network plane named by function"),),
    "synchronous": (("text", f"{MLOPS}: 'Synchronous vs. Asynchronous Processing'"),),
    "approved model": (("text", f"{CASE}: 'Get model approval and deploy them'"),),
    "precomputed score (link inferred by the author)": (("author", "inferred link, dashed"),),
    "dashed = link or component not described in the sources": (("author", "footnote"),),
    "Network planes": (("author", "legend heading"),),
    "training: NVLink intra-node; InfiniBand/RoCE across nodes (gradient all-reduce)": (
        ("author", "network plane reconstructed by the author"),
    ),
    "batch: storage → preprocessing → GPUs (bulk data transfer)": (
        ("author", "network plane reconstructed by the author"),
    ),
    "synchronous: fan-out to services, latency tail, 700 ms budget": (
        ("inputs", (("700", "sla_pix_ms", 1),)),
    ),
}

# retracted: never drawn, never in the module source, in any letter case (pattern, reason)
RETIRADOS = (
    (r"catalogue \(MLflow\)", "the case diagram lists MLflow among the OSS Tools, with no role"),
    (r"reports, Dagster", "the case diagram lists Dagster among the OSS Tools, with no role"),
    (r"A100/H100", "the training section names clusters of H100 or H200 GPUs"),
    (r"\bSCR\b", "the case diagram lists 'Bureau Data'; no source names this registry"),
    (r"Central Bank", "the case diagram lists 'Bureau Data'; no source names this registry"),
    (r"Caixinhas", "no diagram of the case lists this product (Portuguese name)"),
    (r"Money Boxes", "no diagram of the case lists this product (English name)"),
)
MARCADOR_DE_LETRA = re.compile(r"^[ABC](\s|$)")  # the old plane markers and legend prefixes
PLANOS = {"training": "gpu", "batch": "sequencias", "synchronous": "model_server"}
MARGEM_PT, FOLGA_TITULO_PT, TITULO_MIN_PT = 3.0, 3.0, 7.6


def _tabela() -> dict[str, tuple[int, ...]]:
    """Read the sealed counts as ``{month: counts in ESPERADO column order}``."""
    with CSV_ADOCAO.open(encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        assert leitor.fieldnames == ["month", *ADOCAO, *FONTES]
        return {row["month"]: tuple(int(row[c]) for c in (*ADOCAO, *FONTES)) for row in leitor}


def _linha_do_ledger(id_linha: str) -> dict[str, str]:
    """Return one row of the claims ledger by id (a missing row is named, never a traceback)."""
    with LEDGER.open(encoding="utf-8", newline="") as f:
        linhas = [row for row in csv.DictReader(f) if row["id"] == id_linha]
    assert linhas, f"row {id_linha!r} absent from data/claims-ledger.csv"
    assert len(linhas) == 1, f"row {id_linha!r} appears {len(linhas)} times in the ledger"
    return linhas[0]


def _figura_2():
    """Draw Figure 2 as ``fig_architecture`` does; return ``(figure, boxes, texts)``."""
    fig, caixas = case_figures.figura_2()
    fig.canvas.draw()
    textos = {" ".join(t.get_text().split("\n")): t for t in fig.axes[0].texts}
    return fig, caixas, textos


def test_contagens_da_figura_1():
    """Check every plotted count: 8 months x 7 series."""
    assert _tabela() == ESPERADO


def test_abril_2025_bate_com_o_ledger():
    """Check the April 2025 counts against the two ledger rows that recorded them."""
    abril = dict(zip((*ADOCAO, *FONTES), _tabela()["2025-04"], strict=True))
    for id_linha, colunas in (("case-fig-adocao", ADOCAO), ("case-fig-fontes", FONTES)):
        linha = _linha_do_ledger(id_linha)
        assert "abr/2025" in linha["claim"]
        valores = tuple(int(v) for v in linha["valor"].split(" · "))
        assert valores == tuple(abril[c] for c in colunas), id_linha


def test_toda_linha_da_figura_2_tem_fonte():
    """Check that the drawn texts of Figure 2 and the keys of the source table are the same."""
    fig, _, textos = _figura_2()
    plt.close(fig)
    sem_fonte = sorted(set(textos) - set(FONTES_DA_FIGURA_2))
    sem_desenho = sorted(set(FONTES_DA_FIGURA_2) - set(textos))
    assert not sem_fonte, f"Figure 2 draws text with no source in the table: {sem_fonte}"
    assert not sem_desenho, f"source-table entries that Figure 2 does not draw: {sem_desenho}"


def test_rotulos_da_figura_2_tem_linha_no_ledger():
    """Check each diagram label and ledger token against its row, and that it is drawn."""
    for texto, fontes in FONTES_DA_FIGURA_2.items():
        for fonte in fontes:
            if fonte[0] == "diagram":
                linha = _linha_do_ledger(fonte[1])
                assert "captura sha256:" in linha["locator"], f"{fonte[1]}: no capture hash"
                for item in linha["valor"].split(" | "):
                    assert item.casefold() in texto.casefold(), (
                        f"{fonte[1]}: ledger label {item!r} is not drawn in {texto!r}"
                    )
                    assert item.casefold() in linha["claim"].casefold(), (
                        f"{fonte[1]}: the claim does not name {item!r}"
                    )
            elif fonte[0] == "ledger":
                _, id_linha, token = fonte
                assert token in _linha_do_ledger(id_linha)["valor"], f"{id_linha}: not {token!r}"
                assert token in texto, f"{id_linha}: {token!r} is not drawn in {texto!r}"


def test_numeros_da_figura_2_sao_entradas_das_estimativas():
    """Check each quantity drawn in Figure 2 against its input in estimates_inputs.json."""
    entradas = json.loads(ENTRADAS.read_text(encoding="utf-8"))
    for texto, fontes in FONTES_DA_FIGURA_2.items():
        for fonte in fontes:
            if fonte[0] != "inputs":
                continue
            for token, chave, escala in fonte[1]:
                valor = entradas[chave]["value"] / escala
                assert valor == int(valor) and f"{int(valor):,}" == token, (
                    f"{chave}: input {entradas[chave]['value']} / {escala:g} is not {token}"
                )
                assert re.search(rf"(?<![\d,.]){re.escape(token)}(?![\d,.])", texto), (
                    f"{chave}: {token} is not drawn in {texto!r}"
                )


def test_rotulos_retirados_fora_da_figura_2():
    """Check that no retracted label and no letter plane marker is drawn in Figure 2."""
    fig, _, textos = _figura_2()
    plt.close(fig)
    for padrao, motivo in RETIRADOS:
        desenhados = [t for t in textos if re.search(padrao, t, re.I)]
        assert not desenhados, f"Figure 2 draws {desenhados} ({motivo})"
    linhas = [linha for t in fig.axes[0].texts for linha in t.get_text().split("\n")]
    letras = [linha for linha in linhas if MARCADOR_DE_LETRA.match(linha)]
    assert not letras, f"Figure 2 names a network plane by letter, not by function: {letras}"


def test_nome_sem_fonte_publica_fora_do_modulo_da_figura_2():
    """Check that the retracted labels are absent from the figure module, in any letter case."""
    fonte = MODULO_DA_FIGURA_2.read_text(encoding="utf-8")
    presentes = [(p, m) for p, m in RETIRADOS if re.search(p, fonte, re.I)]
    assert not presentes, f"retracted label back in code/case_figures.py: {presentes}"


def test_planos_de_rede_nomeados_por_funcao():
    """Check that each plane tag is drawn inside the box it marks and opens its legend line."""
    fig, caixas, textos = _figura_2()
    plt.close(fig)
    for plano, nome in PLANOS.items():
        assert textos[plano] in caixas[nome], f"tag {plano!r} is not in box {nome!r}"
        assert sum(t.startswith(f"{plano}: ") for t in textos) == 1, f"legend of {plano!r}"


def _extensao(texto, renderizador):
    """Return the drawn extent of a text, including its rounded frame when it has one."""
    extensao = texto.get_window_extent(renderizador)
    moldura = texto.get_bbox_patch()
    if moldura is None:
        return extensao
    return extensao.union([extensao, moldura.get_window_extent(renderizador)])


def _sobrepoe(a, b) -> bool:
    """Return True if two display extents overlap (touching edges do not count)."""
    return a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1


def _problemas_de_layout(fig, caixas) -> list[str]:
    """Measure Figure 2 as drawn; return every layout problem, in points."""
    r = fig.canvas.get_renderer()
    pt = 72 / fig.dpi
    problemas = []
    donos = {}
    for nome, (caixa, titulo, *resto) in caixas.items():
        borda = caixa.get_window_extent(r)
        for texto in (titulo, *resto):
            donos[texto] = nome
            e = _extensao(texto, r)
            margem = min(e.x0 - borda.x0, borda.x1 - e.x1, e.y0 - borda.y0, borda.y1 - e.y1) * pt
            if margem < MARGEM_PT:
                problemas.append(f"{nome}: {texto.get_text()!r} margin {margem:.1f} pt")
        folga = (borda.y1 - titulo.get_window_extent(r).y1) * pt
        if folga < FOLGA_TITULO_PT:
            problemas.append(f"{nome}: title {folga:.1f} pt from the top border")
        if titulo.get_fontsize() < TITULO_MIN_PT:
            problemas.append(f"{nome}: title at {titulo.get_fontsize()} pt")
    textos = fig.axes[0].texts
    for a, b in combinations(textos, 2):
        if _sobrepoe(_extensao(a, r), _extensao(b, r)):
            problemas.append(f"texts overlap: {a.get_text()!r} x {b.get_text()!r}")
    for texto in textos:
        for nome, (caixa, *_) in caixas.items():
            if donos.get(texto) != nome and _sobrepoe(
                _extensao(texto, r), caixa.get_window_extent(r)
            ):
                problemas.append(f"{texto.get_text()!r} lies over box {nome!r}")
    for (n1, (c1, *_)), (n2, (c2, *_)) in combinations(caixas.items(), 2):
        if _sobrepoe(c1.get_window_extent(r), c2.get_window_extent(r)):
            problemas.append(f"boxes overlap: {n1!r} x {n2!r}")
    return problemas


def test_layout_da_figura_2():
    """Check the measured layout: margins, title clearance, no overlap, title size."""
    fig, caixas, _ = _figura_2()
    problemas = _problemas_de_layout(fig, caixas)
    plt.close(fig)
    assert not problemas, "Figure 2 layout: " + "; ".join(problemas)
