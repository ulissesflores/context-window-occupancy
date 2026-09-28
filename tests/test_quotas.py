"""TDD of the quota family (Corollary 5): adaptive quotas by rho against the recency cut.

Specification frozen in ``data/prereg/08-quotas-addendum.md`` (section 11): UT-1 (identity with
the sealed token simulation), UT-2 (policies), UT-3 (exact prediction), UT-4 (pairing), UT-5
(age decay), UT-6 (independence of ``x``, tag and declared streams), plus the anchors and the
evaluator of the pre-registered criteria C5-O, C5-G, C5-C, C5-N and C5-D.
"""

import csv
import hashlib
import itertools
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import displacement as rd
import quotas as qt
import quotas_analytic_table as qat
import run_quotas as rq
import token_kat as kt

RAIZ = Path(__file__).resolve().parents[1]
GRADE = RAIZ / "data/quotas_grid.json"
TABELA = RAIZ / "data/prereg/quotas_analytic_table.txt"
SCRIPT_TABELA = RAIZ / "code/quotas_analytic_table.py"
CSV_KAT = RAIZ / "output/kat_token/celulas.csv"
# sha256 of the frozen grid and analytic table (byte-identical to the private frozen originals)
SHA_GRADE = "b0a82de2a4690143996d5bdf196bd91f44e75e9c774c0515b7a9c767ba97a42b"
SHA_TABELA = "a206f1555df554e761b5d9212451ac65ac3bb2082ff765ad7c4b885697569189"
# streams of section 9 of the pre-registration, written here by hand (never read from the grid):
# (i_celula, i_combo, tag) of default_rng([seed, i_celula, i_combo, tag, i_block])
FLUXOS_S9 = {
    "KNP1": (0, 1, 3),
    "KNP2": (3, 1, 3),
    "KNP3": (2, 0, 8),
    "FIX1": (3, 0, 8),
    "NUL1": (0, 1, 3),
    "DEC1": (0, 1, 3),
}
TODAS = ("REC", "RHO", "EVT", "TAX", "FIXf", "FIXc", "RHOidade")


def _sha(p):
    """Return the sha256 hex digest of the bytes of ``p``."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _celula(g, cid):
    """Return ``(index, cell)`` of the cell ``cid`` of the grid ``g``."""
    return next((i, c) for i, c in enumerate(g["celulas"]) if c["id"] == cid)


def _params(cel, historia="RS"):
    """Return ``(combo, lam, d, k)`` of the sources of a cell, in grid order."""
    fontes = kt.fontes_da_celula(cel, historia)
    return (
        "".join(fontes),
        {n: p["lam"] for n, p in fontes.items()},
        {n: p["d"] for n, p in fontes.items()},
        {n: p["k"] for n, p in fontes.items()},
    )


def _um_usuario(tempos, fonte, lam, d, k, T=100.0, tau=None, x=None):
    """Return a one-user history built by hand (events in input order)."""
    n = len(tempos)
    return qt.historia_de_eventos(
        usuario_idx=np.zeros(n, dtype=np.int64),
        fonte_idx=np.asarray(fonte, dtype=np.int64),
        tempos=np.asarray(tempos, dtype=float),
        x=np.zeros(n) if x is None else np.asarray(x, dtype=float),
        y=np.zeros(1, dtype=bool),
        lam=lam,
        d=d,
        k=k,
        T=T,
        tau=tau,
    )


def _vis(politica, hist, K):
    """Return the visible event indices (input order) of ``politica`` on ``hist``."""
    return np.flatnonzero(qt.janela(politica, hist, K)).tolist()


class _RngTempoArredondado:
    """Delegate to a numpy Generator, rounding the uniform draws of time to force ties."""

    def __init__(self, semente):
        """Wrap ``numpy.random.default_rng(semente)``."""
        self._g = np.random.default_rng(semente)

    def uniform(self, *args, **kwargs):
        """Return the uniform draws rounded to whole days (ties of time become frequent)."""
        return np.round(self._g.uniform(*args, **kwargs), 0)

    def __getattr__(self, nome):
        """Delegate every other draw to the wrapped Generator, in the same order."""
        return getattr(self._g, nome)


# --- pins -----------------------------------------------------------------------------------------


def test_pinos_congelados():
    """Pin the sha256 of the frozen grid and of the frozen analytic table."""
    assert _sha(GRADE) == SHA_GRADE, "grid changed after freezing"
    assert _sha(TABELA) == SHA_TABELA, "analytic table changed after freezing"


# --- UT-3: exact prediction -----------------------------------------------------------------------


def test_ut3_tabela_analitica_portada_reproduz_byte_a_byte():
    """Check UT-3: the ported generator passes its design criteria and reproduces the table."""
    r = subprocess.run(
        [sys.executable, str(SCRIPT_TABELA)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHON_COLORS": "0", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert r.returncode == 0, (
        f"analytic table failed a design criterion: {r.stderr.strip().splitlines()[-1:]}"
    )
    assert r.stdout == TABELA.read_text(encoding="utf-8"), "ported analytic table != frozen file"


def _auc_atomos(D, p):
    """Return ``sum_i sum_j p_i p_j Phi(sqrt(D_i + D_j) / 2)`` over the atoms ``(D, p)``."""
    D = np.asarray(D, dtype=float)
    p = np.asarray(p, dtype=float)
    p = p / p.sum()
    fi = np.vectorize(lambda v: 0.5 * (1 + math.erf(v / math.sqrt(2))))
    return float(np.sum(p[:, None] * p[None, :] * fi(np.sqrt(D[:, None] + D[None, :]) / 2)))


def test_ut3_rec_hipergeometrica_igual_binomial_com_k_homogeneo():
    """Check UT-3: with homogeneous cost the hypergeometric recency equals the binomial form.

    With one cost ``k`` the window is the last ``L = K // k`` events; the marks of a Poisson
    superposition are iid with ``P(A) = lam_A / (lam_A + lam_C)``, so the composition of the
    window is ``Binomial(min(N, L), P(A))`` with ``N ~ Poisson((lam_A + lam_C) T)``.
    """
    T, K, k = 10.0, 14 * 25, 14
    fs = [dict(lam=2.0, d=0.3, k=k), dict(lam=3.0, d=0.1, k=k)]
    exata = qat.auc_exata_rec(fs, T, K)
    mu = (fs[0]["lam"] + fs[1]["lam"]) * T
    pA = fs[0]["lam"] / (fs[0]["lam"] + fs[1]["lam"])
    L = K // k
    D, p = [], []
    for n in range(0, int(mu + 14 * math.sqrt(mu))):
        pn = math.exp(n * math.log(mu) - mu - math.lgamma(n + 1))
        m = min(n, L)
        for a in range(m + 1):
            D.append(a * fs[0]["d"] ** 2 + (m - a) * fs[1]["d"] ** 2)
            p.append(pn * math.comb(m, a) * pA**a * (1 - pA) ** (m - a))
    assert abs(exata - _auc_atomos(D, p)) <= 1e-9, "UT-3: hypergeometric recency != binomial"


@pytest.mark.parametrize("kA,kC,K", [(14, 55, 100), (55, 14, 100), (14, 55, 150), (55, 14, 70)])
def test_ut3_rec_hipergeometrica_igual_forca_bruta(monkeypatch, kA, kC, K):
    """Check UT-3: the exact recency equals brute force over ALL orderings of small histories.

    The Poisson support is replaced by a single point ``(N_A, N_C)`` (probability 1), so the
    exact predictor gives the AUC of the conditional distribution; brute force enumerates every
    distinct ordering of ``N_A`` events of A and ``N_C`` of C (all equally likely) and applies
    the sealed token window.
    """
    d = (0.3, 0.2)
    for NA, NC in [(0, 3), (3, 0), (2, 4), (6, 6), (5, 1), (1, 6), (6, 2), (4, 4)]:
        fs = [dict(lam=1.0, d=d[0], k=kA), dict(lam=2.0, d=d[1], k=kC)]

        def suporte(mu, sd_mult=9, NA=NA, NC=NC):
            """Return a one-point support: ``N_A`` for source A (mean 1), ``N_C`` otherwise."""
            return np.array([NA if mu == 1.0 else NC]), np.array([1.0])

        monkeypatch.setattr(qat, "pois_support", suporte)
        exata = qat.auc_exata_rec(fs, 1.0, K)
        N = NA + NC
        D, p = [], []
        for posicoes_A in itertools.combinations(range(N), NA):
            fonte = np.ones(N, dtype=np.int64)
            fonte[list(posicoes_A)] = 0
            custos = np.where(fonte == 0, kA, kC)
            vis = kt.janela_tokens(np.arange(N, dtype=float), custos, K)
            D.append(float(sum(d[f] ** 2 for f in fonte[vis])))
            p.append(1.0)
        assert abs(exata - _auc_atomos(D, p)) <= 1e-12, (
            f"UT-3: exact recency != brute force at N_A={NA}, N_C={NC}, k=({kA},{kC}), K={K}"
        )


def _tabela():
    """Parse the frozen analytic table: exact AUCs, quotas, comparisons and Consequence."""
    celulas, comps, texto = {}, {}, TABELA.read_text(encoding="utf-8")
    for row in texto.splitlines():
        if not row.startswith("| ") or row.startswith("| célula") or row.startswith("| q_A"):
            continue
        c = [x.strip() for x in row.strip("|").split("|")]
        if len(c) == 19 and c[0] in FLUXOS_S9:
            celulas[c[0]] = {
                "auc": dict(
                    zip(("REC", "RHO", "EVT", "TAX", "FIXf", "FIXc"), c[12:18], strict=True)
                ),
                "cotas": [json.loads(q) for q in c[18].split(" · ")],
            }
        elif len(c) == 19 and c[0].startswith("DEC1"):
            celulas["DEC1"] = {
                "auc": {"REC": c[12], "RHO": c[13].split()[0], "RHOidade": c[18].split()[1]}
            }
        elif len(c) == 12:
            comps[(c[0], c[1])] = c[3]
    return celulas, comps, texto


@pytest.fixture(scope="module")
def prev():
    """Return the predictions recomputed from the grid (computed once per module)."""
    return qt.previsoes(qt.carregar_grade())


def test_ut3_previsoes_do_runner_reproduzem_a_tabela(prev):
    """Check that the predictions used by the evaluator round to the numbers of the table."""
    celulas, _, texto = _tabela()
    for cid, linha in celulas.items():
        fonte = prev["decaimento"] if cid == "DEC1" else prev["exata"][cid]
        for pol, valor in linha["auc"].items():
            assert f"{fonte[pol]:.5f}" == valor, f"prediction {cid}/{pol} != table"
    cq = prev["consequencia"]
    assert f"AUC(R) REC = RHO = {cq['auc_R']:.5f}" in texto
    assert f"ΔAUC_RHO(R -> R ∪ S) = {qat.s(cq['delta_RHO'])} " in texto
    assert f"ΔAUC_REC(R -> R ∪ S) = {qat.s(cq['delta_REC'])} " in texto
    assert f"= {prev['decaimento']['tol_F']:.5f} (nível" in texto


def test_cotas_fixas_e_proporcionais_iguais_a_tabela():
    """Check FIXf, FIXc and TAX fixed quotas against the ``cotas`` column of the frozen table."""
    g = qt.carregar_grade()
    celulas, _, _ = _tabela()
    for cel in g["celulas"]:
        if cel["id"] == "DEC1":
            continue
        _, lam, d, k = _params(cel)
        obtido = [
            qt.cotas_esperadas(p, list(lam.values()), list(d.values()), list(k.values()),
                               cel["T"], g["K"]).tolist()
            for p in ("FIXf", "FIXc", "TAX")
        ]  # fmt: skip
        assert obtido == celulas[cel["id"]]["cotas"], f"{cel['id']}: quotas != table"


# --- UT-1: identity with the sealed token simulation ---------------------------------------------


@pytest.mark.parametrize(
    "lam,T",
    [
        ({"A": 6.0, "C": 3.0}, 30),  # saturated (tokens ~ 7470 > 2048)
        ({"A": 0.5, "C": 0.3}, 30),  # unsaturated (tokens ~ 705)
        ({"A": 1.2, "C": 0.5}, 180),  # sources of cell KNP1
    ],
)
def test_ut1_rec_escores_byte_identicos_ao_simular_literal_tokens(lam, T):
    """Check UT-1: same rng -> the REC path returns scores byte-identical to the sealed path.

    Times are rounded to whole days, which forces many ties of time.
    """
    d, k, K, N = {"A": 0.12, "C": 0.17}, {"A": 14, "C": 55}, 2048, 800
    s_ref, y_ref, _ = kt.simular_literal_tokens("AC", lam, d, k, T, N, _RngTempoArredondado(5), K)
    hist = qt.gerar_historia("AC", lam, d, k, T, N, _RngTempoArredondado(5))
    pares = np.stack([hist["usuario_idx"], hist["tempos"]], axis=1)
    assert len(pares) - len(np.unique(pares, axis=0)) > 50, "the test needs ties of time"
    assert np.array_equal(hist["y"], y_ref), "UT-1: labels differ (order of draws)"
    s = qt.escores(hist, qt.janela("REC", hist, K))
    assert s.tobytes() == s_ref.tobytes(), "UT-1: REC scores not byte-identical to the sealed path"


# --- UT-2: policies on histories written by hand --------------------------------------------------

# two sources: A (rho = 0.09/14 = 0.00643, d^2 = 0.09), C (rho = 0.25/55 = 0.00455, d^2 = 0.25)
LAM2, D2, CUSTO2 = [1.0, 1.0], [0.3, 0.5], [14, 55]


def test_ut2_rho_passa_a_sobra_a_fonte_seguinte():
    """Check UT-2: RHO fills A (higher rho) and gives the leftover to C, most recent first."""
    h = _um_usuario([1, 2, 3, 4, 5, 6], [0, 0, 0, 1, 1, 1], LAM2, D2, CUSTO2)
    # A: 3 events (42 tokens), leftover 58 -> one event of C (the most recent, t = 6)
    assert _vis("RHO", h, 100) == [0, 1, 2, 5], "UT-2: RHO does not pass the leftover to C"
    # recency: t = 6 (55 tokens) fits, t = 5 would reach 110 > 100
    assert _vis("REC", h, 100) == [5]


def test_ut2_rho_pega_os_mais_recentes_da_fonte():
    """Check UT-2: the quota of a source takes its MOST RECENT events, never the oldest."""
    h = _um_usuario([10, 1, 7, 3, 9, 2], [0, 0, 0, 0, 0, 1], LAM2, D2, CUSTO2)
    # 50 // 14 = 3 events of A: the most recent are t = 10, 9, 7
    assert _vis("RHO", h, 50) == [0, 2, 4], "UT-2: quota does not keep the most recent events"


def test_ut2_evt_ordena_por_d2_e_rho_por_rho():
    """Check UT-2: EVT fills by d^2 (C first); RHO by rho (A first)."""
    h = _um_usuario([1, 2, 3, 4, 5, 6], [0, 0, 0, 1, 1, 1], LAM2, D2, CUSTO2)
    assert _vis("EVT", h, 120) == [4, 5], "UT-2: EVT is not ordered by d^2"
    assert _vis("RHO", h, 120) == [0, 1, 2, 5], "UT-2: RHO is not ordered by rho"


def test_ut2_rho_continua_depois_de_fonte_que_nao_cabe():
    """Check UT-2: RHO skips a source that does not fit and CONTINUES with the next one."""
    lam_tres, d_tres, custo_tres = [1.0, 1.0, 1.0], [0.4, 0.4, 0.1], [14, 55, 14]  # rho: X > Y > Z
    h = _um_usuario([1, 2, 3, 4, 5, 6], [0, 0, 1, 1, 2, 2], lam_tres, d_tres, custo_tres)
    # X: 2 events (28), leftover 22: Y (55) does not fit, Z takes 22 // 14 = 1 (t = 6)
    assert _vis("RHO", h, 50) == [0, 1, 5], "UT-2: RHO stops at the first source that does not fit"


def test_ut2_empate_de_rho_segue_a_ordem_da_grade():
    """Check UT-2: equal rho (exact in floating point) is broken by the grid order."""
    lam, d, k = [1.0, 1.0], [0.2, 0.4], [16, 64]  # rho = 0.04/16 = 0.16/64
    assert d[0] ** 2 / k[0] == d[1] ** 2 / k[1]
    h = _um_usuario([1, 2, 3, 4], [0, 0, 1, 1], lam, d, k)
    assert _vis("RHO", h, 64) == [0, 1], "UT-2: rho tie not broken by grid order (A first)"
    # grid order reversed: the source of cost 64 comes first and takes 64 // 64 = 1 event (t = 4);
    # breaking the tie the other way would keep the two events of cost 16 instead
    h_inv = _um_usuario([1, 2, 3, 4], [1, 1, 0, 0], lam[::-1], d[::-1], k[::-1])
    assert _vis("RHO", h_inv, 64) == [3], "UT-2: rho tie not broken by grid order (C first)"


def test_ut2_cotas_fixas_nunca_excedem_e_nao_realocam():
    """Check UT-2: FIXf, FIXc and TAX never exceed the quota and never reallocate the leftover."""
    lam, d, k, T, K = [0.02, 2.3], [1.0, 0.08], [14, 14], 90, 2048  # sources of cell FIX1
    assert qt.cotas_esperadas("FIXf", lam, d, k, T, K).tolist() == [1, 145]
    assert qt.cotas_esperadas("FIXc", lam, d, k, T, K).tolist() == [2, 144]
    contagens = np.array([[0, 300], [5, 300], [1, 10], [3, 100]])
    for pol in ("FIXf", "FIXc", "TAX"):
        q = qt.cotas_esperadas(pol, lam, d, k, T, K)
        n = qt.cotas(pol, contagens, lam, d, k, T, K)
        assert np.array_equal(n, np.minimum(contagens, q[None, :])), f"UT-2: {pol} != min(N, q)"
    # A has no event: RHO gives its budget to C (146), FIXf does NOT (145)
    assert qt.cotas("FIXf", contagens, lam, d, k, T, K)[0].tolist() == [0, 145]
    assert qt.cotas("RHO", contagens, lam, d, k, T, K)[0].tolist() == [0, 146]
    # TAX: q_s = floor(lam_s K / W), W = sum(lam_r k_r)
    W = sum(a * b for a, b in zip(lam, k, strict=True))
    esperado = [math.floor(a * K / W) for a in lam]
    assert qt.cotas_esperadas("TAX", lam, d, k, T, K).tolist() == esperado


# budget policies: a history with cost <= K is returned whole BY CONSTRUCTION
ORCAMENTO = ("REC", "RHO", "EVT", "RHOidade")
FIXAS = ("FIXf", "FIXc", "TAX")


def test_ut2_historia_que_cabe_politicas_de_orcamento_devolvem_tudo():
    """Check UT-2: a history with cost <= K is returned whole by REC, RHO, EVT and RHOidade."""
    h = _um_usuario([5, 1, 3, 2], [0, 1, 0, 1], LAM2, D2, CUSTO2, T=10.0, tau=5.0)
    for pol in ORCAMENTO:
        assert _vis(pol, h, 200) == [0, 1, 2, 3], f"UT-2: {pol} drops events of a history <= K"


def test_ut2_cota_fixa_devolve_tudo_so_dentro_das_cotas():
    """Check UT-2: FIXf, FIXc and TAX return the whole history iff ``N_s <= q_s`` in every source.

    With ``T = 10`` and ``K = 200``: FIXf = FIXc = [10, 1] (rho greedy over the expected counts
    10, 10), TAX = [2, 2] (``floor(200 / 69)``). A history within the quotas is returned whole.
    """
    for pol, q in (("FIXf", [10, 1]), ("FIXc", [10, 1]), ("TAX", [2, 2])):
        assert qt.cotas_esperadas(pol, LAM2, D2, CUSTO2, 10.0, 200).tolist() == q, pol
    h = _um_usuario([5, 2, 3], [0, 1, 0], LAM2, D2, CUSTO2, T=10.0)
    for pol in FIXAS:
        assert _vis(pol, h, 200) == [0, 1, 2], f"UT-2: {pol} drops events within its quotas"


def test_ut2_cota_fixa_corta_historia_que_cabe():
    """Check UT-2 (finding): a fixed quota cuts a history with cost <= K when ``N_s > q_s``.

    By the literal definition of section 4 (fixed quota from the EXPECTED counts, leftover not
    reallocated) the fixed-quota policies are NOT an identity without saturation: they cut the
    OLDEST events of a source above its quota, even when the whole history fits in ``K``.
    """
    # cost 2*14 + 2*55 = 138 <= 200, but FIXf/FIXc give C a quota of 1: the older C (t = 1) drops
    h = _um_usuario([5, 1, 3, 2], [0, 1, 0, 1], LAM2, D2, CUSTO2, T=10.0)
    for pol in ("FIXf", "FIXc"):
        assert _vis(pol, h, 200) == [0, 2, 3], f"UT-2: {pol} does not cap C at its quota"
    # cost 3*14 + 55 = 97 <= 200, but TAX gives A a quota of 2: the oldest A (t = 1) drops
    h_tax = _um_usuario([4, 1, 3, 2], [0, 0, 0, 1], LAM2, D2, CUSTO2, T=10.0)
    assert _vis("TAX", h_tax, 200) == [0, 2, 3], "UT-2: TAX does not cap A at its quota"
    assert _vis("REC", h_tax, 200) == [0, 1, 2, 3]


def test_ut2_custo_exatamente_K_cabe():
    """Check UT-2: a history whose cost is EXACTLY K is visible whole (``<=``, never ``<``)."""
    h = _um_usuario([1, 2, 3], [0, 0, 1], LAM2, D2, CUSTO2, T=10.0, tau=5.0)
    for pol in ORCAMENTO:
        assert _vis(pol, h, 2 * 14 + 55) == [0, 1, 2], f"UT-2: {pol} drops a history of cost K"


def test_ut2_cota_fixa_com_orcamento_exato():
    """Check UT-2: a fixed quota that closes the budget EXACTLY is kept (``<=``, never ``<``).

    With ``T = 10`` and ``K = 10 * 14 + 55 = 195``: A (higher rho) takes ``min(10, 195 // 14) =
    10`` events (140 tokens) and the rest, 55, fits exactly one event of C.
    """
    K = 10 * 14 + 55
    for pol in ("FIXf", "FIXc"):
        q = qt.cotas_esperadas(pol, LAM2, D2, CUSTO2, 10.0, K).tolist()
        assert q == [10, 1], f"UT-2: {pol} drops a quota that fits the budget exactly ({q})"


def test_ut2_historia_vazia_janela_vazia():
    """Check UT-2: an empty history gives an empty window and a zero score."""
    h = _um_usuario([], [], LAM2, D2, CUSTO2, tau=5.0)
    for pol in TODAS:
        assert _vis(pol, h, 100) == [], f"UT-2: {pol} on an empty history"
        assert qt.escores(h, qt.janela(pol, h, 100)).tolist() == [0.0]


def test_ut2_custo_nao_positivo_e_erro():
    """Check UT-2: a non-positive cost per event is an error."""
    with pytest.raises(ValueError):
        _um_usuario([1, 2], [0, 1], LAM2, D2, [0, 55])
    with pytest.raises(ValueError):
        qt.cotas("RHO", np.array([[1, 1]]), LAM2, D2, [14, -1], 100, 2048)
    with pytest.raises(ValueError):
        qt.gerar_historia("AC", {"A": 1, "C": 1}, {"A": 0.1, "C": 0.1}, {"A": 14, "C": 0}, 10, 5,
                          np.random.default_rng(0))  # fmt: skip


def test_ut2_rho_idade_inclui_se_cabe_senao_pula():
    """Check UT-2: RHOidade scans by d_i^2/k, includes an event if it fits, otherwise SKIPS it."""
    d, k, T, tau = [0.12, 0.17], [14, 55], 180.0, 60.0
    # priorities: A at age 1 > C at age 2 > A at age 170
    h = _um_usuario([179, 178, 10], [0, 1, 0], [1.2, 0.5], d, k, T=T, tau=tau)
    # K = 60: A (14, rest 46), C (55 > 46: skipped), old A (14 <= 46: included)
    assert _vis("RHOidade", h, 60) == [0, 2], "UT-2: RHOidade stops instead of skipping"
    # with decay a recent C outranks an old A: K = 55 keeps only the C
    h2 = _um_usuario([10, 178], [0, 1], [1.2, 0.5], d, k, T=T, tau=tau)
    assert _vis("RHOidade", h2, 55) == [1], "UT-2: RHOidade does not use the age of the event"
    assert _vis("RHO", h2, 55) == [0], "UT-2: RHO in the decay cell uses the nominal rho"


def _janela_referencia(pol, tempos, fonte, lam, d, k, T, K, tau):
    """Apply the literal definition of section 4 to ONE user; return the visible indices.

    Written independently of the module, event by event.
    """
    n, nf = len(tempos), len(k)
    recencia = sorted(range(n), key=lambda i: (tempos[i], i))  # old -> new; tie: later = newer
    posto = {i: r for r, i in enumerate(recencia)}
    if pol == "REC":
        vis, custo = [], 0
        for i in reversed(recencia):
            if custo + k[fonte[i]] > K:
                break
            custo += k[fonte[i]]
            vis.append(i)
        return sorted(vis)
    if pol == "RHOidade":

        def prio(i):
            """Return the priority d_i^2 / k of event ``i``."""
            di = d[fonte[i]] * (1.0 if tau is None else math.exp(-(T - tempos[i]) / tau))
            return di**2 / k[fonte[i]]

        vis, resto = [], K
        for i in sorted(range(n), key=lambda i: (-prio(i), -posto[i])):
            if k[fonte[i]] <= resto:
                vis.append(i)
                resto -= k[fonte[i]]
        return sorted(vis)
    N_s = [sum(1 for f in fonte if f == s) for s in range(nf)]
    rho = [d[s] ** 2 / k[s] for s in range(nf)]
    if pol in ("RHO", "EVT"):
        chave = rho if pol == "RHO" else [d[s] ** 2 for s in range(nf)]
        resto, n_s = K, [0] * nf
        for s in sorted(range(nf), key=lambda s: -chave[s]):
            n_s[s] = min(N_s[s], resto // k[s])
            resto -= n_s[s] * k[s]
    elif pol in ("FIXf", "FIXc"):
        resto, q = K, [0] * nf
        for s in sorted(range(nf), key=lambda s: -rho[s]):
            v = lam[s] * T
            q[s] = min(int(math.floor(v) if pol == "FIXf" else math.ceil(v)), resto // k[s])
            resto -= q[s] * k[s]
        n_s = [min(a, b) for a, b in zip(N_s, q, strict=True)]
    else:  # TAX
        W = sum(lam[s] * k[s] for s in range(nf))
        n_s = [min(N_s[s], int(math.floor(lam[s] * K / W))) for s in range(nf)]
    vis = []
    for s in range(nf):
        eventos = [i for i in recencia if fonte[i] == s]
        vis += eventos[len(eventos) - n_s[s] :]
    return sorted(vis)


@pytest.mark.parametrize("tau", [None, 40.0])
def test_vetorizado_igual_a_referencia_por_usuario(tau):
    """Check every vectorised policy against the literal per-user reference (3 sources, ties)."""
    lam = {"A": 0.6, "B": 0.4, "C": 1.1}
    d = {"A": 0.3, "B": 0.5, "C": 0.1}
    k = {"A": 14, "B": 55, "C": 28}
    T, K, N = 30.0, 280, 300
    h = qt.gerar_historia("ABC", lam, d, k, T, N, _RngTempoArredondado(11), tau=tau)
    L, D, C = list(lam.values()), list(d.values()), list(k.values())
    for pol in TODAS:
        vis = qt.janela(pol, h, K)
        custo = np.bincount(h["usuario_idx"][vis], weights=h["custo"][vis], minlength=N)
        assert np.all(custo <= K), f"{pol}: visible cost above K"
        for u in range(N):
            ev = np.flatnonzero(h["usuario_idx"] == u)
            ref = _janela_referencia(
                pol, h["tempos"][ev].tolist(), h["fonte_idx"][ev].tolist(), L, D, C, T, K, tau
            )
            assert np.flatnonzero(vis[ev]).tolist() == ref, f"{pol}: user {u} != reference"


# --- UT-4: pairing --------------------------------------------------------------------------------


def test_ut4_uma_historia_por_bloco_lida_por_todas_as_politicas(monkeypatch):
    """Check UT-4: one history per block, read by every policy; R is R ∪ S without C."""
    g = qt.carregar_grade()
    g["N"], g["bloco_usuarios"] = 600, 300
    i, cel = _celula(g, "KNP1")
    geradas, lidas = [], []
    gerar, janela = qt.gerar_historia, qt.janela

    def gerar_espiao(*args, **kwargs):
        """Record every history drawn."""
        geradas.append(gerar(*args, **kwargs))
        return geradas[-1]

    def janela_espiao(pol, hist, K):
        """Record which history each policy reads."""
        lidas.append((pol, hist))
        return janela(pol, hist, K)

    monkeypatch.setattr(qt, "gerar_historia", gerar_espiao)
    monkeypatch.setattr(qt, "janela", janela_espiao)
    out = rq._uma_tarefa((i, cel, 1, g))
    assert len(geradas) == 2, f"UT-4: {len(geradas)} histories drawn for 2 blocks (pairing broken)"
    lidas_rs = {pol for pol, h in lidas if any(h is x for x in geradas)}
    assert lidas_rs >= set(g["politicas"]), "UT-4: some policy does not read the drawn history"
    for x in geradas:
        n_lidas = sum(1 for _, h in lidas if h is x)
        assert n_lidas >= len(g["politicas"]), "UT-4: a block history is not read by every policy"
    # the history of R is the drawn history of R ∪ S without the events of C
    s_r, y_r = [], []
    for h in geradas:
        hr = qt.restringir(h, [0])
        so_a = h["fonte_idx"] == 0
        assert np.array_equal(hr["tempos"], h["tempos"][so_a]), "UT-4: R has other times"
        assert np.array_equal(hr["x"], h["x"][so_a]), "UT-4: R has other attributes"
        assert np.array_equal(hr["y"], h["y"]), "UT-4: R has other labels"
        s_r.append(qt.escores(hr, janela("REC", hr, g["K"])))
        y_r.append(h["y"])
    linha_r = next(r for r in out["linhas"] if r["historia"] == "R" and r["politica"] == "REC")
    assert linha_r["auc"] == rd.auc_mann_whitney(np.concatenate(s_r), np.concatenate(y_r)), (
        "UT-4: the R of the Consequence is not the drawn R ∪ S without C"
    )


def test_ordens_derivadas_iguais_ao_lexsort():
    """Check that the derived orders (by source; of the restricted history) equal ``np.lexsort``."""
    lam, d, k = (
        {"A": 3.0, "B": 1.0, "C": 2.0},
        {"A": 0.1, "B": 0.2, "C": 0.3},
        {"A": 14, "B": 5, "C": 55},
    )
    h = qt.gerar_historia("ABC", lam, d, k, 30.0, 500, _RngTempoArredondado(2))
    for H in (h, qt.restringir(h, [0, 2]), qt.restringir(h, [1])):
        pos = np.arange(len(H["tempos"]))
        assert np.array_equal(H["ordem"], np.lexsort((pos, H["tempos"], H["usuario_idx"])))
        assert np.array_equal(
            H["ordem_fonte"], np.lexsort((pos, H["tempos"], H["fonte_idx"], H["usuario_idx"]))
        ), "derived order by source != lexsort"


def test_ut4_consequencia_rho_em_r_uniao_s_igual_rec_em_r():
    """Check UT-4: in KNP1, with N_A >= 146, the RHO window of R ∪ S is the REC window of R."""
    g = qt.carregar_grade()
    _, cel = _celula(g, "KNP1")
    combo, lam, d, k = _params(cel)
    h = qt.gerar_historia(combo, lam, d, k, cel["T"], 400, np.random.default_rng(9))
    assert np.all(h["contagens"][:, 0] >= 146)
    hr = qt.restringir(h, [0])
    vis_rs = np.flatnonzero(qt.janela("RHO", h, g["K"]))
    vis_r = np.flatnonzero(qt.janela("REC", hr, g["K"]))
    assert np.array_equal(np.flatnonzero(h["fonte_idx"] == 0)[vis_r], vis_rs), (
        "UT-4: RHO(R ∪ S) and REC(R) differ although every user has N_A >= 146"
    )


# --- UT-5: age decay ------------------------------------------------------------------------------


def test_ut5_tau_infinito_byte_identico_ao_sem_decaimento():
    """Check UT-5: tau = infinity gives a byte-identical generator and byte-identical scores."""
    lam, d, k = {"A": 1.2, "C": 0.5}, {"A": 0.12, "C": 0.17}, {"A": 14, "C": 55}
    h0 = qt.gerar_historia("AC", lam, d, k, 180, 500, np.random.default_rng(3))
    hi = qt.gerar_historia("AC", lam, d, k, 180, 500, np.random.default_rng(3), tau=math.inf)
    for chave in ("y", "usuario_idx", "fonte_idx", "tempos", "x", "d_evento"):
        assert h0[chave].tobytes() == hi[chave].tobytes(), f"UT-5: {chave} differs at tau = inf"
    for pol in ("REC", "RHO", "RHOidade"):
        s0 = qt.escores(h0, qt.janela(pol, h0, 2048))
        si = qt.escores(hi, qt.janela(pol, hi, 2048))
        assert s0.tobytes() == si.tobytes(), f"UT-5: {pol} scores differ at tau = inf"


def test_ut5_oraculo_usa_o_d_do_evento_e_o_mesmo_ruido():
    """Check UT-5: with decay, x ~ N(d_i y, 1), the oracle uses d_i and D = sum of d_i^2."""
    lam, d, k = {"A": 1.2, "C": 0.5}, {"A": 0.12, "C": 0.17}, {"A": 14, "C": 55}
    T, tau, N, K = 180.0, 60.0, 300, 2048
    h = qt.gerar_historia("AC", lam, d, k, T, N, np.random.default_rng(4), tau=tau)
    h0 = qt.gerar_historia("AC", lam, d, k, T, N, np.random.default_rng(4))
    di = np.array([0.12, 0.17])[h["fonte_idx"]] * np.exp(-(T - h["tempos"]) / tau)
    assert np.allclose(h["d_evento"], di, rtol=0, atol=1e-15), "UT-5: d_i != d_s exp(-a/tau)"
    u = h["usuario_idx"]
    assert np.array_equal(h["tempos"], h0["tempos"]) and np.array_equal(h["y"], h0["y"])
    z = h["x"] - di * h["y"][u]
    z0 = h0["x"] - h0["d_evento"] * h0["y"][u]
    assert np.allclose(z, z0, rtol=0, atol=1e-12), "UT-5: decay changes the standardized noise"
    for pol in ("REC", "RHO", "RHOidade"):
        vis = qt.janela(pol, h, K)
        s = qt.escores(h, vis)
        esperado = np.bincount(u[vis], weights=(di * (h["x"] - di / 2))[vis], minlength=N)
        assert np.allclose(s, esperado, rtol=0, atol=1e-12), f"UT-5: {pol} oracle without d_i"
        D = qt.medidas(h, vis, K)["d_usuario"]
        D_esperado = np.bincount(u[vis], weights=(di**2)[vis], minlength=N)
        assert np.allclose(D, D_esperado, rtol=0, atol=1e-12), f"UT-5: {pol} D != sum d_i^2"


# --- UT-6: independence of x, tag and declared streams --------------------------------------------


@pytest.mark.parametrize("tau", [None, 60.0])
def test_ut6_permutar_x_dentro_da_fonte_nao_muda_janela(tau):
    """Check UT-6: permuting x within (user, source) changes no window of any policy."""
    lam, d, k = {"A": 1.2, "C": 0.5}, {"A": 0.12, "C": 0.17}, {"A": 14, "C": 55}
    T, K, N = 180.0, 2048, 300
    h = qt.gerar_historia("AC", lam, d, k, T, N, np.random.default_rng(6), tau=tau)
    chave = h["usuario_idx"] * 2 + h["fonte_idx"]
    rng = np.random.default_rng(7)
    x_perm = h["x"].copy()
    x_perm[np.lexsort((np.arange(len(chave)), chave))] = h["x"][
        np.lexsort((rng.random(len(chave)), chave))
    ]
    assert not np.array_equal(x_perm, h["x"])
    h2 = qt.historia_de_eventos(
        h["usuario_idx"], h["fonte_idx"], h["tempos"], x_perm, h["y"],
        [1.2, 0.5], [0.12, 0.17], [14, 55], T, tau,
    )  # fmt: skip
    for pol in TODAS:
        assert np.array_equal(qt.janela(pol, h, K), qt.janela(pol, h2, K)), (
            f"UT-6: the window of {pol} depends on x"
        )


def test_ut6_tag_exclusivo_e_fluxos_declarados():
    """Check UT-6: tag 8 outside {3, 5, 6, 7}; every declared stream = section 9."""
    g = qt.carregar_grade()
    assert g["tag"] == 8 and g["tag"] not in {3, 5, 6, 7}, "UT-6: tag of the family"
    assert sorted(g["tags_reservados"].values()) == [3, 5, 6, 7]
    assert "tag_r3" not in json.dumps(g), "UT-6: a new grid never has the key tag_r3"
    for cel in g["celulas"]:
        fl = cel["fluxo"]
        assert (fl["i_celula"], fl["i_combo"], fl["tag"]) == FLUXOS_S9[cel["id"]], cel["id"]
    gk = kt.carregar_grade()
    for cid, cid_kat in (("KNP1", "S1a"), ("KNP2", "S2b")):
        i_kat, cel_kat = _celula(gk, cid_kat)
        assert FLUXOS_S9[cid] == (i_kat, 1, gk["tag_r3"]), f"{cid}: anchor stream != KAT"
        _, cel = _celula(g, cid)
        assert (cel["R"], cel["S"], cel["T"]) == (cel_kat["R"], cel_kat["S"], cel_kat["T"])


@pytest.mark.parametrize("cid", list(FLUXOS_S9))
def test_ut6_runner_usa_o_fluxo_declarado(cid):
    """Check UT-6: the runner draws with ``default_rng([seed, *stream of section 9, block])``."""
    g = qt.carregar_grade()
    g["N"], g["bloco_usuarios"] = 400, 200
    i, cel = _celula(g, cid)
    out = rq._uma_tarefa((i, cel, 2, g))
    combo, lam, d, k = _params(cel)
    s, y = [], []
    for b in range(2):
        rng = np.random.default_rng([2, *FLUXOS_S9[cid], b])
        if "tau" in cel:
            h = qt.gerar_historia(combo, lam, d, k, cel["T"], 200, rng, tau=cel["tau"])
            s.append(qt.escores(h, qt.janela("REC", h, g["K"])))
            y.append(h["y"])
        else:
            sb, yb, _ = kt.simular_literal_tokens(combo, lam, d, k, cel["T"], 200, rng, g["K"])
            s.append(sb)
            y.append(yb)
    linha = next(r for r in out["linhas"] if r["historia"] == "RS" and r["politica"] == "REC")
    assert linha["auc"] == rd.auc_mann_whitney(np.concatenate(s), np.concatenate(y)), (
        f"UT-6: runner does not use the declared stream of {cid}"
    )


# --- anchors --------------------------------------------------------------------------------------


def test_ancora_knp1_semente_0_reproduz_a_linha_selada_do_kat():
    """Check the anchor end to end: KNP1 REC at the pre-registered N, seed 0 = sealed KAT row."""
    g = qt.carregar_grade()
    i, cel = _celula(g, "KNP1")
    out = rq._uma_tarefa((i, {**cel, "politicas": ["REC"]}, 0, g))
    linha = next(r for r in out["linhas"] if r["historia"] == "RS" and r["politica"] == "REC")
    with open(CSV_KAT, newline="", encoding="utf-8") as f:
        selada = next(
            r
            for r in csv.DictReader(f)
            if (r["celula"], r["combo"], r["semente"]) == ("S1a", "RS", "0")
        )
    assert repr(linha["auc"]) == selada["auc"], "anchor: KNP1 REC != sealed KAT row S1a/RS/0"
    assert repr(linha["auc"]) == repr(cel["ancora"]["auc_rec_por_semente"][0])


def test_conferir_ancoras_aceita_as_seladas_e_recusa_um_digito():
    """Check the anchor check: sealed values pass; one changed last digit fails."""
    g = qt.carregar_grade()
    linhas = [
        {"celula": c["id"], "historia": "RS", "politica": "REC", "semente": s, "auc": a}
        for c in g["celulas"]
        if "ancora" in c
        for s, a in zip(g["sementes"], c["ancora"]["auc_rec_por_semente"], strict=True)
    ]
    assert qt.conferir_ancoras(linhas, g, CSV_KAT)["passou"]
    linhas[3] = {**linhas[3], "auc": np.nextafter(linhas[3]["auc"], 1.0)}
    assert not qt.conferir_ancoras(linhas, g, CSV_KAT)["passou"], "anchor: one ulp must fail"


# --- evaluator of the pre-registered criteria -----------------------------------------------------


def _linhas(g, prev, ajuste=None):
    """Return synthetic rows: AUC = prediction + a per-seed shift common to every policy.

    The common shift keeps every paired difference equal to its prediction; ``ajuste`` edits
    single AUCs as ``ajuste(cell, history, policy, seed, auc) -> auc``.
    """
    ajuste = ajuste or (lambda c, h, p, s, a: a)
    linhas = []
    for cel in g["celulas"]:
        base = prev["decaimento"] if cel["id"] == "DEC1" else prev["exata"][cel["id"]]
        for pol in cel.get("politicas", g["politicas"]):
            for s in g["sementes"]:
                a = ajuste(cel["id"], "RS", pol, s, base[pol] + 0.001 * s)
                linhas.append(dict(celula=cel["id"], historia="RS", politica=pol, semente=s, auc=a))
    cq = g["consequencia"]["celula"]
    for pol in ("REC", "RHO"):
        for s in g["sementes"]:
            a = ajuste(cq, "R", pol, s, prev["consequencia"]["auc_R"] + 0.001 * s)
            linhas.append(dict(celula=cq, historia="R", politica=pol, semente=s, auc=a))
    return linhas


def _comp(av, cid, par):
    """Return the evaluated comparison ``par`` of cell ``cid``."""
    return next(c for c in av["comparacoes"] if c["celula"] == cid and c["par"] == list(par))


def test_avaliador_aprova_quando_tudo_bate(prev):
    """Check that the evaluator approves rows equal to the predictions (every criterion)."""
    g = qt.carregar_grade()
    av = qt.avaliar_c5(_linhas(g, prev), g, prev, {"passou": True})
    for nome in ("C5-O", "C5-G", "C5-C", "C5-N", "C5-D"):
        assert av["criterios"][nome]["passou"], nome
    assert av["veredito"]["passou"]
    assert "Tudo passa" in av["veredito"]["desfechos"]
    assert "C5-D passa (com o acima)" in av["veredito"]["desfechos"]
    _, comps, _ = _tabela()
    for c in av["comparacoes"]:
        assert qat.s(c["previsto"]) == comps[(c["celula"], " − ".join(c["par"]))], c["par"]


def test_avaliador_reprova_discordancia_de_sinal(prev):
    """Check that a paired difference of the wrong sign fails C5-O (KNP1 RHO - REC)."""
    g = qt.carregar_grade()
    rec = prev["exata"]["KNP1"]["REC"]

    def aj(c, h, p, s, a):
        """Put RHO of KNP1 below REC."""
        return rec - 0.03 + 0.001 * s if (c, h, p) == ("KNP1", "RS", "RHO") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    assert _comp(av, "KNP1", ("RHO", "REC"))["estado_sinal"] == "discorda"
    assert not av["criterios"]["C5-O"]["passou"] and not av["veredito"]["passou"]
    assert "C5-O reprova em KNP1 ou KNP2" in av["veredito"]["desfechos"]


def test_avaliador_reprova_empate_por_falta_de_poder(prev):
    """Check that ``|predicted| < 3 SE_paired`` is a tie and fails C5-O (KNP3 REC - EVT)."""
    g = qt.carregar_grade()
    ruido = [0.02, -0.02, 0.02, -0.02, 0.0]

    def aj(c, h, p, s, a):
        """Add large seed noise to EVT of KNP3."""
        return a + ruido[s] if (c, h, p) == ("KNP3", "RS", "EVT") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    assert _comp(av, "KNP3", ("REC", "EVT"))["estado_sinal"] == "empate"
    assert not av["criterios"]["C5-O"]["passou"]


def test_avaliador_reprova_estouro_de_tamanho(prev):
    """Check that ``|mean - predicted| > tol_X`` fails C5-G (KNP2 TAX - REC equivalence)."""
    g = qt.carregar_grade()

    def aj(c, h, p, s, a):
        """Shift TAX of KNP2 by 0.005."""
        return a + 0.005 if (c, h, p) == ("KNP2", "RS", "TAX") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    assert not _comp(av, "KNP2", ("TAX", "REC"))["dentro_tol"]
    assert not av["criterios"]["C5-G"]["passou"] and av["criterios"]["C5-O"]["passou"]


def test_avaliador_tolerancia_fixa_sem_poder_reprova(prev):
    """Check that tol_X is fixed: ``3 SE_paired > tol_X`` fails C5-G even with the mean inside."""
    g = qt.carregar_grade()
    ruido = [0.006, -0.006, 0.006, -0.006, 0.0]  # mean 0, SE_paired = 0.00268

    def aj(c, h, p, s, a):
        """Add zero-mean seed noise to RHO of NUL1."""
        return a + ruido[s] if (c, h, p) == ("NUL1", "RS", "RHO") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    c = _comp(av, "NUL1", ("RHO", "REC"))
    assert c["dentro_tol"] and c["sem_poder"], "tol_X must stay 0.00405 (never 3 SE of the run)"
    assert c["tol"] == g["tol_X"] == 0.00405
    assert not av["criterios"]["C5-G"]["passou"]
    assert "NUL1 reprova" in av["veredito"]["desfechos"]


def test_avaliador_reprova_consequencia(prev):
    """Check C5-C: RHO losing 0.01 from R to R ∪ S fails the Consequence sub-test."""
    g = qt.carregar_grade()

    def aj(c, h, p, s, a):
        """Raise RHO of R by 0.01 (so R -> R ∪ S loses 0.01)."""
        return a + 0.01 if (c, h, p) == ("KNP1", "R", "RHO") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    assert not av["criterios"]["C5-C"]["passou"] and not av["veredito"]["passou"]
    assert "C5-C reprova" in av["veredito"]["desfechos"]


def test_avaliador_consequencia_tolerancia_fixa(prev):
    """Check C5-C: the Consequence uses the fixed tol_X, never ``max(tol_X, 3 SE_paired)``.

    ``Delta RHO(R -> R ∪ S)`` with mean 0.005 (above tol_X) and zero-mean seed noise
    (``SE_paired = 0.00268``, ``3 SE_paired = 0.00805``): outside the tolerance AND without power.
    """
    g = qt.carregar_grade()
    ruido = [0.006, -0.006, 0.006, -0.006, 0.0]

    def aj(c, h, p, s, a):
        """Lower RHO of R by 0.005 plus zero-mean seed noise."""
        return a - 0.005 - ruido[s] if (c, h, p) == ("KNP1", "R", "RHO") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    rho = av["consequencia"]["RHO"]
    assert rho["sem_poder"], "Consequence: 3 SE_paired above tol_X is a check without power"
    assert not rho["dentro_tol"], "Consequence: tol_X must stay 0.00405 (never 3 SE of the run)"
    assert not av["criterios"]["C5-C"]["passou"]


def test_avaliador_so_nivel_reprova(prev):
    """Check that a level shift common to every policy fails only C5-N."""
    g = qt.carregar_grade()

    def aj(c, h, p, s, a):
        """Shift every policy of KNP2 by 0.005 (paired differences unchanged)."""
        return a + 0.005 if (c, h) == ("KNP2", "RS") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    assert not av["criterios"]["C5-N"]["passou"]
    for nome in ("C5-O", "C5-G", "C5-C"):
        assert av["criterios"][nome]["passou"], nome
    assert "Só C5-N reprova" in av["veredito"]["desfechos"]
    assert "Tudo passa" not in av["veredito"]["desfechos"]


def test_avaliador_fronteira_tem_veredito_proprio(prev):
    """Check that C5-D (decay, sign only) fails on its own without touching the main verdict."""
    g = qt.carregar_grade()
    rec = prev["decaimento"]["REC"]

    def aj(c, h, p, s, a):
        """Put nominal RHO of DEC1 above REC."""
        return rec + 0.01 + 0.001 * s if (c, h, p) == ("DEC1", "RS", "RHO") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    assert not av["criterios"]["C5-D"]["passou"] and av["veredito"]["passou"]
    assert "C5-D reprova" in av["veredito"]["desfechos"]


def test_avaliador_cota_fixa_na_fonte_rara(prev):
    """Check FIX1: FIXc equal to RHO fails C5-G there (the size criterion refutes H-FIX)."""
    g = qt.carregar_grade()
    rho = prev["exata"]["FIX1"]["RHO"]

    def aj(c, h, p, s, a):
        """Make FIXc of FIX1 equal to RHO."""
        return rho + 0.001 * s if (c, h, p) == ("FIX1", "RS", "FIXc") else a

    av = qt.avaliar_c5(_linhas(g, prev, aj), g, prev, {"passou": True})
    c = _comp(av, "FIX1", ("RHO", "FIXc"))
    assert not c["dentro_tol"] and not c["rival_refutado"]
    assert "FIX1 reprova (C5-O/C5-G)" in av["veredito"]["desfechos"]


def test_avaliador_ancora_falha_reprova_e_dado_incompleto_e_erro(prev):
    """Check that failed anchors fail the verdict and that missing rows are a ValueError."""
    g = qt.carregar_grade()
    linhas = _linhas(g, prev)
    assert not qt.avaliar_c5(linhas, g, prev, {"passou": False})["veredito"]["passou"]
    with pytest.raises(ValueError):
        qt.avaliar_c5(linhas[1:], g, prev, {"passou": True})
