#!/usr/bin/env python3
"""Run the whole pipeline: results -> tests -> provenance.

Modes
-----
``python3 run_all.py`` (no flag): the FULL run with the pre-registered parameters (replication
    N = 200,000 users x 5 seeds x 720 cells x 7 combinations; token KAT N = 100,000 x 5 seeds x 8
    cells x 2 combinations; and the four workflow-B families with the parameters of their frozen
    grids: exponent of ``d`` (``data/exponent_grid.json``), occupancy against rate weighting
    (``data/occupancy_grid.json``), event fusion (``data/fusion_grid.json``) and quotas
    (``data/quotas_grid.json``)). Every output is regenerated into ``output/replicated/`` (never
    into a sealed path) and compared BYTE FOR BYTE with the sealed outputs under ``output/``; then
    the test suite runs and the provenance chain is verified. Exit 0 only if all three pass. If a
    sealed output is missing, the run names it and stops before regenerating anything; a
    regenerated output that is missing is named too, never a traceback.
``python3 run_all.py --publish``: the same full run written to the SEALED paths
    (``output/replication/``, ``output/kat_token/``, ``output/exponent/``, ``output/occupancy/``,
    ``output/fusion/``, ``output/quotas/``, ``output/estimativas.json``, ``output/tables/``,
    ``output/figures/``, ``output/results.json``), followed by the tests, the seal
    (``make_provenance.py``) and the verification. The seal is written only if every step and the
    tests passed; otherwise it is skipped and counted as a failure. It is the only step that writes
    a sealed path.
``python3 run_all.py --smoke``: small N for continuous integration, written to ``output/smoke/``
    (never a sealed path); then the tests and the verification of the committed seal.

The write targets of the replicated and smoke modes are disjoint from every sealed glob of
``configs/stages.json``; ``tests/test_stages_disjoint.py`` asserts it.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PY = sys.executable
SAIDA = RAIZ / "output"
# Child processes write no bytecode: a ``__pycache__`` inside the tree would carry the absolute
# path of the machine that ran it (``.gitignore`` excludes it; this keeps the tree clean).
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
REPLICATED_DIR = "output/replicated"
SMOKE_DIR = "output/smoke"

# regenerated outputs compared byte for byte with the sealed ones (paths relative to a base dir)
COMPARADOS = (
    "replication/celulas.csv",
    "replication/resumo.json",
    "kat_token/celulas.csv",
    "kat_token/resumo.json",
    "exponent/celulas.csv",
    "exponent/resumo.json",
    "occupancy/celulas.csv",
    "occupancy/resumo.json",
    "fusion/celulas.csv",
    "fusion/resumo.json",
    "quotas/celulas.csv",
    "quotas/resumo.json",
    "estimativas.json",
    "tables/enlaces_allreduce.csv",
    "tables/fanout_cauda.csv",
    "figures/fig3_values.json",
    "results.json",
)
# rendered images depend on the font rasteriser: compared, but a difference only warns
IMAGENS = (
    "figures/fig1_adoption.png",
    "figures/fig2_architecture.png",
    "figures/fig3_replication.png",
)

FULL = {"replication": ["--N", "200000", "--sementes", "5"], "kat": [], "familias": []}
SMOKE = {
    "replication": ["--N", "2000", "--sementes", "5"],
    "kat": ["--N", "2000", "--bloco-usuarios", "1000"],
    "familias": ["--N", "2000", "--bloco-usuarios", "1000"],
}
# workflow-B families: (step name, output subdirectory, command without --out). The full run uses
# the frozen grids unchanged; the smoke run overrides only N and the block size. The number of
# processes is left at each runner's default: it never enters a random stream.
FAMILIAS = (
    ("EXP family", "exponent", [PY, "code/run_grid.py", "--grid", "data/exponent_grid.json"]),
    ("OCC family", "occupancy", [PY, "code/run_grid.py", "--grid", "data/occupancy_grid.json"]),
    ("CMP family", "fusion", [PY, "code/run_fusion.py"]),
    ("C5 family", "quotas", [PY, "code/run_quotas.py"]),
)


def alvos(base: str) -> list[str]:
    """Return every file (relative to the repository root) that a run into ``base`` writes."""
    return [f"{base}/{rel}" for rel in (*COMPARADOS, *IMAGENS)]


def _rodar(passo: str, cmd: list[str]) -> int:
    """Run one step as a subprocess from the repository root; print its duration; return exit."""
    t0 = time.perf_counter()
    rc = subprocess.run(cmd, cwd=RAIZ, env=ENV).returncode
    print(f"[{'OK' if rc == 0 else 'FAIL'}] {passo} ({time.perf_counter() - t0:.0f} s)", flush=True)
    return rc


def gerar(base: Path, params: dict) -> int:
    """Regenerate every output into ``base``; return the number of failed steps."""
    passos = [
        ("estimates", [PY, "code/estimates.py", "--saida", str(base)]),
        (
            "replication",
            [
                PY,
                "code/run_replication.py",
                *params["replication"],
                "--saida",
                str(base / "replication"),
            ],
        ),
        (
            "token KAT",
            [PY, "code/run_token_kat.py", *params["kat"], "--saida", str(base / "kat_token")],
        ),
        *(
            (nome, [*cmd, *params["familias"], "--out", str(base / sub)])
            for nome, sub, cmd in FAMILIAS
        ),
        (
            "figures",
            [
                PY,
                "scripts/make_figures.py",
                "--destino",
                str(base / "figures"),
                "--csv",
                str(base / "replication" / "celulas.csv"),
            ],
        ),
        ("results", [PY, "code/results.py", "--saida", str(base)]),
    ]
    return sum(_rodar(nome, cmd) != 0 for nome, cmd in passos)


def selados_ausentes() -> list[str]:
    """Return the sealed outputs (relative to ``output/``) that are not files on disk."""
    return [rel for rel in (*COMPARADOS, *IMAGENS) if not (SAIDA / rel).is_file()]


def comparar(base: Path) -> int:
    """Compare the regenerated outputs in ``base`` with the sealed ones; return mismatches.

    A file missing on either side is a failure with its name, images included (a missing image is
    not a rasterizer difference).
    """
    falhas = 0
    for rel in (*COMPARADOS, *IMAGENS):
        faltam = [
            lado
            for lado, raiz in (("regenerated", base), ("sealed", SAIDA))
            if not (raiz / rel).is_file()
        ]
        if faltam:
            falhas += 1
            print(f"[MISSING] {rel} ({' and '.join(faltam)} output absent)")
            continue
        igual = filecmp.cmp(base / rel, SAIDA / rel, shallow=False)
        if rel in IMAGENS:
            print(f"[{'SAME' if igual else 'WARN'}] {rel}" + ("" if igual else " (image differs)"))
        else:
            falhas += not igual
            print(f"[{'SAME' if igual else 'DIFF'}] {rel}")
    return falhas


def main(argv=None) -> int:
    """Run the selected mode; return the number of failed steps (0 = all green)."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    modo = ap.add_mutually_exclusive_group()
    modo.add_argument("--smoke", action="store_true", help="small N into output/smoke/ (CI)")
    modo.add_argument("--publish", action="store_true", help="full run into the sealed paths")
    args = ap.parse_args(argv)

    testes = [PY, "-m", "pytest", "-q", "--color=no", "-p", "no:cacheprovider"]
    verificar = [PY, "make_provenance.py", "--verify"]
    if args.smoke:
        falhas = gerar(RAIZ / SMOKE_DIR, SMOKE)
    elif args.publish:
        falhas = gerar(SAIDA, FULL)
    else:
        ausentes = selados_ausentes()
        for rel in ausentes:
            print(f"[MISSING] output/{rel} (sealed output absent: nothing to compare against)")
        if ausentes:
            print(f"run_all: {len(ausentes)} failure(s), stopped before regenerating anything")
            return len(ausentes)
        falhas = gerar(RAIZ / REPLICATED_DIR, FULL)
        falhas += comparar(RAIZ / REPLICATED_DIR)
    falhas += _rodar("tests", testes) != 0
    if args.publish:  # the tests run BEFORE the seal: a failing run is never sealed
        if falhas:
            print(f"[FAIL] seal skipped: {falhas} failure(s) before it")
            falhas += 1
        else:
            falhas += _rodar("seal", [PY, "make_provenance.py"]) != 0
    falhas += _rodar("provenance verify", verificar) != 0
    print(f"run_all: {'GREEN' if falhas == 0 else f'{falhas} failure(s)'}")
    return falhas


if __name__ == "__main__":
    raise SystemExit(main())
