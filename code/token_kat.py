"""Token KAT: a window defined by a token budget, with heterogeneous per-event cost.

The specification is frozen in ``data/prereg/02-token-kat-addendum.md``; the grid lives in
``data/kat_token_grid.json``. The module extends the displacement replication WITHOUT editing it:
``displacement.py`` is only imported (prevalence, Mann-Whitney AUC, recency rule). The
orchestration of the grid lives in ``run_token_kat.py``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

import displacement as rd

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/kat_token_grid.json"


def carregar_grade(caminho: Path = GRADE) -> dict:
    """Load the pre-registered grid (JSON) from ``caminho``."""
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def fontes_da_celula(cel: dict, combo: str) -> dict:
    """Return the sources of ``R`` (combo "R") or of ``R ∪ S`` (combo "RS"), in grid order.

    Returns
    -------
    dict
        ``name -> {"lam": ..., "d": ..., "k": ...}``.
    """
    if combo not in ("R", "RS"):
        raise ValueError(f"combo {combo!r}: use 'R' ou 'RS'")
    fontes = dict(cel["R"])
    if combo == "RS":
        ((nome_S, p_S),) = cel["S"].items()
        if nome_S in fontes:
            raise ValueError(f"célula {cel['id']}: fonte nova {nome_S} já está em R")
        fontes[nome_S] = p_S
    return fontes


# --- fluid closed form (specification of the theory, docs/THEORY.md) ----------------------------


def delta2_fluido(fontes: dict, T, K) -> float:
    """Return the fluid ``Delta^2 = h * sum(lam d^2)`` with ``h = min(T, K / sum(lam k))``.

    Independent of the analytic table (KT3 compares the two).
    """
    W = sum(p["lam"] * p["k"] for p in fontes.values())
    if W == 0:
        return 0.0
    h = min(T, K / W)
    return h * sum(p["lam"] * p["d"] ** 2 for p in fontes.values())


def auc_fluida(fontes: dict, T, K) -> float:
    """Return the fluid AUC ``Phi(sqrt(Delta^2) / sqrt(2))`` (scipy normal CDF, verbatim)."""
    return float(norm.cdf(math.sqrt(delta2_fluido(fontes, T, K)) / math.sqrt(2)))


# --- token-budget window ------------------------------------------------------------------------


def janela_tokens(tempos, custos, K) -> np.ndarray:
    """Return the LONGEST suffix of most recent events whose summed cost is ``<= K``.

    Indices come in increasing order of recency. The sort by time is stable: among equal times,
    the event that appears LATER in the input is the most recent (the recency rule of
    ``janela_ultimos``). Only whole events: the event that would overflow the budget drops out
    together with every older one, with no partial event and no skipping to fit an older and
    cheaper event.
    """
    tempos = np.asarray(tempos)
    custos = np.asarray(custos, dtype=np.int64)
    ordem = np.argsort(tempos, kind="stable")
    # cost of the suffix that starts at each position (cost > 0 => decreasing => visible = suffix)
    sufixo = np.cumsum(custos[ordem][::-1])[::-1]
    return ordem[sufixo <= K]


def simular_literal_tokens(combo, lam, d, k, T, N, rng, K):
    """Simulate literally with a window of ``K`` tokens.

    The order of draws is the one of ``displacement.simular_literal`` (y; Poisson counts
    users x sources; times; attributes) and the score is the same oracle; only the window rule
    changes.

    Returns
    -------
    tuple
        ``(scores, y, diag)``; ``diag = {"n_saturados": users whose history costs more than K,
        "soma_ociosos": sum of (K - visible tokens) over the saturated users}``.
    """
    y = rng.random(N) < rd.PI
    nf = len(combo)
    lams = np.array([lam[s] for s in combo])
    d_combo = np.array([d[s] for s in combo])
    k_combo = np.array([k[s] for s in combo], dtype=np.int64)
    if np.any(k_combo <= 0):
        raise ValueError("custo por evento tem de ser inteiro positivo")

    contagens = rng.poisson(lams[None, :] * T, size=(N, nf))
    total_por_usuario = contagens.sum(axis=1)
    total_eventos = int(total_por_usuario.sum())
    if total_eventos == 0:
        return np.zeros(N), y, {"n_saturados": 0, "soma_ociosos": 0}

    usuarios_grid, fontes_grid = np.meshgrid(np.arange(N), np.arange(nf), indexing="ij")
    repeticoes = contagens.ravel()
    usuario_idx = np.repeat(usuarios_grid.ravel(), repeticoes)
    fonte_idx = np.repeat(fontes_grid.ravel(), repeticoes)

    tempos = rng.uniform(0.0, T, size=total_eventos)
    x = rng.normal(d_combo[fonte_idx] * y[usuario_idx].astype(float), 1.0, size=total_eventos)

    # sort by user, then time, then input order (recency tie-break), as in the replication
    idx_original = np.arange(total_eventos)
    ordem = np.lexsort((idx_original, tempos, usuario_idx))

    custo_ord = k_combo[fonte_idx[ordem]]
    acumulado = np.cumsum(custo_ord)  # int64, exact
    fim = np.cumsum(total_por_usuario)
    ultimo_do_bloco = np.repeat(fim - 1, total_por_usuario)  # position of the user's newest event
    sufixo = acumulado[ultimo_do_bloco] - acumulado + custo_ord  # cost of the suffix starting here
    visivel = sufixo <= K

    indices_visiveis = ordem[visivel]
    contrib = d_combo[fonte_idx] * (x - d_combo[fonte_idx] / 2)
    scores = np.bincount(
        usuario_idx[indices_visiveis], weights=contrib[indices_visiveis], minlength=N
    )

    custo_total = np.bincount(usuario_idx, weights=k_combo[fonte_idx], minlength=N)
    custo_visivel = np.bincount(
        usuario_idx[indices_visiveis], weights=k_combo[fonte_idx][indices_visiveis], minlength=N
    )
    saturados = custo_total > K
    diag = {
        "n_saturados": int(saturados.sum()),
        "soma_ociosos": int(round(float(np.sum(K - custo_visivel[saturados])))),
    }
    return scores, y, diag


# --- KT-S / KT-N criterion (addendum, "Critério de aprovação") ----------------------------------


def _media_var(valores):
    """Return (mean, sample variance with ddof=1, count) of the values."""
    v = np.asarray(valores, dtype=float)
    return float(np.mean(v)), (float(np.var(v, ddof=1)) if len(v) > 1 else 0.0), len(v)


def avaliar_kat(linhas, grade: dict, tolerancias: dict) -> dict:
    """Apply the pre-registered KT-S / KT-N criterion.

    KT-S: the sign of ``mean(AUC(R ∪ S)) - mean(AUC(R))`` equals the predicted sign in the 8
    cells; a tie (``|predicted| < 3 SE`` of the difference, between-seed variance with
    ``ddof = 1``) fails for lack of power. KT-N: ``|mean(AUC) - fluid AUC| <= tolerancias[(cell,
    combo)]`` in every combination. Predictions are recomputed from the grid, never read from
    the rows.
    """
    sementes = sorted(grade["sementes"])
    aucs: dict[tuple, dict] = {}
    for row in linhas:
        aucs.setdefault((row["celula"], row["combo"]), {})[row["semente"]] = float(row["auc"])
    for cel in grade["celulas"]:
        for combo in ("R", "RS"):
            tem = sorted(aucs.get((cel["id"], combo), {}))
            if tem != sementes:
                raise ValueError(f"célula {cel['id']}/{combo}: sementes {tem} ≠ {sementes}")

    por_celula, discordantes, empates, estouros = [], 0, 0, 0
    for cel in grade["celulas"]:
        prev = {c: auc_fluida(fontes_da_celula(cel, c), cel["T"], grade["K"]) for c in ("R", "RS")}
        m, v, n = {}, {}, {}
        for c in ("R", "RS"):
            m[c], v[c], n[c] = _media_var([aucs[(cel["id"], c)][s] for s in sementes])
        dif_prev = prev["RS"] - prev["R"]
        dif_emp = m["RS"] - m["R"]
        ep = math.sqrt(v["RS"] / n["RS"] + v["R"] / n["R"])
        if abs(dif_prev) < 3 * ep:
            estado_sinal = "empate"
            empates += 1
        elif np.sign(dif_emp) != np.sign(dif_prev):
            estado_sinal = "discorda"
            discordantes += 1
        else:
            estado_sinal = "concorda"
        nivel = {}
        for c in ("R", "RS"):
            desvio = m[c] - prev[c]
            ok = abs(desvio) <= tolerancias[(cel["id"], c)]
            estouros += not ok
            nivel[c] = {
                "media": m[c],
                "fluida": prev[c],
                "desvio": desvio,
                "tol": tolerancias[(cel["id"], c)],
                "dentro": ok,
                "delta2_empirico": 2 * float(norm.ppf(m[c])) ** 2,
                "delta2_fluido": delta2_fluido(fontes_da_celula(cel, c), cel["T"], grade["K"]),
            }
        sinais_semente = [
            int(np.sign(aucs[(cel["id"], "RS")][s] - aucs[(cel["id"], "R")][s])) for s in sementes
        ]
        por_celula.append(
            {
                "celula": cel["id"],
                "regime": cel["bloco"],
                "dif_prevista": dif_prev,
                "dif_empirica": dif_emp,
                "ep_dif": ep,
                "sinal": estado_sinal,
                "sinais_por_semente": sinais_semente,
                "nivel": nivel,
            }
        )

    kt_s = {
        "passou": discordantes == 0 and empates == 0,
        "celulas": len(grade["celulas"]),
        "discordantes": discordantes,
        "empates": empates,
    }
    kt_n = {"passou": estouros == 0, "combos": 2 * len(grade["celulas"]), "estouros": estouros}
    return {
        "passou": kt_s["passou"] and kt_n["passou"],
        "KT_S": kt_s,
        "KT_N": kt_n,
        "por_celula": por_celula,
    }
