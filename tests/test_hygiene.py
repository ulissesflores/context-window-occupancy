"""Repository hygiene: no file carries an absolute path of a user's machine.

The seal, the outputs and the documentation must be relocatable: a path such as a home directory
would not reproduce on another machine and would leak the author's local tree. Binary files are
scanned too (as latin-1), because image metadata can carry paths.
"""

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IGNORAR = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", ".mypy_cache"}
IGNORAR_PREFIXOS = ("output/replicated", "output/smoke")  # local, never committed
CAMINHO_ABSOLUTO = re.compile(r"/(?:Users|home)/[^/\s\"']+|[A-Za-z]:\\\\?Users\\\\?")


def _arquivos():
    """Yield every file of the repository that is committed or committable."""
    for p in sorted(RAIZ.rglob("*")):
        rel = p.relative_to(RAIZ)
        if not p.is_file() or IGNORAR.intersection(rel.parts):
            continue
        if rel.as_posix().startswith(IGNORAR_PREFIXOS):
            continue
        yield p


def _texto(p: Path) -> str:
    """Decode a file as UTF-8, or as latin-1 when it is binary."""
    dados = p.read_bytes()
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return dados.decode("latin-1")


def test_nenhum_arquivo_tem_caminho_absoluto_de_usuario():
    """Check that no file contains an absolute path of a user's home directory."""
    achados = {
        p.relative_to(RAIZ).as_posix(): m.group(0)
        for p in _arquivos()
        if (m := CAMINHO_ABSOLUTO.search(_texto(p)))
    }
    assert achados == {}, achados


def test_manifest_so_tem_caminhos_relativos():
    """Check that every path in the sealed manifests is relative to the repository root."""
    manifests = sorted((RAIZ / "runs").glob("*/manifest.json"))
    assert manifests, "no sealed manifest under runs/"
    for m in manifests:
        prov = json.loads(m.read_text(encoding="utf-8"))
        for estagio in prov["stages"]:
            for folha in estagio["leaves"]:
                caminho = Path(folha["path"])
                assert not caminho.is_absolute() and ".." not in caminho.parts, folha["path"]
