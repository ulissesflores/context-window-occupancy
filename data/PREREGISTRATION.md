# Pre-registration index

The simulations of this repository were specified in writing before their code was run. The frozen
documents live in [`prereg/`](prereg/); this file indexes them, carries the full translation note
and collects the dated amendments of later work. It is **not** sealed and no output records its
hash: amendments are appended here without touching the sealed files
([`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md)).

## Frozen documents

| File | Written | Role |
|---|---|---|
| [`prereg/01-displacement-replication.md`](prereg/01-displacement-replication.md) | 2026-09-24, before any code of the replication | Displacement replication with uniform event cost: question, model, grid, predictions, falsification criteria (`Q1`–`Q3`) |
| [`prereg/02-token-kat-addendum.md`](prereg/02-token-kat-addendum.md) | 2026-09-26, before any code of the token simulation | Token KAT: heterogeneous event cost, the 8 cells of the grid, the sign criterion (`KT-S`) and the level criterion (`KT-N`); leaves file 01 untouched |
| [`prereg/kat_token_analytic_table.txt`](prereg/kat_token_analytic_table.txt) | 2026-09-26, before any simulation of the token KAT | Closed-form prediction for every cell of [`kat_token_grid.json`](kat_token_grid.json), produced by `code/token_kat_analytic_table.py`; its first line is the SHA-256 of the grid |
| [`prereg/03-token-kat-deviations.md`](prereg/03-token-kat-deviations.md) | 2026-09-26, after the token-KAT run | Dated deviations: wording and scope corrections found by adversarial verification; no data, result or criterion changes |
| [`prereg/04-token-kat-deviations-b.md`](prereg/04-token-kat-deviations-b.md) | 2026-09-26, after the second seal of the token KAT | Second dated deviation: the licensed wording with both regime qualifiers (item 1); no data, result or criterion changes |
| [`prereg/05-exponent-addendum.md`](prereg/05-exponent-addendum.md) | 2026-09-26, before any code of the family | Workflow B, family EXP: exponent of `d` in the per-token separability; grid [`exponent_grid.json`](exponent_grid.json), table [`prereg/exponent_analytic_table.txt`](prereg/exponent_analytic_table.txt) |
| [`prereg/06-occupancy-addendum.md`](prereg/06-occupancy-addendum.md) | 2026-09-26, before any code of the family | Workflow B, family OCC: occupancy against rate weighting of the mean `ρ̄`; grid [`occupancy_grid.json`](occupancy_grid.json), table [`prereg/occupancy_analytic_table.txt`](prereg/occupancy_analytic_table.txt) |
| [`prereg/07-fusion-addendum.md`](prereg/07-fusion-addendum.md) | 2026-09-26, before any code of the family | Workflow B, family CMP: event fusion, Corollary 4(b); grid [`fusion_grid.json`](fusion_grid.json), table [`prereg/fusion_analytic_table.txt`](prereg/fusion_analytic_table.txt) |
| [`prereg/08-quotas-addendum.md`](prereg/08-quotas-addendum.md) | 2026-09-26, before any code of the family | Workflow B, family C5: quotas by `ρ` against the recency cut, Corollary 5; grid [`quotas_grid.json`](quotas_grid.json), table [`prereg/quotas_analytic_table.txt`](prereg/quotas_analytic_table.txt) |
| [`prereg/09-exponent-deviations.md`](prereg/09-exponent-deviations.md) | 2026-09-27, after the family's published run | Dated deviations of family EXP: interpretations of ambiguous passages (among them the reading of a tie, corrected in code only), and the dated record that addendum `05` requires for the line of declared limits; no data, criterion, tolerance or verdict changes |
| [`prereg/10-occupancy-deviations.md`](prereg/10-occupancy-deviations.md) | 2026-09-27, after the family's published run | Dated deviations of family OCC: interpretations, the order of the replicated and published runs, a test added after the published run, and the lower bounds of `α` truncated, never rounded; no data, criterion, tolerance or verdict changes |
| [`prereg/11-fusion-deviations.md`](prereg/11-fusion-deviations.md) | 2026-09-27, after the family's published run | Dated deviations of family CMP: interpretations of ambiguous passages and one wording change of the testing-status line; no data, criterion, tolerance or verdict changes |
| [`prereg/12-quotas-deviations.md`](prereg/12-quotas-deviations.md) | 2026-09-27, after the family's published run | Dated deviations of family C5: the text erratum of addendum `08` with its adopted wording (item 1), interpretations, two tests added after the published run, and one wording change; no data, criterion, tolerance or verdict changes |
| [`prereg/13-token-kat-item5-note.md`](prereg/13-token-kat-item5-note.md) | 2026-09-27, after the workflow-B runs | Dated note on item 5 of the token-KAT deviations (`03`): what families EXP and OCC did with two of its three clauses; edits neither deviations file |

What was frozen before which run, and how the repository checks it (the token-KAT summary records
the SHA-256 of the addendum and of the grid it ran with; each workflow-B summary, those of its
addendum, grid and analytic table), is in
[`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md#pre-registration-and-what-was-frozen-before-each-run).

## Translation note

The Markdown files and the analytic tables under `prereg/` were frozen in Portuguese; the
repository keeps them in Portuguese so that their bytes stay what was frozen, apart from
sanitization (the four workflow-B grids and analytic tables are byte-identical to the frozen
ones). Each copy differs
from its original only in the title line, file paths and cell identifiers: private paths were
mapped to the paths of this repository (`code/`, `tests/`, `data/`, `output/`); pointers to private
notes were replaced by bracketed placeholders (`[nota privada, não distribuída]` = private note, not
distributed; `[verificação adversarial privada]` = private adversarial verification;
`[registro privado de estado]` = private state log); and the two token-KAT cells of the mixed regime
were renamed `MIX1` and `MIX2`. Wording, numbers and criteria are otherwise verbatim. The workflow-B
files (`05` to `13`) each open with their own translation note, which lists every change made to
that file, including the few wording changes that a path swap alone could not make.

Every SHA-256 quoted inside those files refers to the private original of the file it names, with
two exceptions, both outputs that this repository holds. The first is the two replication outputs
(`output/replication/celulas.csv` and `output/replication/resumo.json`), which this repository
regenerates byte for byte; `tests/test_paper_numbers.py` checks those two hashes against file 01.
The second is the summary of family EXP quoted in file 09 (`output/exponent/resumo.json`) and the
two outputs of family OCC quoted in file 10 (`output/occupancy/resumo.json` and
`output/occupancy/celulas.csv`), which this repository carries byte for byte; the translation
notes of files 09 and 10 list these exceptions.

**How to read statements about files (note dated 2026-09-27, amended twice later the same day; the
frozen files are unchanged).** Files `01` to `04` were written about the private chain. Because the
sanitization maps their private paths to the paths of this repository, a sentence of those four
files that states a fact about a file (it is a sealed leaf of one of the private seals named `r1` to
`r4`, it was or was not edited, it is or is not listed by a stages file) describes the private
original on the date of that document, not the file of this repository that now sits at the mapped
path. Files `05` to `13` were written for this repository: as their translation notes say, a path
in them names the file of this repository, and a sentence about that file describes it on the date
of the document. For example, item 11 of
[`prereg/10-occupancy-deviations.md`](prereg/10-occupancy-deviations.md) and item 13 of
[`prereg/12-quotas-deviations.md`](prereg/12-quotas-deviations.md) record that
`tests/test_occupancy.py` and `tests/test_quotas.py` of this repository were modified after the
published run of their family, and sections 0.2 and 1.14 of
[`prereg/05-exponent-addendum.md`](prereg/05-exponent-addendum.md) list leaves of this repository's
`configs/stages.json`. In files `05` to `13`, a sentence is about a private file where it says so,
by naming a private original ("original privado"), the private sealed code ("código privado
selado"), one of the seals `r1` to `r4` or a bracketed placeholder, or by keeping the bare name of a
piece of private evidence next to its SHA-256, as the translation note of that file lists. Two
further cases carry their mark in the translation note of the file, not in the sentence. First, a
line number (`l.`) in files `09` to `12` cites the private original of the document named in the
same sentence: the addendum, whose copy under `data/prereg/` opens with a translation note and so
numbers its lines differently, or, where the sentence says so, the author's private draft of the
article. Second, a name that the translation note of a file glosses as a private document of the
author (for example a draft, a design note, a report or a ledger) refers to that private document,
as the note says. The SHA-256 values in all thirteen files follow the paragraph above. In files
`01` to `04`, three kinds of sentence are affected:

- **Sealed leaves and edits.** For example, item 7 of
  [`prereg/03-token-kat-deviations.md`](prereg/03-token-kat-deviations.md) says that
  `tests/test_token_kat.py` is a sealed leaf of `r3` and was not edited: that is true of the private
  test; the file of this repository is its port, with the changes listed in
  [`CHANGELOG.md`](../CHANGELOG.md), sealed in the chain of this repository.
- **Stages files.** Item 8 of the same file refers to the stages files of the private chain; the
  mapped path `configs/stages.json` names this repository's file, which was written later. The
  invariant it states (no sealed glob matches `output/replicated/`) holds here as well and is tested
  by `tests/test_stages_disjoint.py`.
- **Checksum lines.** The block in `sha256sum` format of
  [`prereg/01-displacement-replication.md`](prereg/01-displacement-replication.md) hashes the private
  originals: its two output lines (`output/replication/celulas.csv`, `output/replication/resumo.json`)
  match this repository, as stated above, and its two code lines (`code/displacement.py`,
  `code/run_replication.py`) do not, so `sha256sum -c` on that block reports those two as failed.
  The code of this repository is checked by its own seal instead.

For every file of this repository, the seal of record is `configs/stages.json` with `runs/v0.1.0/`
([`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md#the-provenance-chain)).

Glossary: pré-registro = pre-registration; adendo = addendum; desvio = deviation; réplica =
replication; célula = cell; semente = seed; janela = window; saturado / misto / não saturado =
saturated / mixed / unsaturated; melhora / piora = improves / worsens; selo = provenance seal;
critério de quebra = falsification criterion; frase licenciada = licensed wording (the sentence
that the sealed result supports).

## Amendments

Dated amendments are appended below, oldest first. Each one is preceded by an HTML comment that
names it, and each points to the frozen document it adds, which is written before the code it
specifies.

<!-- amendment: expoente-d -->
### 2026-09-26 — Amendment EXP: exponent of `d` in the per-token separability (limit (a) of the token KAT)

Frozen on 2026-09-26, before any simulation code, test or output of this family existed in this repository;
`data/prereg/01`–`04` are not changed. It closes, for the exponent of `d` only, the open limit (a) of the token-KAT
deviations (the level check is loose: it confirms the fluid form but does not discriminate the exponent of `d`).

| File | Role | sha256 |
|---|---|---|
| `data/prereg/05-exponent-addendum.md` | pre-registration (sanitized Portuguese copy with an English translation note) | frozen private original: `9c9fce0674993e16fccbeee10ec3de20422532acf8352d72cb06908302524428` |
| `data/exponent_grid.json` | grid: 6 cells × 2 combos × 5 seeds = 60 simulations of 100,000 users each | `5a365aee2307ee2fb568f2221bbdf252ffe7c9e2c389b4082de8c9f928a04dda` (byte-identical to the frozen grid) |
| `data/prereg/exponent_analytic_table.txt` | analytic table: closed form computed before any simulation, no random draw (stdout of `code/exponent_analytic_table.py` on the grid; two byte-identical runs) | `4cd78db2bd03b558d522053945e052827d2c529b377f8b3fdd5880cba107556a` (byte-identical to the frozen table) |

- **Random stream tag: `5`.** `numpy.random.default_rng([semente, i_celula, i_combo, 5, i_bloco])` (seed, cell
  index, combo index, tag, block index), exclusive to this family: `3` is the token KAT; `6`, `7` and `8` are the
  sister families. The grid stores it under the key `tag` and has no `tag_r3` key.
- **What is tested.** With the window already saturated before the new source, six cells (`EXP-C1` to `EXP-C4`,
  family C, heterogeneous cost; `EXP-D1` and `EXP-D2`, family D, homogeneous cost `k = 14`; `K = 2048`, `T = 180`)
  in which the linear rule `d/k` (low side) or the cubic rule `d³/k` (high side) predicts the sign opposite to the
  theory's `ρ = d²/k`. **EXS (sign):** the sign of `Δ̄ = mean AUC(R ∪ S) − mean AUC(R)` over the 5 seeds equals the
  theory's in all 6 cells; one disagreement fails, and a tie (`|predicted ΔAUC| < 3·EP_emp`) fails for lack of
  power. **EXN (level of the difference):** `|Δ̄ − fluid ΔAUC| ≤ tolΔ` in all 6 cells, with the frozen per-cell
  `tolΔ = 0.0020 + 3·EP_Δ`. The family passes only if EXS 6/6, EXN 6/6 and the unit tests EX1–EX5 are green.
- **Common limit.** With the window already saturated before the new source, the exponent 2 of `d` is an algebraic
  identity of the generating model (`x ~ N(d_s·y, 1)`) with the optimal (oracle) reader, so this family can falsify
  only the fluid approximation and the literal implementation (token-budget window, reader); a pass reads "checked by
  literal simulation", never "measured" or "established empirically".
- **Files this family adds:** `code/run_grid.py` (runner shared with the OCC family), `code/exponent_analytic_table.py`,
  `tests/test_exponent.py`, `output/exponent/celulas.csv` and `output/exponent/resumo.json`; the verdict goes to the
  EXP block of `output/results.json`, locked by `tests/test_paper_numbers.py`. This amendment does not receive the
  results, and a deviation, if any, goes to a new dated file.

<!-- amendment: occ -->
### 2026-09-26 — Amendment OCC: occupancy × rate weighting of the mean `ρ̄` (limit (b))

Frozen on 2026-09-26, before any code, test or output of this family existed; `data/prereg/01`–`04` are not
changed. This is one of four dated amendments of the same batch (`05` exponent of `d`, `06` occupancy × rate, `07`
fusion, `08` quotas); each family has its own random stream and its own verdict, and no outcome carries another.

| File | Role | sha256 |
|---|---|---|
| `data/prereg/06-occupancy-addendum.md` | pre-registration (Portuguese; sanitized copy with an English translation note) | `14061945a837d79c291d7a2f077621472bd6ee13b2a793802464024c6856d241` (this copy; the frozen private original is `574dccf9065f1860537dab6e5928ea9d1f5f17b6b736b0ac9d78e6639be55c19`) |
| `data/occupancy_grid.json` | grid: 12 cells × 2 combos × 5 seeds = 120 simulations of 100,000 users each | `64ae62f966e22e7de03960a6ca11af70cfa553e3892c0b29d7d15e40a3524b0e` (byte-identical to the frozen grid) |
| `data/prereg/occupancy_analytic_table.txt` | analytic table: closed form computed before any simulation, no random draw | `40d922b5f3119c32e9ef3990aea312772074d70f87e2ce72663cea79f1d622a3` (byte-identical to the frozen table) |

- **Random stream tag: `6`.** `numpy.random.default_rng([semente, i_celula, i_combo, 6, i_bloco])` (seed, cell
  index, combo index, tag, block index), exclusive to this family: `3` is the token KAT; `5`, `7` and `8` are the
  sister families. The grid stores it under the key `tag` and has no `tag_r3` key.
- **What is tested.** The token KAT supported occupancy weighting over rate weighting with a single shallow cell
  (`S3`, `z(R) = 2.87`, one direction). This family asks, on 12 cells in both directions (10 in the verdict, 2
  threshold cells reported apart), with the window already saturated before the new source and `z(R) ≥ 4`, whether
  the sign of `ΔAUC` from the literal token-budget simulation follows `ρ̄` weighted by token occupancy (Corollary 1)
  rather than `ρ̄` weighted by event rate. It passes only if the unit tests OCCT1–OCCT3 are green, all 10 verdict
  cells agree (one disagreement fails; one tie fails for lack of power) and all 20 level combos stay within
  tolerance.
- **Common limit.** With the generator fixed and the oracle reader, occupancy weighting is an algebraic identity of
  the model, so this family can falsify only the fluid approximation (assumption (iii)) and the literal
  implementation; a pass reads "checked by literal simulation", never "measured" or "established empirically".
- The results go to `output/occupancy/` and to the OCC block of `output/results.json`; this amendment does not
  receive them, and a deviation, if any, goes to a new dated file.

<!-- amendment: fusao-cmp -->
<!-- amendment 2026-09-26: CMP family (fusion of events, Corollary 4(b), open limit (c)); frozen document prereg/07-fusion-addendum.md -->
### 2026-09-26 — Amendment: family CMP (fusion of events, Corollary 4(b); open limit (c))

Pre-registration frozen before any code of this family existed; the private original has sha256
`f55d02eddf723b0d215759cf2e9f4c2d0296747afab0b1eddb4296eee27c1585`. It adds a test in files of its own and changes no
earlier file of [`prereg/`](prereg/).

| File | Role | sha256 |
|---|---|---|
| [`prereg/07-fusion-addendum.md`](prereg/07-fusion-addendum.md) | the pre-registration (sanitized Portuguese copy with an English translation note) | private original above |
| [`fusion_grid.json`](fusion_grid.json) | frozen grid, byte-identical to the private original | `869127a0cc6aa6e8bbc56840eb6b907ac354d5110521adc87dd69a5869951de6` |
| [`prereg/fusion_analytic_table.txt`](prereg/fusion_analytic_table.txt) | closed-form analytic table computed before any simulation (stdout of `code/fusion_analytic_table.py` on the grid; its first line is the SHA-256 of the grid), byte-identical to the private original | `a4f55d6bbd3233c4edaa56c86652be1e8d43a5c62e9f0ff889361758146bcb2d` |

- **Random stream:** `numpy.random.default_rng([seed, i_cell, i_stream, 7, i_block])`, tag `7`, exclusive to this
  family (tag `3` = token KAT; tags `5`, `6` and `8` = the EXP, OCC and C5 families).
- **What is tested:** whether a literal token-budget simulation (`K = 2048`, whole events only), with `m` adjacent
  events of the new source `S` fused into one event of cost `k′` (lossless arm `RF`: the fused event carries the sum of
  its `m` members; lossy control `RP`: only the most recent member is kept), follows the sign and the level of the
  closed form with fused parameters in 6 cells × 4 arms (`R`, `RS`, `RF`, `RP`) × 5 seeds with `N = 100,000` users:
  28 signed contrasts at `3·SE`, 1 exact null (`tol_0 = 0.0041`) and 24 level checks, against named rival rules
  (§4 of the addendum).
- **Common limit:** under the fixed generator and the oracle reader, the sufficiency of the sum inside a fused event is
  an algebraic identity of the model, so this family can falsify only the fluid approximation and the literal
  implementation (window, fusion rule, reader), and a pass licenses at most "checked by literal simulation", never
  "measured" or "established empirically", for the sentence "with the window already saturated before the new source,
  fusing `m` events of `S` into one event of `k′` tokens that carries the sufficient statistic multiplies `ρ_S` by
  `m·k_S/k′` and can invert the sign of Corollary 1; keeping a single representative, the factor drops to `k_S/k′`;
  without saturation even with the new source (raw), lossless fusion does not change the ceiling".
- **Files this family adds:** `code/fusion.py`, `code/run_fusion.py`, `code/fusion_analytic_table.py`,
  `tests/test_fusion.py`, `output/fusion/celulas.csv` and `output/fusion/resumo.json`; the verdict goes to the family
  block of `output/results.json`, locked by `tests/test_paper_numbers.py`.

<!-- amendment: cotas-c5 -->
<!-- amendment 2026-09-26: C5 quotas (data/prereg/08-quotas-addendum.md) -->
### 2026-09-26 — Amendment C5: quotas by `ρ` against the recency cut (Corollary 5; open limit (d))

Frozen on 2026-09-26, before any code, test or output of this family existed; `data/prereg/01`–`04` are not changed.
It addresses, for Corollary 5 only, the "analytic only" limit stated in `docs/THEORY.md#testing-status` (see also
`docs/THEORY.md#corollary-5`); Corollary 4(b) is a separate family with a separate verdict. Creation order is the
only proof of precedence: grid, generator, analytic table, then the pre-registration.

| File | Role | sha256 |
|---|---|---|
| `data/prereg/08-quotas-addendum.md` | pre-registration (sanitized Portuguese copy with an English translation note) | frozen private original: `6e30e20d4ddc0283743366ee13c7cf5e1319476fd147489059dde13f55fdf807` |
| `data/quotas_grid.json` | grid (single source): 6 cells × 5 seeds × `N = 100,000` users, each history read by every policy | `b0a82de2a4690143996d5bdf196bd91f44e75e9c774c0515b7a9c767ba97a42b` (byte-identical to the frozen grid) |
| `data/prereg/quotas_analytic_table.txt` | analytic table: exact and fluid predictions computed before any simulation, no random draw (stdout of `code/quotas_analytic_table.py` on the grid; two byte-identical runs) | `a206f1555df554e761b5d9212451ac65ac3bb2082ff765ad7c4b885697569189` (byte-identical to the frozen table) |

- **Random stream tag: `8`.** `numpy.random.default_rng([semente, i_celula, i_combo, 8, i_bloco])` (seed, cell index,
  combo index, tag, block index) for cells KNP3 and FIX1, exclusive to this family: `3` is the token KAT; `5`, `6`
  and `7` are the sister families. The grid stores it under the key `tag` and has no `tag_r3` key. By design, and
  declared, cells KNP1 and KNP2 reuse the sealed token-KAT streams (tag `3`, `R ∪ S` of S1a and S2b), so their recency
  AUCs must reproduce, seed by seed, the rows of `output/kat_token/celulas.csv`; NUL1 and DEC1 reuse the KNP1 stream.
- **What is tested.** In a saturated window of `K = 2048` tokens, with integer events and Poisson counts, whether the
  literal simulation matches the exact prediction frozen in the analytic table for: adaptive per-source quotas ordered
  by `ρ_s = d_s²/k_s` against the recency cut, in sign and size (C5-O, C5-G); ordering by per-event separability
  `d_s²` falling below (KNP1–KNP3); rounded fixed quotas on a rare source (FIX1); and equivalence when `ρ` is
  homogeneous (NUL1). Beside these sit the Consequence sub-test (C5-C, KNP1) and the decay-by-age boundary outside
  assumption (ii) (DEC1, a verdict of its own that uses the sign only, C5-D). The tolerance is fixed at
  `tol_X = 0.00405` and is never recomputed from the data.
- **Common limit.** With the generator fixed and the oracle reader, the user-by-user dominance of quotas ordered by `ρ`
  is an algebraic identity of the model, so this family can falsify only the exact and fluid predictions and the
  literal implementation (window, policies, reader); a pass reads "checked by literal simulation", never "measured"
  or "established empirically", for the order of the policies, and the Consequence sub-test is stated with the window
  already saturated before the new source.
- **Files this family adds:** `code/quotas.py`, `code/run_quotas.py`, `code/quotas_analytic_table.py`,
  `tests/test_quotas.py`, `output/quotas/celulas.csv` and `output/quotas/resumo.json`; the verdict goes to the C5
  block of `output/results.json`, locked by `tests/test_paper_numbers.py`. This amendment does not receive the
  results, and a deviation, if any, goes to a new dated file under `data/prereg/`.

<!-- results: workflow-B 2026-09-27 -->
### 2026-09-27 — Results of the workflow-B families (EXP, OCC, CMP, C5)

Recorded after the runs; the four amendments above and every file under [`prereg/`](prereg/) are
unchanged. Each family ran its frozen grid with its frozen command, first into
`output/replicated/<family>/` and then into its sealed directory, and the two were identical byte
for byte. The verdict of each family is in its summary and in its block of
[`output/results.json`](../output/results.json), locked by `tests/test_paper_numbers.py`; each
summary records the SHA-256 of the grid, analytic table and addendum it ran with.

| Family | Verdict | Summary | Block of `results.json` |
|---|---|---|---|
| EXP (addendum `05`) | passes: EXS 6 of 6 cells, EXN 6 of 6 | [`output/exponent/resumo.json`](../output/exponent/resumo.json) | `exponent` |
| OCC (addendum `06`) | passes: OCC-S 10 of 10 cells, OCC-N 20 of 20 combinations; OCC-L 2 of 2 (outside the verdict) | [`output/occupancy/resumo.json`](../output/occupancy/resumo.json) | `occupancy` |
| CMP (addendum `07`) | passes: CMP-S 28 of 28 contrasts, CMP-0 within `tol_0`, CMP-N 24 of 24 combinations; CMP-T 4 of 4 (outside the verdict) | [`output/fusion/resumo.json`](../output/fusion/resumo.json) | `fusion` |
| C5 (addendum `08`) | passes: anchors 10 of 10, C5-O 13 of 13, C5-G 19 of 19, C5-N 30 of 30, C5-C; C5-D (decay boundary) passes | [`output/quotas/resumo.json`](../output/quotas/resumo.json) | `quotas` |

- The unit tests each verdict requires (EXP: EX1–EX5; OCC: OCCT1–OCCT3; CMP: FU1–FU5; C5: UT-1 to
  UT-6) pass: `tests/test_exponent.py`, `tests/test_occupancy.py`, `tests/test_fusion.py`,
  `tests/test_quotas.py`.
- The number of processes (4 in these runs; 8 in the cost estimates of the addenda) is not a
  parameter: it never enters the random stream.
- Interpretations of ambiguous passages made while implementing the families: the main ones are
  listed in [`CHANGELOG.md`](../CHANGELOG.md), and the full list is in the dated deviation files
  `09` to `12`, indexed above, with a dated note on item 5 of the token-KAT deviations (`13`); none
  changes a criterion, a tolerance, an expected number or a verdict.
- One text erratum of addendum `08`, recorded in
  [`prereg/12-quotas-deviations.md`](prereg/12-quotas-deviations.md), item 1: three passages (§1,
  §10 and unit test UT-2 of §11) say that without saturation every policy returns the whole
  history, which contradicts the definition of the policies in §4 of the same addendum. Adopted
  wording: without saturation, recency and the adaptive quotas (RHO, EVT) return the whole history;
  the fixed quotas (FIXf, FIXc, TAX) stay capped at their quota from the expected counts and can cut
  a history that fits. The definition prevails, the code implements it, and the verdict is
  unaffected because every cell is saturated by design.
