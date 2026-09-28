"""Quota family (Corollary 5): window policies over one literal history of events.

The specification is frozen in ``data/prereg/08-quotas-addendum.md``; the grid lives in
``data/quotas_grid.json`` (policies under ``_politicas``). A history is drawn in the order of
``token_kat.simular_literal_tokens`` (labels; Poisson counts users x sources; times;
attributes) and read by EVERY policy (pairing):

- ``REC``: recency cut, the largest suffix of most recent events with cost ``<= K`` (the sealed
  token window);
- ``RHO``: adaptive quotas by ``rho_s = d_s^2 / k_s`` descending (ties: grid order),
  ``n_s = min(N_s, floor(rest / k_s))`` most recent events, the leftover passing to the next
  source (Dantzig greedy on the realized counts);
- ``EVT``: as ``RHO``, ordered by ``d_s^2`` (ignores the cost);
- ``FIXf`` / ``FIXc``: fixed quotas, greedy by rho over the EXPECTED counts with the floor /
  ceiling of ``lam_s T``; leftover not reallocated;
- ``TAX``: fixed quota ``floor(lam_s K / W)``, ``W = sum(lam_r k_r)``;
- ``RHOidade`` (decay cell only): per-event priority ``d_i^2 / k_s`` with
  ``d_i = d_s exp(-(T - t_i) / tau)``, scanned in descending priority, an event included if it
  fits and skipped otherwise.

Every policy depends only on source, time and counts, never on the realized ``x``. The score is
the oracle ``sum d_i (x_i - d_i / 2)`` over the visible events. The module also recomputes the
predictions from the grid (``previsoes``, through the ported analytic table), checks the anchors
(``conferir_ancoras``) and applies the pre-registered criteria (``avaliar_c5``). The simulation
checks algebraic identities of the model against a literal implementation: no exponent, weight
or order of policies is estimated from the data; a pass reads "checked by literal simulation".
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

import displacement as rd
import quotas_analytic_table as qat
import token_kat_analytic_table as tab

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/quotas_grid.json"
CSV_KAT = RAIZ / "output/kat_token/celulas.csv"
POLITICAS_COTA = ("RHO", "EVT", "FIXf", "FIXc", "TAX")
POLITICAS = ("REC", "RHOidade", *POLITICAS_COTA)


def carregar_grade(caminho: Path = GRADE) -> dict:
    """Load the frozen grid of the family (JSON) from ``caminho``."""
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


# --- history ------------------------------------------------------------------------------------


def _custos(k) -> np.ndarray:
    """Return the per-source costs as int64, rejecting a non-positive cost."""
    k = np.asarray(k, dtype=np.int64)
    if np.any(k <= 0):
        raise ValueError("custo por evento tem de ser inteiro positivo")
    return k


def _d_evento(d_fonte, fonte_idx, tempos, T, tau) -> np.ndarray:
    """Return ``d`` of every event: ``d_s`` without decay, ``d_s exp(-(T - t) / tau)`` with it.

    ``tau`` = None or infinity is the case without decay and returns ``d_s`` itself (no
    multiplication), so the generator stays byte-identical to the sealed one.
    """
    d_s = np.asarray(d_fonte, dtype=float)[fonte_idx]
    if tau is None or math.isinf(tau):
        return d_s
    return d_s * np.exp(-(T - np.asarray(tempos, dtype=float)) / tau)


def historia_de_eventos(
    usuario_idx, fonte_idx, tempos, x, y, lam, d, k, T, tau=None, ordem=None
) -> dict:
    """Return a history from its events (any input order); ``N`` = number of labels ``y``.

    ``lam``, ``d`` and ``k`` are per-source sequences, indexed by ``fonte_idx``. ``ordem`` sorts
    the events by user, time and input position (``np.lexsort``, as in the sealed simulation);
    ``ordem_fonte`` by user, source, time and input position, derived from ``ordem`` by a stable
    sort on (user, source). Among equal times, the event that appears LATER in the input is the
    most recent (the recency rule of the sealed window). A caller that already holds ``ordem``
    (``restringir``) may pass it.
    """
    k = _custos(k)
    usuario_idx = np.asarray(usuario_idx, dtype=np.int64)
    fonte_idx = np.asarray(fonte_idx, dtype=np.int64)
    tempos = np.asarray(tempos, dtype=float)
    y = np.asarray(y, dtype=bool)
    N, nf = len(y), len(k)
    grupo = usuario_idx * nf + fonte_idx
    contagens = np.bincount(grupo, minlength=N * nf).reshape(N, nf)
    if ordem is None:
        ordem = np.lexsort((np.arange(len(tempos)), tempos, usuario_idx))
    return {
        "N": N,
        "T": T,
        "tau": tau,
        "lam": [float(v) for v in lam],
        "d_fonte": np.asarray(d, dtype=float),
        "k_fonte": k,
        "y": y,
        "contagens": contagens,
        "usuario_idx": usuario_idx,
        "fonte_idx": fonte_idx,
        "tempos": tempos,
        "x": np.asarray(x, dtype=float),
        "d_evento": _d_evento(d, fonte_idx, tempos, T, tau),
        "custo": k[fonte_idx],
        "ordem": ordem,
        "ordem_fonte": ordem[np.argsort(grupo[ordem], kind="stable")],
    }


def gerar_historia(combo, lam, d, k, T, N, rng, tau=None) -> dict:
    """Draw one history of ``N`` users in the order of ``token_kat.simular_literal_tokens``.

    Labels ``y``; Poisson counts users x sources (sources in the order of ``combo``); uniform
    times in ``[0, T)``; attributes ``x ~ N(d_i y, 1)``. With ``tau`` (decay cell only)
    ``d_i = d_s exp(-(T - t_i) / tau)``; the standardized noise of ``x`` is the same draw as
    without decay (only its mean changes).
    """
    lams = np.array([lam[s] for s in combo])
    d_combo = [d[s] for s in combo]
    k_combo = _custos([k[s] for s in combo])
    nf = len(combo)
    y = rng.random(N) < rd.PI
    contagens = rng.poisson(lams[None, :] * T, size=(N, nf))
    total_eventos = int(contagens.sum())
    usuarios_grid, fontes_grid = np.meshgrid(np.arange(N), np.arange(nf), indexing="ij")
    repeticoes = contagens.ravel()
    usuario_idx = np.repeat(usuarios_grid.ravel(), repeticoes)
    fonte_idx = np.repeat(fontes_grid.ravel(), repeticoes)
    if total_eventos == 0:  # no draw of times or attributes, as in the sealed simulation
        tempos, x = np.zeros(0), np.zeros(0)
    else:
        tempos = rng.uniform(0.0, T, size=total_eventos)
        d_ev = _d_evento(d_combo, fonte_idx, tempos, T, tau)
        x = rng.normal(d_ev * y[usuario_idx].astype(float), 1.0, size=total_eventos)
    lam_combo = [lam[s] for s in combo]
    return historia_de_eventos(
        usuario_idx, fonte_idx, tempos, x, y, lam_combo, d_combo, k_combo, T, tau
    )


def restringir(hist: dict, manter) -> dict:
    """Return the SAME history keeping only the sources ``manter`` (pairing: no new draw).

    The Consequence sub-test reads ``R`` as the history of ``R ∪ S`` without the events of the
    new source: same users, labels, times and attributes.
    """
    manter = list(manter)
    novo = np.full(len(hist["k_fonte"]), -1, dtype=np.int64)
    novo[manter] = np.arange(len(manter))
    m = novo[hist["fonte_idx"]] >= 0
    posicao = np.cumsum(m) - 1  # new input position of every kept event (order preserved)
    ordem = posicao[hist["ordem"][m[hist["ordem"]]]]
    return historia_de_eventos(
        hist["usuario_idx"][m],
        novo[hist["fonte_idx"][m]],
        hist["tempos"][m],
        hist["x"][m],
        hist["y"],
        [hist["lam"][s] for s in manter],
        hist["d_fonte"][manter],
        hist["k_fonte"][manter],
        hist["T"],
        hist["tau"],
        ordem=ordem,
    )


# --- quotas -------------------------------------------------------------------------------------


def _ordem_fontes(chave) -> list[int]:
    """Return the source indices by ``chave`` descending; ties keep the grid order (stable)."""
    return sorted(range(len(chave)), key=lambda i: chave[i], reverse=True)


def cotas_esperadas(politica, lam, d, k, T, K) -> np.ndarray:
    """Return the fixed quota per source of ``FIXf``, ``FIXc`` or ``TAX`` (no count needed).

    ``FIXf`` / ``FIXc``: greedy by rho over the expected counts,
    ``q_s = min(floor or ceil(lam_s T), floor(rest / k_s))``. ``TAX``: ``floor(lam_s K / W)``.
    """
    k = _custos(k)
    if politica == "TAX":
        W = sum(a * b for a, b in zip(lam, k.tolist(), strict=True))
        return np.array([int(math.floor(a * K / W)) for a in lam], dtype=np.int64)
    if politica not in ("FIXf", "FIXc"):
        raise ValueError(f"política {politica!r} não tem cota fixa")
    resto, q = K, np.zeros(len(k), dtype=np.int64)
    for i in _ordem_fontes([d[s] ** 2 / k[s] for s in range(len(k))]):
        v = lam[i] * T
        v = math.floor(v) if politica == "FIXf" else math.ceil(v)
        q[i] = min(int(v), resto // int(k[i]))
        resto -= int(q[i]) * int(k[i])
    return q


def cotas(politica, contagens, lam, d, k, T, K) -> np.ndarray:
    """Return the number of visible events per (user, source) of a quota policy.

    ``RHO`` / ``EVT`` pass the leftover of each source to the next one (on the realized counts);
    ``FIXf``, ``FIXc`` and ``TAX`` cap the realized counts at a fixed quota and never
    reallocate.
    """
    k = _custos(k)
    contagens = np.asarray(contagens, dtype=np.int64)
    if politica in ("RHO", "EVT"):
        if politica == "RHO":
            chave = [d[s] ** 2 / k[s] for s in range(len(k))]
        else:
            chave = [d[s] ** 2 for s in range(len(k))]
        n = np.zeros_like(contagens)
        resto = np.full(len(contagens), K, dtype=np.int64)
        for i in _ordem_fontes(chave):
            n[:, i] = np.minimum(contagens[:, i], resto // k[i])
            resto -= n[:, i] * k[i]
        return n
    q = cotas_esperadas(politica, lam, d, k, T, K)
    return np.minimum(contagens, q[None, :])


# --- windows ------------------------------------------------------------------------------------


def _janela_recencia(hist: dict, K) -> np.ndarray:
    """Return the mask of the recency cut (the sealed token window, vectorised by user)."""
    ordem = hist["ordem"]
    total_por_usuario = hist["contagens"].sum(axis=1)
    custo_ord = hist["custo"][ordem]
    acumulado = np.cumsum(custo_ord)
    fim = np.cumsum(total_por_usuario)
    ultimo_do_bloco = np.repeat(fim - 1, total_por_usuario)
    sufixo = acumulado[ultimo_do_bloco] - acumulado + custo_ord  # cost of the suffix from here
    visivel = np.zeros(len(ordem), dtype=bool)
    visivel[ordem] = sufixo <= K
    return visivel


def _janela_por_cotas(hist: dict, n) -> np.ndarray:
    """Return the mask keeping the ``n[user, source]`` MOST RECENT events of each source."""
    m, o = len(hist["tempos"]), hist["ordem_fonte"]  # user, source, time, input position
    tam = hist["contagens"].ravel()  # groups (user, source) in the order of ``o``
    pos = np.arange(m) - np.repeat(np.cumsum(tam) - tam, tam)
    corte = np.repeat(tam - np.asarray(n, dtype=np.int64).ravel(), tam)
    visivel = np.zeros(m, dtype=bool)
    visivel[o] = pos >= corte
    return visivel


def _janela_rho_idade(hist: dict, K) -> np.ndarray:
    """Return the mask of RHOidade: scan by ``d_i^2 / k`` descending; include if it fits.

    Ties of priority (measure zero with continuous times) go to the more recent event.
    """
    m, N = len(hist["tempos"]), hist["N"]
    prio = hist["d_evento"] ** 2 / hist["custo"]
    posto = np.empty(m, dtype=np.int64)
    posto[hist["ordem"]] = np.arange(m)  # recency rank (higher = more recent)
    o = np.lexsort((-posto, -prio, hist["usuario_idx"]))
    tot = hist["contagens"].sum(axis=1)
    pos = np.arange(m) - np.repeat(np.cumsum(tot) - tot, tot)
    u = hist["usuario_idx"][o]
    largura = int(tot.max()) if N and m else 0
    custo = np.zeros((N, largura), dtype=np.int64)
    valido = np.zeros((N, largura), dtype=bool)
    custo[u, pos] = hist["custo"][o]
    valido[u, pos] = True
    incluido = np.zeros((N, largura), dtype=bool)
    resto = np.full(N, K, dtype=np.int64)
    for j in range(largura):
        cabe = valido[:, j] & (custo[:, j] <= resto)
        incluido[:, j] = cabe
        resto -= np.where(cabe, custo[:, j], 0)
    visivel = np.zeros(m, dtype=bool)
    visivel[o] = incluido[u, pos]
    return visivel


def janela(politica, hist: dict, K) -> np.ndarray:
    """Return the boolean mask (input order of the events) of the window of ``politica``."""
    if politica == "REC":
        return _janela_recencia(hist, K)
    if politica == "RHOidade":
        return _janela_rho_idade(hist, K)
    if politica in POLITICAS_COTA:
        n = cotas(
            politica,
            hist["contagens"],
            hist["lam"],
            hist["d_fonte"],
            hist["k_fonte"],
            hist["T"],
            K,
        )
        return _janela_por_cotas(hist, n)
    raise ValueError(f"política desconhecida: {politica!r}")


def escores(hist: dict, visivel) -> np.ndarray:
    """Return the oracle score ``sum d_i (x_i - d_i / 2)`` of every user over the visible events.

    The sum runs in the order user, time, input position, as in the sealed simulation (the REC
    scores are then byte-identical to it).
    """
    ordem = hist["ordem"]
    indices = ordem[np.asarray(visivel, dtype=bool)[ordem]]
    d_ev = hist["d_evento"]
    contrib = d_ev * (hist["x"] - d_ev / 2)
    return np.bincount(hist["usuario_idx"][indices], weights=contrib[indices], minlength=hist["N"])


def medidas(hist: dict, visivel, K) -> dict:
    """Return per-user diagnostics of a window: ``D``, visible cost and visible counts.

    ``d_usuario`` is ``D = sum d_i^2`` over the visible events (the variance and the mean gap of
    the oracle score); without decay it is computed from the visible counts per source, so equal
    compositions give the same float in every policy.
    """
    visivel = np.asarray(visivel, dtype=bool)
    N, nf = hist["N"], len(hist["k_fonte"])
    u, f = hist["usuario_idx"][visivel], hist["fonte_idx"][visivel]
    n_vis = np.bincount(u * nf + f, minlength=N * nf).reshape(N, nf)
    if hist["tau"] is None or math.isinf(hist["tau"]):
        D = n_vis @ (hist["d_fonte"] ** 2)
    else:
        ordem = hist["ordem"]
        idx = ordem[visivel[ordem]]
        D = np.bincount(hist["usuario_idx"][idx], weights=hist["d_evento"][idx] ** 2, minlength=N)
    return {
        "d_usuario": D,
        "custo_visivel": n_vis @ hist["k_fonte"],
        "n_visivel": n_vis,
        "custo_total": hist["contagens"] @ hist["k_fonte"],
    }


# --- predictions (ported frozen generator) -------------------------------------------------------


def auc_exata_r(fa: dict, T, K) -> float:
    """Return the exact AUC of the current mix ``R = {A}`` (one source, window of K // k events).

    Same arithmetic as the Consequence block of the frozen generator.
    """
    L = K // fa["k"]
    sA, pA = qat.pois_support(fa["lam"] * T)
    acc = {}
    for n, p in zip(sA, pA, strict=True):
        D = round(min(int(n), L) * fa["d"] ** 2, 10)
        acc[D] = acc.get(D, 0) + p
    u = np.array(sorted(acc))
    pu = np.array([acc[v] for v in u])
    pu /= pu.sum()
    return float(
        np.sum(pu[:, None] * pu[None, :] * qat.Phi_arr(np.sqrt(u[:, None] + u[None, :]) / 2))
    )


def previsoes(grade: dict) -> dict:
    """Recompute from the grid, at full precision, every prediction the criteria use.

    Exact AUC of each policy in each cell (the frozen analytic table prints the same numbers
    rounded), the Consequence of the host cell, the fluid decay cell (with ``tol_F``) and the
    rival's gain without decay.
    """
    K = grade["K"]
    exata, fluida = {}, {}
    for cel in grade["celulas"]:
        fs, T = qat.fontes(cel), cel["T"]
        if cel["id"] == "DEC1":
            rec, nom, otm, _, _ = qat.dec_fluido(fs, T, K, cel["tau"])
            decaimento = {
                "REC": tab.auc(rec),
                "RHO": tab.auc(nom),
                "RHOidade": tab.auc(otm),
                "tol_F": grade["tol_base_r1"] + qat.disc(fs, T, K, rec) + grade["tol_X"],
                "ganho_sem_decaimento": tab.auc(qat.d2_guloso_fluido(fs, T, K, qat.rho))
                - tab.auc(tab.delta2(fs, T, K)),
            }
            continue
        qf, qc = qat.cotas_fix(fs, T, K, "f"), qat.cotas_fix(fs, T, K, "c")
        exata[cel["id"]] = {
            "REC": qat.auc_exata_rec(fs, T, K),
            "RHO": qat.auc_exata_contagens(fs, T, K, "RHO"),
            "EVT": qat.auc_exata_contagens(fs, T, K, "EVT"),
            "TAX": qat.auc_exata_contagens(fs, T, K, "TAX"),
            "FIXf": qat.auc_exata_cotas(fs, T, qf),
            "FIXc": qat.auc_exata_cotas(fs, T, qc),
        }
        fluida[cel["id"]] = {
            "REC": tab.auc(tab.delta2(fs, T, K)),
            "RHO": tab.auc(qat.d2_guloso_fluido(fs, T, K, qat.rho)),
            "EVT": tab.auc(qat.d2_guloso_fluido(fs, T, K, qat.dd)),
        }
    cq = grade["consequencia"]["celula"]
    cel_cq = next(c for c in grade["celulas"] if c["id"] == cq)
    (fa,) = qat.fontes(cel_cq, "R")
    auc_r = auc_exata_r(fa, cel_cq["T"], K)
    return {
        "exata": exata,
        "fluida": fluida,
        "decaimento": decaimento,
        "consequencia": {
            "auc_R": auc_r,
            "delta_RHO": exata[cq]["RHO"] - auc_r,
            "delta_REC": exata[cq]["REC"] - auc_r,
        },
    }


# --- anchors and pre-registered criteria --------------------------------------------------------


def conferir_ancoras(linhas, grade: dict, caminho_csv: Path = CSV_KAT) -> dict:
    """Check the declared anchors with ``repr`` equality, row by row.

    The REC AUC of each anchor cell, per seed, must equal both the value frozen in the grid
    (``ancora.auc_rec_por_semente``) and the ``auc`` column of the sealed token-KAT row of the
    same seed (cell ``ancora.celula_kat``, combination ``ancora.combo_kat``), read by code.
    """
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        seladas = {
            (r["celula"], r["combo"], int(r["semente"])): r["auc"] for r in csv.DictReader(f)
        }
    rec = {
        (r["celula"], int(r["semente"])): float(r["auc"])
        for r in linhas
        if r["historia"] == "RS" and r["politica"] == "REC"
    }
    detalhes = []
    for cel in grade["celulas"]:
        if "ancora" not in cel:
            continue
        an = cel["ancora"]
        for s, valor in zip(grade["sementes"], an["auc_rec_por_semente"], strict=True):
            obtido = rec.get((cel["id"], s))
            selada = seladas.get((an["celula_kat"], an["combo_kat"], s))
            ok = obtido is not None and repr(obtido) == repr(valor) == selada
            detalhes.append(
                {
                    "celula": cel["id"],
                    "semente": s,
                    "auc_rec": obtido,
                    "grade": valor,
                    "selada": selada,
                    "igual": ok,
                }
            )
    return {"aplicavel": True, "passou": all(x["igual"] for x in detalhes), "linhas": detalhes}


def _pareada(a: dict, b: dict, sementes) -> tuple[list[float], float, float]:
    """Return (differences per seed, mean, paired SE = sd with ddof = 1 over sqrt(n))."""
    dif = [a[s] - b[s] for s in sementes]
    ep = float(np.std(dif, ddof=1)) / math.sqrt(len(dif)) if len(dif) > 1 else 0.0
    return dif, float(np.mean(dif)), ep


def _sinal(v) -> int:
    """Return the sign of ``v`` as -1, 0 or +1."""
    return (v > 0) - (v < 0)


def avaliar_c5(linhas, grade: dict, prev: dict, ancoras: dict) -> dict:
    """Apply the pre-registered criteria (section 9 of the addendum) to the result rows.

    C5-O (sign of every strict comparison of the discriminating cells; ``|predicted| < 3
    SE_paired`` is a tie and fails), C5-G (``|mean - predicted| <= tol_X`` in every declared
    comparison of those cells and of the equivalence cell; ``3 SE_paired > tol_X`` is a
    comparison without power and fails), C5-C (Consequence), C5-N (level, secondary) and the
    boundary block C5-D (sign only). ``tol_X`` is the fixed grid constant, never recomputed from
    the data. Predictions come from ``prev`` (recomputed from the grid), never from the rows.
    """
    sementes = sorted(grade["sementes"])
    tolX = grade["tol_X"]
    auc: dict[tuple, dict] = {}
    for r in linhas:
        auc.setdefault((r["celula"], r["historia"], r["politica"]), {})[int(r["semente"])] = float(
            r["auc"]
        )
    cq = grade["consequencia"]["celula"]
    esperadas = [
        (cel["id"], "RS", p)
        for cel in grade["celulas"]
        for p in cel.get("politicas", grade["politicas"])
    ] + [(cq, "R", "REC"), (cq, "R", "RHO")]
    for chave in esperadas:
        tem = sorted(auc.get(chave, {}))
        if tem != sementes:
            raise ValueError(f"{'/'.join(chave)}: sementes {tem} ≠ {sementes}")

    comparacoes = []
    for cel in grade["celulas"]:
        cid = cel["id"]
        fonte = prev["decaimento"] if cid == "DEC1" else prev["exata"][cid]
        for cp in cel["comparacoes"]:
            x, y = cp["par"]
            dif, media, ep = _pareada(auc[(cid, "RS", x)], auc[(cid, "RS", y)], sementes)
            previsto = fonte[x] - fonte[y]
            tol = prev["decaimento"]["tol_F"] if cid == "DEC1" else tolX
            c = {
                "celula": cid,
                "par": [x, y],
                "tipo": cp["tipo"],
                "criterios": list(cp["criterios"]),
                "previsto": previsto,
                "media": media,
                "ep_par": ep,
                "difs_por_semente": dif,
                "sinais_por_semente": [_sinal(v) for v in dif],
                "tol": tol,
                "dentro_tol": abs(media - previsto) <= tol,
                "sem_poder": 3 * ep > tolX,
                "rival": cp["rival"],
                "rival_preve": cp["rival_preve"],
                "refuta_rival": cp["refuta_rival"],
            }
            if cp["tipo"] == "estrita":
                if abs(previsto) < 3 * ep:
                    c["estado_sinal"] = "empate"
                elif _sinal(media) != _sinal(previsto):
                    c["estado_sinal"] = "discorda"
                else:
                    c["estado_sinal"] = "concorda"
            c["passa_C5-O"] = (
                c.get("estado_sinal") == "concorda" if "C5-O" in c["criterios"] else None
            )
            c["passa_C5-G"] = (
                c["dentro_tol"] and not c["sem_poder"] if "C5-G" in c["criterios"] else None
            )
            c["passa_C5-D"] = (
                c.get("estado_sinal") == "concorda" if "C5-D" in c["criterios"] else None
            )
            criterio_rival = cp["refuta_rival"]
            c["rival_refutado"] = bool(c.get(f"passa_{criterio_rival}")) if criterio_rival else None
            comparacoes.append(c)

    def resumo(nome):
        """Return the pass/fail summary of the comparisons under criterion ``nome``."""
        sob = [c for c in comparacoes if c[f"passa_{nome}"] is not None]
        return sob, all(c[f"passa_{nome}"] for c in sob)

    sob_o, passa_o = resumo("C5-O")
    sob_g, passa_g = resumo("C5-G")
    sob_d, passa_d = resumo("C5-D")

    # Consequence (host cell): R -> R ∪ S under RHO (predicted 0) and under REC
    pc = prev["consequencia"]
    cons = {}
    for pol, previsto in (("RHO", 0.0), ("REC", pc["delta_REC"])):
        dif, media, ep = _pareada(auc[(cq, "RS", pol)], auc[(cq, "R", pol)], sementes)
        cons[pol] = {
            "previsto": previsto,
            "previsto_exato": pc[f"delta_{pol}"],
            "media": media,
            "ep_par": ep,
            "difs_por_semente": dif,
            "sinais_por_semente": [_sinal(v) for v in dif],
            "dentro_tol": abs(media - previsto) <= tolX,
            "sem_poder": 3 * ep > tolX,
        }
    cons["REC"]["sinal_negativo"] = cons["REC"]["media"] < 0
    passa_c = (
        cons["RHO"]["dentro_tol"]
        and not cons["RHO"]["sem_poder"]
        and cons["REC"]["sinal_negativo"]
        and cons["REC"]["dentro_tol"]
        and not cons["REC"]["sem_poder"]
    )
    cons["rival"] = grade["consequencia"]["rival"]
    cons["rival_refutado"] = passa_c

    # C5-N: level of every (cell, policy) with an exact prediction
    niveis = []
    for cid, pols in prev["exata"].items():
        for pol, exata in pols.items():
            media = float(np.mean([auc[(cid, "RS", pol)][s] for s in sementes]))
            niveis.append(
                {
                    "celula": cid,
                    "politica": pol,
                    "media": media,
                    "exata": exata,
                    "desvio": media - exata,
                    "dentro_tol": abs(media - exata) <= tolX,
                }
            )
    passa_n = all(v["dentro_tol"] for v in niveis)

    criterios = {
        "ancoras": {"passou": bool(ancoras.get("passou"))},
        "C5-O": {
            "passou": passa_o,
            "comparacoes": len(sob_o),
            "discordantes": sum(c["estado_sinal"] == "discorda" for c in sob_o),
            "empates": sum(c["estado_sinal"] == "empate" for c in sob_o),
        },
        "C5-G": {
            "passou": passa_g,
            "comparacoes": len(sob_g),
            "estouros": sum(not c["dentro_tol"] for c in sob_g),
            "sem_poder": sum(c["sem_poder"] for c in sob_g),
        },
        "C5-C": {"passou": passa_c},
        "C5-N": {
            "passou": passa_n,
            "niveis": len(niveis),
            "estouros": sum(not v["dentro_tol"] for v in niveis),
        },
        "C5-D": {
            "passou": passa_d,
            "comparacoes": len(sob_d),
            "discordantes": sum(c["estado_sinal"] == "discorda" for c in sob_d),
            "empates": sum(c["estado_sinal"] == "empate" for c in sob_d),
        },
    }
    return {
        "comparacoes": comparacoes,
        "consequencia": cons,
        "niveis": niveis,
        "criterios": criterios,
        "veredito": _veredito(criterios, comparacoes),
    }


def _veredito(criterios: dict, comparacoes: list) -> dict:
    """Return the family verdict and the outcome rows of section 10 that apply.

    ``passou`` = anchors, C5-O, C5-G, C5-C and C5-N all pass ("Tudo passa"); C5-D is a block
    with its own verdict. Row labels are the pre-registered ones, verbatim.
    """
    ok = {n: c["passou"] for n, c in criterios.items()}
    tudo = ok["ancoras"] and ok["C5-O"] and ok["C5-G"] and ok["C5-C"] and ok["C5-N"]
    falhas = [c for c in comparacoes if c["passa_C5-O"] is False or c["passa_C5-G"] is False]
    desfechos = []
    if tudo:
        desfechos.append("Tudo passa")
        if ok["C5-D"]:
            desfechos.append("C5-D passa (com o acima)")
    if not ok["C5-D"]:
        desfechos.append("C5-D reprova")
    if any(c["celula"] == "FIX1" for c in falhas):
        desfechos.append("FIX1 reprova (C5-O/C5-G)")
    knp3 = {tuple(c["par"]) for c in falhas if c["celula"] == "KNP3"}
    if knp3 == {("REC", "EVT")}:
        desfechos.append("KNP3 reprova só em REC − EVT")
    if any(c["celula"] == "NUL1" for c in falhas):
        desfechos.append("NUL1 reprova")
    if not ok["C5-C"]:
        desfechos.append("C5-C reprova")
    if any(c["celula"] in ("KNP1", "KNP2") and c["passa_C5-O"] is False for c in comparacoes):
        desfechos.append("C5-O reprova em KNP1 ou KNP2")
    if not ok["C5-N"] and ok["C5-O"] and ok["C5-G"] and ok["C5-C"]:
        desfechos.append("Só C5-N reprova")
    return {
        "passou": bool(tudo),
        "C5-D_passou": bool(ok["C5-D"]),
        "desfechos": desfechos,
        "testes_de_unidade": (
            "UT-1 to UT-6 live in tests/test_quotas.py (pytest), not in this runner"
        ),
    }
