"""Runner of the pre-registered CMP addendum (event fusion, ``data/prereg/07-fusion-addendum.md``).

Runs the 6 cells x 4 arms x 5 seeds of the grid ``data/fusion_grid.json`` through the LITERAL
token-budget simulation, in blocks of users with the stream
``default_rng([semente, i_celula, i_fluxo, tag, i_bloco])`` (tag 7, exclusive to this family):
``i_fluxo = 0`` draws arm ``R`` alone (``token_kat.simular_literal_tokens``); ``i_fluxo = 1``
draws ``R ∪ S`` ONCE, shared by ``RS``, ``RF`` and ``RP`` (``fusion.simular_fusao``: the fusion is
a post-draw transform). Writes ``<out>/celulas.csv`` and ``<out>/resumo.json`` (CMP-S / CMP-0 /
CMP-N / CMP-T criterion, per-contrast and per-arm values, diagnostics), with no date, time or
number of processes, so both are reproducible byte for byte. The number of processes is not a
scientific parameter: it never enters the stream.

``resumo.json`` records the sha256 of the grid read, of the frozen analytic table
``data/prereg/fusion_analytic_table.txt`` and of the sanitized pre-registration
``data/prereg/07-fusion-addendum.md``.

Usage: ``python3 code/run_fusion.py --out output/fusion [--grid data/fusion_grid.json]
[--processos 8]``. The optional ``--N`` and ``--bloco-usuarios`` override the grid values (smoke
runs only); without them the run is the pre-registered one.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import displacement as rd
import fusion as fu
import run_token_kat as rtk
import token_kat as kt

CAMPOS_CSV = [
    "i_celula",
    "celula",
    "regime",
    "braco",
    "regime_braco",
    "semente",
    "auc",
    "auc_fluida",
    "n_pos",
    "n_neg",
    "frac_saturada",
    "ociosos_medio_saturados",
    "blocos_visiveis_medio",
    "frac_bloco_incompleto_visivel",
]
BRACOS_DO_FLUXO = {0: ("R",), 1: ("RS", "RF", "RP")}


def fluxo(semente, i_celula, i_fluxo, i_bloco, grade) -> list:
    """Return the seed sequence of one block: ``[semente, i_celula, i_fluxo, tag, i_bloco]``."""
    return [semente, i_celula, i_fluxo, grade["tag"], i_bloco]


def escores_do_bloco(i_celula, cel, i_fluxo, semente, i_bloco, grade, bracos=None):
    """Simulate one block of ``grade["bloco_usuarios"]`` users of one stream.

    Returns
    -------
    tuple
        ``(resultado, y)`` with ``resultado[braco] = (scores, diag)``: arm ``R`` for
        ``i_fluxo = 0``; arms ``RS``, ``RF`` and ``RP`` (or the subset ``bracos``) on one shared
        draw for ``i_fluxo = 1``.
    """
    rng = np.random.default_rng(fluxo(semente, i_celula, i_fluxo, i_bloco, grade))
    N, K = grade["bloco_usuarios"], grade["K"]
    if i_fluxo == 0:
        fontes = kt.fontes_da_celula(cel, "R")
        s, y, diag = kt.simular_literal_tokens(
            "".join(fontes),
            {n: p["lam"] for n, p in fontes.items()},
            {n: p["d"] for n, p in fontes.items()},
            {n: p["k"] for n, p in fontes.items()},
            cel["T"],
            N,
            rng,
            K,
        )
        return {"R": (s, diag)}, y
    if i_fluxo == 1:
        return fu.simular_fusao(cel, rng, N, K, bracos or BRACOS_DO_FLUXO[1])
    raise ValueError(f"i_fluxo {i_fluxo}: use 0 (R) ou 1 (R ∪ S partilhado)")


def _uma_tarefa(tarefa):
    """Simulate one (cell, stream, seed) task, block by block, and return one row per arm."""
    i_celula, cel, i_fluxo, semente, grade, bracos = tarefa
    N, bloco, K = grade["N"], grade["bloco_usuarios"], grade["K"]
    if N % bloco:
        raise ValueError(f"N = {N} não é múltiplo do bloco {bloco}")
    escores = {b: [] for b in bracos}
    soma = {b: {"n_saturados": 0, "soma_ociosos": 0, "blocos": 0, "incompleto": 0} for b in bracos}
    rotulos = []
    for i_bloco in range(N // bloco):
        res, y = escores_do_bloco(i_celula, cel, i_fluxo, semente, i_bloco, grade, bracos)
        rotulos.append(y)
        for b in bracos:
            s, diag = res[b]
            escores[b].append(s)
            soma[b]["n_saturados"] += diag["n_saturados"]
            soma[b]["soma_ociosos"] += diag["soma_ociosos"]
            soma[b]["blocos"] += diag.get("blocos_visiveis", 0)
            soma[b]["incompleto"] += diag.get("n_incompleto_visivel", 0)
    y = np.concatenate(rotulos)
    n_pos = int(np.sum(y))
    linhas = []
    for b in bracos:
        n_sat = soma[b]["n_saturados"]
        fundido = b in ("RF", "RP")
        linhas.append(
            {
                "i_celula": i_celula,
                "celula": cel["id"],
                "regime": cel["bloco"],
                "braco": b,
                "regime_braco": fu.regime_braco(cel, b, K),
                "semente": semente,
                "auc": rd.auc_mann_whitney(np.concatenate(escores[b]), y),
                "auc_fluida": fu.auc_fluida_braco(cel, b, K),
                "n_pos": n_pos,
                "n_neg": N - n_pos,
                "frac_saturada": n_sat / N,
                "ociosos_medio_saturados": (soma[b]["soma_ociosos"] / n_sat) if n_sat else 0.0,
                "blocos_visiveis_medio": soma[b]["blocos"] / N if fundido else None,
                "frac_bloco_incompleto_visivel": soma[b]["incompleto"] / N if fundido else None,
            }
        )
    return linhas


def escrever_csv(linhas, caminho) -> None:
    """Write the rows to ``caminho`` (``csv.writer`` defaults; floats as ``repr``; None empty)."""
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS_CSV)
        for row in linhas:
            w.writerow([rtk._celula_csv(row[c]) for c in CAMPOS_CSV])


def diagnostico(linhas, grade) -> dict:
    """Return the report-only diagnostics per ``cell/arm`` (means over seeds)."""
    out = {}
    for cel in grade["celulas"]:
        for b in fu.BRACOS:
            itens = [row for row in linhas if row["celula"] == cel["id"] and row["braco"] == b]
            d = {
                "frac_saturada_media": float(np.mean([row["frac_saturada"] for row in itens])),
                "ociosos_medio_saturados": float(
                    np.mean([row["ociosos_medio_saturados"] for row in itens])
                ),
            }
            if b in ("RF", "RP"):
                d["blocos_visiveis_medio"] = float(
                    np.mean([row["blocos_visiveis_medio"] for row in itens])
                )
                d["blocos_visiveis_fluido"] = fu.blocos_visiveis_fluido(cel, b, grade["K"])
                d["frac_bloco_incompleto_visivel_media"] = float(
                    np.mean([row["frac_bloco_incompleto_visivel"] for row in itens])
                )
            out[f"{cel['id']}/{b}"] = d
    return out


def main(argv=None) -> int:
    """Run the CMP grid and write ``celulas.csv`` and ``resumo.json``; return 0."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--grid", type=Path, default=fu.GRADE)
    ap.add_argument("--processos", type=int, default=8)
    ap.add_argument("--N", type=int, default=None, help="smoke only: override the grid N")
    ap.add_argument(
        "--bloco-usuarios", type=int, default=None, help="smoke only: override the block size"
    )
    args = ap.parse_args(argv)

    grade = fu.carregar_grade(args.grid)
    if args.N is not None:
        grade["N"] = args.N
    if args.bloco_usuarios is not None:
        grade["bloco_usuarios"] = args.bloco_usuarios
    if grade["pi"] != rd.PI:
        raise ValueError("π da grade ≠ π do r1")
    if grade["tag"] != fu.TAG_FAMILIA or grade["tag"] in fu.TAGS_OUTRAS:
        raise ValueError(f"tag {grade['tag']}: a família CMP usa a tag {fu.TAG_FAMILIA}")
    tarefas = [
        (i_celula, cel, i_fluxo, semente, grade, BRACOS_DO_FLUXO[i_fluxo])
        for i_fluxo in (1, 0)  # the heavier shared draws first
        for i_celula, cel in enumerate(grade["celulas"])
        for semente in grade["sementes"]
    ]
    with ProcessPoolExecutor(max_workers=args.processos) as ex:
        linhas = [row for rows in ex.map(_uma_tarefa, tarefas) for row in rows]
    linhas.sort(key=lambda row: (row["i_celula"], fu.BRACOS.index(row["braco"]), row["semente"]))

    saida = Path(args.out)
    saida.mkdir(parents=True, exist_ok=True)
    escrever_csv(linhas, saida / "celulas.csv")

    tol = fu.tolerancias(grade)
    avaliacao = fu.avaliar_fusao(linhas, grade, tol, fu.papeis_da_tabela())
    resumo = {
        "veredito": avaliacao["veredito"],
        "grade_sha256": rtk._sha(args.grid),
        "tabela_sha256": rtk._sha(fu.TABELA),
        "preregistro_sha256": rtk._sha(fu.PREREG),
        "K": grade["K"],
        "N": grade["N"],
        "sementes": grade["sementes"],
        "bloco_usuarios": grade["bloco_usuarios"],
        "tag": grade["tag"],
        "fluxo": (
            "numpy.random.default_rng([semente, i_celula, i_fluxo, tag, i_bloco]); i_fluxo 0 = "
            "arm R alone; i_fluxo 1 = one draw of R ∪ S shared by RS, RF and RP"
        ),
        "definicoes": {
            "frac_saturada": (
                "fraction of users whose history costs more than K tokens; for RF and RP the "
                "history is R + blocks (after fusion)"
            ),
            "ociosos_medio_saturados": (
                "mean of K minus the visible tokens over the saturated users of the arm"
            ),
            "blocos_visiveis_medio": "visible blocks per user (RF and RP share the window)",
            "blocos_visiveis_fluido": "(lam_S / m) * h, h = min(T, K / W) of the fused arm",
            "frac_bloco_incompleto_visivel": "fraction of users whose incomplete block is visible",
        },
        "avaliar_fusao": avaliacao,
        "tolerancias": {f"{c}/{b}": v for (c, b), v in tol.items()},
        "diagnostico": diagnostico(linhas, grade),
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
