"""Runner of the pre-registered displacement replication.

Pre-registration: ``data/prereg/01-displacement-replication.md``. Runs the full grid
(``rodar_grade``), writes the rows to ``<saida>/celulas.csv`` and the falsification summary
(``avaliar_quebra`` + ``regiao_p3_analitica`` + shortfall) to ``<saida>/resumo.json``, with no date
or time, so that both files are reproducible byte for byte from the same N and seeds.

Usage: ``python3 code/run_replication.py --N 200000 --sementes 5 --saida output/replication``
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
from pathlib import Path

import displacement as rd

CAMPOS_CSV = [
    "i_celula",
    "T",
    "lam_A",
    "lam_B",
    "lam_C",
    "d_A",
    "d_B",
    "d_C",
    "combo",
    "semente",
    "auc",
    "auc_analitica",
    "saturada",
    "n_pos",
    "n_neg",
]


def _celula_csv(valor):
    """Return a CSV cell: floats in ``repr`` (full precision); int/bool/str as they are."""
    if isinstance(valor, float):
        # float(...) guards against np.float64 (isinstance is True, but its repr differs)
        return repr(float(valor))
    return valor


def main(argv=None) -> int:
    """Run the replication grid and write ``celulas.csv`` and ``resumo.json``; return 0."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--sementes", type=int, required=True)
    ap.add_argument("--saida", type=str, required=True)
    ap.add_argument("--processos", type=int, default=None)
    args = ap.parse_args(argv)

    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)

    linhas = rd.rodar_grade(N=args.N, sementes=range(args.sementes), processos=args.processos)

    with open(saida / "celulas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS_CSV)
        for linha in linhas:
            w.writerow([_celula_csv(linha[campo]) for campo in CAMPOS_CSV])

    quebra = rd.avaliar_quebra(linhas)
    n_celulas, n_padrao, n_ordem = rd.regiao_p3_analitica()
    shortfall = rd.resumo_shortfall(linhas)

    resumo = {
        "N": args.N,
        "sementes": args.sementes,
        "avaliar_quebra": quebra,
        "regiao_p3_analitica": {"n_celulas": n_celulas, "n_padrao": n_padrao, "n_ordem": n_ordem},
        "shortfall_por_celula": shortfall["shortfall_por_celula"],
        "shortfall_padrao_T4": shortfall["shortfall_padrao_T4"],
        "versoes": {
            "python": platform.python_version(),
            "numpy": __import__("numpy").__version__,
            "scipy": __import__("scipy").__version__,
        },
    }
    with open(saida / "resumo.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
