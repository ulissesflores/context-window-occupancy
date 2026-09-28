# Adendo ao pré-registro — KAT-token: custo por evento heterogêneo

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

> Escrito em 2026-09-26 (tarde) ANTES de qualquer código de simulação por orçamento de tokens. **Não altera**
> `data/prereg/01-displacement-replication.md` (sha256 `b1563d973d090bc08a9dd7495f74264ce98c629b1d355bd45fe371f2ab815368`,
> folha do estágio `prereg` dos selos r1 e r2): acrescenta um teste, em arquivo próprio, para que aquele continue
> byte a byte. **Precedência:** não há âncora de tempo externa; o sha256 deste arquivo, da grade e da tabela analítica
> fica registrado em [registro privado de estado] (rodada pós-/clear nº 9) antes de existir qualquer arquivo de simulação
> (`code/token_kat*.py`, `tests/test_token_kat*.py`). **Este arquivo não recebe o resultado** (vai para
> `output/kat_token/resumo.json`, citado no [registro privado de estado]); desvio, se houver, vai para arquivo próprio datado.

## Pergunta

A especificação da teoria (`docs/THEORY.md`, bloco 2.3a, sha256 `1769b0c9…`) generaliza a
regra pré-registrada P1 para custo em tokens por evento `k_s` heterogêneo:

- **Proposição 1** (janela saturada, `T·Σλk ≥ K`): `Δ² = K·Σ_s φ_s ρ_s`, com ocupação `φ_s = λ_s k_s / Σ_r λ_r k_r`
  e separabilidade por token `ρ_s = d_s² / k_s`.
- **Corolário 1:** com `R` saturada, adicionar `S` aumenta a AUC se e somente se `ρ_S > ρ̄ = Σ_R λ_r d_r² / W_R`
  (média de `ρ` ponderada pela OCUPAÇÃO, tomada antes da adição; `W_R = Σ_R λ_r k_r`).
- **Observação (regime misto):** se `R` não satura e `R ∪ S` satura, melhora se e somente se `ρ_S > θ·ρ̄`, com
  `θ = W_R·(T·W′ − K) / (K·λ_S k_S) ∈ [0, 1)` e `W′ = W_R + λ_S k_S`.
- **Corolário 3:** se nem `R ∪ S` satura, adicionar `S` com `d_S > 0` nunca piora.

A réplica r1 testou só `k_s ≡ k` (janela de `L = 146` eventos). Este KAT testa se, numa janela de `K` tokens com
eventos inteiros, a simulação LITERAL segue o sinal e o nível da forma fechada com `k` heterogêneo, inclusive nas
células em que uma regra ingênua prevê o sinal oposto.

## O que NÃO se afirma (escopo)

- Ilustrativo, ordens de grandeza; **não é replicação do nuFormer**. Do case entram só `K = 2.048` (contexto) e
  `k ∈ {14, 55}` (transação compacta × texto puro; entradas E1 de `configs/estimates_inputs.json`).
- **Não cobre:** Corolário 4(b) (fusão sem perda) e Corolário 5 (mochila / alocação ótima) seguem analíticos.
  Corolário 4(a) (escalar todos os `k`) é caso particular de `h = K/Σλk`, que o critério de nível testa, sem célula
  dedicada. Nenhuma figura nova.
- **Produto:** licenciar UMA frase da 2.3a ("com custo `k_s` heterogêneo, a separabilidade relevante é
  `ρ_s = d_s²/k_s`; conferido por simulação literal por orçamento de tokens"). Nenhum número deste KAT vai ao corpo.
- Sinal na contagem e no tempo de chegada segue excluído por desenho (hipótese v; taxas não dependem de `y`).

## Modelo gerador (herda o pré-registro; muda só a janela)

Igual ao pré-registro: `π = 0,2`; eventos da fonte `s` por Poisson de taxa `λ_s` em `T` dias, independente de `y`;
atributo `x ~ N(d_s·y, 1)`; leitor = oráculo `score = Σ_visíveis d_s·(x_i − d_s/2)`; AUC por Mann–Whitney com postos
médios. Novo: cada evento da fonte `s` custa `k_s` tokens (inteiro, fixo por fonte) e a janela comporta `K = 2.048`.

**Regra de truncamento (fixada aqui).** Eventos do usuário ordenados por tempo com ordenação estável; entre tempos
iguais, o que aparece DEPOIS na entrada é o mais recente (regra literal do r1). A janela é o **maior sufixo** de eventos
mais recentes cujo custo somado é `≤ K`. Só eventos inteiros: o evento que estouraria o orçamento cai junto com todos
os mais antigos — **não** se pula para caber um evento mais antigo e mais barato, e **não** entra evento parcial.
Consequência declarada: no regime saturado sobram até `k_max − 1` tokens ociosos por usuário, viés para baixo de no
máximo `k_max/K` do `Δ²` fluido (`55/2.048 = 2,7%`), já contado na tolerância de nível.

**Ordem dos sorteios.** A mesma de `simular_literal` (r1): `y`; contagens Poisson (usuários × fontes); tempos
uniformes em `[0, T)`; atributos `x`. Fluxo por `numpy.random.default_rng([semente, i_celula, i_combo, 3, i_bloco])` —
tag `3` = r3, distinta do r1; `i_combo` = 0 para `R`, 1 para `R ∪ S`; blocos de 10.000 usuários (memória: a
simulação literal gera todos os `Λ·T` eventos do histórico, não só os visíveis).

**Restrições de código (para não quebrar os selos r1/r2).** `code/displacement.py` é folha selada em r1 e
r2: o módulo novo **importa** dele (AUC, janela por eventos, simulação literal do r1) e **nunca o edita**. Os testes
novos NÃO podem casar com o glob selado `tests/test_displacement*.py` (entrariam como folha nova nos selos antigos):
nomes `tests/test_token_kat*.py`. Saída em `output/kat_token/`, nunca em `output/replication/`.

## Previsão (a regra que a simulação testa)

Forma fechada fluida: `W = Σλk`, `h = min(T, K/W)`, `Δ² = h·Σλd²`, `AUC = Φ(√Δ²/√2)`. Sinal previsto de `R → R ∪ S`
= sinal de `ΔΔ²`. A tabela abaixo confere, por aritmética, que esse sinal coincide com o do corolário do regime
(Corolário 1, Observação `θ·ρ̄` ou Corolário 3) e que a regra ingênua declarada em cada célula prevê o OPOSTO.

## Grade (fixada aqui)

Fonte única: `data/kat_token_grid.json` (sha256 `15fbb04efb3843b784a4ad66e4291c1f77dbc414f726e1826541af6c5d0a441f`).
`K = 2.048`; `N = 100.000` usuários por (célula, combo, semente); sementes `0..4`; dois combos por célula (`R` e
`R ∪ S`); 8 células = 80 simulações. Critérios de desenho, conferidos por código antes de simular: regime a pelo
menos 2,5 desvios-padrão do limiar de saturação (tokens por usuário = Poisson composto), no máximo 600 eventos por
usuário, `|ΔAUC previsto| ≥ 1,2·tol`, regra ingênua com sinal oposto; S1a/S1b e S2a/S2b com sinal constante em `λ_S`
(Corolário 2 com `k`); MIX1/MIX2 com o MESMO `(R, S)` e sinal invertido só por `λ_S` (o `θ` do regime misto).

| Célula | Regime | O que discrimina (regra ingênua refutada) |
|---|---|---|
| S1a, S1b | saturado | `R` compacta (`k = 14`), `S` em texto (`k = 55`) com `d_S² ≈ 2·d_R²`: a regra por evento (ignora `k`) prevê MELHORA; `ρ_S < ρ̄` prevê PIORA |
| S2a, S2b | saturado | `R` em texto (`k = 55`), `S` compacta (`k = 14`) com `d_S² ≈ 0,48·d_R²`: a regra por evento prevê PIORA; `ρ_S > ρ̄` prevê MELHORA |
| S3 | saturado | `R` = fonte compacta forte + fonte em texto fraca: `ρ̄` ponderada pela TAXA (`λ`) prevê PIORA; pela OCUPAÇÃO (`λk`) prevê MELHORA |
| MIX1 | misto | `θ·ρ̄ < ρ_S < ρ̄`: MELHORA; o Corolário 1 aplicado sem checar a saturação de `R` prevê PIORA |
| MIX2 | misto | mesmo `(R, S)` de MIX1 com `λ_S` 10× maior: `ρ_S < θ·ρ̄`, PIORA; "fonte com `d_S > 0` nunca piora" prevê MELHORA |
| N1 | não saturado | `ρ_S < ρ̄` sem saturar: MELHORA (Corolário 3); o Corolário 1 aplicado sem saturação prevê PIORA |

## Tabela analítica — calculada ANTES de simular

Script `code/token_kat_analytic_table.py` (stdlib, sem simulação; sha256
`2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`); saída
`data/prereg/kat_token_analytic_table.txt` (sha256
`997d2e5698cafda6f34b8452bf4b29653dea75f97033734a05eb5ede8484f4dc`; duas execuções idênticas; exit 0).

| célula | regime | T | z(R) | z(R∪S) | eventos/usuário | ρ_S | ρ̄ (ocupação) | ρ̄ (taxa) | θ | AUC(R) | AUC(R∪S) | ΔAUC previsto | tol | ΔAUC/tol | forma fechada | regra ingênua |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1a | saturado | 180 | 4.74 | 10.57 | 306 | 0.000525 | 0.001029 | 0.001029 | — | 0.8476 | 0.8041 | -0.0435 | 0.0137 | 3.17 | piora | evento: melhora |
| S1b | saturado | 180 | 4.74 | 17.07 | 486 | 0.000525 | 0.001029 | 0.001029 | — | 0.8476 | 0.7854 | -0.0622 | 0.0137 | 4.54 | piora | evento: melhora |
| S2a | saturado | 180 | 4.10 | 6.54 | 162 | 0.001829 | 0.000962 | 0.000962 | — | 0.8395 | 0.8633 | +0.0237 | 0.0136 | 1.75 | melhora | evento: piora |
| S2b | saturado | 180 | 4.10 | 10.94 | 342 | 0.001829 | 0.000962 | 0.000962 | — | 0.8395 | 0.8832 | +0.0437 | 0.0136 | 3.21 | melhora | evento: piora |
| S3 | saturado | 90 | 2.87 | 13.13 | 252 | 0.001325 | 0.000545 | 0.001641 | — | 0.7724 | 0.8594 | +0.0869 | 0.0137 | 6.35 | melhora | taxa: piora |
| MIX1 | misto | 90 | -26.10 | 3.02 | 76 | 0.000727 | 0.006429 | 0.006429 | 0.0641 | 0.8428 | 0.8733 | +0.0305 | 0.0133 | 2.29 | melhora | cor1_fora_da_saturacao: piora |
| MIX2 | misto | 90 | -26.10 | 21.85 | 562 | 0.000727 | 0.006429 | 0.006429 | 0.1448 | 0.8428 | 0.8153 | -0.0275 | 0.0137 | 2.01 | piora | monotonia: melhora |
| N1 | nao_saturado | 90 | -22.96 | -2.78 | 45 | 0.000727 | 0.004464 | 0.004464 | — | 0.8208 | 0.8637 | +0.0429 | 0.0104 | 4.11 | melhora | cor1_fora_da_saturacao: piora |

**Tolerância de nível** (por combo; a coluna `tol` é a maior das duas): `tol = 0,0079 + disc + 3·EP_média`.
`0,0079` = maior `|AUC média − AUC fluida|` do run selado r1 (`output/replication/celulas.csv`: 0,007801 nos 5.040
pares célula × combo, média das 5 sementes), arredondado PARA CIMA — efeito de Jensen sobre contagens Poisson perto da
quina `h = min`; `disc` = viés de
eventos inteiros, `(dAUC/dΔ²)·Δ²·k_max/K`, só no regime saturado; `EP_média` = Hanley & McNeil (1982) com
`N = 100.000` e `π = 0,2`, dividido por `√5`.

## Testes de unidade (rodam antes de qualquer número da grade)

- **KT1 — identidade com o código selado.** `k ≡ 14` e `K = 2.048` dão `⌊2.048/14⌋ = 146 = L` do r1: (a) a janela por
  tokens devolve exatamente os índices de `janela_ultimos(tempos, 146)` do r1 em vetores aleatórios com empates
  forçados; (b) com o mesmo gerador, os escores da simulação literal por tokens são **byte-idênticos** aos de
  `simular_literal` do r1 numa célula pequena.
- **KT2 — truncamento.** Sufixo máximo com custo `≤ K`; custo exatamente `K` cabe (`≤`, não `<`); o evento que estoura
  cai com todos os mais antigos (sem parcial, sem pular para caber); empate por ordem de entrada; histórico com custo
  total `≤ K` fica inteiro; histórico vazio devolve janela vazia.
- **KT3 — previsão.** A forma fechada do módulo reproduz, célula a célula, a `AUC(R)`, a `AUC(R∪S)` e o sinal da tabela
  analítica (mesmos números, tolerância de ponto flutuante).

## Critério de aprovação (pré-registrado)

O KAT-token **passa** se, e só se, KT1–KT3 estiverem verdes e:

- **KT-S (sinal):** nas 8 células, o sinal de `média(AUC(R∪S)) − média(AUC(R))` (5 sementes) é o previsto.
  **Uma discordância reprova.** Se, contra o desenho, `|ΔAUC previsto| < 3·EP` empírico (EP da diferença das médias,
  variância entre sementes com `ddof = 1`) em alguma célula, ela é reportada como empate e o KAT **reprova por falta
  de poder** — não passa por omissão.
- **KT-N (nível):** em cada uma das 16 combinações (célula, combo), `|média(AUC) − AUC fluida| ≤ tol` do combo.
  **Um estouro reprova.**

Reporta-se também, sem entrar no critério: sinal por semente, `Δ²` empírico recuperado (`2·Φ⁻¹(AUC)²`), média de
tokens ociosos na janela e fração de usuários com janela saturada, por combo.

**Leitura se reprovar.** KT-S reprovado numa célula discriminante ⇒ a generalização para `k` heterogêneo NÃO está
sustentada por simulação; o texto fica com "`k` homogêneo testado; heterogêneo analítico" e a frase da 2.3a não entra.
KT-N reprovado com KT-S aprovado ⇒ a forma fechada acerta o sinal, não o nível; o texto não usa o nível.

## Mutação (antes de valer)

Cópia descartável fora do repo (cópia descartável temporária). Cada mutante tem de morrer, e a **mensagem do
assert que o matou** é impressa e conferida contra o assert pretendido (lição do L07). Obrigatórios:
(1) ignora `k` (janela por contagem com `L = ⌊K/k̄⌋`); (2) `<` no lugar de `≤` no orçamento; (3) guarda os mais
antigos; (4) inclui o evento parcial que estoura; (5) pula o evento que estoura e tenta caber um mais antigo;
(6) empate invertido; (7) `ρ̄` ponderada por `λ` na tabela analítica; (8) `θ` com `W′` no lugar de `W_R`;
(9) ordem de sorteio diferente da do r1 (tem de quebrar KT1b); (10) `h = K/(Σλ·k̄)` na forma fechada do módulo.

## Selo r3

Config nova [selo privado, não distribuído] (nunca editada depois do selo): `environment` = `env.json`;
`code` = `displacement.py` (importado; hash inalterado) + módulo, runner e testes novos +
`code/token_kat_analytic_table.py`; `prereg` = pré-registro original + este adendo + grade + tabela analítica;
`data` = `output/kat_token/celulas.csv`; `scores` = `output/kat_token/resumo.json`. Build com
`--prev 9b15aa517651b9c4b1b1e894cdb465f8dc1aab76b5ad6eb27b88a8c2a64a4ff0` (chain_head r2); linha nova em
[cadeia privada de selos] com o elo assertado; [verificação adversarial privada] no r3; verify r1 e r2 continuam exit 0.
