#!/usr/bin/env python3
"""Generate every figure of the paper, in English, into ``output/figures/`` (or ``--destino``).

Claim map (figure -> what it supports -> where the numbers live -> what asserts them)
-------------------------------------------------------------------------------------
``fig1_adoption.png`` (paper Figure 1)
    Adoption of the foundation-model platform per month: use-case funnel (problems integrated ->
    baselines replicated -> challengers built -> models in production) and sequence-data sources
    (ingested -> modeled -> productized). Numbers: ``configs/adoption_counts.csv``, read from the
    bar charts of Udagawa (2025), sealed in the ``prereg`` stage of ``configs/stages.json``.
    Asserted by ``tests/test_case_figures.py`` (the whole table, and the April 2025 counts against
    the ledger rows ``case-fig-adocao`` and ``case-fig-fontes``). Descriptive only.
``fig2_architecture.png`` (paper Figure 2)
    The author's synthesis of the architecture as a flow, with its three network planes named by
    function (training fabric, batch data throughput, synchronous path). Quantities printed in the
    boxes are inputs of ``configs/estimates_inputs.json`` (each tagged FACT/SPEC/ASSUMPTION with a
    locator), except the LoRA rank (``r = 64``), which is the ledger row ``ARX-lora_rank``. Dashed
    links and the dashed box are not described in the sources and the figure says so: the
    precomputed-score link is an inference of the author, the Kafka (CDC) -> Model Server link is
    a reconstruction that joins two posts (ledger row ``INF-caminho-online-recon``), and the
    customer app -> API entry is the author's reconstruction. Monitoring (field and behavioural
    drift, records compared with historical snapshots) and the training on clusters of H100 or
    H200 GPUs are wording of the nuFormer preprint. Five component names appear in no text of the
    sources, only in diagrams of the case (Udagawa, 2025), each a ledger row whose locator carries
    the capture hash of its diagram: "Raw Data Store" (``case-fig-plataforma-raw-data-store``),
    "Open Finance" (``case-fig-fontes-open-finance``), "Bureau Data" (``case-fig-fontes-bureau``),
    "Model Catalog" and "Reporting Tool" (``case-fig-ferramenta-catalogo``,
    ``case-fig-ferramenta-relatorios``, panel "Internal Tools"); the panel "OSS Tools" is the row
    ``case-pilha-figura-ocr``. The tools box lists both panels without giving any tool a role, as
    the case diagram does. Asserted by ``tests/test_case_figures.py``: every drawn text has an
    entry in its source table and every entry is drawn; each diagram label, ledger token and input
    is checked against its row or input; retracted labels stay out of the drawing and the module;
    the planes are named by function; the layout is measured (margins, title clearance, overlap).
``fig3_replication.png`` (paper Figure 3)
    The synthetic displacement replication: (a) in the mixed regime, the sign of adding C flips at
    the analytic equilibrium d_C* of each context; (b) in the saturated regime, the sign does not
    depend on the rate of C (P1b). Numbers: ``output/figures/fig3_values.json`` (equilibria under
    ``painel_a.equilibrios``; every plotted point with its means, variances and SE). Asserted by
    ``tests/test_figure3.py`` (closed-form equilibria to 4 decimals, empirical sign = analytic
    sign in every tested point, exactly one point below the 0.005 threshold, byte-identical
    sidecar) and, upstream, by the Q2 criterion in ``output/replication/resumo.json``.

Usage: ``python3 scripts/make_figures.py [--destino DIR] [--csv REPLICATION_CSV]``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "code"))

import case_figures  # noqa: E402
import figure3  # noqa: E402


def main(argv=None) -> int:
    """Write the three figures (and the Figure 3 sidecar); return 0."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--destino", type=Path, default=figure3.DESTINO)
    ap.add_argument("--csv", type=Path, default=figure3.CSV_CELULAS)
    args = ap.parse_args(argv)
    for caminho in (
        case_figures.fig_adoption(args.destino),
        case_figures.fig_architecture(args.destino),
        *figure3.gerar(args.destino, args.csv),
    ):
        print(caminho.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
