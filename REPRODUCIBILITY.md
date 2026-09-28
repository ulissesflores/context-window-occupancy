# Reproducibility

Two seals, never conflated.

- **Reproducible derivation.** Everything computed by the code of this repository: the displacement
  replication (`output/replication/`), the token KAT (`output/kat_token/`), the four workflow-B
  families (`output/exponent/`, `output/occupancy/`, `output/fusion/`, `output/quotas/`), the
  order-of-magnitude estimates (`output/estimativas.json`, `output/tables/`), the Figure 3 sidecar
  (`output/figures/fig3_values.json`) and the aggregated `output/results.json`. The simulations are
  synthetic and fully seeded, so seal + code + environment regenerate them. In the sealed
  environment the regeneration is **byte for byte**; see [the environment section](#environment).
- **Frozen evidence.** Inputs that no code of this repository can regenerate, because they were
  transcribed or decided before any run: the source values of the estimates
  (`configs/estimates_inputs.json`, each tagged `FACT`, `SPEC` or `ASSUMPTION` with a locator), the
  adoption counts read from public bar charts (`configs/adoption_counts.csv`), and the
  pre-registrations with their frozen grids and analytic tables (`data/prereg/`,
  `data/kat_token_grid.json` and the four workflow-B grids `data/exponent_grid.json`,
  `data/occupancy_grid.json`, `data/fusion_grid.json`, `data/quotas_grid.json`). For these, the chain proves that the bytes were not altered after
  sealing; it does **not** prove that they match their sources. That is what the locators, the
  capture hashes and the ledger's verification notes are for. The claims ledger
  (`data/claims-ledger.csv`) is not sealed: see
  [what the chain leaves out](#what-the-chain-covers-and-what-it-leaves-out-on-purpose).

## Track 1 — verify the seal and run the smoke pipeline (this is CI)

```bash
python -m pip install -r requirements.txt
python make_provenance.py --verify   # recompute the chain from the files on disk
python run_all.py --smoke            # small N into output/smoke/ -> tests -> verify again
```

`--smoke` regenerates every output with a small `N` into `output/smoke/`, a directory that no
sealed glob matches. The test suite then asserts every published number against the **sealed**
outputs, and the chain is verified again. CI runs exactly these two commands on Python 3.12, the
oldest supported version, and on Python 3.14, the version of the sealed run
(`.github/workflows/ci.yml`).

**Python 3.12 or later is required.** Measured on 2026-09-28 on the machine of the sealed run, with
the exact versions of `requirements.lock` (numpy 2.4.6, scipy 1.17.1, matplotlib 3.10.9, pytest
9.0.3; CI installs instead the newest versions that `requirements.txt` allows): both commands are
green on Python 3.12.14, 3.13.15 and 3.14.7, with 385 tests passed on each. On Python 3.11.16 the
seal verifies but two tests fail, `tests/test_occupancy.py::test_occt2_stdout_igual_a_tabela_congelada`
and `tests/test_exponent.py::test_resumo_publicado_recomputa_do_csv`. The cause, measured on
2026-09-27, is the built-in `sum()`, which from Python 3.12 on adds floats with compensated
summation: with a plain
left-to-right sum in its place, Python 3.12 and 3.14 fail the same two tests with the same messages,
and the table generator prints the Python 3.11 bytes. The differences sit in the last digits: the
ported occupancy analytic-table generator prints 379 instead of 380 events per user in two cells of
the frozen table, and two deviation fields of the recomputed exponent verdict differ from the
published ones from the eleventh significant digit on; no sign, criterion or verdict changes. The
sealed code keeps the built-in `sum()`, so its outputs stay those of the sealed run. Before the
workflow-B families were added, both commands had been green on Python 3.11.15 (numpy 2.4.6, scipy
1.17.1) and on Python 3.12.12 (numpy 2.5.3, scipy 1.18.1).

## Track 2 — full re-run with the pre-registered parameters

```bash
python3 run_all.py
```

Regenerates every output with the pre-registered parameters (replication: `N = 200,000` users per
cell, 5 seeds, 720 cells, 7 source combinations; token KAT: `N = 100,000` users per combination,
5 seeds, 8 cells, 2 combinations), and the outputs of the four workflow-B families with the
parameters of their frozen grids, into `output/replicated/`, which no sealed glob matches, compares
seventeen outputs **byte for byte** with the sealed ones, runs the tests and verifies the chain. The
three PNG images are compared too, but a difference only warns: rasterized pixels depend on the font
renderer, while the numbers behind Figure 3 live in the machine-independent JSON sidecar, which is
compared strictly. Expected tail of the output in the sealed environment (measured on 2026-09-27,
wall time 868 s on an Apple silicon laptop with 14 CPU cores; replication 79 s, token KAT 73 s,
exponent family 111 s, occupancy family 214 s, fusion family 171 s, quota family 74 s, tests 144 s;
before the workflow-B families, on 2026-09-26, the run took 204 s):

```text
[SAME] replication/celulas.csv
[SAME] replication/resumo.json
[SAME] kat_token/celulas.csv
[SAME] kat_token/resumo.json
[SAME] exponent/celulas.csv
[SAME] exponent/resumo.json
[SAME] occupancy/celulas.csv
[SAME] occupancy/resumo.json
[SAME] fusion/celulas.csv
[SAME] fusion/resumo.json
[SAME] quotas/celulas.csv
[SAME] quotas/resumo.json
[SAME] estimativas.json
[SAME] tables/enlaces_allreduce.csv
[SAME] tables/fanout_cauda.csv
[SAME] figures/fig3_values.json
[SAME] results.json
[SAME] figures/fig1_adoption.png
[SAME] figures/fig2_architecture.png
[SAME] figures/fig3_replication.png
[OK] tests (144 s)
[OK] chain verified: root <sha256> · chain_head <sha256>
[OK] provenance verify (0 s)
run_all: GREEN
```

If a sealed output is missing, the full run names it and stops before regenerating anything; a
regenerated output that is missing is named as well and counts as a failure, images included.

`python3 run_all.py --publish` is an authoring step, not a replication step: it is the only mode
that writes the sealed paths. It regenerates the outputs, runs the tests and only then re-seals
(`make_provenance.py`); if a step or a test fails, the seal is skipped and the run fails, so a
failing run is never sealed. A replicator never needs it.

<a id="environment"></a>

## Environment

The sealed run used CPython 3.14.7 on macOS arm64 with numpy 2.4.6, scipy 1.17.1, matplotlib
3.10.9 and pytest 9.0.3 (`env.json`, the genesis of the chain; the full freeze of that environment
is `requirements.lock`). Byte identity of the full run holds in that environment. Every
`resumo.json` records the Python, numpy and scipy versions it ran with, so under any other versions
the summaries differ by construction, and `results.json` differs with them, because it records the
SHA-256 of the replication summary (the workflow-B blocks of `results.json` record only the
SHA-256 of the frozen inputs, never of an output).

Measured outside the sealed environment (2026-09-26, before the workflow-B families were added; the
same machine, Python 3.12.12 with numpy 2.5.3, scipy 1.18.1 and matplotlib 3.11.2): the full run
reported `DIFF` for exactly those three files (so `run_all.py` exited with 3 failures) and `WARN` for the three PNG images; every other compared output is byte-identical,
including both `celulas.csv`. Field by field, the two `resumo.json` differ only in `versoes` and
`results.json` only in the recorded SHA-256 of the replication summary; every number is identical.
The four workflow-B summaries also record `versoes`, so the same run would now also report `DIFF`
for them; that has not been re-measured.
The test suite and the seal verification pass in that run, because the tests assert the published
numbers against the sealed outputs. A run that differs anywhere else is a finding, not noise.

## The provenance chain

`configs/stages.json` declares six sealed stages, in order: `environment -> code -> prereg -> data
-> scores -> figures`. `make_provenance.py` hashes every stage with the vendored
`code/provenance_chain.py` (Merkle tree per stage with RFC 6962 domain separation, stages folded in
order, SHA-256 from the standard library) and writes:

- `runs/v0.1.0/manifest.json`: stage hashes, every leaf with its size and SHA-256, the root and the
  chain head; every path is relative to the repository root;
- `runs/v0.1.0/sha256sums.txt`: one line per sealed file, checkable without Python:
  `sha256sum -c runs/v0.1.0/sha256sums.txt` (macOS: `shasum -a 256 -c …`);
- `runs/CHAIN.jsonl`: one line per sealed run, linking each chain head to the previous one.

`python3 make_provenance.py --verify` recomputes everything from disk and compares it with the
manifest: each stage hash, the root and the chain head; each leaf the manifest lists (path, SHA-256
and size, stage by stage); `sha256sums.txt`, regenerated from the manifest and compared byte for
byte; and `runs/CHAIN.jsonl`, walked line by line (the first line links to the zero head, each
`prev_chain_head` is the previous `chain_head`, each `chain_head` is the link of its
`prev_chain_head` and `root`, and the line of this run equals the manifest). Its exit code is the
number of problems, at most 255 (an exit status is taken modulo 256, so 256 problems would
otherwise read as a pass). The manifest, `configs/stages.json` and `runs/CHAIN.jsonl` are read
first: each one that is missing, unreadable, not valid JSON, or not the structure the build writes
(the manifest, the chain file) or reads (the stages file) is reported as one problem that names
it, and nothing is recomputed: a key missing, or extra in the manifest or a chain line, a value of
another JSON type, a stage path that is not relative to the repository root. A sealed file that is
missing or unreadable is named by its path relative to the repository root; a missing file of a
tree stage also changes the hash of its stage, the root and the chain head, and each of these is
reported. No failure of the verification ends in a traceback or as a pass.
`python3 code/provenance_chain.py selftest` runs the tool's own known-answer and tamper-detection
tests.

**What the chain does not prove.** It proves the integrity of every sealed file and binds
environment, code and inputs to outputs; it does not timestamp anything, and it says nothing about
scientific correctness. Before a release there is no external time anchor, so "frozen before the
run" is checkable inside this repository only in a weaker sense. The token-KAT summary records the
SHA-256 of the addendum and grid it ran with (`adendo_sha256`, `grade_sha256`), and those are the
hashes of the sanitized copies in this repository (`data/prereg/02-token-kat-addendum.md` and
`data/kat_token_grid.json`), made when the code was ported, after the original run in the authoring
environment. They prove that the run of this repository consumed exactly those bytes and that
neither copy was edited after that run without failing the tests and the seal. They do not prove
that the Portuguese original of the addendum was frozen before the original run: that rests on the
SHA-256 of the private originals, which the frozen files quote (the dated deviations
`data/prereg/03-token-kat-deviations.md` quote the hash of the original addendum, and the addendum
quotes the hash of the original grid) and which cannot be recomputed from this repository.

<a id="what-the-chain-covers-and-what-it-leaves-out-on-purpose"></a>

**What the chain covers, and what it leaves out on purpose.** The `code` stage lists the test files
by name. `docs/THEORY.md` and its tripwire test (`tests/test_theory_tripwire.py`), the test that
locks the numbers quoted in the documentation (`tests/test_doc_numbers.py`), this file, the README,
the package metadata, the claims ledger (`data/claims-ledger.csv` and its dictionary
`data/claims-ledger.md`) and the pre-registration index (`data/PREREGISTRATION.md`) are outside the
chain: they may be edited without re-running the simulations, and an edit to them never breaks the
seal. The ledger is left out because it is regenerated from the author's working ledger whenever a
claim is added or corrected; the index is left out because dated amendments are appended to it.
Editing any sealed file does break the chain; a change there means a new sealed run, never an
out-of-band edit.

**Replication never writes a sealed path.** The write targets of the full run
(`output/replicated/`) and of the smoke run (`output/smoke/`) are disjoint from every glob of
`configs/stages.json`; `tests/test_stages_disjoint.py` asserts it with `Path.glob` semantics, after
normalizing every write target and its base directory and refusing a `..` segment.

## Pre-registration and what was frozen before each run

- [`data/PREREGISTRATION.md`](data/PREREGISTRATION.md) indexes the frozen files below, carries the
  full translation note and collects dated amendments; it is not sealed and no output records its
  hash.
- `data/prereg/01-displacement-replication.md` was written before any code of the replication;
  `02-token-kat-addendum.md` before any code of the token KAT; `03-token-kat-deviations.md` and
  `04-token-kat-deviations-b.md` are dated deviations written after the runs, which change wording
  and scope, never data. The four files are sanitized copies of Portuguese originals; each opens
  with a translation note and a glossary. The SHA-256 values quoted inside them refer to the private
  originals, except the two replication outputs, which this repository regenerates byte for byte;
  `tests/test_paper_numbers.py` checks those two hashes against the pre-registration.
- The token-KAT summary records the SHA-256 of the addendum and of the grid it ran with
  (`adendo_sha256`, `grade_sha256`); a test recomputes both from the committed files, so editing
  either after the run fails the suite as well as the seal. Those committed files are the sanitized
  copies; what the two hashes do and do not prove is stated in
  [what the chain does not prove](#the-provenance-chain).
- The analytic table of the token KAT (`data/prereg/kat_token_analytic_table.txt`) was computed from
  the closed form before any simulation; a test reruns `code/token_kat_analytic_table.py` and
  compares its output with the frozen file. Its output is in Portuguese because it is a frozen
  pre-registration artifact.
- The four workflow-B families (`data/prereg/05-exponent-addendum.md`,
  `06-occupancy-addendum.md`, `07-fusion-addendum.md`, `08-quotas-addendum.md`) were each frozen,
  with their grid and analytic table, before any code, test or output of the family existed in this
  repository. Each family draws from its own random stream (tag in its grid, never the tag of the
  token KAT); each summary records the SHA-256 of its grid, analytic table and addendum, and
  `tests/test_paper_numbers.py` recomputes the three from the committed files. Each family test
  file reruns the ported analytic-table generator and compares its output with the frozen table.
  The full runs were written first to `output/replicated/<family>/` and only then published with
  the frozen command, and the two were compared byte for byte.
- `data/prereg/09-exponent-deviations.md` to `12-quotas-deviations.md` are the dated deviations of
  the four workflow-B families, and `13-token-kat-item5-note.md` is a dated note on item 5 of the
  token-KAT deviations, all written after the runs. They record interpretations of ambiguous
  passages, one text erratum of the quotas addendum and wording changes, never a change of data,
  criterion, tolerance or verdict. Each is a sanitized copy of a Portuguese original and opens with
  its own translation note; they are sealed in the `prereg` stage.

## What cannot be re-run here

- **The captures of the sources.** The nuFormer preprint and the Nubank posts were read and captured
  by the author; the ledger keeps the public URL, the locator and the SHA-256 of each capture, not the
  capture. A replicator can re-fetch a source and compare the hash, but a page that changed since the
  capture will not match, and that is expected.
- **The adversarial verification of the authoring phase.** Mutation analysis ran on the original
  implementation before it was ported here; the logs are not distributed. Recorded results: token-KAT
  suite, 22 of 22 mutants killed at the intended assertion; its extra suite, 8 of 8 killed plus 1
  confirmed equivalent mutant. The displacement suite was hardened in two rounds against the mutants
  that survived the first; `tests/test_displacement_locks.py` and `tests/test_displacement_locks2.py`
  are the result. Mutation testing has **not** been re-run on this port. The port changed
  identifiers, docstrings and file paths, never arithmetic, and the byte-for-byte regeneration of the
  sealed outputs is the check of that.
- **Mutation analysis of the workflow-B families.** The four families were written in this
  repository and each was mutation-tested, with the mutant identifiers fixed by its pre-registration,
  on disposable copies of the repository (the repository itself was checked unchanged before and
  after); the harnesses and logs are not distributed. A mutant counts as killed only when the
  intended assertion fails with the intended message. Recorded results: exponent of `d` (EXP),
  8 pre-registered identifiers in 12 variants, 12 of 12 killed; occupancy against rate weighting
  (OCC), 7 identifiers in 16 variants, 16 of 16 killed; event fusion (CMP), 13 identifiers in 21
  variants, 21 of 21 killed, one of them (the choice of the representative member) equivalent in
  the outcome and killed only by the explicit index test; quotas (C5), 14 identifiers in 33
  variants, 33 of 33 killed.

## Port from the authoring environment

The code was written and sealed first in a private authoring environment and then ported here with
sanitization. The changes declared in the port (not relaxations of any criterion) are listed in
[`CHANGELOG.md`](CHANGELOG.md): renamed cell and mutant identifiers, pins that point to this
repository's files, Figure 3 in English with a bundled font, and the PNG compared between two fresh
processes instead of against the sealed file.

## Data dictionary (Portuguese tokens frozen in the outputs)

The byte-for-byte contract freezes the Portuguese column names and keys of the sealed outputs, so
they cannot be translated in place. English key:

| Token | Where | Meaning |
|---|---|---|
| `celulas.csv` | `output/replication/`, `output/kat_token/` and the four workflow-B directories | per-cell, per-combination, per-seed results ("cells") |
| `resumo.json` | same | summary and verdict of the run |
| `i_celula`, `celula` | CSV | cell index; cell name (`S1a`…`S3` saturated, `MIX1`/`MIX2` mixed, `N1` unsaturated) |
| `regime`: `saturado` / `misto` / `nao_saturado` | KAT CSV and summary | saturated (already before the new source) / mixed (only with it) / unsaturated (not even with it) |
| `combo` | CSV | source combination (`A`, `AC`, …; `R` = current mixture, `RS` = with the new source) |
| `semente`, `sementes` | CSV, summary | seed, seeds |
| `lam_*`, `d_*`, `T` | replication CSV | event rate per day, mean attribute shift, history length in days |
| `auc`, `auc_analitica`, `auc_fluida` | CSV | empirical AUC; closed-form AUC; fluid-approximation AUC |
| `saturada`, `frac_saturada`, `frac_saturada_media` | CSV, summary | window saturated (share of users) |
| `n_pos`, `n_neg` | CSV | users with `y = 1` / `y = 0` |
| `ociosos_medio_saturados` | KAT | mean idle tokens of saturated users (whole events only) |
| `avaliar_quebra` (`Q1`, `Q2`, `Q3`) | replication summary | falsification criteria of the pre-registration |
| `falhou`, `pares_testados`, `violacoes` | `Q1` | failed; pairs tested; violations |
| `comparacoes`, `testadas`, `abaixo_limiar`, `empate`, `discordantes`, `frac_discordante` | `Q2` | comparisons; tested; below the pre-registered threshold; ties; discordant; discordant share |
| `celulas_padrao`, `celulas_ordem`, `concordancia_padrao_com_analitico` | `Q3` | cells with the six-sign pattern; cells in full order; agreement with the closed form |
| `regiao_p3_analitica` (`n_celulas`, `n_padrao`, `n_ordem`) | replication summary | closed-form region of prediction P3: cells, pattern, order |
| `shortfall_padrao_T4`, `shortfall_por_celula` | replication summary | cells whose shortfall ratios follow the sign pattern of Table 4 of Braithwaite et al. (2025); shortfall ratio `(1 − AUC_X)/(1 − AUC_ABC)` per cell and combination, on the mean over seeds |
| `versoes` | every summary | Python, numpy and scipy versions of the run |
| `avaliar_kat` (`KT_S`, `KT_N`, `por_celula`, `passou`) | KAT summary | sign criterion; level criterion; per cell; passed |
| `celulas`, `combos`, `estouros`, `empates` | KAT criteria | cells; combinations; exceedances of the tolerance; ties |
| `dif_empirica`, `dif_prevista`, `ep_dif`, `sinal` (`concorda`), `sinais_por_semente` | KAT per cell | empirical difference; predicted difference; its standard error; sign (agrees); sign per seed |
| `nivel` (`media`, `fluida`, `desvio`, `tol`, `dentro`, `delta2_empirico`, `delta2_fluido`) | KAT per cell | level check: mean AUC, fluid AUC, deviation, tolerance, within tolerance, empirical and fluid `Δ²` |
| `tolerancias`, `diagnostico`, `bloco_usuarios` | KAT summary | tolerances; saturation diagnostics; users per random block |
| `adendo_sha256`, `grade_sha256` | KAT summary | SHA-256 of the frozen addendum and grid |
| `tabela_sha256`, `preregistro_sha256` | workflow-B summaries | SHA-256 of the frozen analytic table; of the frozen addendum (fusion and quotas; `adendo_sha256` in the other two) |
| `tag`, `fluxo` | workflow-B summaries | random-stream tag of the family; description of the stream |
| `veredito` (`desfecho`, `passou`, `completo`, `por_celula`, `criterios`) | exponent and occupancy summaries | verdict of the family: outcome, passed, complete grid, per cell, criteria |
| `EXS`, `EXN`, `intervalo_implicado`, `lado`, `sinal_teoria`, `desvio_sobre_tolD` | exponent summary | sign criterion; level-of-difference criterion; report-only implied interval; side (`baixo` low, `alto` high); sign of the theory; deviation over the frozen `tolΔ` |
| `OCC_S`, `OCC_N`, `fora_do_veredito` (`OCC_L`), `relatorio` (`alfa_minimo`, `regra_por_evento`, `invariancia_em_T`) | occupancy summary | sign and level criteria; threshold cells outside the verdict; report-only diagnostics: lower bound of `α`, the per-event rule, the depth pairs |
| `avaliar_fusao` (`CMP_S`, `CMP_0`, `CMP_N`, `CMP_T`, `por_contraste`, `por_braco`) | fusion summary | sign criterion, exact null, level criterion and ceiling check (outside the verdict); per contrast; per arm (`R`, `RS`, `RF` fused, `RP` single representative) |
| `avaliar_c5` (`criterios`, `comparacoes`, `niveis`, `consequencia`, `veredito.desfechos`), `ancoras`, `previsoes` (`exata`, `fluida`, `decaimento`) | quotas summary | criteria C5-O, C5-G, C5-N, C5-C, C5-D; paired comparisons of policies; levels; the Consequence sub-test; outcomes of the pre-registered table; anchor rows against the sealed token KAT; exact, fluid and age-decay predictions |
| `historia`, `politica` (`REC`, `RHO`, `EVT`, `TAX`, `FIXf`, `FIXc`, `RHOidade`) | quotas CSV | history (`RS` with the new source, `R` without it); window policy (recency, adaptive quotas by `ρ`, by `d²`, proportional to the rate, fixed floor, fixed ceiling, age-aware) |
| `estimativas.json` keys `E1_…` to `E7_…` | estimates | `txn_ctx_compacto`/`texto`: transactions per context window (compact/plain-text encoding); `razao`: their ratio; `usuarios_por_gpu_s`: users per A100-second in the daily batch inference; `utilizacao_*`: utilization; `gpu_horas_h100`: H100 GPU-hours; `flops_pretreino`: pre-training FLOPs; `bytes_gradiente`: gradient bytes per step; `t_computo_passo_s`: compute time per step (s); `vazao_media_gbps`: mean throughput (Gb/s) of the daily batch of token ids; `latencia_min_computo_ms`: minimum compute latency of one forward pass (ms); `fracao_sla_pix`: that latency as a share of the 700 ms PIX SLA; `a100_pico_pre_filtro`/`pos_filtro`: A100s needed at the published fraud-detection rate of transactions reaching the model before/after pre-policy filtering (2,800 and 20 per second), at 100% of dense BF16 peak, so a lower bound, in the counterfactual of the model on the synchronous path (the key says `pico`, "peak", but the source gives a rate, not a peak) |
| `enlace`, `t_allreduce_ddp_ms`, `t_allreduce_fsdp_ms`, `razao_ddp_sobre_computo` | `tables/enlaces_allreduce.csv` | link; all-reduce time under DDP and FSDP (ms); DDP communication over compute time |
| `servicos`, `prob_ao_menos_um_acima_do_p99` | `tables/fanout_cauda.csv` | services called per decision; probability that at least one exceeds its own p99 |
| `intra-no` | link names | intra-node |
| `painel_a`, `painel_b`, `equilibrios`, `rodape`, `n_sementes` | `figures/fig3_values.json` | panel (a), panel (b), equilibria, footer, number of seeds |

## Line endings

The eight CSV outputs (the six `celulas.csv` and the two tables) are written by Python's
`csv.writer` with its default CRLF line terminator, and
the byte-for-byte contract includes those bytes; every other sealed file is LF. Version control must
store every file unmodified: `.gitattributes` sets `* -text`, so a clone with `core.autocrlf=true`
(the default of Git for Windows) does not rewrite LF files as CRLF and break the seal. A `*.csv
-text` rule alone would not be enough, because the files it would leave to normalization are the
LF ones.
