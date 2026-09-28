# Roadmap

What is planned, what it depends on, and what would have to be true for it to happen. Items are
ordered by what they unblock; nothing here is a promise of a date, and nothing here is a result.

## Four follow-up simulations on the limits the token KAT leaves open (done)

**Done (2026-09-27, workflow B).** All four were pre-registered, frozen before their code, run and
passed their pre-registered verdicts. Each licensed statement with its regime qualifier, the
per-cell tables and what each family cannot establish are in
[`docs/THEORY.md`](docs/THEORY.md#literal-simulation-checks); the numbers are in
[`output/results.json`](output/results.json); the dated deviations are
`data/prereg/09-exponent-deviations.md` to `data/prereg/12-quotas-deviations.md`. The plan is kept
below as it was written, each item with the family that closed it.

[`docs/THEORY.md`](docs/THEORY.md#testing-status) lists what the displacement replication and the
token KAT do not test. Each item below addressed one of those limits. The rule for all four is the
one already applied to the displacement replication and the token KAT: **the pre-registration is
written and frozen before any code of the family exists**, as a new file under `data/prereg/`; unit
tests and mutation testing come before any number of the grid; the result enters
`output/results.json` and is asserted by `tests/test_paper_numbers.py`; any change after the first
run is a dated amendment, never an edit of a frozen file. A result that contradicts a statement of
the theory is reported as such.

1. **Exponent of `d` in the per-token separability.** The 8 cells of the token KAT were designed
   against four named naive rules, not against the exponent: in them `d/k` and `d²/k` predict the
   same sign. The follow-up uses cells, with the window already saturated before the new source,
   where a linear or a cubic rule in `d` predicts the opposite sign to `d²/k`. Declared scope in
   advance: in this Gaussian model the exponent is an algebraic identity, so the simulation cannot
   *discover* it; it checks that the literal pipeline (token-budget truncation, Poisson arrivals,
   whole events, optimal score, Mann–Whitney AUC) realizes the `d²` accounting and that the fluid
   approximation does not distort it. Done: family EXP.
2. **Occupancy-weighted against rate-weighted mean.** In the token KAT the comparison between
   weighting `ρ̄` by occupancy (Corollary 1) and by rate rested on a single cell (`S3`), which tests
   one direction only. The follow-up uses a family of cells in both directions, with a saturation
   margin, in which the two weightings predict opposite signs. Done: family OCC.
3. **Event fusion (Corollary 4(b)).** Analytic only before workflow B. The follow-up applies a
   literal fusion rule to the generated events and checks sign and level against the closed form
   with the fused parameters, including a lossy-fusion control and a cell in which fusion
   de-saturates the window. Done: family CMP.
4. **Quotas ordered by `ρ` against recency truncation (Corollary 5).** Analytic only before
   workflow B (the linear program itself stays analytic). The follow-up checks, in a saturated
   window with whole events and Poisson counts, that source quotas ordered by per-token
   separability beat recency truncation by the predicted amount, that ordering by per-event
   separability (ignoring `k`) does worse, and where quotas do not win (homogeneous `ρ`, a fixed
   rounded quota on a rare source, age decay outside assumption (ii)). Done: family C5.

Common limit, stated in advance: none of the four can falsify the algebra of the closed forms; they
can falsify the fluid approximation (iii) and the implementation.

## English identifiers in the code

The port kept the Portuguese identifiers of the authoring code (function names, dictionary keys,
CSV columns), because the byte-for-byte contract freezes the keys of the sealed outputs and renaming
the code risked touching arithmetic. The data dictionary in `REPRODUCIBILITY.md` is the English key
today. Renaming to English is a new sealed run (new output schema, new seal), done once, together
with a mapping table, not an edit of the current seal.

## Zero-setup replication notebook

`colab/replication.ipynb`: installs the pinned environment, verifies the seal, runs the smoke
pipeline and reproduces Figure 3 and the headline numbers, without a local setup.

## Release (only with the author's explicit authorization)

The package lives at `0.x` with no release. When the author authorizes publication: the public
repository is created, CI goes green, the version is bumped to `1.0.0` in the commit right before
the first pre-release (which triggers the archival deposit), and `.zenodo.json` changes from
`closed` to `open` only then. No DOI exists before that authorization.

## Not planned

- **A replication of nuFormer.** Everything here is illustrative, in orders of magnitude, on
  synthetic data; the production model, its data and its training are not reproduced.
- **Estimating the real per-source values of `ρ_s`.** Assumption (vi) of the theory: they are not
  identifiable from public data.
- **A packaged library.** The code exists to make one analysis auditable, not to be depended on.
