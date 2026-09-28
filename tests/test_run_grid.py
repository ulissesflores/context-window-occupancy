"""TDD of the shared grid runner ``code/run_grid.py`` (exponent and occupancy families).

Specification: section 0.4 of ``data/prereg/05-exponent-addendum.md`` and
``data/prereg/06-occupancy-addendum.md``. The runner reuses ``run_token_kat._uma_tarefa`` and
``token_kat.avaliar_kat`` unchanged, through the tag adapter; filtered runs keep the ORIGINAL cell
index, so a run of one cell draws the same streams as the full grid.
"""

import json
from pathlib import Path

import pytest

import run_grid
import token_kat as kt

RAIZ = Path(__file__).resolve().parents[1]
GRADE_KAT = RAIZ / "data/kat_token_grid.json"
CSV_KAT = RAIZ / "output/kat_token/celulas.csv"


# --- (a) the adapter accepts both grid forms ------------------------------------------------------


def test_adaptador_aceita_a_grade_do_kat_so_com_tag_r3():
    """The token KAT grid (only ``tag_r3``) keeps its tag through the adapter."""
    grade = kt.carregar_grade(GRADE_KAT)
    assert "tag" not in grade and grade["tag_r3"] == 3
    adaptada = run_grid.adaptar_grade(grade)
    assert adaptada["tag_r3"] == 3
    assert {k: v for k, v in adaptada.items() if k != "tag_r3"} == {
        k: v for k, v in grade.items() if k != "tag_r3"
    }


@pytest.mark.parametrize(("nome", "tag"), [("exponent_grid.json", 5), ("occupancy_grid.json", 6)])
def test_adaptador_aceita_a_grade_nova_so_com_tag(nome, tag):
    """A new grid (only ``tag``) reaches ``_uma_tarefa`` with its tag under ``tag_r3``."""
    grade = kt.carregar_grade(RAIZ / "data" / nome)
    assert "tag_r3" not in grade and grade["tag"] == tag
    adaptada = run_grid.adaptar_grade(grade)
    assert adaptada["tag_r3"] == tag
    assert adaptada["tag"] == tag
    assert "tag_r3" not in grade, "the adapter must not mutate the loaded grid"


def test_adaptador_sem_tag_e_valueerror():
    """A grid with neither ``tag`` nor ``tag_r3`` is rejected before any draw."""
    grade = {k: v for k, v in kt.carregar_grade(GRADE_KAT).items() if k != "tag_r3"}
    with pytest.raises(ValueError, match="tag"):
        run_grid.adaptar_grade(grade)


# --- filtering keeps the original cell index ------------------------------------------------------


def test_filtro_preserva_o_indice_original_da_celula():
    """Filtering the token KAT grid to S3 yields tasks with the original ``i_celula`` = 4."""
    grade = run_grid.adaptar_grade(kt.carregar_grade(GRADE_KAT))
    tarefas = run_grid.montar_tarefas(grade, ["S3"])
    assert len(tarefas) == 2 * len(grade["sementes"])
    assert {t[0] for t in tarefas} == {4}
    assert {t[1]["id"] for t in tarefas} == {"S3"}


def test_filtro_com_id_inexistente_e_valueerror():
    """An unknown cell id is an error, never a silently empty run."""
    grade = run_grid.adaptar_grade(kt.carregar_grade(GRADE_KAT))
    with pytest.raises(ValueError, match="XX"):
        run_grid.montar_tarefas(grade, ["S3", "XX"])


# --- (b) byte-for-byte identity with the sealed token KAT rows ------------------------------------


def test_s3_filtrada_reproduz_byte_a_byte_as_linhas_seladas_do_kat(tmp_path):
    """The runner on the token KAT grid, filtered to S3, rewrites its 10 sealed rows byte for byte.

    Compares the header and the lines ``4,S3,...`` (CRLF terminator included) of
    ``output/kat_token/celulas.csv``, not the file sha256 (the file also holds the other cells).
    Writes only under ``tmp_path``.
    """
    saida = tmp_path / "s3"
    argv = ["--grid", str(GRADE_KAT), "--out", str(saida), "--processos", "4", "--celulas", "S3"]
    assert run_grid.main(argv) == 0

    selado = CSV_KAT.read_bytes()
    novo = (saida / "celulas.csv").read_bytes()
    assert novo.endswith(b"\r\n") and selado.endswith(b"\r\n")
    linhas_seladas = selado.split(b"\r\n")
    linhas_novas = novo.split(b"\r\n")
    assert linhas_novas[0] == linhas_seladas[0], "header differs from the sealed CSV"
    s3_seladas = [x for x in linhas_seladas if x.startswith(b"4,S3,")]
    s3_novas = [x for x in linhas_novas if x.startswith(b"4,S3,")]
    assert len(s3_seladas) == 10
    assert s3_novas == s3_seladas
    assert novo == linhas_seladas[0] + b"\r\n" + b"\r\n".join(s3_seladas) + b"\r\n"

    resumo = json.loads((saida / "resumo.json").read_text(encoding="utf-8"))
    assert resumo["celulas"] == ["S3"]
    assert resumo["tag"] == 3
    assert resumo["avaliar_kat"]["KT_S"]["celulas"] == 1
    assert "veredito" not in resumo, "the token KAT grid has no family verdict module"


# --- family verdict hook (the only way a family puts its verdict in the sealed resumo.json) -------


def test_gancho_de_veredito_da_familia(tmp_path, monkeypatch):
    """``<stem>_analytic_table.veredito(linhas, grade)`` is called and its return is recorded.

    Uses a tiny smoke run (``--N 20 --bloco-usuarios 10``) on a copy of one token KAT cell in the
    new grid form (only ``tag``); the hook receives the loaded grid, never the adapted one.
    """
    grade = kt.carregar_grade(GRADE_KAT)
    grade["tag"] = grade.pop("tag_r3")
    grade["celulas"] = [c for c in grade["celulas"] if c["id"] == "N1"]
    (tmp_path / "gancho_grid.json").write_text(json.dumps(grade), encoding="utf-8")
    (tmp_path / "gancho_analytic_table.py").write_text(
        '"""Fake family module."""\n\n\n'
        "def veredito(linhas, grade):\n"
        '    """Return what the hook received."""\n'
        '    return {"n_linhas": len(linhas), "tem_tag_r3": "tag_r3" in grade,\n'
        '            "celulas": [c["id"] for c in grade["celulas"]]}\n',
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    argv = ["--grid", str(tmp_path / "gancho_grid.json"), "--out", str(tmp_path / "out")]
    argv += ["--processos", "2", "--N", "20", "--bloco-usuarios", "10"]
    assert run_grid.main(argv) == 0
    resumo = json.loads((tmp_path / "out/resumo.json").read_text(encoding="utf-8"))
    assert resumo["veredito"] == {"n_linhas": 10, "tem_tag_r3": False, "celulas": ["N1"]}
    assert resumo["N"] == 20 and resumo["tag"] == grade["tag"]
    assert "tabela_sha256" not in resumo and "adendo_sha256" not in resumo
