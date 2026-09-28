"""Shared matplotlib style of the repository figures (deterministic, byte-stable PNGs).

Importing this module selects the ``Agg`` backend and applies the style. The font is DejaVu Serif,
which ships with matplotlib, so the layout measured by the tests does not depend on the fonts
installed on the machine; the PNG is byte-stable between processes of the same environment, while
the numbers behind each figure live in JSON sidecars that are machine-independent.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "output" / "figures"
plt.rcParams.update(
    {
        "font.family": "DejaVu Serif",
        "font.size": 9,
        "mathtext.fontset": "dejavuserif",
        "svg.hashsalt": "context-window-occupancy",
        "savefig.dpi": 300,
    }
)
META = {"Software": None, "Creation Time": None}  # no software tag, no timestamp: byte-stable
