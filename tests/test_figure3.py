"""Tests of Figure 3 (synthetic displacement replication).

Pre-registration: ``data/prereg/01-displacement-replication.md`` (Q2 = empirical sign x analytic
sign; outside the test if |predicted dAUC| < max(0.005; 3 SE)). The tests write only to
``tmp_path``; they never touch ``output/``.
"""

import csv
import hashlib
import json
import math
import statistics
import struct
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import matplotlib.colors as mcolors
import numpy as np
import pytest
from matplotlib.text import Text
from matplotlib.transforms import Bbox

import figure3 as fr

CSV = fr.CSV_CELULAS
SIDECAR_SELADO = fr.DESTINO / fr.SIDECAR_NOME


@pytest.fixture(scope="module")
def gerado(tmp_path_factory):
    """Generate the figure and its sidecar once per module, in a temporary directory."""
    destino = tmp_path_factory.mktemp("fig3")
    png, sidecar = fr.gerar(destino)
    return png, json.loads(sidecar.read_text(encoding="utf-8"))


# (1) KAT of the equilibrium: closed form derived here, importing nothing from the figure --------


def test_equilibrio_forma_fechada_igual_brentq(gerado):
    """Check the brentq equilibria of panel (a) against the closed form, to 4 decimals."""
    _, valores = gerado
    T, L, lam_c = 90, 146, 3
    lam = {"A": 0.1, "B": 0.3}
    d = {"A": 0.5, "B": 0.15}
    esperado_4casas = {"A->AC": 0.0871, "B->BC": 0.0482, "AB->ABC": 0.1077}
    for antigas in ("A", "B", "AB"):
        a = sum(lam[s] * d[s] ** 2 for s in antigas)
        b = sum(lam[s] for s in antigas)
        # regime: without C unsaturated, with C saturated (validity condition of the closed form)
        assert b * T < L <= (b + lam_c) * T
        # Delta2_without = T a (h = T); Delta2_with = L (a + lam_C d^2) / (b + lam_C); solve for d^2
        fechada = math.sqrt((T * a * (b + lam_c) / L - a) / lam_c)
        chave = f"{antigas}->{antigas}C"
        assert math.isclose(fr.equilibrio_a(antigas, antigas + "C"), fechada, rel_tol=1e-9)
        assert math.isclose(valores["painel_a"]["equilibrios"][chave], fechada, rel_tol=1e-9)
        assert round(fechada, 4) == esperado_4casas[chave]


# (2) P1b: in the saturated regime the sign does not depend on lambda_C ---------------------------


def test_p1b_sinal_constante_em_lambda_c():
    """Check P1b: with B alone saturating, the sign of B->BC is constant over lambda_C."""
    for lc in np.geomspace(0.05, 7, 500):  # B alone saturates => BC saturates in the whole range
        assert fr.rd.saturada("B", {"A": 0.1, "B": 0.6, "C": lc}, 365)
    for d_c, sinal in ((0, -1), (0.1, -1), (0.2, +1)):
        x, y = fr.curva_b(d_c)
        assert x[0] == pytest.approx(0.05) and x[-1] == pytest.approx(7)
        assert np.all(sinal * y > 0), f"d_C = {d_c}: sign changes with lambda_C"
        denso = [
            fr.delta_auc_analitica(
                "B", "BC", {"A": 0.1, "B": 0.6, "C": lc}, {"A": 0.5, "B": 0.15, "C": d_c}, 365
            )
            for lc in np.geomspace(0.05, 7, 2000)
        ]
        assert all(sinal * v > 0 for v in denso)


# (3) empirical mean recomputed with csv + statistics only matches the sidecar ------------------


def test_media_independente_bate_com_sidecar(gerado):
    """Recompute one plotted point from the raw CSV with the standard library only."""
    _, valores = gerado
    alvo = {
        "T": "90",
        "lam_A": 0.1,
        "lam_B": 0.3,
        "lam_C": 3.0,
        "d_A": 0.5,
        "d_B": 0.15,
        "d_C": 0.2,
    }
    aucs = {"AB": [], "ABC": []}
    with open(CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["T"] != alvo["T"] or r["combo"] not in aucs:
                continue
            if all(float(r[k]) == v for k, v in alvo.items() if k != "T"):
                aucs[r["combo"]].append(float(r["auc"]))
    assert len(aucs["AB"]) == len(aucs["ABC"]) == 5
    ponto = next(
        p for p in valores["painel_a"]["pontos"] if p["contexto"] == "AB->ABC" and p["d_C"] == 0.2
    )
    assert math.isclose(ponto["media_com"], statistics.mean(aucs["ABC"]), abs_tol=1e-12)
    assert math.isclose(ponto["media_sem"], statistics.mean(aucs["AB"]), abs_tol=1e-12)
    ep = math.sqrt(statistics.variance(aucs["ABC"]) / 5 + statistics.variance(aucs["AB"]) / 5)
    assert math.isclose(ponto["ep"], ep, rel_tol=1e-9)


# (4) empirical sign = analytic sign at the tested points (Q2 of the pre-registration) -----------


def test_sinal_empirico_igual_analitico(gerado):
    """Check the Q2 sign agreement at every tested point, and lock the single untested point."""
    _, valores = gerado
    pontos = valores["painel_a"]["pontos"] + valores["painel_b"]["pontos"]
    assert len(pontos) == 15 + 9
    fora = []
    for p in pontos:
        limiar = max(0.005, 3 * p["ep"])  # threshold on the PREDICTED value, as in Q2
        assert p["limiar_teste"] == limiar
        if abs(p["delta_analitico"]) < limiar:
            fora.append((p["contexto"], p["d_C"], p["lam_C"]))
            assert p["testado"] is False
            continue
        assert p["testado"] is True
        assert math.copysign(1, p["delta_emp"]) == math.copysign(1, p["delta_analitico"]), p
    # lock the number: only B->BC at d_C = 0.05 (predicted dAUC ~ 0.0035) is outside the test, and
    # for the "abaixo_limiar" cause of the sealed summary (< 0.005), not for "empate" (< 3 SE)
    assert fora == [("B->BC", 0.05, 3)]
    p = next(p for p in pontos if not p["testado"])
    assert abs(p["delta_analitico"]) < 0.005 and 3 * p["ep"] < 0.005


# (5) PNG byte-stable BETWEEN PROCESSES; sidecar identical to the sealed one ----------------------


def _gerar_em_processo_novo(destino: Path) -> None:
    """Generate the figure in a NEW Python process (fresh rcParams, font cache and state)."""
    src = Path(fr.__file__).resolve().parent
    subprocess.run(
        [
            sys.executable,
            "-c",
            f"import sys; sys.path.insert(0, {str(src)!r}); from pathlib import Path; "
            f"import figure3 as f; f.gerar(Path({str(destino)!r}))",
        ],
        check=True,
    )


def test_png_e_sidecar_byte_estaveis(tmp_path):
    """Check that two fresh processes give the same PNG bytes and the sealed sidecar bytes.

    The PNG depends on the font rasteriser, so it is compared between two processes of this
    environment, not against the sealed file; the sidecar is machine-independent and must equal
    ``output/figures/fig3_values.json`` byte for byte.
    """
    um, dois = tmp_path / "um", tmp_path / "dois"
    _gerar_em_processo_novo(um)
    _gerar_em_processo_novo(dois)
    png_um = hashlib.sha256((um / fr.PNG_NOME).read_bytes()).hexdigest()
    png_dois = hashlib.sha256((dois / fr.PNG_NOME).read_bytes()).hexdigest()
    assert png_um == png_dois, f"PNG differs between processes: {png_um[:12]} != {png_dois[:12]}"
    for d in (um, dois):
        assert (d / fr.SIDECAR_NOME).read_bytes() == SIDECAR_SELADO.read_bytes()
    texto = (um / fr.SIDECAR_NOME).read_text(encoding="utf-8")
    assert (
        texto == json.dumps(json.loads(texto), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    )


def test_fmt_num_sem_menos_zero():
    """Check the number formatter: no '-0', decimal point and typographic minus."""
    assert fr._fmt_num(round(-1e-9, 6)) == "0"
    assert fr._fmt_num(-0.0, 4) == "0.0000"
    assert fr._fmt_num(-0.05) == "−0.05"


# (6) layout measured with the renderer ---------------------------------------------------------
# The 7 pt floor holds for the fontsize of every Text. Mathtext subscripts ($d_C$, $\lambda_A$) are
# 70% of the body by construction and stay OUTSIDE the floor, by declared decision: they are
# indices, not running text. Their size is MEASURED in test_subscrito_medido, not estimated.


def test_layout_medido(gerado):
    """Measure the layout: font floor, texts inside the figure, no overlaps, markers at true x."""
    png, valores = gerado
    largura_px, _ = struct.unpack(">II", png.read_bytes()[16:24])  # IHDR
    assert largura_px / 300 <= 6.5

    fig, textos, obstaculos = fr.montar(valores)
    try:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        assert fig.get_size_inches()[0] <= 6.5
        caixa_fig = fig.bbox

        visiveis = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
        assert textos["rodape"].get_text() == fr.RODAPE
        assert textos["nota"].get_text() == fr.NOTA
        for t in visiveis:
            assert t.get_fontsize() >= 7, (t.get_text(), t.get_fontsize())
            bb = t.get_window_extent(r)
            assert (
                bb.x0 >= caixa_fig.x0 - 0.5
                and bb.y0 >= caixa_fig.y0 - 0.5
                and bb.x1 <= caixa_fig.x1 + 0.5
                and bb.y1 <= caixa_fig.y1 + 0.5
            ), t.get_text()

        caixas = {nome: art.get_window_extent(r) for nome, art in textos.items()}
        assert sum(n.startswith("equilibrio_") for n in caixas) == 3
        for (n1, b1), (n2, b2) in combinations(caixas.items(), 2):
            assert not b1.overlaps(b2), f"{n1} overlaps {n2}"

        # no curve nor dotted line crosses a named text (legend, d_C* labels, titles, note)
        assert len(obstaculos["curvas"]) == 6 and len(obstaculos["pontilhados"]) == 3
        for tipo in ("curvas", "pontilhados"):
            for linha in obstaculos[tipo]:
                caminho = linha.get_transform().transform_path(linha.get_path())
                for nome, bb in caixas.items():
                    assert not caminho.intersects_bbox(bb, filled=False), f"{tipo} crosses {nome}"

        # a marker (box of ms pt around each point) does not touch a named text; x = TRUE value
        px_por_pt = fig.dpi / 72
        xs_plotados, formas = [], []
        for marca in obstaculos["marcadores"]:
            meio = marca.get_markersize() * px_por_pt / 2
            formas += [marca.get_marker()] * len(marca.get_xdata())
            xs_plotados += list(marca.get_xdata())
            for xd, yd in marca.get_transform().transform(marca.get_xydata()):
                bb_p = Bbox([[xd - meio, yd - meio], [xd + meio, yd + meio]])
                for nome, bb in caixas.items():
                    assert not bb_p.overlaps(bb), f"marker at ({xd:.0f}, {yd:.0f}) px under {nome}"
        reais = [p["d_C"] for p in valores["painel_a"]["pontos"]] + [
            p["lam_C"] for p in valores["painel_b"]["pontos"]
        ]
        assert sorted(xs_plotados) == sorted(reais)  # no cosmetic offset in x
        assert formas.count("x") == 1 and formas.count("o") == 23  # only the point below the floor

        # the NOTE promises "bar +/- 3 SE smaller than the marker" (drawn without caps): measure it
        assert obstaculos["pontas"] == []  # capsize = 0: no cap drawn
        assert len(obstaculos["barras"]) == len(obstaculos["marcadores"])
        for marca, barra in zip(obstaculos["marcadores"], obstaculos["barras"], strict=True):
            raio = marca.get_markersize() * px_por_pt / 2
            for seg in barra.get_segments():
                (x0, y0), (x1, y1) = marca.get_transform().transform(seg)
                assert abs(x1 - x0) < 1e-6 and abs(y1 - y0) / 2 < raio, (
                    seg,
                    abs(y1 - y0) / 2,
                    raio,
                )

        # the "x" stands out from what crosses it: neutral colour, white halo, above everything
        (x_fora,) = [m for m in obstaculos["marcadores"] if m.get_marker() == "x"]
        cores_linhas = {
            mcolors.to_hex(ln.get_color())
            for t in ("curvas", "pontilhados")
            for ln in obstaculos[t]
        }
        assert mcolors.to_hex(x_fora.get_color()) == fr.COR_FORA.lower()
        assert fr.COR_FORA.lower() not in cores_linhas
        assert x_fora.get_path_effects(), "x without halo"
        assert all(
            x_fora.get_zorder() > ln.get_zorder()
            for t in ("curvas", "pontilhados")
            for ln in obstaculos[t]
        )
        assert "×" not in fr.NOTA or "grey" in fr.NOTA.lower()
        assert any(t.get_text() == fr.ROTULO_FORA for t in textos["legenda_a"].get_texts())
    finally:
        fr.plt.close(fig)


def test_x_legivel_nos_pixels(gerado):
    """Check in the 300 dpi PNG that the grey "x" is drawn whole (both diagonals), not covered."""
    png, valores = gerado
    img = fr.plt.imread(png)[..., :3]
    fig, _, obstaculos = fr.montar(valores)
    try:
        fig.set_dpi(300)
        fig.canvas.draw()
        (x_fora,) = [m for m in obstaculos["marcadores"] if m.get_marker() == "x"]
        xd, yd = x_fora.get_transform().transform(x_fora.get_xydata())[0]
        meio = int(round(x_fora.get_markersize() * 300 / 72 / 2))
    finally:
        fr.plt.close(fig)
    lin, col = int(round(img.shape[0] - yd)), int(round(xd))
    janela = img[lin - meio - 1 : lin + meio + 2, col - meio - 1 : col + meio + 2]
    alvo = np.array(mcolors.to_rgb(fr.COR_FORA))
    escuros = np.linalg.norm(janela - alvo, axis=-1) < 0.12
    # both diagonals of the x (not just a blot): every quadrant of the window has grey stroke
    h = janela.shape[0] // 2
    quadrantes = [
        escuros[:h, :h],
        escuros[:h, h + 1 :],
        escuros[h + 1 :, :h],
        escuros[h + 1 :, h + 1 :],
    ]
    assert escuros.sum() >= 2 * meio, escuros.sum()
    assert all(q.sum() > 0 for q in quadrantes), [int(q.sum()) for q in quadrantes]


def test_subscrito_medido():
    """Measure the fontsize of every mathtext glyph as the renderer builds it (70% subscripts)."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.mathtext import MathTextParser

    parser = MathTextParser("path")
    for corpo in (7, 8):
        glifos = parser.parse("$d_C$", dpi=72, prop=FontProperties(size=corpo)).glyphs
        tamanhos = sorted({round(g[1], 3) for g in glifos})
        assert tamanhos == [round(0.7 * corpo, 3), corpo], tamanhos  # 4.9 pt (7) and 5.6 pt (8)


# (7) colour: contrast against the background and distinction under colour-vision deficiency -----
# Matrices of Machado, Oliveira & Fernandes (2009), severity 1.0, applied in linear RGB; dE = CIE76
# in Lab (D65). Floors: 3:1 against white (WCAG 1.4.11, graphical object); dE >= 20 between curves
# told apart by colour only. The old green of AB->ABC gave dE = 1.2 against B->BC under
# deuteranopia.
_DALTONISMO = {
    "normal": np.eye(3),
    "deuteranopia": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 1.042940],
        ]
    ),
    "protanopia": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
}


def _linear(cor):
    """Return the linear-RGB components of an sRGB colour."""
    c = np.array(mcolors.to_rgb(cor))
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lab(rgb_lin):
    """Convert linear RGB to CIE Lab (D65)."""
    xyz = (
        np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
        @ rgb_lin
    )
    t = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def _delta_e(c1, c2, m):
    """Return the CIE76 distance between two colours as seen through matrix ``m``."""
    return float(
        np.linalg.norm(_lab(np.clip(m @ _linear(c1), 0, 1)) - _lab(np.clip(m @ _linear(c2), 0, 1)))
    )


def _contraste_branco(cor):
    """Return the WCAG contrast ratio of a colour against white."""
    y = float(np.array([0.2126, 0.7152, 0.0722]) @ _linear(cor))
    return 1.05 / (y + 0.05)


def test_cores_distinguiveis():
    """Check contrast >= 3:1 and dE >= 20 between curves told apart by colour only."""
    # KAT: the defect that motivated the test
    assert _delta_e("#C0504D", "#5E8C4A", _DALTONISMO["deuteranopia"]) < 2
    for cor in [*fr.COR_A.values(), *fr.COR_B.values()]:
        assert _contraste_branco(cor) >= 3.0, cor
    for c1, c2 in combinations(fr.COR_A.values(), 2):  # (a): only colour separates the curves
        for visao, m in _DALTONISMO.items():
            assert _delta_e(c1, c2, m) >= 20, (c1, c2, visao)
    for d1, d2 in combinations(fr.COR_B, 2):  # (b): colour OR dash separates each pair
        if fr.TRACO_B[d1] == fr.TRACO_B[d2]:
            for visao, m in _DALTONISMO.items():
                assert _delta_e(fr.COR_B[d1], fr.COR_B[d2], m) >= 20, (d1, d2, visao)
