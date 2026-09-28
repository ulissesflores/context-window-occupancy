"""Failure paths of the two entry points: a named problem and a nonzero exit, never a traceback.

``make_provenance.py --verify`` reports a manifest, stages file or chain file that is missing, not
valid JSON or not the structure the build writes or reads as one problem naming it (one per such
file), a missing sealed file or a stage with no file as one named problem, any other failure as
one problem, and caps its exit code at 255 so that no count of problems exits with status 0.
``run_all.py`` names a missing sealed output before regenerating anything (the full run takes
minutes), names a regenerated output that is missing, and in ``--publish`` mode runs the tests
before the seal and skips the seal when anything failed.

Every test works on temporary files or on stubs of the long steps: none runs a simulation, writes
under ``output/`` or touches the committed seal. A stub that must not be reached fails the test
with its own message, so a regression can never start the full run from inside the test suite.
"""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


def _modulo(nome: str):
    """Import a script of the repository root (``run_all`` or ``make_provenance``) as a module."""
    spec = importlib.util.spec_from_file_location(nome, RAIZ / f"{nome}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _verificar(mp, capsys) -> tuple[int, str]:
    """Run ``make_provenance.py --verify`` in process; return (exit code, printed text)."""
    try:
        rc = mp.main(["--verify"])
    except Exception as erro:  # the old behaviour: a traceback instead of a named problem
        pytest.fail(f"--verify raised {type(erro).__name__} instead of naming the problem: {erro}")
    return rc, capsys.readouterr().out


def _problemas(saida: str) -> list[str]:
    """Return the problem lines of a ``--verify`` output: every ``[FAIL]`` line but the count."""
    return [x for x in saida.splitlines() if x.startswith("[FAIL]") and "problem(s):" not in x]


@pytest.mark.parametrize("atributo", ["MANIFEST", "STAGES", "CHAIN"])
@pytest.mark.parametrize(
    "estragar", [lambda b: b[:40], lambda b: b"\xff\xfe" + b], ids=["truncated", "not-utf8"]
)
def test_verify_nomeia_json_truncado(tmp_path, monkeypatch, capsys, atributo, estragar):
    """Check that a truncated or non-UTF-8 manifest, stages or chain file is one named problem."""
    mp = _modulo("make_provenance")
    original = getattr(mp, atributo)
    truncado = tmp_path / original.name
    truncado.write_bytes(estragar(original.read_bytes()))
    monkeypatch.setattr(mp, atributo, truncado)
    rc, saida = _verificar(mp, capsys)
    assert rc != 0, f"exit {rc} although {original.name} is truncated:\n{saida}"
    assert "cannot verify" in saida and f"{original.name} is not valid JSON" in saida, saida
    assert len(_problemas(saida)) == 1, f"not one problem:\n{saida}"


@pytest.mark.parametrize("atributo", ["MANIFEST", "STAGES", "CHAIN"])
def test_verify_nomeia_arquivo_ausente(tmp_path, monkeypatch, capsys, atributo):
    """Check that a missing manifest, stages file or chain file is one problem naming it."""
    mp = _modulo("make_provenance")
    ausente = tmp_path / getattr(mp, atributo).name
    monkeypatch.setattr(mp, atributo, ausente)
    rc, saida = _verificar(mp, capsys)
    esperado = f"[FAIL] cannot verify: {ausente.name} cannot be read (No such file or directory)"
    assert (rc, _problemas(saida)) == (1, [esperado]), saida


def _trocado(obj, chaves: tuple, valor=None):
    """Return a copy of ``obj`` with the item at ``chaves`` set to ``valor`` (None: deleted)."""
    novo = copy.deepcopy(obj)
    alvo = novo
    for chave in chaves[:-1]:
        alvo = alvo[chave]
    if valor is None:
        del alvo[chaves[-1]]
    else:
        alvo[chaves[-1]] = valor
    return novo


# (file, how its committed content is changed, what the one problem must say); a chain file is
# changed through its last line
ESTRUTURA = [
    ("MANIFEST", lambda m: [], "an array, expected an object"),
    ("MANIFEST", lambda m: _trocado(m, ("stage_order",)), "no key 'stage_order'"),
    ("MANIFEST", lambda m: {**m, "note": "x"}, "extra key(s) ['note']"),
    (
        "MANIFEST",
        lambda m: _trocado(m, ("stages", 0, "leaves", 0, "size"), True),
        "stages[0].leaves[0].size is a boolean, expected an integer",
    ),
    ("STAGES", lambda s: [], "an array, expected an object"),
    ("STAGES", lambda s: _trocado(s, ("stages",)), "no key 'stages'"),
    (
        "STAGES",
        lambda s: _trocado(s, ("stages", 1, "globs"), "code/*.py"),
        "stages[1].globs is a string, expected an array",
    ),
    (
        "STAGES",
        lambda s: _trocado(s, ("stages", 1, "globs", 0), "/etc/*"),
        "stages[1] holds '/etc/*', not a path relative to the repository root",
    ),
    ("CHAIN", lambda c: [], "line 1: an array, expected an object"),
    ("CHAIN", lambda c: _trocado(c, ("root",)), "line 1: no key 'root'"),
    (
        "CHAIN",
        lambda c: _trocado(c, ("chain_head",), 5),
        "line 1: chain_head is an integer, expected a string",
    ),
    (
        "CHAIN",
        lambda c: {**c, "note": "x"},
        "line 1: extra key(s) ['note']",
    ),
]


@pytest.mark.parametrize(
    ("atributo", "estragar", "esperado"),
    ESTRUTURA,
    ids=[
        "manifest-array",
        "manifest-key-missing",
        "manifest-extra-key",
        "manifest-wrong-type",
        "stages-array",
        "stages-key-missing",
        "stages-wrong-type",
        "stages-absolute-glob",
        "chain-array",
        "chain-key-missing",
        "chain-wrong-type",
        "chain-extra-key",
    ],
)
def test_verify_nomeia_estrutura_inesperada(
    tmp_path, monkeypatch, capsys, atributo, estragar, esperado
):
    """Check that valid JSON of another structure is one problem naming the file, exit code 1."""
    mp = _modulo("make_provenance")
    original = getattr(mp, atributo)
    texto = original.read_text(encoding="utf-8")
    cadeia = atributo == "CHAIN"
    obj = estragar(json.loads(texto.splitlines()[-1] if cadeia else texto))
    estragado = tmp_path / original.name
    estragado.write_text(json.dumps(obj, sort_keys=cadeia) + "\n", encoding="utf-8")
    monkeypatch.setattr(mp, atributo, estragado)
    rc, saida = _verificar(mp, capsys)
    linha = (
        f"[FAIL] cannot verify: {original.name} is not the structure the build "
        f"{'reads' if atributo == 'STAGES' else 'writes'} ({esperado})"
    )
    assert (rc, _problemas(saida)) == (1, [linha]), saida


def test_verify_nomeia_cada_arquivo_malformado(tmp_path, monkeypatch, capsys):
    """Check that two unreadable or malformed files are two problems, one naming each."""
    mp = _modulo("make_provenance")
    monkeypatch.setattr(mp, "MANIFEST", tmp_path / "manifest.json")  # missing
    cadeia = tmp_path / "CHAIN.jsonl"
    cadeia.write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(mp, "CHAIN", cadeia)
    rc, saida = _verificar(mp, capsys)
    esperado = [
        "[FAIL] cannot verify: manifest.json cannot be read (No such file or directory)",
        "[FAIL] cannot verify: CHAIN.jsonl is not the structure the build writes "
        "(line 1: an array, expected an object)",
    ]
    assert (rc, _problemas(saida)) == (2, esperado), saida


def test_verify_nomeia_falha_imprevista(monkeypatch, capsys):
    """Check that a failure no check foresaw is still one problem and exit code 1."""
    mp = _modulo("make_provenance")

    def falha():
        """Stand in for a verification that fails in a way no check foresaw."""
        raise RuntimeError("unforeseen")

    monkeypatch.setattr(mp, "verificar", falha)
    rc, saida = _verificar(mp, capsys)
    assert (rc, _problemas(saida)) == (1, ["[FAIL] cannot verify (RuntimeError): unforeseen"]), (
        saida
    )


def test_verify_nunca_sai_com_zero_havendo_problema(monkeypatch, capsys):
    """Check that 256 problems exit with status 255: an exit status is taken modulo 256."""
    mp = _modulo("make_provenance")
    monkeypatch.setattr(mp, "verificar", lambda: [f"problem {i}" for i in range(256)])
    rc, saida = _verificar(mp, capsys)
    assert rc == 255, f"exit {rc} with 256 problems:\n{saida[-200:]}"


@pytest.mark.parametrize(
    ("estagio", "nomeado"),
    [
        ({"name": "environment", "kind": "file", "path": "no-such-env.json"}, "no-such-env.json"),
        (
            {"name": "figures", "kind": "tree", "globs": ["output/figures/no-such-*.png"]},
            "stage 'figures'",
        ),
    ],
    ids=["file-stage-missing", "tree-stage-without-files"],
)
def test_verify_nomeia_estagio_ausente(tmp_path, monkeypatch, capsys, estagio, nomeado):
    """Check that a stage whose files are missing is named, relative to the repository root."""
    mp = _modulo("make_provenance")
    stages = tmp_path / "stages.json"
    stages.write_text(json.dumps({"hash_alg": "sha256", "stages": [estagio]}), encoding="utf-8")
    monkeypatch.setattr(mp, "STAGES", stages)
    rc, saida = _verificar(mp, capsys)
    assert rc != 0, f"exit {rc} although a stage is missing:\n{saida}"
    assert "cannot verify" in saida and nomeado in saida, saida
    assert str(RAIZ) not in saida, "the message carries the absolute path of the repository"


def _nao_rodar(*args, **kwargs):
    """Stand in for a long step that this test must never reach."""
    pytest.fail("the full run started although a sealed output is missing")


def test_run_all_para_antes_de_gerar_se_falta_selado(tmp_path, monkeypatch, capsys):
    """Check that a missing sealed output is named and nothing is regenerated."""
    ra = _modulo("run_all")
    monkeypatch.setattr(ra, "SAIDA", tmp_path / "output")
    monkeypatch.setattr(ra, "gerar", _nao_rodar)
    monkeypatch.setattr(ra, "_rodar", _nao_rodar)
    rc = ra.main([])
    saida = capsys.readouterr().out
    assert rc == len(ra.COMPARADOS) + len(ra.IMAGENS), (
        f"exit {rc}, not one per missing file:\n{saida}"
    )
    assert "[MISSING] output/results.json (sealed output absent" in saida, saida


def test_comparar_nomeia_arquivo_ausente_dos_dois_lados(tmp_path, monkeypatch, capsys):
    """Check that a missing file on either side is a named failure; an image difference warns."""
    ra = _modulo("run_all")
    selado, novo = tmp_path / "sealed", tmp_path / "regenerated"
    for rel in (*ra.COMPARADOS, *ra.IMAGENS):
        for raiz in (selado, novo):
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (raiz / rel).write_bytes(b"x")
    (novo / "results.json").unlink()
    (selado / "estimativas.json").unlink()
    (novo / ra.IMAGENS[0]).write_bytes(b"y")
    monkeypatch.setattr(ra, "SAIDA", selado)
    try:
        falhas = ra.comparar(novo)
    except Exception as erro:  # the old behaviour: a traceback from filecmp
        pytest.fail(f"comparar raised {type(erro).__name__} instead of naming the file: {erro}")
    saida = capsys.readouterr().out
    assert falhas == 2, f"{falhas} failure(s), expected only the 2 missing files:\n{saida}"
    assert "[MISSING] results.json (regenerated output absent)" in saida, saida
    assert "[MISSING] estimativas.json (sealed output absent)" in saida, saida
    assert f"[WARN] {ra.IMAGENS[0]} (image differs)" in saida, saida


def _publicar(monkeypatch, capsys, falha_em: str) -> tuple[int, list[str], str]:
    """Run ``--publish`` with stubbed steps; return (exit code, steps in order, printed text)."""
    ra = _modulo("run_all")
    passos = []

    def gerar(base, params):
        """Record the generation instead of running it; fail it when asked."""
        passos.append("generate")
        return int(falha_em == "generate")

    def rodar(passo, cmd):
        """Record the step instead of running it; fail it when asked."""
        passos.append(passo)
        return int(passo == falha_em)

    monkeypatch.setattr(ra, "gerar", gerar)
    monkeypatch.setattr(ra, "_rodar", rodar)
    rc = ra.main(["--publish"])
    return rc, passos, capsys.readouterr().out


def test_publish_testa_antes_de_selar(monkeypatch, capsys):
    """Check that ``--publish`` runs the tests before the seal when everything passes."""
    rc, passos, saida = _publicar(monkeypatch, capsys, falha_em="")
    assert passos == ["generate", "tests", "seal", "provenance verify"], (
        f"the seal must come after the tests: {passos}"
    )
    assert rc == 0, f"exit {rc} with every stubbed step green:\n{saida}"


@pytest.mark.parametrize("falha_em", ["generate", "tests"])
def test_publish_nao_sela_depois_de_falha(monkeypatch, capsys, falha_em):
    """Check that ``--publish`` skips the seal, and fails, when generation or tests fail."""
    rc, passos, saida = _publicar(monkeypatch, capsys, falha_em)
    assert "seal" not in passos, f"a failing run was sealed: {passos}"
    assert "[FAIL] seal skipped" in saida, saida
    assert rc != 0, f"exit {rc} after a failure before the seal:\n{saida}"
