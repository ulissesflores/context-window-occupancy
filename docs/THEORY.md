# Theory: window occupancy and per-token separability

This document states the closed-form model that the simulations in this repository test, gives the
proofs of the statements marked *Proof*, and fixes the exact scope of each claim. What the tests
lock: the worked instances are recomputed from the closed forms by `tests/test_theory_tripwire.py`,
and the simulation counts quoted in [what is tested](#testing-status) and in
[checked by literal simulation](#literal-simulation-checks) are checked against the sealed outputs,
grids and pre-registrations by `tests/test_doc_numbers.py`.

Contents: [notation and assumptions](#notation) · [Proposition 1](#proposition-1) ·
[Corollary 1](#corollary-1) · [mixed regime](#mixed-regime) · [Corollary 2](#corollary-2) ·
[Corollary 3](#corollary-3) · [Corollary 4](#corollary-4) · [Corollary 5](#corollary-5) ·
[Consequence and scope](#scope) · [what is tested](#testing-status) ·
[checked by literal simulation](#literal-simulation-checks) · [novelty](#novelty) ·
[references](#references)

<a id="notation"></a>

## Notation and assumptions

A model reads a window of `K` tokens that retains the most recent events of a user, the fixed input
context of a Transformer (Vaswani et al., 2017); in the nuFormer transaction model `K = 2048`
(Braithwaite et al., 2025). The history spans `T` days. Events come from sources `s`, each with:

- a rate `λ_s ≥ 0` (events per day) and a cost `k_s > 0` (tokens per event);
- a per-event separability `d_s²`: each event carries an attribute `x ~ N(d_s·y, 1)`, with class
  label `y ∈ {0, 1}`. `d_s²` is the squared separation between the classes, equal to twice the
  Kullback–Leibler divergence per event; it is **not** Shannon information nor Fisher information.

For a mixture `R` of sources, `W_R = Σ_R λ_r k_r` is its token arrival rate (tokens per day). A
mixture saturates the window when `T·W_R ≥ K`. When a source `S` is added, `W′ = W_R + λ_S k_S`.

Assumptions:

- **(i)** events are independent given `y`;
- **(ii)** `d_s` does not depend on the age of the event (with age decay, `ρ_s` below depends on age
  and truncation by recency becomes partly justified, which links this model to the Age of
  Information literature; Kaul et al., 2012);
- **(iii)** fluid approximation: `n_s = λ_s·h`, with horizon `h = min(T, K/Σ_r λ_r k_r)`;
- **(iv)** the reader is optimal: the likelihood ratio over the visible window. This is the
  **ceiling** of any reader of the same window (Neyman & Pearson, 1933), not a prediction of a
  learned model (nor of the nuFormer);
- **(v)** the events of each source arrive by a Poisson process of rate `λ_s` whose whole law does
  not depend on `y` nor on the attributes (signal in the count and in the arrival times is excluded
  by design; the pre-registration fixes Poisson, because an equal rate alone would not suffice:
  regular and clustered processes with the same rate differ in time);
- **(vi)** the values of `ρ_s` for the sources of a production system are not identifiable from
  public data; every numerical instance in this document is illustrative.

Under (i)–(v), with the counts `n_s` of the fluid approximation, the log-likelihood ratio over the
visible events, `Σ_visible d_s·(x_i − d_s/2)`, is Gaussian with mean `+Δ²/2` for `y = 1` and `−Δ²/2`
for `y = 0`, and variance `Δ²` in both classes, where

```text
Δ² = Σ_s n_s d_s²,        AUC = Φ(Δ/√2).
```

The AUC is strictly increasing in `Δ²`, so the sign of a change in AUC is the sign of the change in
`Δ²`.

<a id="proposition-1"></a>

## Proposition 1 — saturated window

**Proposition 1 (saturated window: `T·Σ_r λ_r k_r ≥ K`).** `Δ² = K·Σ_s φ_s ρ_s`, with

```text
φ_s = λ_s k_s / Σ_r λ_r k_r      (occupancy of the window)
ρ_s = d_s² / k_s                 (per-token separability)
```

*Proof.* Saturation gives `h = K/Σλk`, so `Δ² = (K/Σλk)·Σ_s λ_s d_s² = K·Σ_s (λ_s k_s/Σλk)(d_s²/k_s)`. ∎

**Reading.** The window allocates capacity by occupancy `φ_s`, while value comes from per-token
separability `ρ_s`. The corollaries below quantify the mismatch between the two.

<a id="corollary-1"></a>

## Corollary 1 — admission threshold

**Corollary 1 (threshold; equals the pre-registered prediction P1 when `k_s ≡ k`).** Let `R` be the
current mixture, with `W_R = Σ_R λ_r k_r > 0` and saturated (`T·W_R ≥ K`), and let `S` be a source
with `λ_S k_S > 0` (then `R ∪ S` saturates as well). Adding `S` increases the AUC **if and only if**
`ρ_S > ρ̄`, where

```text
ρ̄ = Σ_R φ_r ρ_r = Σ_R λ_r d_r² / W_R
```

is the occupancy-weighted mean of `ρ`, **taken before the addition**.

*Proof.* Let `φ′_S = λ_S k_S / (W_R + λ_S k_S) ∈ (0, 1)`. By Proposition 1,
`Δ²_{R∪S}/K = (1 − φ′_S)·ρ̄ + φ′_S·ρ_S`, the mediant of `ρ̄` and `ρ_S`, while `Δ²_R/K = ρ̄`. Hence
`ΔΔ² = K·φ′_S·(ρ_S − ρ̄)`. ∎

<a id="mixed-regime"></a>

## Observation — mixed regime

**Observation (mixed regime).** This follows from the general formula `h = min(T, K/Σλk)`; it is not
a new corollary. If `R` does not saturate but `R ∪ S` does (`T·W_R < K ≤ T·W′`), adding `S` improves
the AUC if and only if `ρ_S > θ·ρ̄`, with

```text
θ = W_R·(T·W′ − K) / (K·λ_S k_S) ∈ [0, 1).
```

The threshold lies **below** `ρ̄` and depends on `λ_S` and on `T`.

*Proof.* Without `S` the window is not saturated, so `Δ²_R = T·Σ_R λ_r d_r² = T·W_R·ρ̄`. With `S`
it is, so `Δ²_{R∪S} = (K/W′)·(W_R·ρ̄ + λ_S k_S·ρ_S)`. Then `Δ²_{R∪S} > Δ²_R` if and only if
`K·λ_S k_S·ρ_S > W_R·ρ̄·(T·W′ − K)`, that is, `ρ_S > θ·ρ̄`. `θ ≥ 0` because `T·W′ ≥ K`; and, since
`K·λ_S k_S = K·(W′ − W_R)`, `θ < 1` if and only if `T·W_R·W′ < K·W′`, that is, `T·W_R < K`. ∎

**Worked instances.** The grid of the pre-registered replication uses a uniform cost: the window
holds `L = ⌊K/k⌋ = ⌊2048/14⌋ = 146` events, so in event units `K = L` and `k ≡ 1`, and `ρ_C = d_C²`.
With `T = 90`, `λ_A = 0.1`, `λ_B = 0.3`, `λ_C = 3`, `d_A = 0.5` and `d_B = 0.15`, the three additions
of source `C` are all in the mixed regime, and the break-even `d_C* = √(θ·ρ̄)` follows from the
Observation:

| Addition | `T·W_R` | `T·W′` | `θ` | break-even `d_C*` | Corollary 1 threshold `√ρ̄` |
|---|---|---|---|---|---|
| A → AC | 9 | 279 | 0.0304 | 0.087 | 0.50 |
| B → BC | 27 | 297 | 0.1034 | 0.048 | 0.15 |
| AB → ABC | 36 | 306 | 0.1461 | 0.108 | 0.28 |

These break-evens are mixed-regime thresholds: reading them as the Corollary 1 threshold would give
the last column instead, so `d_C*` is never "the threshold of Corollary 1". Two single additions show
both sides of the Observation for A → AC, where `θ·ρ̄ = 0.0076` and `ρ̄ = 0.25`:

| Addition | `d_C` | `ρ_C` | `Δ²` before | `Δ²` after | Reading |
|---|---|---|---|---|---|
| A → AC | 0.05 | 0.0025 | 2.25 | 1.53 | `ρ_C < θ·ρ̄`: worse, although `d_C > 0` |
| A → AC | 0.2 | 0.04 | 2.25 | 6.83 | `θ·ρ̄ < ρ_C < ρ̄`: better, although `ρ_C < ρ̄` |

Panel (a) of Figure 3 (`output/figures/fig3_replication.png`) instantiates this Observation. Panel
(b) (B → BC with `T = 365` and `λ_B = 0.6`, so that `λ_B·T = 219 ≥ 146`) is an instance of
Corollary 1 and Corollary 2: the break-even is `d_C* = d_B = 0.15` for every `λ_C`.

<a id="corollary-2"></a>

## Corollary 2 — frequency sets magnitude, not sign

**Corollary 2 (generalizes P1b; equals P1b when `k_s ≡ k`).** Under the condition of Corollary 1
(`R` already saturated without `S`), `λ_S` enters only through `φ′_S`: the frequency of the new
source decides the magnitude of the change in AUC, never the sign in the saturated regime. This is
the translated literal qualifier of the pre-registration (`data/prereg/01-displacement-replication.md`,
prediction P1b), which also says "and the onset of saturation", a clause that has content only
outside this condition. In the mixed regime, `λ_S` decides both the onset of saturation and the sign,
through `θ`.

<a id="corollary-3"></a>

## Corollary 3 — monotonicity without saturation

**Corollary 3 (generalizes P2; equals P2 when `k_s ≡ k`).** If `T·W′ < K`, that is, without
saturation even with the new source, then `Δ² = T·Σ_s λ_s d_s²` and adding `S` with `d_S > 0` never
decreases the AUC. At the equality `T·W′ = K` the saturated and unsaturated formulas coincide and the
result still holds.

*Proof.* Neither `R` nor `R ∪ S` saturates, so `h = T` for both and
`Δ²_{R∪S} − Δ²_R = T·λ_S d_S² ≥ 0`. ∎

Outside this hypothesis monotonicity fails: see the A → AC instance with `d_C = 0.05` above, and the
mixed-regime cell MIX2 of the token test below.

<a id="corollary-4"></a>

## Corollary 4 — tokenization as a channel lever

**Corollary 4 (tokenization as a channel lever).**

- <a id="corollary-4a"></a>**(a)** Multiplying every `k_s` by `c > 0` divides the saturated `Δ²` by
  `c`, and preserves `φ_s` and every sign of Corollary 1 while the regime remains saturated. `c < 1`
  can de-saturate the window: if only `R ∪ S` saturates, the mixed-regime Observation applies, with
  threshold `θ·ρ̄`; if not even `R ∪ S` saturates, Corollary 3 applies. **Supposition:** `d_s` is
  preserved across tokenizations. This is the theoretical reading of the window capacity of the two
  encodings reported for the nuFormer: `2048/14 ≈ 146.3` transactions at an average of 14 tokens per
  transaction in the compact encoding, against `2048/55 ≈ 37.2` at about 55 tokens per transaction in plain text
  (Braithwaite et al., 2025).
- <a id="corollary-4b"></a>**(b)** Fusing `m` adjacent events of `S` into one event of cost
  `k′ < m·k_S` **without loss**, so that the fused event carries the sufficient statistic of the `m`
  events (rate `λ_S/m`, and `d_S² → m·d_S²`), multiplies `ρ_S` by `m·k_S/k′`, keeps `λ_S d_S²` (the
  separability per day) and reduces the occupancy. The factor is a **fluid ceiling of an ideal
  encoding**: it assumes non-overlapping groups of `m`, with no cost or delay for an incomplete block;
  the fused process is no longer Poisson, so the statement holds in expected value; with loss the
  factor is smaller (for instance `k_S/k′` when only one representative of the `m` events is
  retained). Fusion can flip the sign of Corollary 1. In the mixed regime, the fused source enters
  the Observation with the fused parameters; if fusion de-saturates `R ∪ S`, Corollary 3 applies.

<a id="corollary-5"></a>

## Corollary 5 — optimal allocation

**Corollary 5 (optimal allocation; a ceiling).** Maximizing `Σ_s n_s d_s²` subject to
`Σ_s n_s k_s ≤ K` and `0 ≤ n_s ≤ λ_s T` is the continuous relaxation of the knapsack problem:
filling the window by decreasing `ρ_s`, each source up to `λ_s T`, is optimal (Dantzig, 1957).

- The recency window, `n_s = λ_s·min(T, K/Σλk)` (equal to `λ_s·K/Σλk` under saturation), is a
  **feasible point** of the same problem.
- The ceiling holds among fluid per-source allocations that do not depend on the realized
  attributes; it does not cover policies that select events by the observed value of `x`.
- The cost of displacement is the difference in the objective, `Δ²_opt − Δ²_rec ≥ 0`, not a
  distance between allocations.
- Under (ii), which events of a source enter is immaterial, so per-source quotas (the `n_s` most
  recent events of each source) implement the optimum; with age decay the order uses `ρ` at the
  age of the event, and the nominal `ρ` can lose to recency.

Design implication: adaptive per-source quotas ordered by `ρ_s` (the leftover of one source passes
to the next), or differential compression of the frequent source with low per-token separability.

<a id="scope"></a>

## Consequence and exact scope

**Consequence (exact scope).** Under the model specified, (i)–(v), and with the window already
saturated before the new source (the condition of Corollary 1: `R` already saturated,
`T·W_R ≥ K`), when `ρ_S < ρ̄`, adding `S` lowers the ceiling of the AUC of any reader of the same
observable window.

The ceiling follows from assumption (iv): the Neyman–Pearson bound applies because the reader
receives exactly the specified observation. With `ρ_S ≥ ρ̄`, Corollary 1 gives an increase or
equality. In the mixed regime the threshold is `θ·ρ̄`, and a source with `θ·ρ̄ < ρ_S < ρ̄` improves
the AUC (the A → AC instance with `d_C = 0.2` above).

The harm is displacement of the events of `R`, not confusion with `S`: the optimal reader already uses
`S` in the best possible way. More model capacity does not remove it, because the displaced
information is not in the input; only the design of the channel removes it (selection, compression,
adaptive quotas, a larger `K`).

The Consequence does not predict the change of a specific model, which can lie below the prior
ceiling; Table 4 of Braithwaite et al. (2025) reports a real model and is read separately. Any
shortened restatement, including "a property of the channel, not of the model", must keep the four
qualifiers together: under the model and (i)–(v); the saturation condition of Corollary 1; `ρ_S < ρ̄`;
and the word ceiling.

<a id="testing-status"></a>

## What is tested by simulation and what is analytic only

- **General fluid formula `h = min(T, K/Σλk)` with uniform cost** (pre-registered replication,
  `data/prereg/01-displacement-replication.md`; synthetic and illustrative, in orders of magnitude;
  not a replication of nuFormer): window of `L = 146` events, tested in the saturated
  and the mixed regimes over a grid of 720 cells, with `N = 200,000` users per cell and 5 seeds. For
  the sign of the change in AUC when source `C` is added (A → AC, B → BC, AB → ABC), 149 of the 2,160
  comparisons fall below the pre-registered `|Δ| = 0.005` and stay outside the sign test, there are 0
  ties, and 0 of the 2,011 tested comparisons are discordant. The empirical and closed-form
  indicators of the six-sign pattern agree in 717 of 720 cells. Corollary 1 is the saturated case of
  this formula. Source: `output/replication/resumo.json` (`avaliar_quebra.Q2` and `avaliar_quebra.Q3`).
- **Heterogeneous cost `k_s`** (pre-registered token addendum, `data/prereg/02-token-kat-addendum.md`):
  literal simulation with a budget of `K = 2048` tokens, whole events only, two costs
  `k ∈ {14, 55}`, `N = 100,000` users per combination and 5 seeds, over 8 cells (5 saturated, 2 mixed
  and 1 unsaturated). Each cell refutes a named naive rule (per-event separability that ignores `k`;
  a rate-weighted `ρ̄`; Corollary 1 applied outside saturation; unconditional monotonicity). The sign
  criterion passes in 8 of 8 cells (40 of 40 seed-level signs, 0 ties) and the level criterion in 16
  of 16 combinations. This checks Corollary 1 with `ρ_s = d_s²/k_s` and the occupancy-weighted `ρ̄`;
  the mixed-regime Observation (cell MIX1, with `θ·ρ̄ < ρ_S < ρ̄`, improves in all 5 seeds; cell MIX2,
  with the same `R` and `S` and only `λ_S` changed, has `ρ_S < θ·ρ̄` and worsens in all 5 seeds, so
  `λ_S` alone inverts the sign); and Corollary 3 (cell N1). Source: `output/kat_token/resumo.json`
  (`avaliar_kat`).
- **Limits of the token test** (`data/prereg/03-token-kat-deviations.md`, items 4 and 5): the level
  criterion checks the fluid form and would catch only a gross level error (the literal truncation
  rule is pinned by unit tests); the 8 cells do not discriminate the exponent of `d` when Corollary 1
  is applied without checking the regime (`d/k` and `d²/k` then give the same sign in all 8); under
  the general fluid formula, the mixed cell MIX2 does separate them (`d/k` predicts an improvement,
  `d²/k` the worsening observed in all 5 seeds), a post hoc reading of a single cell that was not
  pre-registered and is recomputed by `tests/test_theory_tripwire.py`; the pre-registered check of
  the exponent, in cells designed against the linear and the cubic rules, is in
  [workflow B](#literal-simulation-checks) (EXP); the comparison of occupancy against rate weighting
  rests on a single cell (S3) in this test, and is checked on a family of cells in both directions
  by the OCC family of [workflow B](#literal-simulation-checks); and `θ` is located only within
  `λ_S ∈ (0.6, 6.0)`.
- **Analytic only.** Corollary 4(a) is an algebraic consequence of the closed form that the level
  criterion checks loosely, and "`d_s` preserved across tokenizations" remains a supposition.
  Corollary 4(b) is checked by literal simulation, with its regime qualifiers, in
  [workflow B](#literal-simulation-checks) (CMP). The linear program of Corollary 5 is analytic
  (Dantzig's ratio rule); its implementation by adaptive per-source quotas is checked by literal
  simulation, with its regime qualifier, in [workflow B](#literal-simulation-checks) (C5).
  Assumption (vi) cannot be tested with public data.
- **Arithmetic checks, not simulations.** `tests/test_theory_tripwire.py` recomputes the worked
  instances of this document from the closed forms, and re-derives the sign statements of
  Corollary 1, of the Observation and of Corollary 3 against the general fluid formula on seeded
  random instances.

<a id="literal-simulation-checks"></a>

## Checked by literal simulation (workflow B)

Each subsection below reports one pre-registered family of literal token-budget simulations, frozen
before its code (the addenda under [`data/prereg/`](../data/prereg/) and the dated amendments in
[`data/PREREGISTRATION.md`](../data/PREREGISTRATION.md)), and checked against the closed forms of
this document. Under the fixed generator and the oracle reader each checked statement is an
algebraic identity of the model, so a family can falsify only the fluid approximation (assumption
(iii)) and the literal implementation: a pass reads "checked by literal simulation", never
"measured" or "established empirically". Each licensed statement carries its regime qualifier, which
is part of the claim. The numbers are rendered from the block of each family in
[`output/results.json`](../output/results.json), derived from the sealed summary of the family, and
are locked by `tests/test_paper_numbers.py` and `tests/test_doc_numbers.py`.

### EXP — exponent of `d` in the per-token separability

Licensed statement (English translation of the Portuguese wording frozen in
[`data/prereg/05-exponent-addendum.md`](../data/prereg/05-exponent-addendum.md), outcome "passes"):
with the window already saturated before the new source, the accounting `ρ_s = d_s²/k_s` of the
optimal reader (exponent 2 analytic, under Gaussian `x`) is preserved by the literal token-budget
window in cells where the rules d/k and d³/k predict the opposite sign, with heterogeneous and
homogeneous cost; checked by literal simulation.

**Status: checked by literal simulation** (the regime qualifier is part of the claim). Under the
fixed generator (Gaussian `x`, Poisson arrivals) and the oracle reader, the exponent of `d` is an
algebraic identity of the model, so the simulation does not measure it: it checks that the literal
pipeline (token-budget truncation, whole events, oracle score, Mann–Whitney AUC) realizes the `d²`
accounting and that the fluid approximation does not distort it, in cells where a rival rule of
thumb `d^p/k^q` predicts the opposite sign. What the grid detects is a reader that does not weight
each event by `d_s`, or weights it by another power. Family C (`EXP-C1` to `EXP-C4`, costs
`k ∈ {14, 55}`, `R` a single source) identifies only the ratio p/q; family D (`EXP-D1` and `EXP-D2`,
homogeneous cost) identifies `p` alone; together, the six signs exclude `d/k`, `d³/k`, `d/√k` and
`d²/k²` as descriptions of this pipeline. In every cell both `R` and `R ∪ S` fill the budget of
`K = 2048` tokens with a margin of at least `z = 4`; `N = 100,000` users per combination and 5
seeds. Outputs: [`output/exponent/resumo.json`](../output/exponent/resumo.json) and
[`output/exponent/celulas.csv`](../output/exponent/celulas.csv). Nothing here concerns the real
`ρ_s` (assumption (vi)), and this is not a replication of nuFormer.

| Cell | Family, side | Rival the cell was designed against | Theory | Fluid `ΔAUC` | Observed `Δ̄` (SE) | Deviation / `tolΔ` |
|---|---|---|---|---|---|---|
| `EXP-C1` | C, low | d/k | improves | +0.0324 | +0.0311 (0.0009) | 0.25 |
| `EXP-C2` | C, low | d/k | worsens | -0.0233 | -0.0242 (0.0012) | 0.15 |
| `EXP-C3` | C, high | d³/k | worsens | -0.0248 | -0.0247 (0.0008) | 0.02 |
| `EXP-C4` | C, high | d³/k | improves | +0.0213 | +0.0199 (0.0008) | 0.25 |
| `EXP-D1` | D, low | d/k | worsens | -0.0250 | -0.0249 (0.0010) | 0.02 |
| `EXP-D2` | D, high | d³/k | improves | +0.0266 | +0.0274 (0.0010) | 0.14 |

EXS (sign): 6 of 6 cells agree with the theory (30 of 30 seed-level signs, 0 ties, 0 discordant).
EXN (level of the difference): 6 of 6 cells within the frozen per-cell `tolΔ`, with deviation
`abs(Δ̄ − ΔAUC)`; largest ratio 0.25. Report only, for this pipeline and not for the world: a rival
rule with ratio p/q outside [1.604, 2.498] (family C) or exponent `p` outside [1.591, 2.510] (family
D) predicts the opposite sign in at least one cell (switch points rounded to three decimals); inside
those intervals the grid does not discriminate.

### OCC — occupancy against rate weighting of the mean `ρ̄` (Corollary 1)

With the window already saturated before the new source, the weight is token occupancy, not event
rate; checked by literal simulation on a 10-cell family in both directions.

**Status: checked by literal token-budget simulation** (pre-registered addendum
[`data/prereg/06-occupancy-addendum.md`](../data/prereg/06-occupancy-addendum.md), amendment OCC in
[`data/PREREGISTRATION.md`](../data/PREREGISTRATION.md); the regime qualifier is part of the claim).
Budget of `K = 2048` tokens, whole events, costs `k ∈ {14, 55}`, `N = 100,000` users per combination
and 5 seeds, over 12 cells in which `R` alone fills the window with a margin (`z(R) ≥ 4`) and the
occupancy-weighted and rate-weighted means of `ρ` predict opposite signs. The verdict family has 10
cells, 5 in which adding `S` improves the AUC and 5 in which it worsens it; 2 threshold cells are
reported apart. Outputs: [`output/occupancy/resumo.json`](../output/occupancy/resumo.json) and
[`output/occupancy/celulas.csv`](../output/occupancy/celulas.csv).

| Criterion | Result |
|---|---|
| OCC-S — sign of the change in AUC, verdict family | 10 of 10 cells agree with occupancy weighting; 50 of 50 seed-level signs; 0 ties; 0 discordant |
| OCC-N — level within the tolerance of the fluid form | 20 of 20 combinations; largest absolute deviation 0.0039 AUC |
| OCC-L — threshold cells, outside the verdict | 2 of 2 agree |

- **Report-only.** In the family of weights `w_r ∝ λ_r k_r^α` (`α = 1` is occupancy, `α = 0` is
  rate), a cell whose sign follows occupancy excludes every `α` below its own `α*`: agreement in the
  verdict family excludes `α < 0.515`, and with the threshold cells `α < 0.748` (truncated, not
  rounded); `α > 1` is not tested. The per-event rule of the token KAT predicts the opposite of
  occupancy in 7 of the 12 cells and is refuted in all 7. The four pairs of cells with the same `R`
  and `S` at two depths agree within their pre-registered bound.
- **Scope.** Under the fixed generator and the oracle reader, occupancy weighting is an algebraic
  identity of the model: the simulation checks the fluid approximation (assumption (iii)) and the
  literal implementation, and cannot discover the weight. The threshold cells only locate `α`; a
  disagreement there would not have favored rate weighting.
- **Disclosure.** The largest level deviation, in the table above, is about twice the largest of the
  token KAT and stays within the loose level tolerance. The design estimate of the
  literal-minus-fluid bias of the difference, outside the criteria, missed the observed sign in half
  of the cells. No criterion depends on either.

### CMP — event fusion (Corollary 4(b))

With the window already saturated before the new source, fusing `m` events of `S` into one event of
`k′` tokens that carries the sufficient statistic multiplies `ρ_S` by `m·k_S/k′` and can invert the
sign of Corollary 1; keeping a single representative, the factor drops to `k_S/k′`; without
saturation even with the new source (raw), lossless fusion does not change the ceiling.

**Status: checked by literal token-budget simulation** (pre-registered addendum
[`data/prereg/07-fusion-addendum.md`](../data/prereg/07-fusion-addendum.md); the regime qualifier of
each clause is part of the claim). The fusion rule is literal: blocks of `m` events anchored at the
most recent event, the incomplete block is the oldest and still costs `k′`; the lossless arm `RF`
sums its members, the lossy control `RP` keeps only the most recent one, and `RS` is the raw
token-budget simulation; the three share one draw. Under the fixed generator and the oracle reader
the sufficiency of the sum is an algebraic identity, so the simulation checks the fluid factor under
literal blocks and truncation, not the sufficiency. The cost `k′` is illustrative, streaming fusion
is not covered, and loss is tested only as a single representative. Outputs:
[`output/fusion/resumo.json`](../output/fusion/resumo.json) and
[`output/fusion/celulas.csv`](../output/fusion/celulas.csv).

| Criterion | Result |
|---|---|
| CMP-S — sign and `3·SE` of the signed contrasts | 28 of 28 agree; 140 of 140 seed-level signs; 0 ties; 0 discordant; 0 without significance |
| CMP-0 — exact null `RF − RS` in cell CMP6 | within `tol_0 = 0.0041` |
| CMP-N — level within the tolerance of the fluid form | 24 of 24 combinations; largest absolute deviation 0.0026 AUC |
| CMP-T — ceiling of the fused arms (outside the verdict) | 4 of 4 |

### C5 — adaptive quotas by per-token separability (Corollary 5)

Pre-registration [`data/prereg/08-quotas-addendum.md`](../data/prereg/08-quotas-addendum.md)
(amendment C5 in [`data/PREREGISTRATION.md`](../data/PREREGISTRATION.md)); outputs
[`output/quotas/resumo.json`](../output/quotas/resumo.json) and
[`output/quotas/celulas.csv`](../output/quotas/celulas.csv). Policies: recency cut (REC); adaptive
quotas by `ρ_s`, where the leftover budget of one source passes to the next (RHO); the same by
per-event separability `d_s²`, ignoring `k` (EVT); fixed quotas from the expected counts, floor and
ceiling (FIXf, FIXc), and proportional to the rate (TAX), none of which reallocates; age-aware
quotas (RHOidade, decay cell only).

**Licensed statement.** With the window saturated and heterogeneous `ρ_s`, adaptive per-source
quotas in the order of `ρ_s` (Dantzig, 1957) beat the recency cut, and ordering by per-event
separability can fall below recency itself; checked by literal simulation with a token budget.

**Per user.** With counts `N_s`, the recency window is a feasible point of the linear program with
ceilings `N_s`, whose optimum the greedy RHO reaches up to the rounding of the critical item (at
most `k_max − 1` idle tokens); since `score | y, D ~ N((y − ½)·D, D)` with `D = Σ_visible d_i²`
independent of `y`, `AUC = E[Φ(√(D₁ + D₀)/2)]` with `D₁, D₀` independent and identically
distributed.

- **Status.** Budget of `K = 2048` tokens, whole events, costs `k ∈ {14, 55}`, `N = 100,000` users
  per cell and 5 seeds, 6 cells, each history read by every policy. The recency AUCs of the two
  anchor cells reproduce the sealed token-KAT rows seed by seed (10 of 10). Sign (C5-O): 13 of 13
  strict comparisons, 0 ties. Size (C5-G): 19 of 19 within `tol_X = 0.00405`, 0 without power. Level
  (C5-N): 30 of 30 (cell, policy) pairs, largest deviation 0.00142 AUC.
- **Rare source (FIX1).** Fixed quotas are sensitive to the quota of the rare source: the ceiling
  beats recency and the floor loses to it. The rival reading "fixed quotas taken from the fluid
  solution implement the optimum" is refuted by size (RHO − FIXc = +0.0154, predicted +0.0159).
- **Equivalence (NUL1, homogeneous `ρ_s`).** The declared comparisons (RHO, EVT and TAX against REC;
  RHO against EVT) agree within `tol_X`; no rival is refutable in this cell.
- **Consequence sub-test (KNP1).** With the window already saturated before the new source, adding
  `S` leaves the adaptive-quota window of `R` unchanged for every user (change in AUC exactly 0 in 5
  of 5 seeds), while the recency cut loses 0.0459 AUC (predicted 0.0441, the harm of Corollary 1).
  Under the pairing, the zero change is close to a tautology (same visible events, same scores): it
  checks the code, not the content.
- **Decay boundary (DEC1, a verdict of its own, sign only).** Same sources as KNP1 with `τ = 60`
  days, outside assumption (ii): with age decay the order uses `ρ` at the age of the event, and the
  nominal `ρ` can lose to recency. Recency minus nominal-`ρ` quotas: +0.0343 (fluid prediction
  +0.0365); age-aware minus nominal-`ρ` quotas: +0.0364 (fluid prediction +0.0379); same sign in 5
  of 5 seeds. Levels are report-only; only this value of `τ` is simulated.
- **Without saturation (by construction, unit test UT-2; not simulated).** Recency and the adaptive
  quotas (RHO, EVT) return the whole history; the fixed quotas (FIXf, FIXc, TAX) stay capped at
  their quota from the expected counts and can cut a history that fits.
- **Disclosure.** The largest distance from the exact prediction, still within `tol_X`, is RHO − REC
  in KNP1 (+0.0459 against +0.0441) and in NUL1 (+0.0029 against +0.0009), about four paired
  standard errors estimated from 5 seeds. The two cells share one random stream (same counts, times
  and noise), so this is one correlated observation, not two.

Exact prediction / mean AUC over the seeds, per cell and policy (the DEC1 row: fluid prediction /
mean, report-only; RHOidade runs only there):

| Cell | REC | RHO | EVT | TAX | FIXf | FIXc | RHOidade |
|---|---|---|---|---|---|---|---|
| KNP1 | 0.80332 / 0.80258 | 0.84738 / 0.84844 | 0.76767 / 0.76805 | 0.80329 / 0.80270 | 0.84738 / 0.84844 | 0.84738 / 0.84844 | — |
| KNP2 | 0.88238 / 0.88198 | 0.91419 / 0.91423 | 0.83873 / 0.83787 | 0.88258 / 0.88222 | 0.91419 / 0.91423 | 0.91419 / 0.91423 | — |
| KNP3 | 0.86645 / 0.86694 | 0.89578 / 0.89600 | 0.85888 / 0.85923 | 0.86666 / 0.86693 | 0.89316 / 0.89330 | 0.89316 / 0.89330 | — |
| FIX1 | 0.84395 / 0.84464 | 0.86993 / 0.87017 | 0.86993 / 0.87017 | 0.82467 / 0.82608 | 0.82467 / 0.82608 | 0.85400 / 0.85476 | — |
| NUL1 | 0.84645 / 0.84552 | 0.84738 / 0.84844 | 0.84685 / 0.84718 | 0.84685 / 0.84602 | 0.84738 / 0.84844 | 0.84738 / 0.84844 | — |
| DEC1 (fluid) | 0.72959 / 0.72793 | 0.69312 / 0.69361 | — | — | — | — | 0.73106 / 0.73000 |

<a id="novelty"></a>

## Novelty

There is no new mathematics here. Proposition 1 and Corollary 1 are the mediant inequality applied to
the fluid window; Corollary 5 is the continuous knapsack relaxation solved by ratio ordering
(Dantzig, 1957); the reader ceiling is the Neyman–Pearson lemma (Neyman & Pearson, 1933). What
belongs to this work is the application to the composition of the input of a transactional
foundation model: which event sources share a fixed window of `K` tokens, at what cost per event,
and the pre-registered simulations that check the resulting sign predictions.

<a id="references"></a>

## References

Braithwaite, D. T., Cavalcanti, M., McEver, R. A., Udagawa, H., Silva, D., Ramanath, R., Meneses, F.,
Yoshida, A., Wingert, E., Ramos, M., Zanfelice, B., & Gupta, A. (2025). *Your spending needs
attention: Modeling financial habits with transformers* (arXiv:2507.23267) [Preprint]. arXiv.
https://doi.org/10.48550/arXiv.2507.23267 — read in version 2, submitted on 2026-08-10
(arXiv:2507.23267v2); the page, section, table and figure numbers cited in this repository refer to
that version.

Dantzig, G. B. (1957). Discrete-variable extremum problems. *Operations Research, 5*(2), 266–288.
https://doi.org/10.1287/opre.5.2.266

Kaul, S., Yates, R., & Gruteser, M. (2012). Real-time status: How often should one update? In *2012
Proceedings IEEE INFOCOM* (pp. 2731–2735). IEEE. https://doi.org/10.1109/INFCOM.2012.6195689

Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient tests of statistical
hypotheses. *Philosophical Transactions of the Royal Society of London. Series A, Containing Papers
of a Mathematical or Physical Character, 231*(694–706), 289–337.
https://doi.org/10.1098/rsta.1933.0009

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., &
Polosukhin, I. (2017). Attention is all you need. In I. Guyon, U. von Luxburg, S. Bengio, H. Wallach,
R. Fergus, S. Vishwanathan, & R. Garnett (Eds.), *Advances in Neural Information Processing Systems*
(Vol. 30). Curran Associates.
https://proceedings.neurips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html
