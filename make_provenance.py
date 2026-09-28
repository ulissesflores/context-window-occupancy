#!/usr/bin/env python3
"""Build or verify the provenance chain of this repository.

``python3 make_provenance.py`` (build): freezes ``env.json`` if it is absent (genesis), hashes
every stage of ``configs/stages.json`` (environment -> code -> prereg -> data -> scores ->
figures) with the vendored ``code/provenance_chain.py`` and writes the seal:

- ``runs/<RUN_ID>/manifest.json``: the provenance object (stage hashes, leaves, ROOT, chain head);
  every path in it is relative to the repository root;
- ``runs/<RUN_ID>/sha256sums.txt``: one line per sealed file, checkable with ``sha256sum -c``;
- ``runs/CHAIN.jsonl``: one line per run (``run_id``, ``prev_chain_head``, ``root``,
  ``chain_head``).

``python3 make_provenance.py --verify``: recomputes the chain from the files on disk and compares
it with the sealed manifest: every stage hash, the ROOT and the chain head, and also every leaf the
manifest lists (path, SHA-256 and size, stage by stage) and ``sha256sums.txt``, regenerated from
the manifest and compared byte for byte. It checks that the manifest holds no absolute path and
walks ``runs/CHAIN.jsonl`` line by line: the first line links to the zero head, each
``prev_chain_head`` is the ``chain_head`` of the line before, each ``chain_head`` is the link of
its ``prev_chain_head`` and ``root``, and the line of this run equals the manifest. Exit code =
number of problems, at most 255 (an exit status is taken modulo 256; 0 = verified).

The manifest, ``configs/stages.json`` and ``runs/CHAIN.jsonl`` are read first. Each one that is
missing, unreadable, not valid JSON, or not the structure the build writes (the manifest, the
chain file) or reads (the stages file) is one problem that names it, and nothing is recomputed:
a key missing, or extra in the manifest or a chain line, a value of another JSON type, a stage
path that is not relative to the root. A sealed file that is missing or unreadable is named by
its path relative to the root; a missing file of a tree stage also changes the hash of its stage,
the root and the chain head, and each of these is reported. No failure of ``--verify`` ends in a
traceback or with exit code 0.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "code"))

import freeze_env  # noqa: E402
import provenance_chain as pc  # noqa: E402

RUN_ID = "v0.1.0"
STAGES = RAIZ / "configs" / "stages.json"
RUNS = RAIZ / "runs"
MANIFEST = RUNS / RUN_ID / "manifest.json"
CHAIN = RUNS / "CHAIN.jsonl"
CAMPOS_DA_CADEIA = ("chain_head", "prev_chain_head", "root", "run_id")

# The structure the build writes, which --verify checks before it recomputes anything: a dict lists
# the keys, a one-item list gives the form of every item, a type is the exact JSON type.
FORMA_MANIFEST = {
    "hash_alg": str,
    "domain_separation": {"leaf": str, "node": str, "link": str},
    "stage_order": [str],
    "stages": [
        {
            "name": str,
            "kind": str,
            "nfiles": int,
            "hash": str,
            "leaves": [{"path": str, "sha256": str, "size": int}],
        }
    ],
    "prev_chain_head": str,
    "root": str,
    "chain_head": str,
}
FORMA_DO_ESTAGIO = {"file": {"name": str, "path": str}, "tree": {"name": str, "globs": [str]}}
TIPO_JSON = {
    dict: "an object",
    list: "an array",
    str: "a string",
    int: "an integer",
    float: "a number",
    bool: "a boolean",
    type(None): "null",
}


def _nome(caminho: Path) -> str:
    """Return ``caminho`` relative to the repository root, or its bare name if it lies outside."""
    return str(caminho.relative_to(RAIZ)) if caminho.is_relative_to(RAIZ) else caminho.name


def _texto(caminho: Path) -> str:
    """Return the text of ``caminho``; a file that cannot be read as UTF-8 text is named.

    Raises
    ------
    ValueError
        If the file is missing or unreadable, or its bytes are not UTF-8 text.
    """
    try:
        return caminho.read_text(encoding="utf-8")
    except OSError as erro:
        raise ValueError(f"{_nome(caminho)} cannot be read ({erro.strerror or erro})") from erro
    except UnicodeDecodeError as erro:
        raise ValueError(f"{_nome(caminho)} is not valid JSON ({erro})") from erro


def _json(caminho: Path, texto: str | None = None):
    """Parse ``texto`` (default: the whole file ``caminho``); a parse error names the file.

    Raises
    ------
    ValueError
        If the file cannot be read, or the text is not valid JSON (truncated, or nested too deeply
        for the parser).
    """
    try:
        return json.loads(_texto(caminho) if texto is None else texto)
    except (json.JSONDecodeError, RecursionError) as erro:
        raise ValueError(f"{_nome(caminho)} is not valid JSON ({erro})") from erro


def _cadeia() -> list[dict]:
    """Return the lines of ``runs/CHAIN.jsonl`` (empty list if the file does not exist)."""
    if not CHAIN.exists():
        return []
    return [_json(CHAIN, x) for x in _texto(CHAIN).splitlines() if x.strip()]


def _relativo(caminho: str) -> bool:
    """Return True if ``caminho`` is a non-empty path inside the root (not absolute, no ``..``)."""
    return bool(caminho) and not Path(caminho).is_absolute() and ".." not in Path(caminho).parts


def _desvio(obj, forma, onde: str = "", exato: bool = False) -> str | None:
    """Return where ``obj`` departs from ``forma``, or None if it has that structure.

    Parameters
    ----------
    obj : object
        A parsed JSON value.
    forma : dict, list or type
        A dict of required keys, a one-item list with the form of every item, or the exact type (a
        JSON boolean is not an integer).
    onde : str
        Where ``obj`` sits in the file, for the message (empty at the top level).
    exato : bool
        If True, an object with a key that ``forma`` does not list departs too, at every depth.

    Returns
    -------
    str or None
        The first departure found, e.g. ``"stages[0].leaves[0] has no key 'size'"``.
    """
    esperado = type(forma) if isinstance(forma, dict | list) else forma
    if type(obj) is not esperado:
        tipo = f"{TIPO_JSON.get(type(obj), type(obj).__name__)}, expected {TIPO_JSON[esperado]}"
        return f"{onde} is {tipo}" if onde else tipo
    if isinstance(forma, dict):
        if exato and set(obj) - set(forma):
            extra = f"extra key(s) {sorted(set(obj) - set(forma))}"
            return f"{onde} has {extra}" if onde else extra
        for chave, sub in forma.items():
            if chave not in obj:
                return f"{onde} has no key {chave!r}" if onde else f"no key {chave!r}"
            desvio = _desvio(obj[chave], sub, f"{onde}.{chave}" if onde else chave, exato)
            if desvio:
                return desvio
    if isinstance(forma, list):
        for i, item in enumerate(obj):
            desvio = _desvio(item, forma[0], f"{onde}[{i}]", exato)
            if desvio:
                return desvio
    return None


def _desvio_dos_stages(cfg) -> str | None:
    """Return where a stages file departs from what the build reads, or None."""
    desvio = _desvio(cfg, {"stages": [{"kind": str}]})
    if desvio:
        return desvio
    if cfg.get("hash_alg", "sha256") != "sha256":
        return f"hash_alg is {cfg['hash_alg']!r}, expected 'sha256'"
    if not cfg["stages"]:
        return "stages is empty"
    for i, estagio in enumerate(cfg["stages"]):
        forma = FORMA_DO_ESTAGIO.get(estagio["kind"])
        if forma is None:
            return f"stages[{i}].kind is {estagio['kind']!r}, expected 'file' or 'tree'"
        desvio = _desvio(estagio, forma, f"stages[{i}]")
        if desvio:
            return desvio
        for rel in [estagio["path"]] if estagio["kind"] == "file" else estagio["globs"]:
            if not _relativo(rel):
                return f"stages[{i}] holds {rel!r}, not a path relative to the repository root"
    return None


def _desvio_da_cadeia(linhas: list) -> str | None:
    """Return where the lines of the chain file depart from what the build writes, or None."""
    forma = dict.fromkeys(CAMPOS_DA_CADEIA, str)
    for i, linha in enumerate(linhas, start=1):
        desvio = _desvio(linha, forma, exato=True)
        if desvio:
            return f"line {i}: {desvio}"
    return None


def _caminhos(obj) -> list[str]:
    """Return every ``path`` value found anywhere inside a JSON-like object."""
    if isinstance(obj, dict):
        achados = [obj["path"]] if isinstance(obj.get("path"), str) else []
        return achados + [p for v in obj.values() for p in _caminhos(v)]
    if isinstance(obj, list):
        return [p for v in obj for p in _caminhos(v)]
    return []


def construir() -> dict:
    """Seal the current files: write manifest, sha256sums and chain line; return the manifest."""
    if not (RAIZ / "env.json").exists():
        freeze_env.main(["--root", str(RAIZ)])
    anteriores = [x for x in _cadeia() if x["run_id"] != RUN_ID]
    prev = anteriores[-1]["chain_head"] if anteriores else ""
    stages_cfg = json.loads(STAGES.read_text(encoding="utf-8"))
    prov = pc.build_chain(RAIZ, stages_cfg, prev)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8")
    pc.write_sha256sums(prov, MANIFEST.parent / "sha256sums.txt")
    linha = {
        "chain_head": prov["chain_head"],
        "prev_chain_head": prov["prev_chain_head"],
        "root": prov["root"],
        "run_id": RUN_ID,
    }
    CHAIN.write_text(
        "".join(json.dumps(x, sort_keys=True) + "\n" for x in [*anteriores, linha]),
        encoding="utf-8",
    )
    return prov


def _folhas(prov: dict) -> dict[str, list[tuple]]:
    """Return ``{stage: [(path, sha256, size), ...]}`` in manifest order."""
    return {
        s["name"]: [(f["path"], f["sha256"], f["size"]) for f in s["leaves"]]
        for s in prov.get("stages", [])
    }


def _problemas_das_folhas(prov: dict) -> list[str]:
    """Compare every listed leaf and ``sha256sums.txt`` with what the files on disk give."""
    problemas = []
    stages_cfg = json.loads(STAGES.read_text(encoding="utf-8"))
    disco = _folhas(pc.build_chain(RAIZ, stages_cfg, ""))
    selado = _folhas(prov)
    for nome in sorted(set(disco) | set(selado)):
        a, b = selado.get(nome, []), disco.get(nome, [])
        if a != b:
            so_manifest = sorted(set(a) - set(b))
            so_disco = sorted(set(b) - set(a))
            problemas.append(
                f"stage {nome}: leaf list differs (manifest only {so_manifest[:3]}, "
                f"disk only {so_disco[:3]})"
            )
    for s in prov.get("stages", []):
        if s.get("nfiles") != len(s["leaves"]):
            problemas.append(f"stage {s['name']}: nfiles {s.get('nfiles')} != {len(s['leaves'])}")
    somas = MANIFEST.parent / "sha256sums.txt"
    with tempfile.TemporaryDirectory() as tmp:  # same writer as the build, never re-implemented
        esperado = Path(tmp) / "sha256sums.txt"
        pc.write_sha256sums(prov, esperado)
        if not somas.exists() or somas.read_bytes() != esperado.read_bytes():
            problemas.append(f"{somas.relative_to(RAIZ)} differs from the manifest")
    return problemas


def _problemas_da_cadeia(prov: dict) -> list[str]:
    """Walk ``runs/CHAIN.jsonl``: genesis, links between lines, and this run's line.

    Each line has already been checked to hold exactly the four string fields the build writes.
    """
    problemas = []
    anterior = pc.ZERO_HEX
    for i, linha in enumerate(_cadeia(), start=1):
        if linha["prev_chain_head"] != anterior:
            problemas.append(f"runs/CHAIN.jsonl line {i}: prev_chain_head is not the previous head")
        hashes = (linha["chain_head"], linha["prev_chain_head"], linha["root"])
        if not all(isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes):
            problemas.append(f"runs/CHAIN.jsonl line {i}: a hash is not 64 lowercase hex digits")
        elif pc.link_head(linha["prev_chain_head"], linha["root"]) != linha["chain_head"]:
            problemas.append(f"runs/CHAIN.jsonl line {i}: chain_head != link(prev, root)")
        anterior = linha["chain_head"]
    elo = [x for x in _cadeia() if x.get("run_id") == RUN_ID]
    if len(elo) != 1:
        problemas.append(f"runs/CHAIN.jsonl: {len(elo)} lines for {RUN_ID} (expected 1)")
    elif elo[0] != {c: (RUN_ID if c == "run_id" else prov.get(c)) for c in CAMPOS_DA_CADEIA}:
        problemas.append("runs/CHAIN.jsonl: the line of this run differs from the manifest")
    return problemas


def _ler_para_verificar() -> tuple[dict | None, list[str]]:
    """Read the manifest, the stages file and the chain file and check their structure.

    Returns
    -------
    tuple of (dict or None, list of str)
        The parsed manifest, and one problem for each of the three files that is missing,
        unreadable, not valid JSON or not the structure the build writes or reads, naming the file.
    """
    leitores = (
        (
            MANIFEST,
            "writes",
            lambda: _json(MANIFEST),
            lambda m: _desvio(m, FORMA_MANIFEST, exato=True),
        ),
        (STAGES, "reads", lambda: _json(STAGES), _desvio_dos_stages),
        (
            CHAIN,
            "writes",
            lambda: [_json(CHAIN, x) for x in _texto(CHAIN).splitlines() if x.strip()],
            _desvio_da_cadeia,
        ),
    )
    lidos, problemas = {}, []
    for caminho, verbo, ler, desvio_de in leitores:
        try:
            lidos[caminho] = ler()
        except ValueError as erro:
            problemas.append(f"cannot verify: {erro}")
            continue
        desvio = desvio_de(lidos[caminho])
        if desvio:
            problemas.append(
                f"cannot verify: {_nome(caminho)} is not the structure the build {verbo} ({desvio})"
            )
    return lidos.get(MANIFEST), problemas


def verificar() -> list[str]:
    """Recompute the chain from disk against the sealed manifest; return the problems found."""
    prov, problemas = _ler_para_verificar()
    if problemas:  # nothing is recomputed against a file of another structure
        return problemas
    problemas = pc.verify(RAIZ, STAGES, prov)
    for caminho in _caminhos(prov):
        if not _relativo(caminho):
            problemas.append(f"path in the manifest is not relative to the root: {caminho}")
    return problemas + _problemas_das_folhas(prov) + _problemas_da_cadeia(prov)


def main(argv=None) -> int:
    """Build the seal, or verify it with ``--verify``; return the problem count (at most 255)."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify", action="store_true", help="recompute and compare; exit = problems")
    args = ap.parse_args(argv)
    if args.verify:
        try:
            problemas = verificar()
        except Exception as erro:  # a sealed file that cannot be read, or any other failure:
            # one problem, never a traceback; the message names the file relative to the root,
            # never the machine's absolute path
            detalhe = str(erro).replace(f"{RAIZ}/", "")
            problemas = [f"cannot verify ({type(erro).__name__}): {detalhe}"]
        for p in problemas:
            print(f"[FAIL] {p}")
        if problemas:
            print(f"[FAIL] {len(problemas)} problem(s): the chain is BROKEN")
        else:
            prov = json.loads(MANIFEST.read_text(encoding="utf-8"))
            print(f"[OK] chain verified: root {prov['root']} · chain_head {prov['chain_head']}")
        return min(len(problemas), 255)  # 256 problems would otherwise exit with status 0
    prov = construir()
    n = sum(s["nfiles"] for s in prov["stages"])
    print(f"[OK] sealed {n} files in {len(prov['stages'])} stages: root {prov['root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
