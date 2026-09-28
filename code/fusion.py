"""Fusion of events of the new source under a token-budget window (Corollary 4(b), family CMP).

The specification is frozen in ``data/prereg/07-fusion-addendum.md``; the grid lives in
``data/fusion_grid.json`` and the analytic table in ``data/prereg/fusion_analytic_table.txt``.
The generative model, the oracle reader and the window rule are the ones of the token KAT
(``token_kat.py``, only imported): Poisson counts, uniform times on ``[0, T)``,
``x ~ N(d_s y, 1)``, score ``sum d_s (x_i - d_s / 2)`` over the LONGEST suffix of most recent
whole events whose cost is ``<= K``.

New here, and only this: the fusion rule (the ``S`` events of each user, ordered by time and input
order, are grouped into blocks of ``m`` counted from the most recent; the incomplete block, if
any, is the OLDEST; each block becomes one event with the time and input order of its most recent
member and cost ``k'``, the incomplete one included), the window over ``R`` + blocks, and the
CMP-S / CMP-0 / CMP-N / CMP-T criterion. Arm ``RF`` (lossless) carries the sum of the members'
contributions; arm ``RP`` (control, ``d`` NOT preserved) carries only the most recent member's.
``RS`` is exactly the token KAT simulation. ``RS``, ``RF`` and ``RP`` share ONE draw (fusion is a
post-draw transform); the stream is chosen by ``run_fusion.py``.

Under the oracle reader the sufficiency of the sum inside a fused event is an algebraic identity
of the model: what the simulation checks is the fluid factor under literal blocks and truncation
(checked by literal simulation).

Dictionary keys and identifiers follow the Portuguese names of the reused modules
(``celula``, ``braco`` = arm, ``semente`` = seed): they become the columns of
``output/fusion/celulas.csv`` and the keys of ``output/fusion/resumo.json``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

import displacement as rd
import fusion_analytic_table as fat
import token_kat as kt
import token_kat_analytic_table as tab

RAIZ = kt.RAIZ
GRADE = RAIZ / "data/fusion_grid.json"
TABELA = RAIZ / "data/prereg/fusion_analytic_table.txt"
PREREG = RAIZ / "data/prereg/07-fusion-addendum.md"

BRACOS = ("R", "RS", "RF", "RP")
CONTRASTES = (("RS", "R"), ("RF", "R"), ("RP", "R"), ("RF", "RS"), ("RP", "RS"))
TAG_FAMILIA = 7
TAGS_OUTRAS = frozenset({3, 5, 6, 8})  # 3 = token KAT; 5, 6, 8 = the other three families


def carregar_grade(caminho: Path = GRADE) -> dict:
    """Load the pre-registered grid (JSON) from ``caminho``."""
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


# --- fluid closed form with fused parameters (pre-registration, section 2) -----------------------


def fontes_do_braco(cel: dict, braco: str) -> dict:
    """Return the sources of an arm, in grid order, as ``name -> {"lam", "d", "k"}``.

    ``RF`` replaces ``S`` by ``(lam/m, sqrt(m) d, k')``; ``RP`` by ``(lam/m, d, k')``, with the
    same expressions as the frozen analytic table.
    """
    if braco in ("R", "RS"):
        return kt.fontes_da_celula(cel, braco)
    if braco not in ("RF", "RP"):
        raise ValueError(f"braço {braco!r}: use R, RS, RF ou RP")
    fontes = kt.fontes_da_celula(cel, "R")
    ((nome_S, S),) = cel["S"].items()
    m, k_fund = cel["m"], cel["k_fund"]
    if braco == "RF":
        fontes[nome_S + "f"] = {"lam": S["lam"] / m, "d": math.sqrt(m) * S["d"], "k": k_fund}
    else:
        fontes[nome_S + "p"] = {"lam": S["lam"] / m, "d": S["d"], "k": k_fund}
    return fontes


def delta2_fluido_braco(cel: dict, braco: str, K) -> float:
    """Return the fluid ``Delta^2`` of an arm (``token_kat.delta2_fluido``)."""
    return kt.delta2_fluido(fontes_do_braco(cel, braco), cel["T"], K)


def auc_fluida_braco(cel: dict, braco: str, K) -> float:
    """Return the fluid AUC of an arm (``token_kat.auc_fluida``, scipy normal CDF)."""
    return kt.auc_fluida(fontes_do_braco(cel, braco), cel["T"], K)


def regime_braco(cel: dict, braco: str, K) -> str:
    """Return ``"sat"`` if ``T * W >= K`` with the arm's own (fused) sources, else ``"nao"``."""
    W = sum(p["lam"] * p["k"] for p in fontes_do_braco(cel, braco).values())
    return "sat" if cel["T"] * W >= K else "nao"


def blocos_visiveis_fluido(cel: dict, braco: str, K) -> float:
    """Return the fluid number of visible blocks per user, ``(lam_S / m) * h`` (fused arms)."""
    fontes = fontes_do_braco(cel, braco)
    W = sum(p["lam"] * p["k"] for p in fontes.values())
    ((_, S),) = cel["S"].items()
    return S["lam"] / cel["m"] * min(cel["T"], K / W)


# --- literal simulation --------------------------------------------------------------------------


def sortear_eventos(nomes, lam, d, k, T, N, rng) -> dict:
    """Draw the events of the sources ``nomes`` in the order of ``simular_literal_tokens``.

    Order of draws: labels ``y``; Poisson counts (users x sources); times; attributes. The input
    order of an event (``ordem``) is its position in the draw (user, then source in grid order,
    then draw index), the recency tie-break of the token KAT.

    Returns
    -------
    dict
        ``y`` (N,), and per event ``usuario``, ``fonte``, ``tempos``, ``ordem``, ``custos``
        (int64) and ``contrib`` = ``d_s (x - d_s / 2)`` (the oracle term, same expression).
    """
    y = rng.random(N) < rd.PI
    nf = len(nomes)
    lams = np.array([lam[s] for s in nomes])
    d_combo = np.array([d[s] for s in nomes])
    k_combo = np.array([k[s] for s in nomes], dtype=np.int64)
    if np.any(k_combo <= 0):
        raise ValueError("custo por evento tem de ser inteiro positivo")

    contagens = rng.poisson(lams[None, :] * T, size=(N, nf))
    total_eventos = int(contagens.sum())
    if total_eventos == 0:
        vazio = np.zeros(0)
        return {
            "y": y,
            "usuario": vazio.astype(np.int64),
            "fonte": vazio.astype(np.int64),
            "tempos": vazio,
            "ordem": vazio.astype(np.int64),
            "custos": vazio.astype(np.int64),
            "contrib": vazio,
        }
    usuarios_grid, fontes_grid = np.meshgrid(np.arange(N), np.arange(nf), indexing="ij")
    repeticoes = contagens.ravel()
    usuario_idx = np.repeat(usuarios_grid.ravel(), repeticoes)
    fonte_idx = np.repeat(fontes_grid.ravel(), repeticoes)
    tempos = rng.uniform(0.0, T, size=total_eventos)
    x = rng.normal(d_combo[fonte_idx] * y[usuario_idx].astype(float), 1.0, size=total_eventos)
    return {
        "y": y,
        "usuario": usuario_idx,
        "fonte": fonte_idx,
        "tempos": tempos,
        "ordem": np.arange(total_eventos),
        "custos": k_combo[fonte_idx],
        "contrib": d_combo[fonte_idx] * (x - d_combo[fonte_idx] / 2),
    }


def janela_eventos(usuario, tempos, ordem, custos, contrib, N, K):
    """Apply the token-budget window of the token KAT to an event list and score every user.

    Per user, the visible events are the LONGEST suffix of most recent events whose summed cost is
    ``<= K`` (whole events, no skipping); recency = ``(tempos, ordem)`` ascending. The score is the
    sum of the visible contributions, added in that sorted order (the order of
    ``simular_literal_tokens``, hence byte-identical scores on the raw draw).

    Returns
    -------
    tuple
        ``(scores, visivel, diag)``: ``visivel`` is aligned with the input arrays;
        ``diag = {"n_saturados": users whose events cost more than K, "soma_ociosos": sum of
        (K - visible tokens) over the saturated users}``.
    """
    custos = np.asarray(custos, dtype=np.int64)
    visivel = np.zeros(len(usuario), dtype=bool)
    if len(usuario) == 0:
        return np.zeros(N), visivel, {"n_saturados": 0, "soma_ociosos": 0}
    idx = np.lexsort((ordem, tempos, usuario))
    custo_ord = custos[idx]
    acumulado = np.cumsum(custo_ord)  # int64, exact
    total_por_usuario = np.bincount(usuario, minlength=N)
    fim = np.cumsum(total_por_usuario)
    ultimo_do_usuario = np.repeat(fim - 1, total_por_usuario)  # position of the newest event
    sufixo = acumulado[ultimo_do_usuario] - acumulado + custo_ord  # cost of the suffix from here
    indices_visiveis = idx[sufixo <= K]
    visivel[indices_visiveis] = True
    scores = np.bincount(usuario[indices_visiveis], weights=contrib[indices_visiveis], minlength=N)
    custo_total = np.bincount(usuario, weights=custos, minlength=N)
    custo_visivel = np.bincount(
        usuario[indices_visiveis], weights=custos[indices_visiveis], minlength=N
    )
    saturados = custo_total > K
    diag = {
        "n_saturados": int(saturados.sum()),
        "soma_ociosos": int(round(float(np.sum(K - custo_visivel[saturados])))),
    }
    return scores, visivel, diag


def fundir(usuario, tempos, ordem, contrib, m, N) -> dict:
    """Group the events of ``S`` of each user into blocks of ``m`` anchored on the most recent.

    The events are ordered by ``(tempos, ordem)`` (stable; later input = more recent); rank
    ``r = 0`` is the most recent; block ``b = r // m``, so block 0 holds the ``m`` most recent
    and the incomplete block, if any, is the OLDEST. A block takes the time and the input order of
    its most recent member (``r = b m``), which is also its representative.

    Returns
    -------
    dict
        Per block, ordered by user and then by ``b`` (0 = most recent): ``usuario``, ``bloco``
        (``b``), ``tempo``, ``ordem``, ``representante`` (index, in the input arrays, of the most
        recent member), ``membros``, ``incompleto`` and ``soma`` = sum of the members'
        contributions (the lossless event of arm RF).
    """
    usuario = np.asarray(usuario)
    idx = np.lexsort((ordem, tempos, usuario))  # per user, from the oldest to the most recent
    u = usuario[idx]
    n_por_usuario = np.bincount(u, minlength=N)
    inicio = np.cumsum(n_por_usuario) - n_por_usuario
    posicao = np.arange(len(idx)) - inicio[u]  # 0 = the oldest event of the user
    r = n_por_usuario[u] - 1 - posicao  # 0 = the most recent
    b = r // m
    blocos_por_usuario = (n_por_usuario + m - 1) // m
    primeiro_bloco = np.cumsum(blocos_por_usuario) - blocos_por_usuario
    id_bloco = primeiro_bloco[u] + b
    n_blocos = int(blocos_por_usuario.sum())

    e_rep = r % m == 0  # the most recent member of each block
    representante = np.empty(n_blocos, dtype=np.int64)
    representante[id_bloco[e_rep]] = idx[e_rep]
    bloco = np.empty(n_blocos, dtype=np.int64)
    bloco[id_bloco[e_rep]] = b[e_rep]
    membros = np.bincount(id_bloco, minlength=n_blocos)
    return {
        "usuario": usuario[representante],
        "bloco": bloco,
        "tempo": np.asarray(tempos)[representante],
        "ordem": np.asarray(ordem)[representante],
        "representante": representante,
        "membros": membros,
        "incompleto": membros < m,
        "soma": np.bincount(id_bloco, weights=np.asarray(contrib)[idx], minlength=n_blocos),
    }


def lista_fundida(ev: dict, i_S: int, m: int, k_fund: int, N: int) -> dict:
    """Return the event list of the fused arms: the events of ``R`` unchanged + the blocks of ``S``.

    ``ev`` is a draw (``sortear_eventos``); ``i_S`` is the source index of ``S`` in it. Every block
    costs ``k_fund`` (the incomplete one included). ``contrib_RF`` of a block = the sum of its
    members; ``contrib_RP`` = the contribution of its most recent member only. The events of ``R``
    come first, in input order, then the blocks in the order of ``fundir``.
    """
    e_S = ev["fonte"] == i_S
    pos_S = np.flatnonzero(e_S)
    pos_R = np.flatnonzero(~e_S)
    bl = fundir(
        ev["usuario"][pos_S], ev["tempos"][pos_S], ev["ordem"][pos_S], ev["contrib"][pos_S], m, N
    )
    n_bl = len(bl["soma"])
    contrib_R = ev["contrib"][pos_R]
    return {
        "usuario": np.concatenate([ev["usuario"][pos_R], bl["usuario"]]),
        "tempos": np.concatenate([ev["tempos"][pos_R], bl["tempo"]]),
        "ordem": np.concatenate([ev["ordem"][pos_R], bl["ordem"]]),
        "custos": np.concatenate(
            [np.asarray(ev["custos"], dtype=np.int64)[pos_R], np.full(n_bl, k_fund, np.int64)]
        ),
        "contrib_RF": np.concatenate([contrib_R, bl["soma"]]),
        "contrib_RP": np.concatenate([contrib_R, ev["contrib"][pos_S][bl["representante"]]]),
        "e_bloco": np.concatenate([np.zeros(len(pos_R), bool), np.ones(n_bl, bool)]),
        "incompleto": np.concatenate([np.zeros(len(pos_R), bool), bl["incompleto"]]),
    }


def simular_fusao(cel: dict, rng, N: int, K, bracos=("RS", "RF", "RP")):
    """Simulate the arms ``RS``, ``RF`` and ``RP`` of a cell on ONE shared draw of ``R ∪ S``.

    The draw is the one of ``simular_literal_tokens`` on ``R ∪ S`` (grid order); ``RS`` is its
    token window; ``RF`` and ``RP`` apply the fusion rule to the same events (post-draw
    transform) and the window to ``R`` + blocks.

    Returns
    -------
    tuple
        ``(resultado, y)``; ``resultado[braco] = (scores, diag)``; for ``RF`` and ``RP`` the diag
        also has ``blocos_visiveis`` (visible blocks, summed over users) and
        ``n_incompleto_visivel`` (users whose incomplete block is visible).
    """
    if not set(bracos) <= {"RS", "RF", "RP"}:
        raise ValueError(f"braços {bracos!r}: só RS, RF e RP partilham o sorteio")
    fontes = kt.fontes_da_celula(cel, "RS")
    nomes = "".join(fontes)
    ev = sortear_eventos(
        nomes,
        {n: p["lam"] for n, p in fontes.items()},
        {n: p["d"] for n, p in fontes.items()},
        {n: p["k"] for n, p in fontes.items()},
        cel["T"],
        N,
        rng,
    )
    resultado = {}
    if "RS" in bracos:
        s, _, diag = janela_eventos(
            ev["usuario"], ev["tempos"], ev["ordem"], ev["custos"], ev["contrib"], N, K
        )
        resultado["RS"] = (s, diag)
    fundidos = [b for b in ("RF", "RP") if b in bracos]
    if fundidos:
        ((nome_S, _),) = cel["S"].items()
        lf = lista_fundida(ev, list(fontes).index(nome_S), cel["m"], cel["k_fund"], N)
        for braco in fundidos:
            s, vis, diag = janela_eventos(
                lf["usuario"], lf["tempos"], lf["ordem"], lf["custos"], lf[f"contrib_{braco}"], N, K
            )
            diag["blocos_visiveis"] = int(np.sum(vis & lf["e_bloco"]))
            diag["n_incompleto_visivel"] = int(np.sum(vis & lf["incompleto"]))
            resultado[braco] = (s, diag)
    return resultado, ev["y"]


# --- CMP-S / CMP-0 / CMP-N / CMP-T criterion (pre-registration, section 9) -----------------------


def tolerancias(grade: dict) -> dict:
    """Return, per (cell, arm), the level tolerance and the terms of the ceiling CMP-T.

    ``tol = tol_sem_disc + disc_bloco``: ``tol_sem_disc`` is the token KAT tolerance of the arm's
    sources and ``disc_bloco`` the analytic block bound, both from the SAME functions as the frozen
    analytic table (``fusion_analytic_table``); ``ep_media`` = Hanley-McNeil SE of the fluid AUC
    divided by ``sqrt(n_seeds)``.
    """
    K = grade["K"]
    n_pos = round(grade["pi"] * grade["N"])
    out = {}
    for cel in grade["celulas"]:
        a = fat.analisar(cel, grade)
        for braco in BRACOS:
            disc = fat.disc_bloco(cel, braco, a, K)
            ep = tab.ep_hanley_mcneil(a["A"][braco], n_pos, grade["N"] - n_pos)
            out[(cel["id"], braco)] = {
                "tol_sem_disc": a["TOL"][braco],
                "disc_bloco": disc,
                "tol": a["TOL"][braco] + disc,
                "ep_media": ep / math.sqrt(len(grade["sementes"])),
            }
    return out


def papeis_da_tabela(caminho: Path = TABELA) -> dict:
    """Read the role and the predicted sign of every contrast from the frozen analytic table.

    Returns
    -------
    dict
        ``(cell, "A-B") -> {"papel": "critério" | "critério (nulo)" | "só reportado",
        "sinal": "melhora" | "piora" | "nulo", "prev": printed predicted dAUC}``.
    """
    out = {}
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cel) != 8 or not cel[0].startswith("CMP") or " − " not in cel[1]:
            continue
        a, b = cel[1].split(" − ")
        out[(cel[0], f"{a}-{b}")] = {
            "papel": cel[5],
            "sinal": cel[3].strip("*"),
            "prev": float(cel[2]),
        }
    if len(out) != 5 * 6:
        raise ValueError(f"tabela analítica: {len(out)} contrastes lidos (esperado 30)")
    return out


def _media_var(valores):
    """Return (mean, sample variance with ddof = 1, count) of the values."""
    v = np.asarray(valores, dtype=float)
    return float(np.mean(v)), (float(np.var(v, ddof=1)) if len(v) > 1 else 0.0), len(v)


def avaliar_fusao(linhas, grade: dict, tol: dict, papeis: dict) -> dict:
    """Apply the pre-registered CMP-S / CMP-0 / CMP-N / CMP-T criterion to the result rows.

    CMP-S (contrasts with role "critério"): sign of ``mean(AUC_a) - mean(AUC_b)`` = predicted and
    ``|difference| >= 3 SE``, ``SE = sqrt(v_a / n + v_b / n)`` with ``ddof = 1``; ``|predicted| <
    3 SE`` is a tie (fails for lack of power). CMP-0 (role "critério (nulo)", CMP6 RF - RS):
    ``|difference| <= tol_0``. CMP-N: ``|mean(AUC) - fluid AUC| <= tol`` of the arm, in every
    (cell, arm). CMP-T (outside the verdict): in the saturated ``RF`` arms,
    ``mean(AUC_RF) <= fluid AUC + disc_bloco + 3 ep_media``. Predictions are recomputed from the
    grid (closed form), never read from the rows; the recomputed sign must match the frozen table.
    The unit tests FU1-FU5, also required by the criterion, are run by pytest, not here.
    """
    sementes = sorted(grade["sementes"])
    K = grade["K"]
    aucs: dict[tuple, dict] = {}
    for row in linhas:
        aucs.setdefault((row["celula"], row["braco"]), {})[int(row["semente"])] = float(row["auc"])
    for cel in grade["celulas"]:
        for braco in BRACOS:
            tem = sorted(aucs.get((cel["id"], braco), {}))
            if tem != sementes:
                raise ValueError(f"{cel['id']}/{braco}: seeds {tem} != {sementes}")

    media, var, fluida, n = {}, {}, {}, {}
    por_braco, estouros_n, estouros_t, n_teto = [], 0, 0, 0
    for cel in grade["celulas"]:
        for braco in BRACOS:
            chave = (cel["id"], braco)
            media[chave], var[chave], n[chave] = _media_var([aucs[chave][s] for s in sementes])
            fluida[chave] = auc_fluida_braco(cel, braco, K)
            t = tol[chave]
            desvio = media[chave] - fluida[chave]
            dentro = abs(desvio) <= t["tol"]
            estouros_n += not dentro
            item = {
                "celula": cel["id"],
                "braco": braco,
                "regime": regime_braco(cel, braco, K),
                "media": media[chave],
                "fluida": fluida[chave],
                "desvio": desvio,
                "tol": t["tol"],
                "disc_bloco": t["disc_bloco"],
                "dentro": dentro,
                "delta2_empirico": 2 * float(norm.ppf(media[chave])) ** 2,
                "delta2_fluido": delta2_fluido_braco(cel, braco, K),
            }
            if braco == "RF" and item["regime"] == "sat":
                teto = fluida[chave] + t["disc_bloco"] + 3 * t["ep_media"]
                n_teto += 1
                estouros_t += media[chave] > teto
                item["teto"] = teto
                item["abaixo_do_teto"] = media[chave] <= teto
            por_braco.append(item)

    por_contraste = []
    cont = {"concorda": 0, "discorda": 0, "empate": 0, "sem_significancia": 0}
    n_crit, nulo = 0, None
    for cel in grade["celulas"]:
        for a, b in CONTRASTES:
            nome = f"{a}-{b}"
            p = papeis[(cel["id"], nome)]
            ka, kb = (cel["id"], a), (cel["id"], b)
            dif_prev = fluida[ka] - fluida[kb]
            dif_emp = media[ka] - media[kb]
            ep = math.sqrt(var[ka] / n[ka] + var[kb] / n[kb])
            if p["papel"] == "critério (nulo)":
                if abs(dif_prev) > 1e-12:
                    raise ValueError(f"{cel['id']} {nome}: nulo com ΔAUC previsto {dif_prev:+.2e}")
                estado = "dentro" if abs(dif_emp) <= grade["tol_0"] else "fora"
                nulo = {
                    "passou": estado == "dentro",
                    "celula": cel["id"],
                    "contraste": nome,
                    "dif_empirica": dif_emp,
                    "tol_0": grade["tol_0"],
                }
            else:
                sinal_prev = "melhora" if dif_prev > 0 else "piora"
                if sinal_prev != p["sinal"]:
                    raise ValueError(
                        f"{cel['id']} {nome}: sinal {sinal_prev} != tabela {p['sinal']}"
                    )
                if abs(dif_prev) < 3 * ep:
                    estado = "empate"
                elif np.sign(dif_emp) != np.sign(dif_prev):
                    estado = "discorda"
                elif abs(dif_emp) < 3 * ep:
                    estado = "sem_significancia"
                else:
                    estado = "concorda"
                if p["papel"] == "critério":
                    n_crit += 1
                    cont[estado] += 1
            por_contraste.append(
                {
                    "celula": cel["id"],
                    "contraste": nome,
                    "papel": p["papel"],
                    "dif_prevista": dif_prev,
                    "dif_empirica": dif_emp,
                    "ep_dif": ep,
                    "estado": estado,
                    "sinais_por_semente": [
                        int(np.sign(aucs[ka][s] - aucs[kb][s])) for s in sementes
                    ],
                }
            )
    if nulo is None:
        raise ValueError("tabela sem o contraste nulo")

    cmp_s = {
        "passou": cont["concorda"] == n_crit,
        "contrastes": n_crit,
        "concordam": cont["concorda"],
        "discordantes": cont["discorda"],
        "empates": cont["empate"],
        "sem_significancia": cont["sem_significancia"],
    }
    cmp_n = {"passou": estouros_n == 0, "combos": len(por_braco), "estouros": estouros_n}
    cmp_t = {
        "passou": estouros_t == 0,
        "no_veredito": False,
        "bracos": n_teto,
        "estouros": estouros_t,
    }
    passou = cmp_s["passou"] and nulo["passou"] and cmp_n["passou"]
    return {
        "passou": passou,
        "veredito": "PASSA" if passou else "REPROVA",
        "CMP_S": cmp_s,
        "CMP_0": nulo,
        "CMP_N": cmp_n,
        "CMP_T": cmp_t,
        "testes_de_unidade": (
            "FU1-FU5 (tests/test_fusion.py) are also required by the criterion; they are run by "
            "pytest, not by this evaluator"
        ),
        "por_contraste": por_contraste,
        "por_braco": por_braco,
    }
