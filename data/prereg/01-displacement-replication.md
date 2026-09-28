# Pré-registro — réplica sintética de deslocamento na janela (D5)

> **Translation note (English).** Sanitized copy of a pre-registration document that was frozen in
> Portuguese before the code it specifies was run. Only the title line, file paths and cell ids changed:
> private paths were mapped to the paths of this repository (`code/`, `tests/`, `data/`, `output/`),
> pointers to private notes were replaced by bracketed placeholders (`[nota privada, não distribuída]` =
> private note, not distributed; `[verificação adversarial privada]` = private adversarial verification;
> `[registro privado de estado]` = private state log), and the two token-KAT cells of the mixed regime
> were renamed `MIX1`/`MIX2`. Wording, numbers and criteria are otherwise verbatim. Every sha256 quoted
> below refers to the private original of the file it names, except the two replication outputs
> (`output/replication/celulas.csv`, `3201f044…`, and `output/replication/resumo.json`, `a2848f52…`),
> which this repository regenerates byte for byte. Glossary: pré-registro = pre-registration; adendo =
> addendum; desvio = deviation; réplica = replication; célula = cell; semente = seed; janela = window;
> saturado/misto/não saturado = saturated/mixed/unsaturated; melhora/piora = improves/worsens;
> selo = provenance seal; critério de quebra = falsification criterion.

> Escrito em 2026-09-24 (noite) ANTES de qualquer código da réplica. Qualquer mudança depois do primeiro run entra
> numa seção "Desvios" datada, com o motivo — nunca reescrita silenciosa. Teto de tempo: fim de 2026-09-25; se não
> fechar, a réplica cai e fica só a reanálise da Tabela 4 ([nota privada, não distribuída], T4-*).

## Pergunta

Sob uma janela finita que guarda os `L` eventos mais recentes, adicionar uma fonte de eventos pode PIORAR a
separabilidade do rótulo mesmo quando essa fonte carrega sinal próprio positivo? E o sinal (melhora/piora) é previsível
por uma regra fechada, sem ajuste aos números do nuFormer?

Motivo: a Tabela 4 do nuFormer (arXiv 2507.23267v2, Apêndice A) mostra que adicionar a fonte C aumenta o shortfall de
AUC em 3 de 3 contextos e adicionar B o reduz em 2 de 2; os autores atribuem o efeito a "contention in the already
limited context window". A réplica testa se o mecanismo declarado basta para produzir esse padrão.

## O que NÃO se afirma

Não é replicação do nuFormer, não estima parâmetros do Nubank, não usa dado real. Todo número sai rotulado
**"ilustrativo, ordens de grandeza"**. O sinal na CONTAGEM de eventos fica excluído por desenho (`λ` não depende de
`y`): em dado real a própria frequência de transação pode predizer default e compensar parte do deslocamento — isso
entra como limitação explícita em 3.3/CF. A única amarração ao case é `L = 146` (2.048 tokens ÷ ~14 tokens/transação,
entrada E1 de `configs/estimates_inputs.json`).

## Modelo gerador (fixado aqui)

- Usuário com rótulo `y ∈ {0,1}`, prevalência `π = 0,2` (fixa para estabilidade da AUC; a AUC não depende de `π`).
- Três fontes `s ∈ {A, B, C}`; eventos da fonte `s` chegam por Poisson com taxa `λ_s` por dia num histórico de
  `T` dias; as taxas **não dependem de `y`** (isola o efeito de deslocamento; sinal na contagem fica fora por desenho).
- Cada evento carrega um atributo `x ~ N(d_s · y, 1)`, independente entre eventos dado `y` (fontes ortogonais dado
  `y`, como os autores dizem de A e B).
- Janela: o modelo vê os `L` eventos mais recentes da união das fontes incluídas, ordenados por tempo.
- Classificador principal: **oráculo** = razão de verossimilhança do modelo gerador sobre os eventos visíveis,
  `score = Σ_visíveis d_s·(x_i − d_s/2)`. É o teto do que qualquer modelo extrai da janela; isola o canal do aprendizado.
- Classificador secundário (stretch, só se sobrar tempo): regressão logística sobre (soma e contagem de `x` por fonte
  visível), para mostrar que um modelo treinado segue o mesmo sinal. Não entra no critério de quebra.

## Previsão analítica (a regra que a simulação testa)

Com contagens no valor esperado, o horizonte visível é `h = min(T, L / Σ_incl λ_s)`, a contagem visível de cada fonte
é `n_s = λ_s · h` e a separabilidade é `Δ² = Σ_incl n_s · d_s²`, com `AUC ≈ Φ(Δ/√2)`.

- **P1 (janela saturada):** se `Σ λ · T ≥ L` com e sem a fonte nova, adicionar `S` melhora **se e somente se**
  `d_S² > (Σ_incl λ_s d_s²) / (Σ_incl λ_s)` — a informação por evento da fonte nova supera a média ponderada por taxa
  da mistura atual (break-even `d_S*`).
- **P1b (a taxa da fonte nova não decide o sinal):** na condição de P1, `λ_S` sai da desigualdade. A frequência
  governa a MAGNITUDE do efeito e o INÍCIO da saturação, nunca o sinal em regime saturado; o sinal depende só de a
  informação por evento da fonte nova estar abaixo ou acima da média da mistura. Previsão testável, não suposição.
  Corolário para a grade: com `d_B < d_A`, `AB > A` é impossível se A sozinha saturar; na grade A nunca satura
  (`λ_A·T ≤ 73 < 146`), então `AB > A` se decide no regime misto — não ler isso como falha de P3.
- **P2 (janela não saturada):** se `Σ λ · T < L` mesmo com a fonte nova, adicionar qualquer fonte com `d_S > 0`
  nunca piora (monotonicidade).
- **P3 (padrão da Tabela 4 como previsão):** existe região do espaço (fonte esparsa e forte A, moderada B, frequente e
  fraca C) em que a regra produz a ordem de sinais `AB > A`, `BC > C`, `AC < A`, `BC < B`, `ABC < AB`, `C` pior sozinha.
  Declarado antes: esta é uma demonstração de **existência** de parâmetros, não um ajuste; a região é reportada inteira
  (fração do grid que produz o padrão), não um ponto escolhido.
- **Região de P3 calculada ANTES de simular** (aritmética pura sobre a grade abaixo, sem simulação;
  [nota privada, não distribuída]): padrão de sinais em **407/720 células (56,5%)**; a
  ordem completa da Tabela 4 (`AB > A > ABC > AC > B > BC > C`) em **50/720 (6,9%)**. Grade não alargada. A simulação
  testa a forma fechada; não caça o padrão.

## Grade (fixada aqui)

`L = 146`; `T ∈ {90, 180, 365}` dias; `λ_A ∈ {0,1; 0,2}`, `λ_B ∈ {0,3; 0,6}`, `λ_C ∈ {1; 3; 6}` por dia;
`d_A ∈ {0,3; 0,5}`, `d_B ∈ {0,15; 0,25}`, `d_C ∈ {0; 0,025; 0,05; 0,1; 0,2}`. Combinações de fontes: as 7 da Tabela 4.
`N = 200.000` usuários por célula; sementes `0..4` (5 réplicas); AUC por Mann–Whitney; reporta-se também a razão de
shortfall `(1 − AUC_X)/(1 − AUC_ABC)` para comparar com a métrica da Tabela 4.

## Redução exata (velocidade — protege o teto de 25/09)

A composição dos `L` últimos eventos de Poissons superpostos é `Multinomial(min(N_tot, L), λ/Λ)` com
`N_tot ~ Poisson(Λ·T)` (rótulos de fonte i.i.d. e independentes dos tempos). Dado o vetor de contagens `n`, o escore do
oráculo é Normal com média `±Δ²/2` e variância `Δ²`, `Δ² = Σ n_s d_s²`. Custo O(1) por usuário. A simulação LITERAL
(gera tempos, ordena, trunca, soma `x`) roda numa grade pequena como KAT da redução (KAT 4).

## Testes conhecidos (KAT) — rodam antes de qualquer número sair

1. **Forma fechada:** contagens FIXAS (não Poisson), sem truncamento: AUC empírica do oráculo = `Φ(√(Σ n_s d_s²)/√2)`
   dentro de 3 erros-padrão (N = 200.000).
2. **Sem C, histórico completo:** `λ_C = 0` e `L ≥` contagem máxima ⇒ AUC idêntica à do oráculo com histórico completo.
3. **Ruído puro não ajuda:** `d_C = 0`, janela saturada ⇒ AUC com C `<` AUC sem C em todas as sementes.
4. **Truncamento correto + redução:** teste de unidade de que a janela guarda exatamente os `L` mais recentes (empate
   por tempo resolvido por ordem estável documentada); e, numa grade pequena (≥ 6 células, N = 50.000), a AUC da
   simulação literal e a da redução multinomial concordam dentro de 3 erros-padrão.

## Critério de quebra (pré-registrado)

A lente de deslocamento **falha** se qualquer um ocorrer:

- **Q1:** em janela saturada com `d_C = 0`, a AUC não cair monotonicamente com `λ_C` (média das 5 sementes).
- **Q2:** nas células em que a previsão analítica de `|AUC(com C) − AUC(sem C)|` (fórmula de `Δ²` com
  `h = min(T, L/Σλ)`, cobrindo também o regime misto em que só a mistura com C satura) é `≥ 0,005`, o sinal empírico
  (média das 5 sementes) discordar do previsto em mais de 5% dessas células. Zona de empate: células com
  `|ΔAUC previsto| < max(0,005; 3·SE)`, com `SE` = erro-padrão empírico da diferença das médias (desvio entre sementes)
  — ficam fora do teste de sinal e são contadas no relatório.
- **Q3:** nenhuma célula do grid produzir o padrão completo de P3.

Se Q1 ou Q2 falhar, o artigo diz que o mecanismo declarado pelos autores não basta sob este modelo. Se só Q3 falhar, a
réplica sustenta o mecanismo mas não o padrão da Tabela 4, e o texto diz isso.

## Selo e reprodutibilidade

Código em `code/displacement.py`, testes em `tests/test_displacement.py` (TDD: KATs primeiro),
saída em `output/replication/`. O run é selado com `code/provenance_chain.py` (reuso, nada novo); teste de
mutação: alterar 1 byte de uma saída selada ⇒ `verify_chain` com exit ≠ 0. É evidência de não-adulteração, não
controle de vazamento (ver laudo [nota privada, não distribuída], item 5).

## Operacionalização declarada ANTES do primeiro run (2026-09-24, noite; nenhum código da réplica existe)

Não muda nada acima; fixa por escrito o que o texto deixava implícito, para que os testes cobrem isto e não uma
leitura escolhida depois de ver número.

- **Definições de P3 = as do cálculo analítico já selado** (script reproduzido em
  `code/displacement.py::regiao_p3_analitica`, que tem de devolver exatamente `(720, 407, 50)`):
  padrão de sinais = `AB>A ∧ BC>C ∧ AC<A ∧ BC<B ∧ ABC<AB ∧ C<min(A,B)`; ordem completa = ordenação decrescente
  igual a `[AB, A, ABC, AC, B, BC, C]`. `AUC_analítica(combo) = Φ(√Δ²/√2)`, `h = min(T, L/Σλ)`.
- **Sorteios:** fluxo independente por `(semente, índice da célula, índice do combo)` —
  `numpy.random.default_rng([semente, i_celula, i_combo])`; sem números aleatórios comuns entre combos (escolha
  conservadora: não reduz artificialmente a variância das diferenças).
- **AUC** = Mann–Whitney com postos médios nos empates (AUC 0,5 quando todos os escores empatam). **Erro-padrão de
  uma AUC** nos KATs = Hanley & McNeil (1982); de uma diferença = `√(se₁² + se₂²)`.
- **Saturação** (para Q1 e para o relatório) = no valor esperado, `Σ_incl λ_s · T ≥ L`.
- **Q1 operacionalizado:** células com `d_C = 0`, combos `AC`, `BC`, `ABC`; para cada par consecutivo
  `λ_C ∈ (1→3), (3→6)` em que as DUAS configurações estão saturadas, a AUC média (5 sementes) tem de cair
  estritamente. Uma violação basta para Q1 falhar. `C` sozinha fica fora (AUC 0,5 constante por construção).
- **Q2 operacionalizado:** três adições de C por célula — `A→AC`, `B→BC`, `AB→ABC` (2.160 comparações).
  `ΔAUC_prev` = diferença das AUC analíticas; `SE = √(s²_com/5 + s²_sem/5)`, `s²` = variância entre sementes
  (`ddof = 1`). Testadas = `|ΔAUC_prev| ≥ max(0,005; 3·SE)`; discordância = sinal da diferença das médias ≠ sinal
  previsto. Q2 falha se discordâncias / testadas > 5%. Relatório conta as excluídas por zona de empate.
- **Q3 operacionalizado:** padrão de sinais de P3 avaliado nas AUC médias empíricas por célula; Q3 falha se 0 de 720.
  Reporta-se também a contagem empírica da ordem completa e a concordância célula a célula com o analítico (407/50).
- **KAT 4, grade pequena:** 6 células com `T = 90`, `λ_A = 0,1`, `λ_B = 0,3`, `λ_C ∈ {1; 3}`, `d = (0,5; 0,15;
  d_C ∈ {0; 0,05; 0,2})`, combo `ABC` (cobre regime não saturado `λ_C = 1` e saturado `λ_C = 3`), N = 50.000.
  Janela literal: ordena por tempo com ordenação estável; entre tempos iguais, o evento que aparece DEPOIS na entrada
  conta como mais recente.
- **Escala:** 720 células × 7 combos × 5 sementes = 25.200 simulações de N = 200.000 pela redução multinomial.

## Resultado — primeiro run (2026-09-24, ~22h30)

Suíte antes do run: 46 testes verdes (40 da réplica = 17 da rodada 1 + 18 travas da rodada 2 + 5 da rodada 3; + 6 das
estimativas). Mutação: 40/40 mutantes obrigatórios mortos + 4 extras (N04, N05, N06, N09). Run: `python3 code/run_replication.py --N 200000 --sementes 5 --saida output/replication`
(81 s, 12 processos; python 3.14.7, numpy 2.4.6, scipy 1.17.1). 25.200 linhas em `output/replication/celulas.csv`.

| Critério | Resultado | Veredito |
|---|---|---|
| Q1 (monotonicidade com `d_C = 0`, saturada) | 248 pares testados, 0 violações | não falha |
| Q2 (sinal empírico × previsto) | 2.160 comparações: 149 abaixo do limiar 0,005, 0 na zona de empate, 2.011 testadas, **0 discordantes (0%)** | não falha |
| Q3 (padrão de sinais de P3 em alguma célula) | 410/720 células (analítico: 407); ordem completa em 55/720 (analítico: 50); concordância célula a célula com o analítico no padrão: 717/720 | não falha |

**Veredito:** sob este modelo gerador, o mecanismo declarado pelos autores (competição na janela finita) basta para
produzir o padrão de sinais da Tabela 4, e a regra fechada (P1/P1b/P2) prevê o sinal de adicionar C em todas as 2.011
comparações testáveis. Diferenças entre contagens empíricas e analíticas (410 × 407; 55 × 50) vêm da aproximação por
contagem esperada (Jensen sobre contagens Poisson) perto do break-even — reportar as duas, nunca só a que favorece.
Razão de shortfall por célula em `resumo.json` (`shortfall_por_celula`; `shortfall_padrao_T4` = 410 células).
Rótulo obrigatório no texto: **ilustrativo, ordens de grandeza; não é replicação do nuFormer**.

sha256 (antes do selo):
```text
3201f0442551935324595b22a46811058e5fd2eafaa5aafc728ab6f3c16f3865  output/replication/celulas.csv
a2848f520f795ce69b5cc657db3344299e69baf2e5902bf5fafc8510f5251579  output/replication/resumo.json
616b2445a6479f1fde7c1ff6d980dca12887be9743633484bfad21925b36a4ec  code/displacement.py
f9ef18500276615dd9bd49b9e64936758e2aa95e330609833151eb32aec8588a  code/run_replication.py
```

## Desvios

Nenhum. As rodadas 2 e 3 de testes (antes do primeiro run) só acrescentaram travas, `ValueError` em dado incompleto e o
cálculo da razão de shortfall já prometido na seção Grade; nenhuma constante, grade ou critério mudou.
