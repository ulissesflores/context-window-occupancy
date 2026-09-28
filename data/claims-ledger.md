# Claims ledger — data dictionary

`data/claims-ledger.csv` records the numbers and factual statements of the companion case study, taken from its sources or derived from them, one row per claim, with the source, the exact locator, how the value was obtained and what code checked. It is not a list of every number in this repository: the worked instances of `docs/THEORY.md` are recomputed by its tripwire test, and the simulation results live in the sealed outputs. It is UTF-8, comma-separated, CRLF line endings, RFC 4180 quoting; some cells contain line breaks. Cell contents are kept in Portuguese, as recorded by the author; this file is the English key.

Rows: **251**. Columns: **10**.

## Columns

| Column | Meaning |
|---|---|
| `id` | Stable claim identifier. The prefix groups rows by source family (see the prefix table below). |
| `tipo` | Claim type (vocabulary below). |
| `claim` | The statement being recorded, in Portuguese, as written by the author. Theory rows (`TEO-*`) point instead to the English statement in `docs/THEORY.md`. A passage of a source quoted inside the statement, between quotation marks, is held to the word limit of `valor` and cut the same way, inside its quotation marks. |
| `valor` | The value, or the verbatim passage copied from the source (source language preserved); a pointer where the value is wording of the companion text (theory rows, and the licensed wordings of the token KAT and of the workflow-B families). Passages are short quotations: a cell holds at most 39 words (a word is a whitespace-separated token with a letter or a digit; separators and elision marks do not count), below the 40-word threshold at which APA 7 turns a quotation into a block quotation; a longer passage is cut after its first 39 words and ends with `[...]`, and the full text is at the source that `fonte` and `locator` point to. |
| `unidade` | Unit of `valor`, when numeric. |
| `fonte` | Source: a reference key, a public URL, or a path in this repository. |
| `locator` | Where in the source: section/page/table, a repository path (`path::key` points to a JSON key or a Python function), or a public URL followed by the capture hash (markers below). Parts separated by a vertical bar (`\|`) are independent pointers. |
| `derivado_de` | Rows or model inputs this row is derived from (ids, or input names of `configs/estimates_inputs.json`), separated by `, ` or ` ; `. |
| `status` | How the value was obtained (vocabulary below). |
| `nota` | Verification note: what code checked, scope limits, divergences found. Passages quoted between quotation marks are held to the word limit of `valor`. |

## `tipo` vocabulary

| Value | Rows | Meaning |
|---|---|---|
| `ASSUMPTION` | 10 | Modelling assumption declared by the author. |
| `DERIVED` | 76 | Computed by code from other rows. |
| `DIVERGENCE` | 17 | A discrepancy found between two sources, or between a secondary report and the raw capture. |
| `FACT` | 127 | Stated by the source. |
| `INFERENCE` | 5 | Inference drawn by the author from other rows; not stated by any single source. |
| `SPEC` | 7 | Hardware figure taken from a vendor datasheet. |
| `THEOREM` | 9 | Statement of the theory under the declared hypotheses; `docs/THEORY.md` proves Proposition 1, Corollary 1, the mixed-regime Observation and Corollary 3, and the other statements are direct readings of those closed forms or an application of a cited result. |

## `status` vocabulary

| Value | Rows | Meaning |
|---|---|---|
| `ancora-do-autor` | 18 | Author's anchor or reconstruction; not a quotation. |
| `calculado-por-codigo` | 76 | Computed by the code in this repository. |
| `conferido-por-assert-no-cru` | 29 | A finding of code about the raw capture (presence or absence of a passage, metadata), proved by assertion; not a literal copy. |
| `conferido-por-codigo` | 11 | Measured or checked by a code procedure (for example OCR or pixel measurement). |
| `copiado-de-fonte` | 39 | Copied from the source. |
| `datasheet` | 7 | Copied from a vendor datasheet. |
| `demonstrado-sob-hipoteses-declaradas` | 9 | Stated under the declared hypotheses: `docs/THEORY.md` proves Proposition 1, Corollary 1, the mixed-regime Observation and Corollary 3, and the other statements are direct readings of those closed forms or an application of a cited result. |
| `leitura-conferida-llm` | 51 | Value written by a language-model reader of the source; `nota` records what a code assertion against the raw capture confirmed. |
| `leitura-llm-fonte-externa-nao-salva-em-disco` | 1 | Value read by a language model from an external query whose response was not saved; nothing on disk confirms or refutes it. |
| `suposicao-declarada` | 10 | Declared assumption (no source can confirm it). |

## Id prefixes

The prefix before the first `-` groups rows by source family; the `fonte` column names the source of each row.

| Prefix | Rows | Distinct `fonte` values |
|---|---|---|
| `ARX` | 4 | 1 |
| `BCB` | 3 | 3 |
| `C5` | 2 | 1 |
| `CMP` | 1 | 1 |
| `DU` | 1 | 1 |
| `EST` | 49 | 1 |
| `EVID` | 2 | 2 |
| `EXP` | 1 | 1 |
| `IN` | 37 | 7 |
| `INF` | 2 | 2 |
| `JM` | 1 | 1 |
| `JU` | 2 | 1 |
| `KAT` | 1 | 1 |
| `LER` | 52 | 20 |
| `OCC` | 1 | 1 |
| `REPL` | 21 | 3 |
| `RN` | 1 | 1 |
| `T1` | 1 | 1 |
| `T3` | 1 | 1 |
| `T4` | 9 | 2 |
| `TEO` | 9 | 7 |
| `WEB` | 24 | 20 |
| `case` | 16 | 4 |
| `clientes` | 1 | 1 |
| `foust` | 1 | 1 |
| `fraude` | 1 | 1 |
| `jev` | 1 | 1 |
| `mlops` | 5 | 1 |
| `t3` | 1 | 1 |

## Sources (`fonte` keys)

Every bibliographic key used in the `fonte` column, with the reference it stands for. References come from the author's verified reference records (not distributed): the APA 7 string when the record has one; otherwise the verified record fields, labelled as such. An alias is resolved to its record only after a code check (same arXiv identifier, same title, or the product named in every locator that uses it). A key with no bibliographic record says why. `fonte` cells that hold a public URL or a path of this repository need no key.

| Key | Rows | Reference | Record |
|---|---|---|---|
| `autor` | 10 | The author of this repository: a declared assumption (rows of `tipo` `ASSUMPTION`), not a source. | no verified bibliographic record |
| `bcb_ia` | 1 | Banco Central do Brasil. (2025). *Relatório de estabilidade financeira* (v. 24, n. 2). https://www.bcb.gov.br/content/publicacoes/ref/202510/RELESTAB202510-refPub.pdf | APA 7; verified |
| `bcb_participantes_pix` | 2 | Banco Central do Brasil. (2026a). *Lista de participantes ativos do Pix* (versão de 25 de setembro de 2026) [Conjunto de dados]. Recuperado em 26 de setembro de 2026, de https://www.bcb.gov.br/content/estabilidadefinanceira/participantes_pix/lista-participantes-instituicoes-em-adesao-pix-20260925.csv | APA 7; verified |
| `bcb_spi_pfmi2026` | 2 | Banco Central do Brasil. (2026b). *Princípios para infraestruturas do mercado financeiro: Divulgação de informações sobre o Sistema de Pagamentos Instantâneos (SPI)*. https://www.bcb.gov.br/content/estabilidadefinanceira/sistemapagamentosinstantaneos_docs/principios_infraestruturas_mercado_financeiro.pdf | APA 7; verified |
| `braithwaite2025nuformer` | 13 | Braithwaite, D. T., Cavalcanti, M., McEver, R. A., Udagawa, H., Silva, D., Ramanath, R., Meneses, F., Yoshida, A., Wingert, E., Ramos, M., Zanfelice, B., & Gupta, A. (2025). Your spending needs attention: Modeling financial habits with transformers. arXiv. https://doi.org/10.48550/arXiv.2507.23267 | APA 7; verified |
| `crosby2009tamper` | 1 | https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf | verified record fields, not APA-formatted; page reachable (web check only) |
| `dorkenwald2024` | 4 | Dorkenwald, S., Matsliah, A., Sterling, A.R., et al. · 2024 · Neuronal wiring diagram of an adult brain · Nature · https://doi.org/10.1038/s41586-024-07558-y | verified record fields, not APA-formatted; verified |
| `du2025contextlength` | 1 | Du, Y., Tian, M., Ronanki, S., Rongali, S., Bodapati, S. B., Galstyan, A., Wells, A., Schwartz, R., Huerta, E. A., & Peng, H. (2025). Context length alone hurts LLM performance despite perfect retrieval. In *Findings of the Association for Computational Linguistics: EMNLP 2025* (pp. 23281–23298). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-emnlp.1264 | APA 7; verified |
| `evidently_catalogo` | 2 | Evidently AI. (s.d.). *ML and LLM system design: 800 case studies to learn from* [Base de dados]. Recuperado em 24 de setembro de 2026, de https://www.evidentlyai.com/ml-system-design | APA 7; verified |
| `flores2026noisytv` | 3 | Flores, Carlos Ulisses · 2026 · The Noisy TV in the Measurement Channel: Unbudgeted Instrument Noise in the Intrinsic-Motivation Instrumentation of LLM Agents — paper + replication package · https://doi.org/10.5281/zenodo.22112679 | verified record fields, not APA-formatted; verified, with a divergence from the expected record (the ledger rows record it) |
| `foust2025` | 1 | Foust, T. (2025, 29 de julho). Optimizing user narratives for foundation models. *Building Nubank*. https://building.nu.com/optimizing-user-narratives-for-foundation-models/ | APA 7; verified |
| `haber1991timestamp` | 1 | Haber, S., Stornetta, W.S. · 1991 · How to time-stamp a digital document · Journal of Cryptology · https://doi.org/10.1007/bf00196791 | verified record fields, not APA-formatted; verified |
| `hu2023bert4eth` | 4 | Hu, S., Zhang, Z., Luo, B., et al. · 2023 · BERT4ETH: A Pre-trained Transformer for Ethereum Fraud Detection · https://doi.org/10.1145/3543507.3583345 (published version: https://doi.org/10.1145/3543507.3583345) | verified record fields, not APA-formatted; verified |
| `ju2025autocdsr` | 2 | Ju, C. M., Neves, L., Kumar, B., Collins, L., Zhao, T., Qiu, Y., Dou, Q., Nizam, S., Yang, S., & Shah, N. (2025). Revisiting self-attention for cross-domain sequential recommendation. In *Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2* (pp. 1094–1105). ACM. https://doi.org/10.1145/3711896.3737108 | APA 7; verified |
| `jurafskymartin2026` | 1 | Jurafsky, D., & Martin, J. H. (2026). *Speech and language processing: An introduction to natural language processing, computational linguistics, and speech recognition with language models* (3ª ed.) [Manuscrito online, versão de 19 de agosto de 2026]. https://web.stanford.edu/~jurafsky/slp3/ | APA 7; verified |
| `kaufman2012leakage` | 3 | Kaufman, S., Rosset, S., Perlich, C., et al. · 2012 · Leakage in data mining: Formulation, detection, and avoidance · ACM Transactions on Knowledge Discovery from Data · https://doi.org/10.1145/2382577.2382579 | verified record fields, not APA-formatted; verified |
| `kaul2012aoi` | 1 | Kaul, S., Yates, R., Gruteser, M. · 2012 · Real-time status: How often should one update? · 2012 Proceedings IEEE INFOCOM · https://doi.org/10.1109/infcom.2012.6195689 | verified record fields, not APA-formatted; verified |
| `lakkaraju2017selective` | 4 | Lakkaraju, H., Kleinberg, J., Leskovec, J., et al. · 2017 · The Selective Labels Problem: Evaluating Algorithmic Predictions in the Presence of Unobservables · Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining · https://doi.org/10.1145/3097983.3098066 | verified record fields, not APA-formatted; verified |
| `lappalainen2024` | 8 | Lappalainen, J.K., Tschopp, F.D., Prakhya, S., et al. · 2024 · Connectome-constrained networks predict neural activity across the fly visual system · Nature · https://doi.org/10.1038/s41586-024-07939-3 | verified record fields, not APA-formatted; verified |
| `lin2024rho1` | 3 | Lin, Z., Gou, Z., Gong, Y., et al. · 2024 · Rho-1: Not All Tokens Are What You Need · https://arxiv.org/abs/2404.07965 | verified record fields, not APA-formatted; verified, with a divergence from the expected record (the ledger rows record it) |
| `liu2024lostmiddle` | 3 | Liu, N.F., Lin, K., Hewitt, J., et al. · 2024 · Lost in the Middle: How Language Models Use Long Contexts · Transactions of the Association for Computational Linguistics · https://doi.org/10.1162/tacl_a_00638 | verified record fields, not APA-formatted; verified |
| `mlops` | 3 | Nubank Editorial. (2025, 7 de abril). Practices to scale machine learning operations. *Building Nubank*. https://building.nu.com/practices-to-scale-machine-learning-operations/ | alias of `nubank2025mlops`, checked by code |
| `nubank2024fraude` | 2 | Nubank Editorial. (2024, 18 de dezembro). Unlocking the potential of sequential modeling in fraud prevention: Insights from experts at Nubank. *Building Nubank*. https://building.nu.com/the-potential-of-sequential-modeling-in-fraud-prevention-insights-from-experts-at-nubank/ | APA 7; verified |
| `nubank2025mlops` | 6 | Nubank Editorial. (2025, 7 de abril). Practices to scale machine learning operations. *Building Nubank*. https://building.nu.com/practices-to-scale-machine-learning-operations/ | APA 7; verified |
| `nubank_aws` | 1 | Amazon Web Services. (s.d.). *Nubank adopts AWS Graviton processing and optimizes costs by 14%* [Estudo de caso]. Recuperado em 24 de setembro de 2026, de https://aws.amazon.com/solutions/case-studies/nubank-graviton-case-study/ | APA 7; verified |
| `nubank_clientes` | 1 | Nu Holdings Ltd. (2026). *Nu Holdings Ltd. reports second quarter 2026 financial results* (Form 6-K). U.S. Securities and Exchange Commission. https://www.sec.gov/Archives/edgar/data/0001691493/000129281426004222/nupr2q26_6k.htm | APA 7; verified |
| `nubank_hyperplane` | 1 | Nu Holdings Ltd. (2024, 26 de junho). *Nubank acquires Hyperplane to accelerate AI-first strategy* [Comunicado de imprensa]. https://nu.com/en/newsroom/company/nubank-acquires-hyperplane-to-accelerate-ai-first-strategy | APA 7; verified |
| `nuformer` | 17 | Braithwaite, D. T., Cavalcanti, M., McEver, R. A., Udagawa, H., Silva, D., Ramanath, R., Meneses, F., Yoshida, A., Wingert, E., Ramos, M., Zanfelice, B., & Gupta, A. (2025). Your spending needs attention: Modeling financial habits with transformers. arXiv. https://doi.org/10.48550/arXiv.2507.23267 | alias of `braithwaite2025nuformer`, checked by code |
| `nvidia_a100` | 3 | NVIDIA Corporation. (2022, May). NVIDIA A100 Tensor Core GPU datasheet. https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf | alias of `nvidia_specs`, checked by code |
| `nvidia_h100` | 2 | NVIDIA Corporation. (2022, September). NVIDIA H100 Tensor Core GPU datasheet. https://resources.nvidia.com/en-us-gpu-resources/h100-datasheet-24306 | alias of `nvidia_specs`, checked by code |
| `nvidia_l4` | 1 | NVIDIA Corporation. (n.d.). NVIDIA L4 Tensor Core GPU datasheet [URL oficial resources.nvidia.com/en-us-gpu-resources/l4-tensor-datasheet nao serviu o PDF diretamente; numeros confirmados via mirror AceCloud]. | alias of `nvidia_specs`, checked by code |
| `nvidia_quantum2` | 1 | NVIDIA Corporation. (s.d.). *NVIDIA Quantum-2 InfiniBand platform*. Recuperado em 24 de setembro de 2026, de https://www.nvidia.com/en-us/networking/quantum2/ | APA 7; verified |
| `perdomo2020performative` | 4 | Perdomo, J.C., Zrnic, T., Mendler-Dünner, C., et al. · 2020 · Performative Prediction · https://arxiv.org/abs/2002.06673 | verified record fields, not APA-formatted; verified |
| `recht2019imagenet` | 3 | Recht, B., Roelofs, R., Schmidt, L., et al. · 2019 · Do ImageNet Classifiers Generalize to ImageNet? · https://arxiv.org/abs/1902.10811 | verified record fields, not APA-formatted; verified |
| `russellnorvig2021` | 1 | Russell, S. J., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4ª ed.). Pearson. | APA 7; verified |
| `shiu2024` | 5 | Shiu, P.K., Sterne, G.R., Spiller, N., et al. · 2024 · A Drosophila computational brain model reveals sensorimotor processing · Nature · https://doi.org/10.1038/s41586-024-07763-9 | verified record fields, not APA-formatted; verified |
| `sorscher2022pruning` | 2 | Sorscher, B., Geirhos, R., Shekhar, S., et al. · 2022 · Beyond neural scaling laws: beating power law scaling via data pruning · https://arxiv.org/abs/2206.14486 (published version: https://doi.org/10.52202/068431-1419) | verified record fields, not APA-formatted; verified |
| `typesafe2026jev` | 1 | Almeida, D. (2026, 15 de setembro). Introducing System One Models & Jev. *TypeSafe AI Blog*. https://typesafe.ai/blog/introducing-system-one-models-and-jev | APA 7; verified |
| `udagawa2025` | 17 | Udagawa, H. (2025, 11 de junho). Building foundation models into Nubank's AI platform. *Building Nubank*. https://building.nu.com/foundation-models-ai-nubank-transformation/ | APA 7; verified |
| `xie2023doremi` | 3 | Xie, S.M., Pham, H., Dong, X., et al. · 2023 · DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining · https://arxiv.org/abs/2305.10429 (published version: https://doi.org/10.52202/075280-3059) | verified record fields, not APA-formatted; verified |

## Markers inside cells

| Marker | Meaning |
|---|---|
| `captura sha256:<64 hex>` | SHA-256 of the file the author captured from the public URL written next to it (or already present in the same cell): the raw download, or its text extraction for PDFs. The capture itself is not redistributed (copyright); the hash lets anyone holding a copy check it byte for byte. |
| `sha256 do original privado <8 hex>…` | Prefix of the SHA-256 of a private original cited by the row (the original pre-registration and deviation files, private review notes and mutation reports, or a private sealed output). The sanitized copies in `data/prereg/` and the regenerated outputs of this repository differ byte-wise from those originals by declared renames. |
| `[registro privado, não distribuído]` | A private working record (review notes, measurement logs, research notes) that is not part of this repository. |
| `[selo privado]`, `[selos privados]` | A private provenance seal whose root hash corresponds to no artifact of this repository. This repository seals its own chain (`configs/stages.json`). |
| `docs/THEORY.md#<anchor>` | A statement of the theory, in this repository. |
| `path::key` | A JSON key (dotted path) or a Python function inside a file of this repository. |

## Changes from the author's working ledger

This file is generated from the author's private working ledger by a deterministic sanitization step (not distributed, because it reads the unsanitized ledger). Nothing in the retained rows is re-worded beyond the transformations counted here.

| Transformation | Count |
|---|---|
| Rows read from the working ledger | 287 |
| Rows removed (they check statements against source material that is not public and cannot be redistributed) | 23 |
| Rows removed (prices or costs of a vendor's product — stated by the vendor on its blog or its founder's social-media account, repeated by a news article, or measured by third parties; every row of such a source document) | 13 |
| References to removed rows dropped from `derivado_de` | 0 |
| Rows removed because they lost every source | 0 |
| Theory rows whose `claim`, `valor` and `nota` are a pointer to `docs/THEORY.md` (the repository does not carry the text of the companion paper) | 9 |
| Rows whose `valor` is a pointer to the frozen pre-registration that fixes the wording | 6 |
| Rows written | 251 |
| Column removed (planned placement in the companion text) | 1 |
| Mixed-regime cell identifiers renamed to `MIX1`/`MIX2` (identifier collision) | 0 |
| Private paths mapped to paths of this repository | 184 |
| Theory pointers mapped to `docs/THEORY.md` anchors | 15 |
| Local captures replaced by public URL + capture hash (occurrences) | 89 |
| Distinct captures hashed (of which cross-checked against a sealed checksum manifest) | 54 (17) |
| Private working records replaced by a marker (occurrences) | 50 |
| Private original hashes labelled | 54 |
| Declared in-cell text edits (pointers to removed rows, private seals, private names) | 34 |
| Notes about the author's private working process removed or replaced by a neutral word (the name of a research tool, the numbering of review rounds, and wording or voice labels addressed to the companion text; the verification content of the cell is kept) | 15 |
| Verbatim passages in `valor` longer than 39 words, cut after their first 39 words and ended with `[...]` (the `locator` is unchanged) | 22 |
| Verbatim passages quoted in `claim` or `nota` longer than 39 words, cut the same way inside their quotation marks | 3 |
