# Desvios e registros pós-run — adendo EXP (expoente de `d` na separabilidade por token; limite (a))

> **Translation note (English).** Sanitized copy of a dated deviations file of workflow B, written in Portuguese on 2026-09-27, after
> the published run of the family; it amends nothing that was frozen (the pre-registration addendum it
> refers to stays untouched). The private original has sha256
> `c36fa99c1928307323e569c4b6d8dc848e1ecaa304c09bda24004a6272800110`. What changed, and nothing else: (1) file paths:
> the pre-registration addenda and the dated files of this series were mapped to their names in this
> repository (`data/prereg/05` to `08`, `data/prereg/09` to `13`); (2) pointers to the
> author's private reports (the impact report of the family and the consolidated report of workflow B)
> were replaced by `[nota privada, não distribuída]` = private note, not distributed, keeping their
> sha256. Line numbers (`l.`) cite the private original of the document named in the same
> sentence (the addendum or, where so stated, the outline). Wording, numbers and criteria are otherwise
> verbatim. Every sha256 quoted below refers to the private original of the file it names, except the summary of the family (`output/exponent/resumo.json`, `46aeb445…`), which
> this repository carries byte for byte.
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
> `data/prereg/05-exponent-addendum.md` (sha256 `9c9fce0674993e16fccbeee10ec3de20422532acf8352d72cb06908302524428`) fica intocado
> (congelado): o que precisou de interpretação, registro ou correção de texto está aqui, cada item com "o veredito
> depende disto?". Origem: §4 do laudo de impacto
> [nota privada, não distribuída] (sha256 `1a05fa6503ef805300c76047f85de731d68101226c46191bc6af27e5c010e16d`), itens copiados verbatim,
> e §4 do laudo consolidado [nota privada, não distribuída] (sha256 `e7a8fb9f3be6ac29102bedf7306d6fe4078ef616bf95853767c5fa6e633d24d7`).

**Nenhuma tolerância, nenhum número esperado, nenhum assert e nenhum critério foi alterado ou afrouxado; nenhum dado foi descartado; veredito PASSA sob a letra da §1.9.**

## Parte A — interpretações do corretor

| # | Item (pré-registro) | Classe | Interpretação adotada | O veredito depende? |
|---|---|---|---|---|
| 1 | "Estado: congelado" itens 1–2 (l.459–462) × §1.11 (l.360, "vermelhos antes do runner") | ordem | porte do gerador (e `cmp` byte a byte) ANTES dos testes; como o `run_grid.py` já existia (Base), o "vermelho antes do runner" foi tomado no gancho `veredito(linhas, grade)` (8 falhas EX5 + 1 do run publicado); EX1–EX4 nasceram verdes | não. O que prova que EX1 e EX2 mordem são os mutantes 4a/4b, 5a–5d, 7 e 8 mortos no assert pretendido; EX3 e EX4 caem só como colateral (EX3 no mutante 7; EX4 nos 4a/4b e 5a–5d) |
| 2 | §1.9 l.333 e §1.13 l.414 (sinal da teoria; EXS = `KT_S`) | lacuna preenchida | `sign(dif_prevista)` de `token_kat.avaliar_kat` (scipy) cruzado com o "teo" da tabela (NormalDist); divergência -> `ValueError` | não (nunca divergiu) |
| 3 | §1.9 l.328 (`tolΔ` congelada por célula) | lacuna preenchida | o gancho recomputa `tolΔ` com a aritmética congelada sobre a grade recebida; no run publicado = Tabela 1 a 4 casas (EX5 pina); no smoke difere e o smoke não é veredito | **não: maior razão 0,25** |
| 4 | §1.9 l.337 (report-only, desvio ao exato "em EP") | lacuna preenchida | EP = `EP_emp` (entre sementes, `ddof = 1`); `None` se `EP_emp = 0` | não (report-only) |
| 5 | §1.9 l.338–339 (intervalo implicado) | lacuna preenchida | gravado só com as 6 células rodadas e EXS aprovado; das raízes exatas (máximo do lado baixo, mínimo do lado alto, por família), 3 casas; `2.51` no JSON = 2,510 | não (report-only) |
| 6 | §1.10 l.344–347 (leituras de reprovação) | lacuna preenchida | strings EN em `veredito.leitura_EXS` por (família, lado); vazio neste run | não |
| 7 | não previsto | endurecimento | `veredito.completo` e desfecho `"incompleto"` para grade filtrada (`--celulas`), para que run parcial (EX4, harness) nunca grave "passa"; `completo` exige `N`, sementes e bloco da grade congelada | não (run publicado `completo = true`) |
| 8 | §1.8 (porte do gerador) | forma | mensagens de assert e stdout do gerador portado em PT verbatim (artefato congelado; precedente `token_kat_analytic_table.py`); docstrings e comentários em EN | não (stdout = tabela congelada byte a byte, EX2) |
| 9 | §1.10 ("Empate -> reprova por poder") | correção só no código (execução 3 do corretor) | o gancho dava a um empate a leitura de discordância; ramo `empate` -> leitura de empate; testes só acrescentados (texto da leitura no empate e na discordância; 3 casos de grade fora do congelado; mensagem nomeada no valor absoluto) | **não: 0 empates, 0 discordâncias**; saída publicada byte-idêntica antes da correção |
| 10 | "8 processos" (§0.6, §1.14) | não é desvio | runs com `--processos 4`; o nº de processos não entra em `default_rng([semente, i_celula, i_combo, 5, i_bloco])`; o "8" é base de tempo | não (publicado = replicado byte a byte) |
| 11 | §1.12 (harness de mutação) | correção só no harness | execução 1: substring do mutante 6 supunha prefixo que o JUnit não põe; corrigida no harness antes da execução 2; nenhum teste, tolerância ou código mudou | não (mutante 6 morto nos dois testes pretendidos, com mensagem nomeada na execução 3) |

## Parte B — linha de limites do outline (a l.352 do pré-registro exige "por desvio datado")

**Parte B — mudança da linha de limites do outline** (a l.352 exige "por desvio datado"): registrar que, a partir
desta data, o item "não discrimina o expoente de `d`" da linha de limites do outline (l.248, que cita os itens 4–5
dos desvios selados do KAT) ganha o fecho "contabilidade `d²` conferida contra rivais `d/k`, `d³/k` (EXP)", com a
janela já saturada antes da fonte nova, pelo adendo EXP (`9c9fce06…`) e pelo resultado (`46aeb445…`); os desvios
selados do KAT (`4ceba2bb…`) não são editados.

## Parte C — nota datada sobre o item 5 dos desvios do KAT

Em arquivo próprio, `data/prereg/13-token-kat-item5-note.md` (sha256 `6d054978403f5642eeb96ed1f8e5290f740481d935ec5d69f8790761863c2e24`): um dono (o KAT) e duas orações afetadas (expoente e ocupação × taxa); o
texto não se repete aqui. O veredito depende disto? Não (não entra em critério nenhum).

## Não é desvio (só `CHANGELOG.md`)

Runs com `--processos 4` (o "8 processos" é base de tempo; o número de processos não entra no fluxo aleatório) —
é o item 10 da Parte A, registrado lá como "não é desvio".
