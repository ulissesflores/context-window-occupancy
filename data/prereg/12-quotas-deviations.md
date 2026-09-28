# Desvios e registros pós-run — adendo C5 (cotas por `ρ` contra o corte por recência, Corolário 5; limite (d))

> **Translation note (English).** Sanitized copy of a dated deviations file of workflow B, written in Portuguese on 2026-09-27, after
> the published run of the family; it amends nothing that was frozen (the pre-registration addendum it
> refers to stays untouched). The private original has sha256
> `03057e4d4db0fea5189770d37f6a248b21f3090dd0773834e36261b1854e87bc`. What changed, and nothing else: (1) file paths:
> the pre-registration addenda and the dated files of this series were mapped to their names in this
> repository (`data/prereg/05` to `08`, `data/prereg/09` to `13`); (2) pointers to the
> author's private reports (the impact report of the family and the consolidated report of workflow B)
> were replaced by `[nota privada, não distribuída]` = private note, not distributed, keeping their
> sha256; (3) item 1 named the author's main working session as the one that would decide the
> proposed wording: it now reads "decisão registrada abaixo" (decision recorded below), which
> is the adopted wording that follows it. Line numbers (`l.`) cite the private original of the document named in the same
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
> `data/prereg/08-quotas-addendum.md` (sha256 `6e30e20d4ddc0283743366ee13c7cf5e1319476fd147489059dde13f55fdf807`) fica intocado
> (congelado): o que precisou de interpretação, registro ou correção de texto está aqui, cada item com "o veredito
> depende disto?". Origem: §4 do laudo de impacto
> [nota privada, não distribuída] (sha256 `5f41841a8f14efd61f7fafeb77f699dfacdeec69e104af56c8e3b71c4ea88d3b`), itens copiados verbatim,
> e §4 do laudo consolidado [nota privada, não distribuída] (sha256 `e7a8fb9f3be6ac29102bedf7306d6fe4078ef616bf95853767c5fa6e633d24d7`).

**Nenhuma tolerância, nenhum número esperado, nenhum assert e nenhum critério foi alterado ou afrouxado; nenhum dado foi descartado; veredito PASSA sob a letra da §9–§10.**

## Item 1 — errata de texto (substantivo)

**Item 1 — ERRO DE TEXTO do pré-registro (substantivo; muda uma frase que a linha "Tudo passa" manda ao THEORY).**
§1 l.135–136 ("O caso 'sem saturação' (todas devolvem a história inteira) é identidade por construção"), §10 l.379
("sem saturação, todas devolvem a história inteira (por construção, UT-2)") e §11 UT-2 l.403–404 ("história com custo
`≤ K` -> todas devolvem tudo") contradizem a definição literal da §4 (l.170–172) e da chave `_politicas` da grade:
FIXf, FIXc e TAX são cotas fixas tiradas das contagens ESPERADAS, sem realocação, e cortam os eventos mais antigos de
uma fonte sempre que `N_s > q_s`, mesmo quando a história inteira cabe em `K`. **A §4 prevalece** (é a definição
congelada das políticas); o código implementa a §4; o defeito está nas três passagens. Evidência do corretor: numa
célula ilustrativa não saturada (`T·W = 1.494 < K`), FIXf/FIXc cortam 69% das histórias que cabem e TAX 7% (número de
conferência, não da grade); o UT-2 confere a identidade só para REC, RHO, EVT e RHOidade e trava o corte das cotas
fixas como comportamento (`test_ut2_cota_fixa_corta_historia_que_cabe`). **Não afeta o veredito:** as 6 células são
saturadas por desenho (`z ≥ 4,33`; fração saturada 1,0 medida), e a tabela congelada já modela FIX/TAX como
`min(N_s, q_s)`. **Redação proposta** (decisão registrada abaixo): PT "sem saturação, a recência e as cotas adaptativas
(RHO, EVT) devolvem a história inteira; as cotas fixas (FIXf, FIXc, TAX) ficam limitadas à cota tirada das contagens
esperadas e podem cortar uma história que cabe (por construção, UT-2)"; EN = bullet "Without saturation" da §2.7.

**Redação adotada (2026-09-27):** a proposta do laudo, sem mudança. PT: "sem saturação, a recência e as cotas adaptativas (RHO, EVT) devolvem a história inteira; as cotas fixas (FIXf, FIXc, TAX) ficam limitadas à cota tirada das contagens esperadas e podem cortar uma história que cabe (por construção, UT-2)". EN (bullet "Without
saturation" do laudo C5 §2.7): "Recency and the adaptive quotas (RHO, EVT) return the whole history; the fixed
quotas (FIXf, FIXc, TAX) stay capped at their quota from the expected counts and can cut a history that fits." A
frase "sem saturação, todas devolvem a história inteira" (e "todas devolvem tudo") não se usa mais, em lugar
nenhum. O veredito depende disto? Não: as 6 células são saturadas por desenho.

## Itens 2–12 — interpretações de ambiguidade

Do laudo C5 §4: interpretações de ambiguidade (não mudam critério nem número; registrar no mesmo arquivo como "interpretações" e no `CHANGELOG.md`):

2. ordem porte -> TDD -> run da §12 prevaleceu sobre a ordem genérica da tarefa; o vermelho registrado é o erro de coleta `ModuleNotFoundError: No module named 'quotas'`. O veredito depende disto? Não (interpretação; não muda critério nem número).
3. CLI `python3 code/run_quotas.py --out <dir>` (o pré-registro do C5 não fixa CLI), replicado em `output/replicated/quotas` e publicação em `output/quotas` (§0.2), `cmp` byte a byte = iguais (sha acima). O veredito depende disto? Não (interpretação; não muda critério nem número).
4. `veredito.passou` = âncoras ∧ C5-O ∧ C5-G ∧ C5-C ∧ C5-N, desfechos calculados à parte, C5-D fora do `passou`, UT pelo pytest. O veredito depende disto? Não (interpretação; não muda critério nem número).
5. regra "sem poder" aplicada às comparações medidas contra `tol_X` (C5-G e as duas do C5-C), não aos níveis nem ao C5-D. O veredito depende disto? Não (interpretação; não muda critério nem número).
6. previsões em precisão cheia pelo gerador portado, com teste de que o arredondamento reproduz a tabela impressa. O veredito depende disto? Não (interpretação; não muda critério nem número).
7. **RHOidade: desempate de prioridades iguais não especificado na §4 — adotado "mais recente primeiro"** (preenche lacuna de definição congelada; medida zero com tempos contínuos — sinalizar como tal). O veredito depende disto? Não (interpretação; não muda critério nem número).
8. C5-N = 5 células × 6 políticas = 30, fora DEC1 e a história R-só. O veredito depende disto? Não (interpretação; não muda critério nem número).
9. âncoras conferidas contra a grade E contra as linhas seladas do KAT; no smoke, não aplicáveis. O veredito depende disto? Não (interpretação; não muda critério nem número).
10. definições dos report-only (ociosos = média de `K` − custo visível nos saturados; `D` sem ruído de soma). O veredito depende disto? Não (interpretação; não muda critério nem número).
11. `rival_refutado` = o critério de `refuta_rival` passa naquela comparação; H-EST fica `null`. O veredito depende disto? Não (interpretação; não muda critério nem número).
12. UT-1 com empates forçados por proxy do `Generator` que arredonda só os uniformes; UT-3 força bruta por `monkeypatch` do suporte Poisson, sem editar o gerador portado. O veredito depende disto? Não (interpretação; não muda critério nem número).

## Itens NOVOS do laudo consolidado (§4)

13. **Registro, análogo ao item 11 do OCC.** `tests/test_quotas.py` foi modificado às 20:49:42, **depois** do run
    publicado (20:29:40): a mutação execução 1 (53 testes) achou M13c sobrevivente e M05d morto fora do assert
    pretendido, e acrescentou `test_ut2_cota_fixa_com_orcamento_exato` e
    `test_avaliador_consequencia_tolerancia_fixa`; código de produção intacto, nenhum assert removido ou afrouxado;
    explica 53 -> 55 testes; execução 2 = 33/33. O veredito depende disto? Não (acréscimo de cobertura).
14. **Redação.** "Corolário 5: conferido (adendo cotas-c5)" (l.379) -> forma longa "Corolário 5: conferido por
    simulação literal por orçamento de tokens (adendo cotas-c5)", a mesma do Corolário 4(b) (frase única da linha
    de estado de teste do outline). O veredito depende disto? Não.

## Não é desvio (só `CHANGELOG.md`)

**Não é desvio (só `CHANGELOG.md`):** `--processos 4` (o nº de processos não entra no fluxo
`default_rng([semente, i_celula, i_combo, tag, i_bloco])`; o "8 processos" da §0.6 é base de tempo).
Edição só de docstring de `code/quotas.py` (20:31) depois do run (20:29): saídas provadas inalteradas (laudo
consolidado §4).
