"""Replication never writes a sealed path (invariant of the provenance chain).

``run_all.py`` regenerates every output into ``output/replicated/`` (full run) or
``output/smoke/`` (CI). If any of those write targets matched a glob of ``configs/stages.json``, a
legitimate replication would silently overwrite sealed evidence and the next verification would
report tampering. The match uses ``Path.glob`` semantics: ``*`` never crosses ``/``. Write targets
and their base directories are normalized first (``posixpath.normpath``) and a ``..`` segment is
refused outright: ``output/smoke/../figures`` would otherwise escape the segment-wise match while
the run writes into ``output/figures``.
"""

import fnmatch
import importlib.util
import json
import posixpath
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def _run_all():
    """Import ``run_all.py`` from the repository root as a module."""
    spec = importlib.util.spec_from_file_location("run_all", RAIZ / "run_all.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _selados() -> list[str]:
    """Return every sealed path or glob of ``configs/stages.json``."""
    cfg = json.loads((RAIZ / "configs" / "stages.json").read_text(encoding="utf-8"))
    padroes = []
    for estagio in cfg["stages"]:
        padroes += [estagio["path"]] if estagio["kind"] == "file" else estagio["globs"]
    return padroes


def _normal(caminho: str) -> str:
    """Return ``caminho`` normalized; fail if it has a ``..`` segment or leaves the repository."""
    assert ".." not in caminho.split("/"), f"write path climbs with '..': {caminho}"
    normal = posixpath.normpath(caminho)
    assert not posixpath.isabs(normal), f"write path is absolute: {caminho}"
    return normal


def _casa(caminho: str, padrao: str) -> bool:
    """Match like ``Path.glob``: same number of segments, ``fnmatch`` segment by segment."""
    partes, globs = caminho.split("/"), padrao.split("/")
    return len(partes) == len(globs) and all(
        fnmatch.fnmatchcase(p, g) for p, g in zip(partes, globs, strict=True)
    )


def test_globs_selados_sem_recursao():
    """Check that no sealed glob uses ``**`` (the segment-wise match below would not cover it)."""
    assert not any("**" in g for g in _selados())


def test_alvos_de_replicacao_e_smoke_disjuntos_dos_selados():
    """Check that no file written by the replicated or smoke runs matches a sealed glob."""
    ra = _run_all()
    selados = _selados()
    for base in (ra.REPLICATED_DIR, ra.SMOKE_DIR):
        base_normal = _normal(base)
        for alvo in ra.alvos(base):
            colisoes = [g for g in selados if _casa(_normal(alvo), g)]
            assert colisoes == [], (alvo, colisoes)
        assert not any(g.startswith(base_normal + "/") for g in selados), base


def test_publish_escreve_so_caminhos_selados():
    """Check that every output of ``--publish`` is covered by a sealed glob (nothing unsealed)."""
    ra = _run_all()
    selados = _selados()
    for alvo in ra.alvos("output"):
        assert any(_casa(_normal(alvo), g) for g in selados), alvo
