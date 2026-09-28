"""Test configuration: put ``code/`` on ``sys.path``.

``code/`` has no ``__init__.py`` on purpose: ``code`` is also a standard-library module (imported by
``pdb``), so the modules are imported by name (``import displacement``), never as ``code.x``.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "code") not in sys.path:
    sys.path.insert(0, str(RAIZ / "code"))
