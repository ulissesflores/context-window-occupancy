# Desvios e registros pós-run — adendo CMP (fusão de eventos, Corolário 4(b); limite (c))

> **Translation note (English).** Sanitized copy of a dated deviations file of workflow B, written in Portuguese on 2026-09-27, after
> the published run of the family; it amends nothing that was frozen (the pre-registration addendum it
> refers to stays untouched). The private original has sha256
> `e834726806e7e7f261201b6411883c7b6bdcd1529643184a7ba9afc7e2e593e0`. What changed, and nothing else: (1) file paths:
> the pre-registration addenda and the dated files of this series were mapped to their names in this
> repository (`data/prereg/05` to `08`, `data/prereg/09` to `13`); (2) pointers to the
> author's private reports (the impact report of the family and the consolidated report of workflow B)
> were replaced by `[nota privada, não distribuída]` = private note, not distributed, keeping their
> sha256. Line numbers (`l.`) cite the private original of the document named in the same
> sentence (the addendum or, where so stated, the outline). Wording, numbers and criteria are otherwise
> verbatim. Every sha256 quoted below refers to the private original of the file it names.
> Names kept from the original: "laudo" (de impacto, consolidado) = the author's private report, whose
> items were copied verbatim; "corretor" = the agent that applied corrections during the run; "outline"
> = private draft of the article, whose block 2.3a is rendered in English in `docs/THEORY.md`;
> "Base" = the shared runner that existed before the family; mutant identifiers = entries of the private
> mutation reports, whose counts are in `REPRODUCIBILITY.md`. Glossary: desvio = deviation; adendo =
> addendum; pré-registro = pre-registration; grade = grid; tabela analítica = analytic table; gerador =
> generator; célula = cell; semente = seed; janela = window; veredito = verdict; passa / reprova =
> passes / fails; empate = tie; interpretação = interpretation; lacuna preenchida = gap filled; o
> veredito depende disto? = does the verdict depend on this?

> Arquivo NOVO. Runs do workflow B em 2026-09-26; escrito em 2026-09-27, DEPOIS do run publicado. O pré-registro
> `data/prereg/07-fusion-addendum.md` (sha256 `f55d02eddf723b0d215759cf2e9f4c2d0296747afab0b1eddb4296eee27c1585`) fica intocado
> (congelado): o que precisou de interpretação, registro ou correção de texto está aqui, cada item com "o veredito
> depende disto?". Origem: §4 do laudo de impacto
> [nota privada, não distribuída] (sha256 `0643b17d7b79dadcf438addeb35c3ea443ebd68e0194d09b91341550f7846fd0`), itens copiados verbatim,
> e §4 do laudo consolidado [nota privada, não distribuída] (sha256 `e7a8fb9f3be6ac29102bedf7306d6fe4078ef616bf95853767c5fa6e633d24d7`).

**Nenhuma tolerância, nenhum número esperado, nenhum assert e nenhum critério foi alterado ou afrouxado; nenhum dado foi descartado; veredito PASSA sob a letra do §9.**

## Itens

| # | Item (pré-registro) | Classe | Interpretação adotada | O veredito depende? |
|---|---|---|---|---|
| 1 | §11 itens 1–2 (l.480–485) × ordem do prompt | ordem | o gerador foi portado ANTES do TDD, como o §11 manda; `code/fusion_analytic_table.py` 20:03:05 com `cmp` = tabela congelada provado à parte; `tests/test_fusion.py` 20:06:43; vermelho 20:07:02 **de coleta** (`ModuleNotFoundError`, o arquivo único importa `fusion` no topo) | não. Mas o FU4(b) nunca esteve vermelho por assert; o que prova que ele morde são os mutantes FX07b, FX08b e FX09b mortos no gerador portado |
| 2 | §5 l.216–217 e §0.4 l.76–79 (CLI do `run_fusion.py` não fixada) | lacuna preenchida | `--out <dir>` (obrigatório), `--grid` (default `data/fusion_grid.json`), `--processos`, e `--N`/`--bloco-usuarios` só no smoke; publicação = `python3 code/run_fusion.py --out output/fusion` | não (interface; o fluxo aleatório não lê nenhum desses argumentos) |
| 3 | §9 l.369 ("FU1–FU5 verdes e CMP-S/0/N") | composição | `resumo.json` computa só S/0/N/T; FU1–FU5 = pytest; veredito da família = os dois (declarado em `avaliar_fusao.testes_de_unidade`) | não (os dois lados passaram) |
| 4 | §8 l.344–346 (report-only: ociosos, fração saturada, bloco incompleto, blocos visíveis) | lacuna preenchida | para `RF`/`RP` a história de referência é `R` + blocos (pós-fusão); definições em `resumo.json["definicoes"]` | não (report-only) |
| 5 | §9 l.378 (CMP-N, "AUC fluida") | lacuna preenchida | `token_kat.auc_fluida` (scipy) com os parâmetros fundidos, como no `avaliar_kat`; `tol` e `disc_bloco` das mesmas funções do gerador portado; FU4(a) confere `|scipy − gerador| ≤ 1e-12` e as 4 casas da tabela | não (diferença ≤ 1e-12) |
| 6 | §9 l.379–380 (CMP-T, `EP_média`) | lacuna preenchida | Hanley–McNeil da AUC fluida do braço com `N` e `π` da grade, dividido por `√5` (o termo da `tol` do KAT) | **não: o CMP-T passa com `EP_média = 0`** (§1.2) |
| 7 | §9 l.371–373 (CMP-S, estados) | lacuna preenchida | ordem empate -> discorda -> sem significância -> concorda; sinal previsto recomputado e conferido contra a coluna "sinal" da tabela congelada (`ValueError` se divergir); papel lido da tabela | **não: 0 empates, 0 discordantes, 0 sem significância** |
| 8 | §8 l.347–355 (FU1(c)) | lacuna preenchida | o `RS` com o fluxo do KAT passa pelo próprio runner da família, com `{**grade, "tag": 3}` e `i_celula` = posição na grade do KAT (1 = S1b, 3 = S2b), só no teste; comparação por linha (`repr` da auc, `n_pos`, `n_neg`) em `tmp_path` | não (fora do veredito por construção) |
| 9 | §8 l.359 (FU3, "allclose, atol 1e−12") | endurecimento | `rtol = 0` (o default 1e-5 tornaria o teste vácuo); FU1(a)/(b) rodam com `K` real em células que saturam (senão a janela por contagem, FX11, sobreviveria) | não (mais estrito que a letra) |
| 10 | §5 l.209 (um sorteio para `R`, `i_fluxo = 0`) | lacuna preenchida | braço `R` = `token_kat.simular_literal_tokens` importado; `RS`/`RF`/`RP` usam uma cópia da ordem de sorteio dele (o selado não devolve os eventos), com a identidade byte a byte travada pelo FU1(a) | não (FU1(a) verde; FX11 morto) |
| 11 | "8 processos" (§0.6, §10) | não é desvio | runs com `--processos 4`; o número de processos não entra em `default_rng([semente, i_celula, i_fluxo, 7, i_bloco])`; o "8" é base de tempo | não (publicado = replicado byte a byte) |
| 12 | §9 l.395 (linha "Estado de teste" que a célula "Passa" manda ao outline) | redação (NOVO, laudo consolidado §2b e §4) | "(adendo CMP)" -> "(adendo fusao-cmp)", o slug do arquivo; e a parte "Corolário 5: analítico" da mesma célula fica superada pelo veredito do C5 ("Tudo passa"). A linha do outline fica: "Corolário 4(b): conferido por simulação literal por orçamento de tokens (adendo fusao-cmp); Corolário 5: conferido por simulação literal por orçamento de tokens (adendo cotas-c5)." | não (só redação do status; o status do Corolário 5 vem do veredito do C5) |

## Não é desvio (só `CHANGELOG.md`)

Runs com `--processos 4` (item 11). Edição só de docstring de `code/fusion.py` (20:26) depois do run (20:22): saídas
provadas inalteradas (laudo consolidado §4).
