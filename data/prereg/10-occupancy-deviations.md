# Desvios e registros pós-run — adendo OCC (ocupação × taxa na média `ρ̄`; limite (b))

> **Translation note (English).** Sanitized copy of a dated deviations file of workflow B, written in Portuguese on 2026-09-27, after
> the published run of the family; it amends nothing that was frozen (the pre-registration addendum it
> refers to stays untouched). The private original has sha256
> `30edeefc0b136fe7241d273129f038a7bae4696d615fcd7e77eb99b945a22cac`. What changed, and nothing else: (1) file paths:
> the pre-registration addenda and the dated files of this series were mapped to their names in this
> repository (`data/prereg/05` to `08`, `data/prereg/09` to `13`), and the `repo/` prefix of the original was dropped; (2) pointers to the
> author's private reports (the impact report of the family and the consolidated report of workflow B)
> were replaced by `[nota privada, não distribuída]` = private note, not distributed, keeping their
> sha256; (3) item 2 cited a numbered entry of the author's private state log and a decision of the
> author's working session: it now cites `[registro privado de estado]` = private state log, and
> reads "decisão registrada" (recorded decision). Line numbers (`l.`) cite the private original of the document named in the same
> sentence (the addendum or, where so stated, the outline). Wording, numbers and criteria are otherwise
> verbatim. Every sha256 quoted below refers to the private original of the file it names, except the two published outputs of the family quoted in item 2
> (`output/occupancy/resumo.json`, `fc86a7ba…`, and `output/occupancy/celulas.csv`,
> `21e64fe3…`), which this repository carries byte for byte.
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
> `data/prereg/06-occupancy-addendum.md` (sha256 `574dccf9065f1860537dab6e5928ea9d1f5f17b6b736b0ac9d78e6639be55c19`) fica intocado
> (congelado): o que precisou de interpretação, registro ou correção de texto está aqui, cada item com "o veredito
> depende disto?". Origem: §4 do laudo de impacto
> [nota privada, não distribuída] (sha256 `73cee842642f1b913d1493403c3198f49683459d3300e28ebda61b95fb9e53a2`), itens copiados verbatim,
> e §4 do laudo consolidado [nota privada, não distribuída] (sha256 `e7a8fb9f3be6ac29102bedf7306d6fe4078ef616bf95853767c5fa6e633d24d7`).

**Nenhuma tolerância, nenhum número esperado, nenhum assert e nenhum critério foi alterado ou afrouxado; nenhum dado foi descartado; veredito PASSA sob a letra da §2.8, com o item 1 abaixo.**

## Itens

| # | Item (pré-registro) | Classe | Interpretação adotada | O veredito depende? |
|---|---|---|---|---|
| 1 | §2.8 l.305 ("passa se, e só se, OCCT1–OCCT3 verdes e:") | composição | `veredito()` não prova que o pytest rodou: OCCT1–OCCT3 = pré-condição verificada pelo pytest (`testes_unidade.verificados_neste_run = false`); `veredito.passou` = OCC-S ∧ OCC-N; PASSA = pytest verde ∧ `veredito.passou` | não (os dois lados verdes; 51 passed re-executado por este laudo) |
| 2 | §3 item 3 l.419–420 ("Este 1º run é o ato de publicação") | ordem | invertida por decisão registrada ([registro privado de estado], ordem do C5 §0.2): 1º run em `output/replicated/occupancy/` (não selado); publicação = 2º run com o comando congelado `--grid data/occupancy_grid.json --out output/occupancy`; `cmp` byte a byte = idênticos | não (sha iguais: `fc86a7ba…`, `21e64fe3…`) |
| 3 | §2.11 l.346 e §2.8 l.307 (`avaliar_kat` duas vezes; "`\|ΔAUC previsto\|`") | lacuna preenchida | literal no gancho `veredito()`; o ΔAUC previsto do OCC-S vem de `token_kat.auc_fluida` (scipy) via `avaliar_kat`, não do `auc` (NormalDist) da tabela congelada | não (diferença ~1e−16; menor razão 19,3 ≫ 3) |
| 4 | §2.8 l.316 ("0,75 se OCC-L também concordar") | lacuna preenchida | `alfa_minimo.com_occ_l` só é calculado se as DUAS de OCC-L concordam (senão `null`); `α*` por célula sempre gravado | não (report-only) |
| 5 | §2.8 l.317–318 (invariância em `T`) | lacuna preenchida | pares = agrupamento `(R, S)` das células do núcleo, ordenados por `T` (moderado primeiro); limite `3·√(EP₁² + EP₂²)` com o `EP_emp` de `avaliar_kat` | não (report-only; 4/4) |
| 6 | §2.8 l.319–320 (regra "por evento" "refutada ou não") | lacuna preenchida | refutada se, e só se, as 7 células em que ela prevê o oposto da ocupação estão em `concorda` (empate não refuta) | não (report-only; 7/7) |
| 7 | §2.12 l.368–369 (OCCT2: "a S3 reproduz a linha congelada do KAT") | lacuna preenchida | comparação nos 10 campos numéricos da linha, na precisão impressa (`.2f/.0f/.6f/.4f/+.4f`) | não (OCCT2 verde) |
| 8 | §2.9 l.322–329 (leitura do desfecho) | lacuna preenchida | codificada em `veredito.leitura`; discordância e empate juntos → prevalece a discordância (falsifica); discordância só na OCC10 → "(iii) falha com janela esparsa" | não (10/10 concorda) |
| 9 | fora do pré-registro | acréscimo | run de subconjunto (`--celulas`) grava `grade_completa = false` e `passou = false`, sem `ValueError` (para a mutação rodar célula mínima) | não (run publicado: `grade_completa = true`) |
| 10 | §3 item 2 (TDD antes do runner e do porte) | registro | a ordem do pré-registro coincidiu com a da tarefa; o runner partilhado já existia (Base), por isso o OCCT1 nasceu verde | não |
| 11 | §3 itens 2–3 (testes antes do run) | registro (NOVO) | `tests/test_occupancy.py` foi modificado às 20:58:39, **depois** do run publicado (20:33:29): a mutação (1ª rodada) achou lacuna de TESTE (X06a/X06b só caíam por `KeyError: 'tag_r3'`) e acrescentou `test_adaptador_leva_o_tag_6_da_grade_da_familia_ate_a_simulacao`; código de produção (`occupancy_analytic_table.py` 20:17:06, `run_grid.py` 20:04:39) e saídas intocados; nenhum assert removido ou afrouxado | não (acréscimo de cobertura; X06a/b mortos no assert na 2ª rodada) |
| 12 | §2.10 l.336 e §2.8 l.316 ("α ≥ 0,75", "0,52") | interpretação de redação (NOVO) | o rótulo de 2 casas arredonda PARA CIMA um limite inferior (`α*` = 0,74890 e 0,51564); texto no `THEORY.md` e no ledger usa o truncamento ("exclui `α < 0,748`" / "`α < 0,515`") | não (report-only) |
| 13 | §2.13 (mutação) | interpretações declaradas antes de rodar (relatório `786b481a…`) | X01 mutado no ponto da previsão (`analisar`, ramo saturado), não na definição de `ρ̄` (evita `ZeroDivisionError`); X02 em 4 variantes (tags 3, 5, 7, 8); X03/X04 em grade e pino; **X04 só morre no pino** (nenhuma célula discrimina 1,2 de 1,5: menor ΔAUC/tol da tabela = 1,61), não é equivalente; X05 em 3 leituras; X06c (sem queda, sorteia o fluxo do KAT) morre no assert do adaptador | não (16/16 mortas no assert pretendido) |

## Não é desvio (só `CHANGELOG.md`)

**Não é desvio (só `CHANGELOG.md`):** `--processos 4` (o "8 processos" da §0.6 é base de tempo; o nº de processos não
entra no fluxo).

## Superação do item 5 dos desvios do KAT (linha 335 do pré-registro)

A oração "a comparação ocupação × taxa depende de uma célula só (S3, `z(R) = 2,87`)" fica SUPERADA pelo adendo OCC;
o registro datado está em `data/prereg/13-token-kat-item5-note.md` (sha256 `6d054978403f5642eeb96ed1f8e5290f740481d935ec5d69f8790761863c2e24`), composto com o
EXP (dono da oração do expoente no mesmo item 5); a oração de `θ` segue aberta. Os desvios selados do KAT não são
editados. O veredito depende disto? Não.
