"""Runner of the pre-registered quota family (``data/prereg/08-quotas-addendum.md``).

Runs the 6 cells x 5 seeds of the grid ``data/quotas_grid.json``: per (cell, seed) ONE literal
history of ``N`` users, drawn in blocks with the stream declared under the cell's ``fluxo``
(``default_rng([semente, i_celula, i_combo, tag, i_bloco])``, never derived from the position of
the cell), is read by every policy of the cell (pairing); in the host cell of the Consequence the
history of ``R`` is the same history without the events of the new source. Writes
``<out>/celulas.csv`` (one row per cell, history, policy and seed) and ``<out>/resumo.json``
(anchors, predictions recomputed from the grid, every pre-registered criterion with its result,
the verdict and the report-only diagnostics), with no date or time, so that both are
reproducible byte for byte.

In the pre-registered run the anchors (REC of KNP1 and KNP2 = the sealed token-KAT rows, ``repr``
equality) are checked BEFORE any criterion; a mismatch aborts with exit 2 and writes nothing. A
smoke run (``--N`` or ``--bloco-usuarios``) marks the anchors as not applicable.

Usage: ``python3 code/run_quotas.py --out output/quotas [--processos 8]``. The optional ``--N``
and ``--bloco-usuarios`` override the grid values (smoke runs only). The number of processes is
not a parameter of the simulation (it never enters the random stream).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import displacement as rd
import quotas as qt
import token_kat as kt

RAIZ = qt.RAIZ
TABELA = RAIZ / "data/prereg/quotas_analytic_table.txt"
PREREG = RAIZ / "data/prereg/08-quotas-addendum.md"
CAMPOS_CSV = [
    "i_celula",
    "celula",
    "bloco",
    "historia",
    "politica",
    "semente",
    "auc",
    "n_pos",
    "n_neg",
    "frac_saturada",
    "ociosos_medio_saturados",
    "d_medio",
    "frac_d_abaixo_rec",
]
ORDEM_HISTORIA = ("RS", "R")


def _politicas(cel: dict, grade: dict) -> list[str]:
    """Return the policies of a cell (its own ``politicas`` key, else the grid list)."""
    return list(cel.get("politicas", grade["politicas"]))


def _uma_tarefa(tarefa):
    """Simulate one (cell, seed) task block by block; return its rows and diagnostics.

    ``i_celula`` of the task is the position of the cell in the grid (the ``i_celula`` column of
    the CSV); the random stream uses the declared ``fluxo`` of the cell.
    """
    i_celula, cel, semente, grade = tarefa
    fontes = kt.fontes_da_celula(cel, "RS")
    combo = "".join(fontes)
    lam = {n: p["lam"] for n, p in fontes.items()}
    d = {n: p["d"] for n, p in fontes.items()}
    k = {n: p["k"] for n, p in fontes.items()}
    K, T, tau, fl = grade["K"], cel["T"], cel.get("tau"), cel["fluxo"]
    N, bloco = grade["N"], grade["bloco_usuarios"]
    if N % bloco:
        raise ValueError(f"N = {N} não é múltiplo do bloco {bloco}")
    politicas = {"RS": _politicas(cel, grade)}
    consequencia = cel["id"] == grade["consequencia"]["celula"]
    if consequencia:
        politicas["R"] = ["REC", "RHO"]
    acum = {
        (h, p): {"s": [], "ociosos": 0, "d_soma": 0.0, "d_abaixo": 0}
        for h, pols in politicas.items()
        for p in pols
    }
    n_sat = dict.fromkeys(politicas, 0)
    rotulos, difere = [], 0
    for i_bloco in range(N // bloco):
        rng = np.random.default_rng([semente, fl["i_celula"], fl["i_combo"], fl["tag"], i_bloco])
        hist = qt.gerar_historia(combo, lam, d, k, T, bloco, rng, tau=tau)
        rotulos.append(hist["y"])
        historias = {"RS": hist}
        if consequencia:
            historias["R"] = qt.restringir(hist, range(len(cel["R"])))
        n_vis_rho = {}
        for h, H in historias.items():
            med_rec = qt.medidas(H, qt.janela("REC", H, K), K)
            saturados = med_rec["custo_total"] > K
            n_sat[h] += int(saturados.sum())
            extra = ["RHO"] if consequencia and "RHO" not in politicas[h] else []
            for p in politicas[h] + extra:
                vis = qt.janela(p, H, K)
                med = qt.medidas(H, vis, K)
                if p == "RHO":
                    n_vis_rho[h] = med["n_visivel"]
                if p not in politicas[h]:
                    continue
                a = acum[(h, p)]
                a["s"].append(qt.escores(H, vis))
                a["ociosos"] += int(np.sum(K - med["custo_visivel"][saturados]))
                a["d_soma"] += float(np.sum(med["d_usuario"]))
                a["d_abaixo"] += int(np.sum(med["d_usuario"] < med_rec["d_usuario"]))
        if consequencia:
            n_rs, n_r = n_vis_rho["RS"], n_vis_rho["R"]
            nr = n_r.shape[1]
            difere += int(
                np.sum(np.any(n_rs[:, :nr] != n_r, axis=1) | np.any(n_rs[:, nr:] > 0, axis=1))
            )
    y = np.concatenate(rotulos)
    n_pos = int(np.sum(y))
    linhas = []
    for (h, p), a in acum.items():
        linhas.append(
            {
                "i_celula": i_celula,
                "celula": cel["id"],
                "bloco": cel["bloco"],
                "historia": h,
                "politica": p,
                "semente": semente,
                "auc": rd.auc_mann_whitney(np.concatenate(a["s"]), y),
                "n_pos": n_pos,
                "n_neg": N - n_pos,
                "frac_saturada": n_sat[h] / N,
                "ociosos_medio_saturados": (a["ociosos"] / n_sat[h]) if n_sat[h] else 0.0,
                "d_medio": a["d_soma"] / N,
                "frac_d_abaixo_rec": a["d_abaixo"] / N,
            }
        )
    return {
        "linhas": linhas,
        "consequencia": (
            {"celula": cel["id"], "semente": semente, "usuarios_janela_rho_difere": difere}
            if consequencia
            else None
        ),
    }


def _celula_csv(valor):
    """Return a CSV cell: floats in ``repr`` of a Python float; everything else as it is."""
    if isinstance(valor, float):
        return repr(float(valor))
    return valor


def _sha(p: Path) -> str:
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _diagnostico(linhas, consequencia, grade: dict) -> dict:
    """Return the report-only diagnostics, averaged over the seeds, per cell and policy."""
    out = {}
    for r in linhas:
        chave = f"{r['celula']}/{r['historia']}"
        c = out.setdefault(chave, {"frac_saturada_media": [], "politicas": {}})
        c["frac_saturada_media"].append(r["frac_saturada"])
        p = c["politicas"].setdefault(
            r["politica"], {"ociosos_medio_saturados": [], "d_medio": [], "frac_d_abaixo_rec": []}
        )
        for campo in p:
            p[campo].append(r[campo])
    for c in out.values():
        c["frac_saturada_media"] = float(np.mean(c["frac_saturada_media"]))
        for p in c["politicas"].values():
            for campo in p:
                p[campo] = float(np.mean(p[campo]))
    cons = sorted((x for x in consequencia if x), key=lambda x: x["semente"])
    out["consequencia_usuarios_janela_rho_difere"] = {
        "celula": grade["consequencia"]["celula"],
        "por_semente": [x["usuarios_janela_rho_difere"] for x in cons],
    }
    return out


def main(argv=None) -> int:
    """Run the quota grid and write ``celulas.csv`` and ``resumo.json``; return the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--processos", type=int, default=8)
    ap.add_argument("--N", type=int, default=None, help="smoke only: override the grid N")
    ap.add_argument(
        "--bloco-usuarios", type=int, default=None, help="smoke only: override the block size"
    )
    args = ap.parse_args(argv)

    grade = qt.carregar_grade()
    preregistrado = args.N is None and args.bloco_usuarios is None
    if args.N is not None:
        grade["N"] = args.N
    if args.bloco_usuarios is not None:
        grade["bloco_usuarios"] = args.bloco_usuarios
    if grade["pi"] != rd.PI:
        raise ValueError("π da grade ≠ π do r1")
    tarefas = [
        (i_celula, cel, semente, grade)
        for i_celula, cel in enumerate(grade["celulas"])
        for semente in grade["sementes"]
    ]
    with ProcessPoolExecutor(max_workers=args.processos) as ex:
        resultados = list(ex.map(_uma_tarefa, tarefas))
    linhas = [r for res in resultados for r in res["linhas"]]
    ordem_pol = {p: i for i, p in enumerate([*grade["politicas"], "RHOidade"])}
    linhas.sort(
        key=lambda r: (
            r["i_celula"],
            ORDEM_HISTORIA.index(r["historia"]),
            ordem_pol[r["politica"]],
            r["semente"],
        )
    )

    # anchors BEFORE any criterion; a mismatch aborts the pre-registered run
    if preregistrado:
        ancoras = qt.conferir_ancoras(linhas, grade)
        if not ancoras["passou"]:
            falhas = [x for x in ancoras["linhas"] if not x["igual"]]
            print(f"ÂNCORA FALHOU (run abortado): {json.dumps(falhas)}", file=sys.stderr)
            return 2
    else:
        ancoras = {
            "aplicavel": False,
            "passou": False,
            "motivo": "N or block size differ from the grid (smoke run)",
        }
    prev = qt.previsoes(grade)
    avaliacao = qt.avaliar_c5(linhas, grade, prev, ancoras)

    saida = Path(args.out)
    saida.mkdir(parents=True, exist_ok=True)
    with open(saida / "celulas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS_CSV)
        for r in linhas:
            w.writerow([_celula_csv(r[c]) for c in CAMPOS_CSV])
    resumo = {
        "preregistrado": preregistrado,
        "N": grade["N"],
        "bloco_usuarios": grade["bloco_usuarios"],
        "sementes": grade["sementes"],
        "K": grade["K"],
        "tag": grade["tag"],
        "tol_X": grade["tol_X"],
        "grade_sha256": _sha(qt.GRADE),
        "tabela_sha256": _sha(TABELA),
        "preregistro_sha256": _sha(PREREG),
        "ancoras": ancoras,
        "previsoes": prev,
        "avaliar_c5": avaliacao,
        "diagnostico": _diagnostico(linhas, [r["consequencia"] for r in resultados], grade),
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
