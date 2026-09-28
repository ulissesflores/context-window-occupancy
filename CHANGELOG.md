# Changelog

All notable changes to this package are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The package lives at `0.x` until the
author authorizes a release; no version below has been tagged or released, and no DOI exists.

## [0.1.0] — 2026-09-28

### Changed — Figure 2: sourced labels, complete flow, network planes named by function (2026-09-27)

No expected number, assertion, tolerance or criterion of the simulations was changed; the change is
in the figure code, its test and the figure itself (of the files of the previous seal:
`code/case_figures.py`, `scripts/make_figures.py`, `tests/test_case_figures.py` and
`output/figures/fig2_architecture.png`; see the re-seal below).

- **Figure 2 (`code/case_figures.py`)**: every label now has a source. Retracted: the roles given to
  two tools ("catalogue (MLflow)", "reports, Dagster"; the case diagram lists MLflow and Dagster
  among its "OSS Tools" with no role, and "Model Catalog" and "Reporting Tool" among its "Internal
  Tools"), "A100/H100" for the training (the nuFormer preprint trains on clusters of H100 or H200
  GPUs) and "SCR (Central Bank)" among the data sources (the case diagram lists "Bureau Data"); "PIX"
  left the data sources (it was a specification of the author). Added: a tools box that lists the
  two tool panels of the case diagram without giving any tool a role; "Monitoring" (field and
  behavioural drift, records compared with historical snapshots, from the preprint) fed by the
  sequences; and the customer app -> API entry of the synchronous path, drawn as a dashed box with
  dashed links because it is a reconstruction of the author. The network planes are named by
  function (training, batch, synchronous) instead of the letters A, B and C. The figure is drawn in
  inches on a canvas of 5.55 x 5.35 in, three rows of boxes, titles at 7.6 pt.
- **`tests/test_case_figures.py`**: locks every drawn text of Figure 2. Each text (box title and
  body, plane tag, arrow label, legend line, footnote) is a key of a source table, and every key is
  drawn; a diagram label must be the value of its ledger row, whose locator carries the capture
  hash (`case-fig-fontes-bureau`, `case-fig-ferramenta-catalogo` and `case-fig-ferramenta-relatorios`
  join the two rows already used; the "OSS Tools" panel is `case-pilha-figura-ocr`); each quantity
  must equal its input in `configs/estimates_inputs.json`; the retracted labels and the letter
  markers must stay out of the drawing and out of the module source, in any letter case; the layout
  is measured on the drawn figure (each text at least 3 pt inside its box, title at least 3 pt from
  the top border, no two texts overlapping, no free text over a box, titles at 7.6 pt or more).
  Twelve mutants (each retracted label put back, a letter marker, "money boxes" in lower case, a
  ledger row renamed, titles at 7.4 pt, a label moved over a box, an input changed, an overflowing
  line, an unsourced label) each fail at the intended assertion, and an untouched copy passes.
- **Claim map** (`scripts/make_figures.py`) and the Figure 2 paragraph of `README.md` updated to
  match.

### Fixed — structure checks and exit code of the verification (2026-09-27)

No expected number, tolerance, criterion or output was changed: of the files of the previous seal,
this fix changed only `make_provenance.py` and `tests/test_failure_paths.py` (see the re-seal below).

- **`make_provenance.py --verify`**: the manifest, `configs/stages.json` and `runs/CHAIN.jsonl` are
  read first and checked against the structure the build writes (the manifest and the chain file:
  exactly the keys it writes, each with its JSON type) or reads (the stages file: stages of kind
  `file` or `tree` whose paths and globs are relative to the repository root). Each file that is
  missing, unreadable, not valid JSON (bytes that are not UTF-8 text included) or of another
  structure is one problem that names it and says where it departs, for example
  `stages[0].leaves[0].size is a boolean, expected an integer`, and nothing is recomputed against
  it. Any other failure is still one problem, with the type of the error, and the exit code is
  capped at 255. Before, the entry below said that such a file was reported as one named problem,
  but a malformed file could still end in a traceback (an array or `null` in place of the
  manifest or of the stages file; an array or a string in place of a chain line; a glob that is not
  relative; JSON nested too deeply for the parser) or in one or more problems that did not name the
  file; a manifest without `stage_order`, `hash_alg` or `domain_separation`, or with a key the build
  does not write, verified with exit code 0; bytes that are not UTF-8 text were reported without the
  name of the file; and 256 problems exited with status 0, since an exit status is taken modulo 256.
  Two messages of the verification that were not in English are now in English.
- **`tests/test_failure_paths.py`** (sealed in the `code` stage): each of the three files missing,
  truncated, not UTF-8 text, or valid JSON of another structure (an array in place of the object, a
  key missing, an extra key in the manifest or in a chain line, a value of the wrong type, a glob
  that is not relative) must give exactly one problem line that names the file, with exit code 1;
  a missing file and a malformed one give one line each; a failure that no check foresees gives one
  line; 256 problems exit with status 255. Fourteen mutants of the verification (each of the three
  structure checks removed, the keys the verification does not read dropped from the expected
  structure, extra keys accepted in the manifest and in a chain line, the relative-path check, the
  naming of a missing file and of bytes that are not UTF-8 text, the reading stopped at the first
  bad file, the recomputation not skipped, the last-resort handler narrowed, the cap removed, a
  boolean accepted as an integer), each run on a copy re-sealed with the mutant, fail at the
  intended assertion, and an untouched copy passes.
- **`REPRODUCIBILITY.md`** and **`README.md`**: the verification and its exit code are described as
  above.

### Re-sealed — one seal for the two entries above (2026-09-28)

- **`v0.1.0` re-sealed in place once more** (staging): root `ce772027…` →
  `1307f172ad9149f48d2f834f104224a889f83e59ca0108ea37c18cd5e2c3c5e1` (89 sealed files, as in the previous seal, of which only
  `make_provenance.py`, `tests/test_failure_paths.py`, `code/case_figures.py`,
  `scripts/make_figures.py`, `tests/test_case_figures.py` and `output/figures/fig2_architecture.png`
  changed), written once by `python3 run_all.py --publish` after the two entries above; every other
  file kept its SHA-256 (diff of `sha256sums.txt`).

### Changed — supported Python (2026-09-27)

No sealed file changed (`python3 make_provenance.py --verify`); the change is outside the chain.

- **Python 3.12 or later** (`requires-python` and ruff `target-version` in `pyproject.toml`,
  `codemeta.json`, the README badge and environment row, and the matrix of
  `.github/workflows/ci.yml`, now Python 3.12 and 3.14): on Python 3.11 two tests fail, because the
  built-in `sum()` adds floats with compensated summation only from Python 3.12 on. The
  measurement, the two tests and the size of the differences are in `REPRODUCIBILITY.md` (Track 1).
  No code changed.

### Added — a test of the licence statements (2026-09-28)

No sealed file changed; the test is outside the chain.

- **`tests/test_doc_numbers.py`**: a new test checks that `NOTICE` lists third-party material only
  as not redistributed and that the README License section and the `.zenodo.json` notes say, in a
  sentence with no exception, that third-party sources are not redistributed.

### Fixed — line numbers and names of private documents in the note on statements about files (2026-09-27)

No expected number, assertion, tolerance, criterion or sealed file was changed; the change is
outside the chain.

- **`data/PREREGISTRATION.md`**: the dated note on how to read statements about files names two
  cases of files `05` to `13` whose mark is in the translation note of the file, not in the
  sentence. A line number (`l.`) in files `09` to `12` cites the private original of the document
  named in the same sentence, so it does not give the line of the copy under `data/prereg/`; and a
  name that a translation note glosses as a private document of the author refers to that private
  document. Before, the note said that a sentence of those files is about a private file only where
  the sentence itself says so, and so did the earlier entry on this note, below.

### Changed — quoted passages and theory rows of the claims ledger, the preprint-version check and the note on statements about files (2026-09-27)

No expected number, assertion, tolerance, criterion or sealed file was changed; everything below is
outside the chain.

- **Claims ledger** (`data/claims-ledger.csv` and its dictionary `data/claims-ledger.md`,
  regenerated): a passage of a source quoted between quotation marks inside `claim` or `nota` is now
  held to the same limit as `valor` and cut the same way, inside its quotation marks, with `[...]`.
  Before, the limit covered `valor` only, and a few `claim` cells quoted a longer passage, up to a
  whole post. The dictionary states the limit for both columns and counts the cut passages.
- **Theory rows of the claims ledger**: the pointer of a `TEO-*` row to `docs/THEORY.md` mentions a
  proof only for the statements that the document proves (Proposition 1, Corollary 1, the
  mixed-regime Observation, Corollary 3); the other rows point to the statement and its exact
  scope, argued in place as a direct reading of the closed forms or as an application of a cited
  result. The dictionary's meanings of the type `THEOREM` and of the status of these rows name the
  same statements. Before, the rows and both meanings said that every statement of the theory was
  proved.
- **`tests/test_doc_numbers.py`** (outside the chain): the check of the preprint version reads every
  declaration of the version in `README.md` and `docs/THEORY.md`, and each must name the pinned
  version and its date. Before, one correct declaration per document was enough, so a wrong version
  or date in the other declaration of the README passed.
- **`data/PREREGISTRATION.md`**: the dated note on how to read statements about files is narrowed.
  The reading "the sentence describes the private original" applies to files `01` to `04`, which were
  written about the private chain; files `05` to `13` were written for this repository, and a path
  in them names the file of this repository unless the sentence marks the file as private.

### Fixed — failure paths of the entry points, the write-path check and the Figure 2 lock (2026-09-27)

No expected number, tolerance, criterion or output was changed: every output kept its SHA-256 in
the re-seal below.

- **`make_provenance.py --verify`**: a sealed file, the manifest, `configs/stages.json` or
  `runs/CHAIN.jsonl` that is missing or malformed no longer ends in a traceback. It is reported as
  one named problem (the file or the stage, relative to the repository root; a malformed JSON file
  is named as such) with a nonzero exit code.
- **`run_all.py`**, full run: a missing sealed output is named and the run stops before
  regenerating anything, instead of raising after the whole regeneration; a regenerated output that
  is missing is named and counted as a failure, images included, where the comparison used to
  raise.
- **`run_all.py --publish`**: the tests now run before the seal, and the seal is written only if
  every generation step and the tests passed; otherwise it is skipped and the run fails. Before,
  the seal was written first and the tests ran after it.
- **`tests/test_stages_disjoint.py`**: write targets and their base directories are normalized
  (`posixpath.normpath`) before the match against the sealed globs, and a `..` segment or an
  absolute path is refused. A base such as `output/smoke/..` or `output/.` used to pass the
  segment-wise match although the run would write into sealed paths.
- **`tests/test_case_figures.py`**: the product that no diagram of the case lists is checked under
  its Portuguese and its English name ("Caixinhas", "Money Boxes"), in any letter case, both in the
  text drawn in Figure 2 and in the module source. The previous check let "caixinhas" and
  "Money Boxes" pass.
- **`tests/test_failure_paths.py`** (new, sealed in the `code` stage): locks the behaviours of the
  three entry-point items above on temporary files and on stubs of the long steps, so no test runs
  a simulation or writes a sealed path. Eighteen mutants (of the verification, the full run, the
  publish order, the write-path check and the Figure 2 lock) each fail at the intended assertion,
  and an untouched copy passes; the previous `tests/test_stages_disjoint.py` and
  `tests/test_case_figures.py` let the mutants of their own checks pass.
- **`REPRODUCIBILITY.md`**: the full run, the publish step, the verification and the write-path
  check are described as above.
- **`tests/test_doc_numbers.py`** (outside the chain; one test appended, none changed): the newest
  re-seal entry of this changelog must quote the root of the committed manifest and its number of
  sealed files.
- **`v0.1.0` re-sealed in place once more** (staging): root `cff91928…` →
  `ce7720278b10663df669609402849c5ae3c4e4ca29b42c00023f39425fd8a3a1` (89 sealed files: the 88 of the previous seal, of which only `configs/stages.json`,
  `make_provenance.py`, `run_all.py`, `tests/test_case_figures.py` and
  `tests/test_stages_disjoint.py` changed, plus the new `tests/test_failure_paths.py`), written by
  `python3 run_all.py --publish`; every other file kept its SHA-256 (diff of `sha256sums.txt`).

### Changed — claims ledger and documentation scope (2026-09-27)

No expected number, assertion, tolerance, criterion or sealed file was changed; everything below is
outside the chain.

- **Claims ledger** (`data/claims-ledger.csv` and its dictionary `data/claims-ledger.md`,
  regenerated): notes about the author's private working process (the name of a research tool, the
  numbering of review rounds, wording and voice labels addressed to the companion text) are removed
  or replaced by a neutral word, 25 occurrences, and the verification content of each cell is kept;
  every `valor` is now a short quotation of at most 39 words, below the 40-word threshold of an APA 7
  block quotation, so 28 longer passages are cut after their first 39 words and end with `[...]`,
  while `fonte` and `locator` still point to the full source. The dictionary counts both
  transformations, states the word rule, and states the ledger's scope: the numbers and factual
  statements of the case study, not every number of the repository.
- **`README.md`**: `θ` is defined where it first appears, with the formula of the mixed-regime
  Observation; "with their proofs" is restricted to the four statements that `docs/THEORY.md` proves
  (Proposition 1, Corollary 1, the Observation, Corollary 3), the other corollaries and the
  Consequence being readings argued in place and Corollary 5 an application of Dantzig's ratio rule;
  the ledger is no longer said to record "each number"; the version of the nuFormer preprint that was
  read is declared (version 2, submitted on 2026-08-10).
- **`docs/THEORY.md`**: the opening says what the tests lock (the worked instances, recomputed by the
  tripwire test; the simulation counts of the two testing sections, checked against the sealed files
  by `tests/test_doc_numbers.py`) instead of "every number"; the reference to the nuFormer preprint
  declares the version read, to which its page and table numbers refer.
- **`REPRODUCIBILITY.md`**: what the two hashes recorded by the token-KAT summary prove. They are the
  hashes of the sanitized copies in this repository, made after the original run; that the
  Portuguese original preceded that run rests on hashes of private originals, quoted by the frozen
  files, which cannot be recomputed here.
- **`data/PREREGISTRATION.md`**: a dated note on how to read statements about files in the frozen
  copies (sealed leaves and edits, stages files, and the checksum block of file `01`, whose two code
  lines hash the private originals and fail a `sha256sum -c` against this repository).
- The references cited in code comments (Dean & Barroso, 2013; Machado et al., 2009) were checked
  against their DOI records and needed no change.
- **`tests/test_doc_numbers.py`** (outside the chain; three tests appended, none changed): the
  definition of `θ` in the README must be the formula of the theory and precede no use of it; the
  preprint version and its date in README and THEORY must match the version pinned in
  `configs/estimates_inputs.json` (the day is declared in the test with its source, the arXiv
  submission history); and the "Claimed" paragraph must name as proved exactly the sections of
  `docs/THEORY.md` that carry a proof, with no number outside a statement label or the Dantzig
  citation. Seven mutants of the documents (the interval of `θ`, its definition removed, the date,
  the version, another version cited, "with their proofs" restored, a stray corollary number) each
  fail at the intended assertion, and an untouched copy passes.

### Changed — case-study Figure 2, dated deviations of workflow B and documentation (2026-09-27)

No expected number, assertion, tolerance or criterion was changed; every change below is in code,
data or wording, with its reason.

- **Figure 2 (`code/case_figures.py`)**: the data-sources box no longer prints "Caixinhas" (the line
  now reads "loans"). No diagram of the case lists it: the data-sources diagram of the case does not,
  and a later post of the same series mentions the product ("Money Boxes") only as a source under
  test. The two component names that appear in no text of the sources, only in diagrams of the case,
  are now rows of the claims ledger with the capture hash of their diagram: "Raw Data Store"
  (platform diagram, `case-fig-plataforma-raw-data-store`) and "Open Finance" (data-sources diagram,
  `case-fig-fontes-open-finance`), each label read by OCR. The claim map of `scripts/make_figures.py`
  cites both rows.
- **`tests/test_case_figures.py`**: locks Figure 2 as well. Each of the two names must be drawn (the
  box drawing is intercepted while the figure is drawn into a temporary directory) and must be the
  value of its ledger row, whose locator carries the capture hash; "Caixinhas" must be absent from
  the module source. Four mutants (the name put back; "Open Finance" left out of its box; the ledger
  value changed; the ledger row renamed) each fail at the intended assertion, and an untouched copy
  passes.
- **Dated deviations of the workflow-B families and a dated note** (`data/prereg/09-exponent-deviations.md`,
  `10-occupancy-deviations.md`, `11-fusion-deviations.md`, `12-quotas-deviations.md`,
  `13-token-kat-item5-note.md`): sanitized copies of Portuguese originals written after the runs,
  each opening with its own translation note that lists every change; sealed in the `prereg` stage
  and indexed in `data/PREREGISTRATION.md`. They record interpretations of ambiguous passages, the
  text erratum of addendum `08`, tests added after the published runs and two wording changes of
  the testing-status line; no data, criterion, tolerance, expected number or verdict changes. File
  `13` records what families EXP and OCC did with two of the three clauses of item 5 of the
  token-KAT deviations; the clause on `θ` remains open.
- **Text erratum of addendum `08`** (file `12`, item 1): three passages say that without saturation
  every policy returns the whole history, against the definition of the policies in the same
  addendum. Adopted wording: without saturation, recency and the adaptive quotas (RHO, EVT) return
  the whole history; the fixed quotas (FIXf, FIXc, TAX) stay capped at their quota from the expected
  counts and can cut a history that fits. `docs/THEORY.md` gains that bullet ("Without saturation",
  by construction, unit test UT-2, not simulated) and `data/PREREGISTRATION.md` states the adopted
  wording; the verdict is unaffected (every cell is saturated by design).
- **`docs/THEORY.md`**: the regime clause of Corollary 4(b), a finding of the fusion addendum valid
  for any outcome ("In the mixed regime, the fused source enters the Observation with the fused
  parameters; if fusion de-saturates `R ∪ S`, Corollary 3 applies.").
- **`tests/test_doc_numbers.py`** (outside the chain; one entry appended, none changed): "unit test
  UT-2" is declared as structural text of the workflow-B section of `docs/THEORY.md`, so that the
  "2" of the test identifier is not read as a quoted number.
- **Claims ledger** (`data/claims-ledger.csv`, outside the chain): 7 new rows, 255 in all (was 248).
  Five record the licensed wording of each workflow-B outcome (`EXP-expoente-resultado`,
  `OCC-resultado`, `CMP-resultado`, `C5-cotas-resultado`, `C5-cotas-decaimento`); their `valor` is a
  pointer to the outcome row of the frozen addendum that fixes the wording, as for the token KAT, so
  the Portuguese wording is not repeated in the ledger. Two are the Figure 2 rows above. The
  `derivado_de` of `TEO-corolario-4b` and `TEO-corolario-5` now cite the family rows, and the note of
  `KAT-token-resultado` says that the companion text paraphrases the licensed wording with the row
  identifier and keeps only the regime qualifiers literal.
- **`ROADMAP.md`**: the four follow-up simulations are marked done, each with the family that closed
  it, and point to `docs/THEORY.md#literal-simulation-checks`; the sentences "Today … rests on a
  single cell" and "Today analytic only" became past statements.
- **`CITATION.cff`, `codemeta.json`, `.zenodo.json`**: "two pre-registered simulations" became six,
  naming the four families, as in `README.md`.
- **`REPRODUCIBILITY.md`**: the pre-registration section lists files `09` to `13`.
- **`data/PREREGISTRATION.md`** (outside the chain): the translation note names every SHA-256 quoted
  under `data/prereg/` that refers to an output of this repository rather than to a private
  original: the two replication outputs, as before, and now also the three outputs of families EXP
  and OCC quoted in files `09` and `10` (`output/exponent/resumo.json`,
  `output/occupancy/resumo.json`, `output/occupancy/celulas.csv`).
- **`v0.1.0` re-sealed in place once more** (staging): root `4939b2c9…` → `cff91928448b38da24510872a8e13756629aff4d808c71937bb7a81e4b2cc6b9` (88 sealed
  files: the 83 of the previous seal, of which only `code/case_figures.py`, `scripts/make_figures.py`,
  `tests/test_case_figures.py`, `configs/stages.json` and `output/figures/fig2_architecture.png`
  changed, plus the five new files of `data/prereg/`), written by `python3 run_all.py --publish`;
  every other output kept its SHA-256 (diff of `sha256sums.txt`).

### Added — workflow B: pre-registered literal-simulation checks of the open limits (2026-09-27)

Four families of literal token-budget simulations, each frozen before its code (addenda
`data/prereg/05` to `08`, with grid and analytic table, and a dated amendment in
`data/PREREGISTRATION.md`), each with its own random stream (tags 5, 6, 7 and 8; the token KAT is
3). All four passed their pre-registered verdicts; the numbers are in `output/results.json` (blocks
`exponent`, `occupancy`, `fusion`, `quotas`), `README.md` and `docs/THEORY.md`. Under the fixed
generator and the oracle reader each checked statement is an algebraic identity of the model, so a
pass reads "checked by literal simulation", never "measured". No family was left out of the seal.
No expected number, assertion, tolerance or criterion was changed after a result was seen; every
decision below is in code or data, with its reason. In every family the full run used 4 processes:
the number of processes is not a parameter (it never enters the stream
`default_rng([seed, i_cell, i_combo, tag, i_block])`), and the "8 processes" of the
pre-registrations is only the time base of their cost estimates. In every family the full run was
written first to `output/replicated/<family>/` and then published with the frozen command, and the
two were identical byte for byte.

- **EXP — exponent of `d` in the per-token separability** (`data/prereg/05-exponent-addendum.md`;
  `code/exponent_analytic_table.py`, `tests/test_exponent.py`, shared runner `code/run_grid.py`).
  Passes: EXS 6 of 6 cells (30 of 30 seed-level signs, 0 ties, 0 discordant), EXN 6 of 6 (largest
  deviation over `tolΔ` 0.25). Mutation analysis: 12 of 12 variants of the 8 pre-registered mutant
  identifiers killed at the intended assertion.
  - The frozen analytic-table generator was ported with its arithmetic, expression order and
    Portuguese stdout verbatim (byte-identical to `data/prereg/exponent_analytic_table.txt`, checked
    twice after formatting). Changes: `import token_kat_analytic_table as tab` instead of loading
    the private module by path; default grid `data/exponent_grid.json`; the bytecode switch of the
    private copy removed; assigned lambdas turned into `def` (E731); `zip(..., strict=True)` on two
    lists of the same source (B905).
  - `auc_exata` is memoized with `functools.cache` over its only inputs (rates, separations and
    costs of each source, and `K`), with the same arithmetic: the verdict hook needs all six cells
    at every call. The table was compared byte for byte again after the change.
  - Verdict hook `veredito(linhas, grade)`, called by `code/run_grid.py`: EXS is the sign criterion
    of the token KAT (tie before disagreement, `ddof = 1`); EXN compares the empirical and fluid
    differences with the frozen per-cell `tolΔ`, never with the level tolerance of the KAT. A tie is
    read as a tie (a failure for lack of power), not as a disagreement: the first version of the
    hook gave a tie the reading of a disagreement; corrected in code only, with tests added and no
    assertion changed (the published output was byte-identical before and after, having no tie).
    A filtered grid records `completo: false` and the outcome `incompleto`, so a partial run never
    records a pass.
  - `tests/test_exponent.py`: EX1–EX5 (EX1 split into seven functions so that a grid mutant dies at
    the content assertion, not only at the hash pin), plus distinct tags across the five grids, the
    pin of the frozen table, and the published summary recomputed from the published CSV.
- **OCC — occupancy against rate weighting of the mean `ρ̄`** (`data/prereg/06-occupancy-addendum.md`;
  `code/occupancy_analytic_table.py`, `tests/test_occupancy.py`, shared runner `code/run_grid.py`).
  Passes: OCC-S 10 of 10 verdict cells (50 of 50 seed-level signs), OCC-N 20 of 20; the two
  threshold cells (OCC-L, outside the verdict) agree. Mutation analysis: 16 of 16 variants of the 7
  pre-registered identifiers killed at the intended assertion.
  - The generator port imports `token_kat_analytic_table`, defaults to `data/occupancy_grid.json`
    and `data/kat_token_grid.json`, and prints the frozen table byte for byte; the private generator
    run over this repository's token-KAT grid gives the same bytes, because only cell `S3` and the
    totals are read. Style only: `def` for lambdas (E731), `zip(..., strict=True)` where lengths
    are equal by construction (B905), long strings split by implicit concatenation (E501);
    identifiers verbatim.
  - The verdict hook lives in the same module (OCC-S, OCC-N, OCC-L and the report-only items) and
    imports the simulation modules inside the function, so that the generator keeps using the
    standard library only.
  - `tests/test_occupancy.py` is the single test file the pre-registration seals. OCCT1 repeats the
    `S3` identity of the shared-runner test through the command line, because the pre-registration
    fixes it in this file (about 16 s more in CI); OCCT2 and OCCT3 are parametrized per cell, so
    that a prediction mutant dies once per cell; the family module is imported inside each test so
    that the red phase failed test by test; the frozen addendum is pinned with the grid and the
    table. The test that the family tag reaches the simulation through the grid adapter was added
    by the mutation step, after the published run (no output changed).
  - Report-only lower bounds of `α` are truncated to three decimals (0.515 and 0.748), never
    rounded: a lower bound rounded up would claim an exclusion the data do not support.
- **CMP — event fusion, Corollary 4(b)** (`data/prereg/07-fusion-addendum.md`; `code/fusion.py`,
  `code/run_fusion.py`, `code/fusion_analytic_table.py`, `tests/test_fusion.py`). Passes: CMP-S 28
  of 28 signed contrasts (140 of 140 seed-level signs), CMP-0 within `tol_0`, CMP-N 24 of 24; CMP-T
  (outside the verdict) 4 of 4 fused arms. Mutation analysis: 21 of 21 variants killed at the
  intended assertion, covering the 13 pre-registered identifiers; one (which member represents a
  lossy block) is equivalent in the outcome and dies only in the explicit index test.
  - Generator port: only the import, the default grid and English docstrings changed; stdout
    byte-identical to the frozen table (FU4(b)).
  - `sortear_eventos` copies the draw order of `token_kat.simular_literal_tokens`, because the
    sealed function does not return the events; FU1(a) locks the identity byte for byte.
    `janela_eventos` generalizes the token-KAT window to a list of events, summing visible
    contributions in sorted order (user, time, entry order): scores byte-identical to the KAT for
    `RS` and, with `m = 1` and `k′ = k_S`, for `RF` and `RP` (FU1(b)). `fundir` and `lista_fundida`
    implement the fusion rule of the addendum literally; `avaliar_fusao` recomputes the predictions
    from the grid, reads role and sign from the frozen table, and takes the tolerances from the
    ported generator.
  - `code/run_fusion.py`: stream `[seed, i_cell, i_stream, tag, i_block]` with the tag read from the
    grid and checked to be 7; stream 0 is arm `R` through `simular_literal_tokens`, stream 1 one draw
    of `R ∪ S` shared by `RS`, `RF` and `RP`. The docstring of `code/fusion.py` was edited after the
    runs (text only); the smoke run repeated with the same command gave the same SHA-256.
  - The smoke summary (`N = 2,000`) records a failing verdict (one tie for lack of power): the smoke
    run is not the pre-registered run, and no test locks its verdict.
- **C5 — quotas against the recency cut, Corollary 5** (`data/prereg/08-quotas-addendum.md`;
  `code/quotas.py`, `code/run_quotas.py`, `code/quotas_analytic_table.py`, `tests/test_quotas.py`).
  Passes (outcomes "everything passes" and "C5-D passes"): anchors 10 of 10, C5-O 13 of 13, C5-G 19
  of 19, C5-N 30 of 30, the Consequence sub-test (C5-C) and the decay boundary (C5-D). Mutation
  analysis: 33 of 33 variants of the 14 pre-registered identifiers killed at the intended
  assertion.
  - Generator port with stdout byte-identical to the frozen table: import of
    `token_kat_analytic_table`; the bytecode switch removed; English docstrings, Portuguese stdout
    and assertion messages (a frozen artifact); `zip(..., strict=True)` (B905); an unused loop
    variable renamed (B007); long f-strings split by implicit concatenation (E501).
  - One history per (cell, seed), drawn in the order of `simular_literal_tokens` and read by every
    policy; the history of `R` in the Consequence is the same history without the new source (no
    new draw). The stream is read from the `fluxo` key of each cell, never from its position. The
    recency path returns scores byte-identical to `simular_literal_tokens` (same summation order and
    contribution formula); without age decay the separation of each event is the source's.
  - `ordem_fonte` is derived from the event order by a stable sort on (user, source), and the
    restricted history reuses the order of the full one, for speed (about 48 s to 14 s per task); a
    test proves both equal to `np.lexsort`.
  - Anchors that fail in the pre-registered run abort with exit code 2 and write nothing; a smoke
    run marks them not applicable. Outputs carry no date or time.
  - Finding recorded for a dated deviation: unit test UT-2 locks, as behavior, that the fixed quotas
    (FIXf, FIXc, TAX) cut a history whose cost is at most `K` whenever a source exceeds its quota,
    while three passages of the frozen addendum say that without saturation every policy returns the
    whole history. The definition of the policies in the addendum prevails and the code implements
    it; no definition changed, and the verdict is unaffected (every cell is saturated by design).
    The deviation is `data/prereg/12-quotas-deviations.md`, item 1, with the adopted wording:
    without saturation, recency and the adaptive quotas (RHO, EVT) return the whole history, while
    the fixed quotas (FIXf, FIXc, TAX) stay capped at their quota from the expected counts and can
    cut a history that fits; `docs/THEORY.md` states it (C5, "Without saturation").
  - Test identifiers were renamed to pass the repository's leakage check. The module docstring of
    `code/quotas.py` was rewritten after the run (text only; the summary records no code hash, and
    the tests and the leakage check were run again).

### Changed — integration of workflow B (2026-09-27)

- **`run_all.py`**: the full, smoke and publish modes run the four families (the full run with the
  frozen grids unchanged; the smoke run with `--N 2000 --bloco-usuarios 1000` into
  `output/smoke/<family>/`); the byte-for-byte comparison covers seventeen outputs (the eight new
  ones are the `celulas.csv` and `resumo.json` of each family).
- **`code/results.py`**: one block per family, derived from its summary (verdict, criteria, the
  numbers the documents quote, and the SHA-256 of the frozen grid, analytic table and addendum the
  run used; never the hash of an output, so the blocks do not depend on library versions). The
  report-only decay row of C5 averages the sealed CSV. Missing keys (smoke runs) are read as absent,
  never as a failure of the aggregation.
- **`configs/stages.json`**: `prereg` gains the four addenda, grids and analytic tables; `code`
  gains `tests/test_run_grid.py` and the four family test files by name (`code/*.py` already covers
  the family modules); `data` and `scores` gain the four `celulas.csv` and `resumo.json`.
- **`tests/test_paper_numbers.py`**: verdict and key numbers of each family, the SHA-256 of the
  frozen inputs recorded by each summary against the committed files, and the four family tags.
- **`tests/test_doc_numbers.py`** (outside the chain; entries appended, none changed): the new
  sections (`docs/THEORY.md` "Checked by literal simulation (workflow B)" and the README subsection
  "Pre-registered simulation checks (workflow B)") are scoped, with every quoted number rendered
  from `output/results.json` and the grids; the number word "seventeen" was added for the Track 2
  count of compared outputs.
- **`docs/THEORY.md`** (outside the chain): the section `literal-simulation-checks`, one subsection
  per family with its licensed statement and regime qualifier; the testing status points to it
  (exponent of `d`; occupancy against rate weighting; Corollary 4(b) and Corollary 5 no longer
  "analytic only"); Corollary 5 now reads that with age decay the order uses `ρ` at the age of the
  event, the design implication and the Consequence name adaptive quotas.
- **`README.md`**, **`REPRODUCIBILITY.md`**, **`data/PREREGISTRATION.md`**: the results, the
  mutation results, how to re-run the families, the data dictionary of the new outputs and a dated
  results block.
- **`v0.1.0` re-sealed in place again** (staging): root `9d737de0…` → `4939b2c97d475ea6c629920ecd61a9b85fb24878b7b08210b02cc5b1bf80f525` (83 sealed files: the 49 of the previous seal, of which only `code/results.py`, `configs/stages.json`, `output/results.json`, `run_all.py` and `tests/test_paper_numbers.py` changed, plus 34 new ones: the family modules, the shared runner, the five new test files, the four addenda, grids and analytic tables, and the four `celulas.csv` and `resumo.json`).

### Earlier in this release (2026-09-26): corrections from an adversarial review

Corrections from an adversarial review of the staging package (leakage, reproducibility and claims
lenses). No expected number, assertion, tolerance or criterion was changed; every change below is
in code, data or wording, with its reason.

### Changed

- **Theory tripwire scoped for the pre-registered simulations** (`tests/test_theory_tripwire.py`,
  outside the seal). The section anchored `literal-simulation-checks` (heading "Checked by literal
  simulation (workflow B)") will hold one subsection per simulation family. The rule that each
  regime qualifier appears exactly once now applies to the rest of the document; inside that
  section each subsection must state at least one qualifier of its own family, at most once each,
  with no qualifier of another family, no bare fragment of a qualifier and none in the section
  preamble. Nothing was relaxed: without the section every check is identical to before, and nine
  synthetic documents (three controls, six defects) plus a duplicate outside the section lock the
  rules.
- **`v0.1.0` re-sealed in place** (staging: no tag, no release, no DOI existed). Root
  `b1d460f6…` → `9d737de0122e81be08f6d0fef8025f705075dc8ba462860ee1b7b8d255e8e885`, written by
  `python3 run_all.py --publish`. Only the files edited below changed in the seal
  (`make_provenance.py`, `run_all.py`, `code/case_figures.py`, `scripts/make_figures.py`,
  `configs/stages.json`, the new `tests/test_case_figures.py`) plus
  `output/figures/fig2_architecture.png`; every other output kept its SHA-256 (diff of
  `sha256sums.txt`), and the regenerated outputs still match the private sealed ones.
- **`pyproject.toml`**: `requires-python = ">=3.11"` and ruff `target-version = "py311"`, matching
  the CI matrix, the badge, `codemeta.json` and the measured run on Python 3.11.15 (`ruff check`
  and `ruff format --check` stay clean).

### Fixed

- **`make_provenance.py --verify` checked less than it claimed.** It compared stage hashes, root and
  chain head only, so a manifest with an edited leaf SHA-256, a renamed or removed leaf, an edited
  `sha256sums.txt`, an edited `prev_chain_head` or an extra line in `runs/CHAIN.jsonl` still
  verified. It now also compares every leaf (path, SHA-256, size) stage by stage, regenerates
  `sha256sums.txt` from the manifest with the same writer and compares bytes, and walks
  `runs/CHAIN.jsonl` (genesis, links between lines, 64-hex hashes, the run's line equal to the
  manifest). Each of those tampers now fails; an untouched copy still verifies.
- **The claims ledger was described as sealed and is not.** `README.md` (§Frozen) and
  `REPRODUCIBILITY.md` said the chain proves the ledger unaltered; the ledger is in no stage. The
  sentences now say it is outside the chain and why (it is regenerated whenever a claim is added or
  corrected); it is listed with the other unsealed files.
- **Figure 2 drew a reconstruction as a sourced link.** The Kafka (CDC) → Model Server arrow was
  solid while the legend reads "dashed line = link not described in the sources"; no post connects
  the two. The arrow is dashed. The claim map in `scripts/make_figures.py` now says the LoRA rank
  comes from the ledger row `ARX-lora_rank`, not from `configs/estimates_inputs.json`.
- **`docs/THEORY.md`**: the replication is labelled "synthetic and illustrative, in orders of
  magnitude; not a replication of nuFormer"; "the 8 cells do not discriminate the exponent of `d`"
  is qualified (true when Corollary 1 is applied without checking the regime; under the general
  fluid formula the mixed cell `MIX2` separates `d/k` from `d²/k`, a post hoc reading of one cell,
  not pre-registered, recomputed by the tripwire); the Neyman & Pearson (1933) reference carries the
  published title prefix "IX." (the verified form). The same qualifier and reference in `README.md`.
- **`README.md`**: item 1 of "What this contributes" attributes the mixed-regime threshold and
  Corollaries 3–5 to the general fluid formula, and keeps "even with the new source" on Corollary
  3; the synchronous-path counterfactual quotes the published fraud-detection rate (2,800 and 20
  transactions per second) instead of a "peak", and states that 100% of dense BF16 peak makes the
  A100 count a lower bound (same wording in the data dictionary of `REPRODUCIBILITY.md`).

### Added

- **Case-study figures in the README**: Figure 1 and Figure 2 mapped to their files, with the credit
  of Figure 1 (post URL, Wayback Machine snapshot 20250613214328 and the SHA-256 of the two chart
  captures, the same as in the ledger).
- **`tests/test_case_figures.py`** (sealed, `code` stage): locks the 8 × 7 counts of
  `configs/adoption_counts.csv` and checks April 2025 against the ledger rows `case-fig-adocao` and
  `case-fig-fontes`.
- **`tests/test_doc_numbers.py`** (outside the chain, like the tripwire): every number in the
  scoped sections of `README.md`, `docs/THEORY.md` and `REPRODUCIBILITY.md` must sit in a phrase
  rendered from its source file, or in a declared structural phrase; the Figure 1 credit must match
  the ledger. The seven document mutants of the review, and 162 of the 167 number tokens of those
  sections mutated one at a time, fail the suite; the 5 that survive are corollary numbers
  (declared structural).
- **Tripwire**: the post hoc statement on the exponent of `d`, the "synthetic" label and the "IX."
  title are recomputed or asserted in `tests/test_theory_tripwire.py`.
- **`data/PREREGISTRATION.md`**: index of the frozen pre-registrations, the full translation note
  and the section where dated amendments are appended; not sealed.
- **`data/claims-ledger.md`**: a table of every bibliographic key of the `fonte` column with its
  verified reference (APA 7 where the record has it, otherwise the verified fields, labelled; an
  alias only after a code check; a key without a record says why). The theory rows of the ledger
  point to the English statements in `docs/THEORY.md` instead of repeating the text of the companion
  paper, and the licensed token-KAT wording points to the pre-registration that fixes it.
- **`.gitattributes`** with `* -text`: a clone with `core.autocrlf=true` rewrote the LF files and
  broke the seal (a `*.csv -text` rule alone did not prevent it); with this file the clone verifies.
- **No bytecode caches in the tree**: `run_all.py` and CI set `PYTHONDONTWRITEBYTECODE=1`, and CI
  runs ruff with `--no-cache` (a cache inside the tree carries the absolute path of the machine).

### Pending the author's authorization

- Public repository URL and DOI identifiers in `CITATION.cff`, `codemeta.json`, `.zenodo.json` and
  `README.md`. They are added when the repository is created and a release is authorized; until
  then the metadata carries neither, rather than a placeholder.
- `CITATION.cff`, `codemeta.json`, `.zenodo.json` and `ROADMAP.md` still describe two
  pre-registered simulations and list the limits closed by workflow B as future work; they are
  updated by the author with the rest of the package metadata.

## [0.1.0] — 2026-09-26 (staging: no tag, no release, no DOI)

First sealed version of the package, ported from the private authoring environment where the code
was written and first sealed. Seal: `runs/v0.1.0/manifest.json` (6 stages), verified by
`python3 make_provenance.py --verify`.

### Added

- **Closed-form model** (`docs/THEORY.md`): Proposition 1 (saturated window), Corollaries 1–5, the
  mixed-regime Observation, the exact scope of the Consequence and the testing status of each
  claim; arithmetic tripwire in `tests/test_theory_tripwire.py`.
- **Displacement replication** (`code/displacement.py`, `code/run_replication.py`): pre-registered
  grid of 720 cells, 7 source combinations, `N = 200,000` users per cell, 5 seeds; sealed outputs in
  `output/replication/`.
- **Token KAT** (`code/token_kat.py`, `code/run_token_kat.py`,
  `code/token_kat_analytic_table.py`): literal token-budget simulation with heterogeneous event
  cost, 8 cells, `N = 100,000` users per combination, 5 seeds; frozen grid and analytic table;
  sealed outputs in `output/kat_token/`.
- **Order-of-magnitude estimates** (`code/estimates.py`, inputs in `configs/estimates_inputs.json`):
  context capacity, batch inference, fine-tuning and pre-training compute, all-reduce time per link,
  batch throughput and the synchronous-path counterfactual; tables in `output/tables/`.
- **Figures** (`scripts/make_figures.py`, with the claim map in its docstring): Figure 3 from the
  replication, with a JSON sidecar of every plotted number; the two case-study figures
  (`code/case_figures.py`, counts in `configs/adoption_counts.csv`).
- **Published numbers** aggregated in `output/results.json` by `code/results.py` and asserted in
  `tests/test_paper_numbers.py`.
- **Claims ledger** (`data/claims-ledger.csv`, dictionary in `data/claims-ledger.md`).
- **Pre-registrations** (`data/prereg/`): sanitized copies of the four frozen documents, each with a
  translation note.
- **Provenance chain**: `make_provenance.py`, vendored `code/provenance_chain.py`,
  `configs/stages.json`, `env.json` (genesis), `runs/`; `run_all.py` with the full, `--smoke` and
  `--publish` modes; hygiene and stage-disjointness tests.
- **Package metadata**: `README.md`, `REPRODUCIBILITY.md` (two seals, tracks, data dictionary),
  `ROADMAP.md`, `CITATION.cff`, `codemeta.json`, `.zenodo.json` (`access_right: closed`),
  `LICENSE`, `LICENSES/` (Apache-2.0, CC BY 4.0), `NOTICE`, `.gitignore`, and CI
  (`.github/workflows/ci.yml`: seal verification and smoke run on Python 3.11 and 3.12; ruff and
  docstring coverage).

### Port decisions (declared; none relaxes a criterion, a tolerance or an expected number)

- **Identifiers renamed.** The two mixed-regime cells of the token KAT are `MIX1` and `MIX2` (grid,
  code, tests, outputs, pre-registration copies). Mutant identifiers in test docstrings are `X01`…;
  short test variables became descriptive names (`mean_pos`, `mean_neg`, `var_pos`, `var_neg`).
- **Pins point to this repository.** The frozen-pin test asserts the SHA-256 of this repository's
  grid and analytic table. The pin on the SHA-256 of the original implementation file was dropped:
  the integrity of the code here is the job of the seal (`make_provenance.py --verify`). The
  token-KAT summary records the SHA-256 of this repository's sanitized addendum and grid
  (`adendo_sha256`, `grade_sha256`).
- **Figure 3 in English.** Labels, notes and footer in English with decimal points; text assertions
  translated. The font is DejaVu Serif, bundled with matplotlib, instead of a system font, so the
  measured layout does not depend on the fonts installed on the machine. The PNG is compared
  between two fresh processes instead of against the sealed PNG (it depends on the rasterizer); the
  JSON sidecar is still compared byte for byte with the sealed one.
- **Analytic-table test** compares the output of this repository's script, run over this
  repository's grid, with `data/prereg/kat_token_analytic_table.txt`.
- **Lint-driven edits without arithmetic change**: `itertools.pairwise` for adjacent pairs, a
  loop variable renamed from `l`, a `lambda` turned into a `def`; English numpy docstrings.

### Verified before this entry

- Full run in the sealed environment (`python3 run_all.py`, 2026-09-26): the nine compared outputs
  are byte-identical to the sealed ones, and so are the three PNG images; tests pass; the chain
  verifies.
- CI commands run locally on Python 3.11.15 and 3.12.12: seal verified and smoke run green.
