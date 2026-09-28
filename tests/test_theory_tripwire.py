"""Tripwire for ``docs/THEORY.md``.

The theory document is the only English statement of the closed-form model. These tests fail when
an edit drops or duplicates a regime qualifier, loses a statement, a proof or an anchor, detaches a
qualifier from the Consequence, quotes a number that the closed form does not reproduce, or swaps a
verified reference identifier. They also re-derive the sign statements of Corollary 1, of the
mixed-regime Observation and of Corollary 3 against the general fluid formula. None of these checks
is a simulation: they are arithmetic on the closed forms.
"""

from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
THEORY = RAIZ / "docs" / "THEORY.md"
KAT_GRID = RAIZ / "data" / "kat_token_grid.json"
KAT_SUMMARY = RAIZ / "output" / "kat_token" / "resumo.json"

# Regime qualifiers translated literally from the pre-registration; each must appear exactly once.
QUALIFIERS = (
    "with the window already saturated before the new source",
    "without saturation even with the new source",
    "never the sign in the saturated regime",
)
QUALIFIER_CORES = (
    "before the new source",
    "even with the new source",
    "in the saturated regime",
)

# Workflow B (pre-registered literal simulations of the four open limits): the family statements
# live in their own section, one subsection "### <ID> — <title>" per family. There, each qualifier
# appears at most once per subsection, never in the section preamble, never from another family and
# never as a bare fragment; the "exactly once" rule above holds for the rest of the document.
SIM_ANCHOR = "literal-simulation-checks"
SIM_HEADING = "## Checked by literal simulation (workflow B)"
OWN_C5 = (
    "with the window saturated"  # the quota family's own regime: the whole history is saturated
)
FAMILY_QUALIFIERS = {  # family -> qualifiers it may state (at least one is required)
    "EXP": {QUALIFIERS[0]},
    "OCC": {QUALIFIERS[0]},
    "CMP": {QUALIFIERS[0], QUALIFIERS[1]},
    "C5": {OWN_C5, QUALIFIERS[0]},
}
FRAGMENTS = {  # fragment -> the only qualifier it may appear inside
    "before the new source": QUALIFIERS[0],
    "already saturated": QUALIFIERS[0],
    "even with the new source": QUALIFIERS[1],
    "in the saturated regime": QUALIFIERS[2],
}

# anchor -> (bold statement label, formula that must appear in the same section)
STATEMENTS = {
    "proposition-1": ("**Proposition 1 (", "`Δ² = K·Σ_s φ_s ρ_s`"),
    "corollary-1": ("**Corollary 1 (", "`ρ_S > ρ̄`"),
    "mixed-regime": (
        "**Observation (mixed regime).**",
        "θ = W_R·(T·W′ − K) / (K·λ_S k_S) ∈ [0, 1)",
    ),
    "corollary-2": ("**Corollary 2 (", "`φ′_S`"),
    "corollary-3": ("**Corollary 3 (", "`T·W′ < K`"),
    "corollary-4": ("**Corollary 4 (", "`m·k_S/k′`"),
    "corollary-5": ("**Corollary 5 (", "`Δ²_opt − Δ²_rec ≥ 0`"),
    "scope": ("**Consequence (exact scope).**", "lowers the ceiling of the AUC"),
}
ANCHORS = (
    "notation",
    *STATEMENTS,
    "corollary-4a",
    "corollary-4b",
    "testing-status",
    "novelty",
    "references",
)
PROVED = ("proposition-1", "corollary-1", "mixed-regime", "corollary-3")

# Verified bibliographic identifiers; the spurious DOI prefix attached to Vaswani et al. by a
# metadata aggregator must never appear.
REFERENCE_IDS = (
    "https://doi.org/10.48550/arXiv.2507.23267",
    "https://doi.org/10.1287/opre.5.2.266",
    "https://doi.org/10.1109/INFCOM.2012.6195689",
    "https://doi.org/10.1098/rsta.1933.0009",
    # the published title carries the prefix "IX." (the verified form of the reference)
    "Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient tests",
    "https://proceedings.neurips.cc/paper_files/paper/2017/hash/"
    "3f5ee243547dee91fbd053c1c4a845aa-Abstract.html",
)

# Grid of the pre-registered replication used by the worked instances (uniform cost, k = 1).
WINDOW_EVENTS = 146
GRID_T = 90
GRID_RATES = {"A": 0.1, "B": 0.3, "C": 3.0}
GRID_SEPARATIONS = {"A": 0.5, "B": 0.15}


@pytest.fixture(scope="module")
def theory() -> str:
    """Load the theory document.

    Returns
    -------
    str
        Full text of ``docs/THEORY.md``.
    """
    return THEORY.read_text(encoding="utf-8")


def _section(text: str, anchor: str) -> str:
    """Return the text between a top-level anchor and the next top-level anchor.

    Parameters
    ----------
    text : str
        Full theory document.
    anchor : str
        Anchor id written as ``<a id="..."></a>`` alone on its line.

    Returns
    -------
    str
        Section body; inline anchors (inside list items) do not end a section.
    """
    parts = re.split(r'^<a id="([^"]+)"></a>$', text, flags=re.M)
    sections = dict(zip(parts[1::2], parts[2::2], strict=True))
    return sections[anchor]


def _without_sim_section(text: str) -> str:
    """Return the document without the workflow-B section (unchanged when the anchor is absent).

    Parameters
    ----------
    text : str
        Full theory document.

    Returns
    -------
    str
        Document with the anchor line and the body of ``SIM_ANCHOR`` removed.
    """
    parts = re.split(r'^(<a id="[^"]+"></a>)$', text, flags=re.M)
    kept = [parts[0]]
    for tag, body in zip(parts[1::2], parts[2::2], strict=True):
        if tag != f'<a id="{SIM_ANCHOR}"></a>':
            kept += [tag, body]
    return "".join(kept)


def sim_section_problems(text: str) -> list[str]:
    """Check the workflow-B section against the qualifier rules.

    Parameters
    ----------
    text : str
        Full theory document.

    Returns
    -------
    list of str
        One message per violation; empty when the section is compliant or absent.
    """
    tag = f'<a id="{SIM_ANCHOR}"></a>'
    count = len(re.findall(rf"^{re.escape(tag)}$", text, flags=re.M))
    if count == 0:
        return []
    if count > 1:
        return [f"anchor {SIM_ANCHOR!r} defined {count} times"]
    section = _section(text, SIM_ANCHOR)
    problems = [] if SIM_HEADING in section else ["heading missing under the anchor"]
    preamble, *subsections = re.split(r"^### ", section, flags=re.M)
    every = set(QUALIFIERS) | {OWN_C5} | set(FRAGMENTS)
    flat = " ".join(preamble.split()).lower()  # sentences may start with a capital letter
    problems += [f"preamble quotes {q!r}" for q in sorted(every) if q in flat]
    for sub in subsections:
        family = sub.split(" ", 1)[0].strip()
        if family not in FAMILY_QUALIFIERS:
            problems.append(f"unknown family subsection {family!r}")
            continue
        flat = " ".join(sub.split()).lower()
        present = {q for q in set(QUALIFIERS) | {OWN_C5} if q in flat}
        problems += [
            f"{family}: {q!r} appears {flat.count(q)} times"
            for q in sorted(present)
            if flat.count(q) > 1
        ]
        if not present & FAMILY_QUALIFIERS[family]:
            problems.append(f"{family}: no regime qualifier")
        problems += [
            f"{family}: qualifier of another family {q!r}"
            for q in sorted(present - FAMILY_QUALIFIERS[family])
        ]
        problems += [
            f"{family}: bare fragment {frag!r}"
            for frag, full in FRAGMENTS.items()
            if flat.count(frag) != flat.count(full)
        ]
    return problems


def _delta2(sources: dict[str, tuple[float, float, float]], horizon: float, window: float) -> float:
    """Evaluate the general fluid formula for the squared separation.

    Parameters
    ----------
    sources : dict of str to tuple of float
        Map from source name to ``(rate, cost, separation)``.
    horizon : float
        History length ``T`` in days.
    window : float
        Window size ``K`` in tokens.

    Returns
    -------
    float
        ``Δ² = h·Σ λ_s d_s²`` with ``h = min(T, K / Σ λ_s k_s)``.
    """
    load = sum(rate * cost for rate, cost, _ in sources.values())
    visible_days = min(horizon, window / load)
    return visible_days * sum(rate * sep**2 for rate, _, sep in sources.values())


def _grid_mixture(names: str, sep_c: float | None = None) -> dict[str, tuple[float, float, float]]:
    """Build a mixture of the replication grid with unit cost per event.

    Parameters
    ----------
    names : str
        Source letters, for instance ``"AB"``.
    sep_c : float or None, optional
        Separation of source ``C`` when it is part of the mixture.

    Returns
    -------
    dict of str to tuple of float
        Map from source name to ``(rate, 1.0, separation)``.
    """
    seps = {**GRID_SEPARATIONS, "C": sep_c}
    return {name: (GRID_RATES[name], 1.0, seps[name]) for name in names}


@pytest.mark.parametrize("phrase", QUALIFIERS + QUALIFIER_CORES)
def test_regime_qualifier_appears_exactly_once(theory: str, phrase: str) -> None:
    """Assert that each literal regime qualifier, and its core, appears exactly once.

    Parameters
    ----------
    theory : str
        Full theory document.
    phrase : str
        Qualifier or qualifier core.
    """
    # Markdown wraps lines; compare on normalized whitespace, outside the workflow-B section
    flat = " ".join(_without_sim_section(theory).split())
    assert flat.count(phrase) == 1, f"{phrase!r} appears {flat.count(phrase)} times"


@pytest.mark.parametrize("anchor", ANCHORS)
def test_anchor_defined_once(theory: str, anchor: str) -> None:
    """Assert that each anchor used by external links is defined exactly once.

    Parameters
    ----------
    theory : str
        Full theory document.
    anchor : str
        Anchor id.
    """
    assert theory.count(f'<a id="{anchor}"></a>') == 1


@pytest.mark.parametrize(("anchor", "label", "formula"), [(a, *v) for a, v in STATEMENTS.items()])
def test_statement_lives_in_its_section(theory: str, anchor: str, label: str, formula: str) -> None:
    """Assert that each statement and its key formula sit under the matching anchor.

    Parameters
    ----------
    theory : str
        Full theory document.
    anchor : str
        Anchor id of the section.
    label : str
        Bold label that opens the statement.
    formula : str
        Formula or phrase that the statement must carry.
    """
    body = _section(theory, anchor)
    assert label in body
    assert formula in body


@pytest.mark.parametrize("anchor", PROVED)
def test_proofs_are_present_and_closed(theory: str, anchor: str) -> None:
    """Assert that the proved statements keep a proof that ends with a tombstone.

    Parameters
    ----------
    theory : str
        Full theory document.
    anchor : str
        Anchor id of a proved statement.
    """
    body = _section(theory, anchor)
    proof = body.split("*Proof.*", 1)
    assert len(proof) == 2
    assert "∎" in proof[1]


def test_consequence_keeps_its_qualifiers_together(theory: str) -> None:
    """Assert that the Consequence states all four scope qualifiers in one paragraph.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    paragraphs = [p for p in _section(theory, "scope").split("\n\n") if "lowers the ceiling" in p]
    assert len(paragraphs) == 1
    paragraph = " ".join(paragraphs[0].split())
    for needed in (
        "Under the model specified, (i)–(v)",
        QUALIFIERS[0],
        "when `ρ_S < ρ̄`",
        "ceiling",
    ):
        assert needed in paragraph, needed


def test_worked_break_evens_match_closed_form(theory: str) -> None:
    """Assert that the break-even table is the mixed-regime closed form on the replication grid.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    body = _section(theory, "mixed-regime")
    for base in ("A", "B", "AB"):
        load_before = sum(GRID_RATES[name] for name in base)
        load_after = load_before + GRID_RATES["C"]
        rho_bar = sum(GRID_RATES[n] * GRID_SEPARATIONS[n] ** 2 for n in base) / load_before
        theta = (
            load_before * (GRID_T * load_after - WINDOW_EVENTS) / (WINDOW_EVENTS * GRID_RATES["C"])
        )
        assert GRID_T * load_before < WINDOW_EVENTS <= GRID_T * load_after  # mixed regime
        assert 0 <= theta < 1
        break_even = math.sqrt(theta * rho_bar)
        before = _delta2(_grid_mixture(base), GRID_T, WINDOW_EVENTS)
        after = _delta2(_grid_mixture(base + "C", break_even), GRID_T, WINDOW_EVENTS)
        assert math.isclose(before, after, rel_tol=1e-12)
        row = (
            f"| {base} → {base}C | {GRID_T * load_before:.0f} | {GRID_T * load_after:.0f} "
            f"| {theta:.4f} | {break_even:.3f} | {math.sqrt(rho_bar):.2f} |"
        )
        assert row in body, row


def test_worked_additions_match_closed_form(theory: str) -> None:
    """Assert that the two quoted additions A to AC reproduce the fluid formula.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    body = _section(theory, "mixed-regime")
    rho_bar = GRID_SEPARATIONS["A"] ** 2
    theta = (
        GRID_RATES["A"]
        * (GRID_T * (GRID_RATES["A"] + GRID_RATES["C"]) - WINDOW_EVENTS)
        / (WINDOW_EVENTS * GRID_RATES["C"])
    )
    assert f"`θ·ρ̄ = {theta * rho_bar:.4f}` and `ρ̄ = {rho_bar:.2f}`" in body
    for sep_c in (0.05, 0.2):
        before = _delta2(_grid_mixture("A"), GRID_T, WINDOW_EVENTS)
        after = _delta2(_grid_mixture("AC", sep_c), GRID_T, WINDOW_EVENTS)
        row = f"| A → AC | {sep_c:g} | {sep_c**2:g} | {before:.2f} | {after:.2f} |"
        assert row in body, row
        # The reading column must agree with the sign that the Observation predicts.
        assert (after > before) == (sep_c**2 > theta * rho_bar)


def test_panel_b_is_saturated_and_window_capacities(theory: str) -> None:
    """Assert the panel (b) saturation check and the window capacities of the two encodings.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    rate_b, horizon_b = 0.6, 365
    assert rate_b * horizon_b >= WINDOW_EVENTS
    assert f"`λ_B·T = {rate_b * horizon_b:.0f} ≥ {WINDOW_EVENTS}`" in theory
    assert f"`L = ⌊K/k⌋ = ⌊2048/14⌋ = {2048 // 14}`" in theory
    assert 2048 // 14 == WINDOW_EVENTS
    corollary_4 = _section(theory, "corollary-4")
    assert f"`2048/14 ≈ {2048 / 14:.1f}`" in corollary_4
    assert f"`2048/55 ≈ {2048 / 55:.1f}`" in corollary_4


@pytest.mark.parametrize("identifier", REFERENCE_IDS)
def test_reference_identifiers_are_the_verified_ones(theory: str, identifier: str) -> None:
    """Assert that every reference carries its verified DOI or canonical URL.

    Parameters
    ----------
    theory : str
        Full theory document.
    identifier : str
        Verified DOI URL or canonical proceedings URL.
    """
    assert identifier in _section(theory, "references")


def test_no_spurious_doi_for_the_transformer_reference(theory: str) -> None:
    """Assert that the aggregator DOI wrongly attached to Vaswani et al. (2017) is absent.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    assert "10.65215" not in theory


def test_sign_statements_hold_on_random_instances() -> None:
    """Re-derive the sign statements against the general fluid formula on seeded instances.

    Corollary 1 (``R`` saturated): the sign of the change is the sign of ``ρ_S − ρ̄``.
    Observation (only ``R ∪ S`` saturated): it is the sign of ``ρ_S − θ·ρ̄`` with
    ``θ ∈ [0, 1)``. Corollary 3 (neither saturated): the change is never negative. Proposition 1
    is checked as an identity on every saturated mixture.
    """
    rng = random.Random(20260926)
    window = 2048.0
    seen = {"saturated": 0, "mixed": 0, "unsaturated": 0}
    for _ in range(3000):
        # Log-uniform rates put several hundred instances in each of the three regimes.
        base = {
            f"r{i}": (10 ** rng.uniform(-2, 0.8), float(rng.randint(1, 60)), rng.uniform(0, 0.6))
            for i in range(rng.randint(1, 3))
        }
        new = (10 ** rng.uniform(-2, 0.8), float(rng.randint(1, 60)), rng.uniform(0.01, 0.6))
        horizon = float(rng.randint(10, 365))
        load_before = sum(rate * cost for rate, cost, _ in base.values())
        load_after = load_before + new[0] * new[1]
        rho_bar = sum(rate * sep**2 for rate, _, sep in base.values()) / load_before
        rho_new = new[2] ** 2 / new[1]
        change = _delta2({**base, "s": new}, horizon, window) - _delta2(base, horizon, window)
        scale = max(abs(_delta2(base, horizon, window)), 1e-12)

        if horizon * load_before >= window:
            seen["saturated"] += 1
            occupancy = [rate * cost / load_before for rate, cost, _ in base.values()]
            per_token = [sep**2 / cost for _, cost, sep in base.values()]
            identity = window * sum(o * r for o, r in zip(occupancy, per_token, strict=True))
            assert math.isclose(_delta2(base, horizon, window), identity, rel_tol=1e-9)
            margin = rho_new - rho_bar
        elif horizon * load_after >= window:
            seen["mixed"] += 1
            theta = load_before * (horizon * load_after - window) / (window * new[0] * new[1])
            assert 0 <= theta < 1
            margin = rho_new - theta * rho_bar
        else:
            seen["unsaturated"] += 1
            assert change >= 0
            continue

        if abs(change) > 1e-9 * scale:
            assert (change > 0) == (margin > 0)
    assert min(seen.values()) > 300, seen


def _kat_change(cell: dict, exponent: int, check_regime: bool) -> float:
    """Return the predicted change of ``Δ²`` for a token-KAT cell, ``d`` raised to ``exponent``.

    Parameters
    ----------
    cell : dict
        Cell of ``data/kat_token_grid.json``: ``T`` and the sources ``R`` and ``S``, each with
        ``lam``, ``d`` and ``k``.
    exponent : int
        Power of the per-event separation (2 is the model; 1 is the naive alternative).
    check_regime : bool
        True: general fluid formula ``h = min(T, K/Σλk)``. False: the saturated rule of Corollary 1
        applied to the cell whatever its regime, that is, the sign of ``ρ_S − ρ̄`` with
        ``ρ = d^exponent / k`` (only the sign of the returned value is meaningful).

    Returns
    -------
    float
        Signed change whose sign is the predicted direction of the change in AUC.
    """
    window = json.loads(KAT_GRID.read_text(encoding="utf-8"))["K"]
    base = list(cell["R"].values())
    new = list(cell["S"].values())

    def value(sources: list[dict]) -> float:
        """Return the summed separation per day, ``Σ λ d^exponent``."""
        return sum(s["lam"] * s["d"] ** exponent for s in sources)

    def load(sources: list[dict]) -> float:
        """Return the token arrival rate ``Σ λ k``."""
        return sum(s["lam"] * s["k"] for s in sources)

    if not check_regime:
        return value(new) / load(new) - value(base) / load(base)
    horizon = cell["T"]
    after = min(horizon, window / load(base + new)) * value(base + new)
    return after - min(horizon, window / load(base)) * value(base)


def test_exponent_of_d_discriminated_only_by_mix2_post_hoc(theory: str) -> None:
    """Recompute the post hoc statement on the exponent of ``d`` quoted in the testing status.

    Under the saturated rule applied without checking the regime, ``d/k`` and ``d²/k`` give the same
    sign in all 8 cells; under the general fluid formula only MIX2 separates them, with ``d/k``
    predicting an improvement and ``d²/k`` the worsening that every sealed seed shows.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    cells = json.loads(KAT_GRID.read_text(encoding="utf-8"))["celulas"]
    assert len(cells) == 8
    for cell in cells:
        signs = [_kat_change(cell, p, check_regime=False) > 0 for p in (1, 2)]
        assert signs[0] == signs[1], cell["id"]
    separating = [
        c["id"]
        for c in cells
        if (_kat_change(c, 1, check_regime=True) > 0) != (_kat_change(c, 2, check_regime=True) > 0)
    ]
    assert separating == ["MIX2"]
    mix2 = next(c for c in cells if c["id"] == "MIX2")
    assert _kat_change(mix2, 1, check_regime=True) > 0 > _kat_change(mix2, 2, check_regime=True)
    summary = json.loads(KAT_SUMMARY.read_text(encoding="utf-8"))
    seeds = next(c for c in summary["avaliar_kat"]["por_celula"] if c["celula"] == "MIX2")
    assert seeds["sinais_por_semente"] == [-1] * 5
    flat = " ".join(_section(theory, "testing-status").split())
    assert "when Corollary 1 is applied without checking the regime" in flat
    assert "the mixed cell MIX2 does separate them" in flat
    assert "post hoc" in flat and "not pre-registered" in flat


def test_simulations_are_labelled_synthetic(theory: str) -> None:
    """Assert the mandatory label of the replication: synthetic, illustrative, not nuFormer.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    flat = " ".join(_section(theory, "testing-status").split())
    assert (
        "synthetic and illustrative, in orders of magnitude; not a replication of nuFormer" in flat
    )


def test_literal_simulation_section_follows_the_qualifier_rules(theory: str) -> None:
    """Assert that the workflow-B section, when present, follows the qualifier rules.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    assert sim_section_problems(theory) == []


def _with_sim_section(theory: str, body: str) -> str:
    """Insert a workflow-B section with ``body`` right before the novelty anchor.

    Parameters
    ----------
    theory : str
        Full theory document.
    body : str
        Section text after the heading.

    Returns
    -------
    str
        Document with the section inserted.
    """
    block = f'<a id="{SIM_ANCHOR}"></a>\n\n{SIM_HEADING}\n\n{body}\n\n'
    return theory.replace('<a id="novelty"></a>', block + '<a id="novelty"></a>', 1)


_GOOD = (
    "Each family below was checked against its frozen pre-registration.\n\n"
    f"### EXP — exponent of d\n\n{QUALIFIERS[0].capitalize()}, the rule is checked.\n\n"
    f"### CMP — fusion\n\n{QUALIFIERS[0].capitalize()}, fusion helps; "
    f"{QUALIFIERS[1]}, it does not.\n\n"
    f"### C5 — quotas\n\n{OWN_C5.capitalize()}, adaptive quotas beat recency."
)
_SIM_CASES = {  # label -> (section body or None for no section, expected first problem or "")
    "no section": (None, ""),
    "heading without subsection": ("Pending.", ""),
    "compliant families": (_GOOD, ""),
    "preamble quotes a qualifier": (f"Status: {QUALIFIERS[0]}.\n\n" + _GOOD, "preamble quotes"),
    "family without qualifier": (
        "### OCC — occupancy\n\nThe weight is occupancy.",
        "OCC: no regime",
    ),
    "qualifier of another family": (
        f"### EXP — x\n\n{OWN_C5.capitalize()}, it holds.",
        "EXP: qualifier of",
    ),
    "bare fragment": (f"### OCC — x\n\n{QUALIFIERS[0]}; only before the new source.", "OCC: bare"),
    "qualifier twice in a subsection": (
        f"### OCC — x\n\n{QUALIFIERS[0]}; {QUALIFIERS[0]}.",
        "OCC: 'with",
    ),
    "unknown family": (f"### XYZ — x\n\n{QUALIFIERS[0]}.", "unknown family"),
}


@pytest.mark.parametrize("label", _SIM_CASES)
def test_sim_section_rules_on_synthetic_documents(theory: str, label: str) -> None:
    """Check each rule of the workflow-B section on a synthetic document (a mutant or a control).

    Parameters
    ----------
    theory : str
        Full theory document.
    label : str
        Case name in ``_SIM_CASES``.
    """
    body, expected = _SIM_CASES[label]
    text = theory if body is None else _with_sim_section(_without_sim_section(theory), body)
    problems = sim_section_problems(text)
    if expected:
        assert any(p.startswith(expected) for p in problems), problems
    else:
        assert problems == [], problems
    outside = " ".join(_without_sim_section(text).split())
    assert all(outside.count(q) == 1 for q in QUALIFIERS + QUALIFIER_CORES), label


def test_duplicate_outside_the_section_is_still_caught(theory: str) -> None:
    """Check that a qualifier duplicated outside the workflow-B section still breaks the count.

    Parameters
    ----------
    theory : str
        Full theory document.
    """
    text = _with_sim_section(theory, _GOOD).replace(
        "## Novelty", f"## Novelty\n\n{QUALIFIERS[0]}.", 1
    )
    outside = " ".join(_without_sim_section(text).split())
    assert outside.count(QUALIFIERS[0]) == 2
