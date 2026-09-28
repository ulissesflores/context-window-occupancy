"""Shared runner of the exponent and occupancy families (section 0.4 of their addenda).

``data/prereg/05-exponent-addendum.md`` and ``data/prereg/06-occupancy-addendum.md`` fix ONE thin
runner for both families: ``python3 code/run_grid.py --grid <json> --out <dir>``. It runs every
cell x combination (R, R ∪ S) x seed of the grid through the token KAT machinery, imported and
never edited: ``run_token_kat._uma_tarefa`` (literal token-budget simulation, stream
``default_rng([semente, i_celula, i_combo, tag, i_bloco])``), ``run_token_kat.tolerancias`` and
``token_kat.avaliar_kat``. The number of processes is not a scientific parameter: it is not part
of the stream, so any ``--processos`` gives the same bytes.

Tag adapter. New grids keep their tag under ``tag``; the token KAT grid keeps it under
``tag_r3``, the key that ``_uma_tarefa`` reads. ``adaptar_grade`` passes it a copy of the grid
whose ``tag_r3`` is ``tag`` when present, else the grid's own ``tag_r3``, so both forms are
accepted (the expression is the one fixed in section 0.4, written once, in ``adaptar_grade``).

Filtering. ``--celulas ID [ID ...]`` runs only those cells, with their ORIGINAL index in the grid
(``i_celula``), so a filtered run draws the same streams as the full one; ``tolerancias`` and
``avaliar_kat`` then see ``{**grade, "celulas": <the filtered cells>}``.

Outputs, with no date or time, reproducible byte for byte:

- ``<out>/celulas.csv``: the schema and serialization of ``run_token_kat`` (``CAMPOS_CSV``,
  ``_celula_csv``: floats as ``repr(float(...))``, CRLF terminator of ``csv.writer``).
- ``<out>/resumo.json``: ``grade`` (path relative to the repository root, else the file name),
  ``grade_sha256``, ``tag`` (the value the adapter passed on), ``celulas`` (ids run), ``N``,
  ``sementes``, ``bloco_usuarios``, ``avaliar_kat``, ``tolerancias``, ``diagnostico``, ``versoes``,
  and, only when the file exists, ``tabela_sha256`` (``data/prereg/<stem>_analytic_table.txt``)
  and ``adendo_sha256`` (the single ``data/prereg/0?-<stem>-addendum.md``), where ``<stem>`` is
  the grid file name without ``_grid.json``.

The ``avaliar_kat`` block is the shared KT-S / KT-N criterion applied to ALL the cells run, with
the level tolerance of the token KAT. It is NOT, by itself, the verdict of a family (for the
occupancy grid it would mix the threshold sub-block, which is outside that verdict).

Family verdict hook. If a module ``<stem>_analytic_table`` is importable (``code/`` is on
``sys.path``) and defines ``veredito(linhas, grade)``, the runner calls it with the result rows
(the dicts of ``_uma_tarefa``, sorted by cell, combination and seed) and the LOADED grid, filtered
but not adapted, and records the returned JSON-serializable dict under ``veredito``. This is where
each family computes its pre-registered criteria from its own frozen analytic table. The module
must be importable without side effects: no top-level run and no ``print`` (keep the generator's
command line under ``if __name__ == "__main__":``). For the token KAT grid (stem ``kat_token``)
no such module exists and no ``veredito`` key is written.

Usage: ``python3 code/run_grid.py --grid data/exponent_grid.json --out output/exponent
[--processos 8]``. ``--N`` and ``--bloco-usuarios`` override the grid values (smoke runs only);
without them the run is the pre-registered one.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import itertools
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import displacement as rd
import run_token_kat
import token_kat as kt

RAIZ = kt.RAIZ
PREREG = RAIZ / "data/prereg"


def adaptar_grade(grade: dict) -> dict:
    """Return the grid ``_uma_tarefa`` expects: the tag under ``tag_r3``, from either grid form.

    Raises
    ------
    ValueError
        If the grid has neither ``tag`` nor ``tag_r3``.
    """
    adaptada = {**grade, "tag_r3": grade.get("tag", grade.get("tag_r3"))}
    if adaptada["tag_r3"] is None:
        raise ValueError("grid without 'tag' or 'tag_r3': no stream tag to draw with")
    return adaptada


def _filtrar(grade: dict, ids) -> list[tuple[int, dict]]:
    """Return ``(original index, cell)`` of the cells in ``ids`` (all cells if ``ids`` is None).

    Raises
    ------
    ValueError
        If an id in ``ids`` is not a cell of the grid.
    """
    indexadas = list(enumerate(grade["celulas"]))
    if ids is None:
        return indexadas
    pedidas = set(ids)
    faltam = sorted(pedidas - {cel["id"] for _, cel in indexadas})
    if faltam:
        raise ValueError(f"cells not in the grid: {faltam}")
    return [(i, cel) for i, cel in indexadas if cel["id"] in pedidas]


def montar_tarefas(grade: dict, ids=None) -> list[tuple]:
    """Return the ``_uma_tarefa`` tasks of the (adapted) grid, keeping the original cell index.

    Parameters
    ----------
    grade : dict
        Grid already passed through ``adaptar_grade``.
    ids : iterable of str, optional
        Cell ids to run; all cells when omitted.

    Returns
    -------
    list of tuple
        ``(i_celula, cel, i_combo, combo, semente, grade)``, in grid order.
    """
    return [
        (i_celula, cel, i_combo, combo, semente, grade)
        for i_celula, cel in _filtrar(grade, ids)
        for i_combo, combo in enumerate(("R", "RS"))
        for semente in grade["sementes"]
    ]


def _sha(p: Path) -> str:
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _caminho_relativo(p: Path) -> str:
    """Return ``p`` relative to the repository root (POSIX), or its file name if outside it."""
    try:
        return p.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return p.name


def _stem(p: Path) -> str:
    """Return the grid file name without the ``_grid.json`` suffix."""
    return p.name.removesuffix("_grid.json")


def _shas_do_preregistro(stem: str) -> dict:
    """Return the sha256 of the frozen analytic table and addendum of ``stem``, when they exist.

    Raises
    ------
    ValueError
        If more than one addendum matches ``0?-<stem>-addendum.md``.
    """
    out = {}
    tabela = PREREG / f"{stem}_analytic_table.txt"
    if tabela.is_file():
        out["tabela_sha256"] = _sha(tabela)
    adendos = sorted(PREREG.glob(f"0?-{stem}-addendum.md"))
    if len(adendos) > 1:
        raise ValueError(f"more than one addendum for {stem!r}: {[a.name for a in adendos]}")
    if adendos:
        out["adendo_sha256"] = _sha(adendos[0])
    return out


def _veredito_da_familia(stem: str, linhas: list, grade: dict):
    """Return ``<stem>_analytic_table.veredito(linhas, grade)``, or None if there is no hook."""
    nome = f"{stem}_analytic_table"
    try:
        modulo = importlib.import_module(nome)
    except ModuleNotFoundError as e:
        if e.name != nome:  # the module exists but one of ITS imports is missing: surface it
            raise
        return None
    veredito = getattr(modulo, "veredito", None)
    return None if veredito is None else veredito(linhas, grade)


def main(argv=None) -> int:
    """Run a grid and write ``celulas.csv`` and ``resumo.json`` under ``--out``; return 0."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grid", type=str, required=True)
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--processos", type=int, default=8)
    ap.add_argument("--N", type=int, default=None, help="smoke only: override the grid N")
    ap.add_argument(
        "--bloco-usuarios", type=int, default=None, help="smoke only: override the block size"
    )
    ap.add_argument(
        "--celulas", nargs="+", default=None, help="run only these cell ids (original index kept)"
    )
    args = ap.parse_args(argv)

    caminho_grade = Path(args.grid)
    grade = kt.carregar_grade(caminho_grade)
    if args.N is not None:
        grade["N"] = args.N
    if args.bloco_usuarios is not None:
        grade["bloco_usuarios"] = args.bloco_usuarios
    if grade["pi"] != rd.PI:
        raise ValueError("π of the grid ≠ π of the displacement replication")
    adaptada = adaptar_grade(grade)
    tarefas = montar_tarefas(adaptada, args.celulas)
    with ProcessPoolExecutor(max_workers=args.processos) as ex:
        linhas = list(ex.map(run_token_kat._uma_tarefa, tarefas))
    linhas.sort(key=lambda row: (row["i_celula"], ("R", "RS").index(row["combo"]), row["semente"]))

    saida = Path(args.out)
    saida.mkdir(parents=True, exist_ok=True)
    with open(saida / "celulas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(run_token_kat.CAMPOS_CSV)
        for row in linhas:
            w.writerow([run_token_kat._celula_csv(row[c]) for c in run_token_kat.CAMPOS_CSV])

    celulas = [cel for _, cel in _filtrar(grade, args.celulas)]
    grade_rodada = {**grade, "celulas": celulas}
    tol = run_token_kat.tolerancias(grade_rodada)
    avaliacao = kt.avaliar_kat(linhas, grade_rodada, tol)
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
    stem = _stem(caminho_grade)
    resumo = {
        "grade": _caminho_relativo(caminho_grade),
        "grade_sha256": _sha(caminho_grade),
        **_shas_do_preregistro(stem),
        "tag": adaptada["tag_r3"],
        "celulas": [cel["id"] for cel in celulas],
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
    veredito = _veredito_da_familia(stem, linhas, grade_rodada)
    if veredito is not None:
        resumo["veredito"] = veredito
    with open(saida / "resumo.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
