"""Runner of the pre-registered token KAT (``data/prereg/02-token-kat-addendum.md``).

Runs the 8 cells x 2 combinations (R, R ∪ S) x 5 seeds of the grid ``data/kat_token_grid.json``
through the LITERAL token-budget simulation (``token_kat.simular_literal_tokens``), in blocks of
users with the stream ``default_rng([semente, i_celula, i_combo, tag_r3, i_bloco])``. Writes
``<saida>/celulas.csv`` and ``<saida>/resumo.json`` (KT-S / KT-N criterion + diagnostics), with no
date or time, so that both are reproducible byte for byte. The level tolerance comes from the SAME
function as the frozen analytic table (``token_kat_analytic_table.tolerancia``).

``adendo_sha256`` in ``resumo.json`` is the sha256 of the sanitized addendum
``data/prereg/02-token-kat-addendum.md``; ``grade_sha256`` is the sha256 of the grid.

Usage: ``python3 code/run_token_kat.py --saida output/kat_token [--processos 8]``. The optional
``--N`` and ``--bloco-usuarios`` override the grid values (smoke runs only); without them the
run is the pre-registered one.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import displacement as rd
import token_kat as kt
import token_kat_analytic_table

RAIZ = kt.RAIZ
ADENDO = RAIZ / "data/prereg/02-token-kat-addendum.md"
CAMPOS_CSV = [
    "i_celula",
    "celula",
    "regime",
    "combo",
    "semente",
    "auc",
    "auc_fluida",
    "n_pos",
    "n_neg",
    "frac_saturada",
    "ociosos_medio_saturados",
]


def _tabela_analitica():
    """Return the analytic-table module (source of the pre-registered tolerance function)."""
    return token_kat_analytic_table


def tolerancias(grade: dict) -> dict:
    """Return the level tolerance of every (cell, combination), computed from its own sources."""
    tab = _tabela_analitica()
    out = {}
    for cel in grade["celulas"]:
        for combo in ("R", "RS"):
            fs = [dict(nome=n, **p) for n, p in kt.fontes_da_celula(cel, combo).items()]
            out[(cel["id"], combo)] = tab.tolerancia(fs, cel["T"], grade)
    return out


def _uma_tarefa(tarefa):
    """Simulate one (cell, combination, seed) task, block by block, and return its result row."""
    i_celula, cel, i_combo, combo, semente, grade = tarefa
    fontes = kt.fontes_da_celula(cel, combo)
    nomes = "".join(fontes)
    lam = {n: p["lam"] for n, p in fontes.items()}
    d = {n: p["d"] for n, p in fontes.items()}
    k = {n: p["k"] for n, p in fontes.items()}
    N, bloco = grade["N"], grade["bloco_usuarios"]
    if N % bloco:
        raise ValueError(f"N = {N} não é múltiplo do bloco {bloco}")
    escores, rotulos, n_sat, ociosos = [], [], 0, 0
    for i_bloco in range(N // bloco):
        rng = np.random.default_rng([semente, i_celula, i_combo, grade["tag_r3"], i_bloco])
        s, y, diag = kt.simular_literal_tokens(nomes, lam, d, k, cel["T"], bloco, rng, grade["K"])
        escores.append(s)
        rotulos.append(y)
        n_sat += diag["n_saturados"]
        ociosos += diag["soma_ociosos"]
    s = np.concatenate(escores)
    y = np.concatenate(rotulos)
    n_pos = int(np.sum(y))
    return {
        "i_celula": i_celula,
        "celula": cel["id"],
        "regime": cel["bloco"],
        "combo": combo,
        "semente": semente,
        "auc": rd.auc_mann_whitney(s, y),
        "auc_fluida": kt.auc_fluida(fontes, cel["T"], grade["K"]),
        "n_pos": n_pos,
        "n_neg": N - n_pos,
        "frac_saturada": n_sat / N,
        "ociosos_medio_saturados": (ociosos / n_sat) if n_sat else 0.0,
    }


def _celula_csv(valor):
    """Return a CSV cell: floats in ``repr`` of a Python float; everything else as it is."""
    if isinstance(valor, float):
        return repr(float(valor))
    return valor


def _sha(p: Path) -> str:
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    """Run the token KAT grid and write ``celulas.csv`` and ``resumo.json``; return 0."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=str, required=True)
    ap.add_argument("--processos", type=int, default=8)
    ap.add_argument("--N", type=int, default=None, help="smoke only: override the grid N")
    ap.add_argument(
        "--bloco-usuarios", type=int, default=None, help="smoke only: override the block size"
    )
    args = ap.parse_args(argv)

    grade = kt.carregar_grade()
    if args.N is not None:
        grade["N"] = args.N
    if args.bloco_usuarios is not None:
        grade["bloco_usuarios"] = args.bloco_usuarios
    if grade["pi"] != rd.PI:
        raise ValueError("π da grade ≠ π do r1")
    tarefas = [
        (i_celula, cel, i_combo, combo, semente, grade)
        for i_celula, cel in enumerate(grade["celulas"])
        for i_combo, combo in enumerate(("R", "RS"))
        for semente in grade["sementes"]
    ]
    with ProcessPoolExecutor(max_workers=args.processos) as ex:
        linhas = list(ex.map(_uma_tarefa, tarefas))
    linhas.sort(key=lambda row: (row["i_celula"], ("R", "RS").index(row["combo"]), row["semente"]))

    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    with open(saida / "celulas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS_CSV)
        for row in linhas:
            w.writerow([_celula_csv(row[c]) for c in CAMPOS_CSV])

    tol = tolerancias(grade)
    avaliacao = kt.avaliar_kat(linhas, grade, tol)
    diagnostico = {}
    for chave, itens in itertools.groupby(
        linhas, key=lambda row: f"{row['celula']}/{row['combo']}"
    ):
        itens = list(itens)
        diagnostico[chave] = {
            "frac_saturada_media": float(np.mean([row["frac_saturada"] for row in itens])),
            "ociosos_medio_saturados": float(
                np.mean([row["ociosos_medio_saturados"] for row in itens])
            ),
        }
    resumo = {
        "adendo_sha256": _sha(ADENDO),
        "grade_sha256": _sha(kt.GRADE),
        "N": grade["N"],
        "sementes": grade["sementes"],
        "bloco_usuarios": grade["bloco_usuarios"],
        "avaliar_kat": avaliacao,
        "tolerancias": {f"{c}/{combo}": v for (c, combo), v in tol.items()},
        "diagnostico": diagnostico,
        "versoes": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
    }
    with open(saida / "resumo.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
