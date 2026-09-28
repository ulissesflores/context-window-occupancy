# Pré-registro — adendo EXP (expoente de `d` na separabilidade por token; limite (a) do KAT-token)

> **Translation note (English).** Sanitized copy of a pre-registration document that was frozen in
> Portuguese before the code it specifies was written or run; the private original has sha256
> `9c9fce0674993e16fccbeee10ec3de20422532acf8352d72cb06908302524428`. Only the header, file paths and pointers to
> private records changed: paths written as `repo/…` in the original lost that prefix and name files of this
> repository (`code/`, `tests/`, `data/`, `output/`, `docs/`, `configs/`); other private paths were mapped to the
> file of this repository they were ported to, or replaced by bracketed placeholders (`[nota privada, não
> distribuída]` = private note, not distributed; `[verificação adversarial privada]` = private adversarial
> verification; `[registro privado de estado]` = private state log; `[selo privado, não distribuído]` = private
> provenance seal, not distributed; `[cadeia privada de selos]` = private seal chain); pointers to numbered entries
> of the private state log were removed. Where a literal path swap would have made a sentence false here, the
> minimum wording changed: a private file that this repository ports is cited as its "original privado" (private
> original) next to its sha256, the private code tree whose seals this family leaves untouched is called "código
> privado selado" (private sealed code), and "`repo/`" became "este repositório" (this repository). Wording,
> numbers and criteria are otherwise verbatim. Every sha256 quoted below refers to the private original of the
> file it names, except the grid (`data/exponent_grid.json`, `5a365aee…`) and the analytic table
> (`data/prereg/exponent_analytic_table.txt`, `4cd78db2…`), which this repository carries byte for byte. The
> mixed-regime token-KAT cells are `MIX1`/`MIX2` here as in the original. Glossary: pré-registro =
> pre-registration; adendo = addendum; desvio = deviation; grade = grid; tabela analítica = analytic table;
> gerador = generator; célula = cell; semente = seed; janela = window; leitor = reader; mutante = mutant;
> melhora/piora = improves/worsens; selo = provenance seal; critério de quebra = falsification criterion; "com a
> janela já saturada antes da fonte nova" = "with the window already saturated before the new source".

> **Status:** CONGELADO 2026-09-26 (sha256 registrado no [registro privado de estado] antes de existir qualquer código da família).
>
> **Artefatos congelados antes deste arquivo, nesta ordem (sha256 completos):**
>
> | Artefato | Caminho | sha256 |
> |---|---|---|
> | grade | `data/exponent_grid.json` (cópia byte a byte do original privado) | `5a365aee2307ee2fb568f2221bbdf252ffe7c9e2c389b4082de8c9f928a04dda` |
> | gerador da tabela analítica | original privado de `code/exponent_analytic_table.py` | `e98d707fb21ecc27ff9f22e9d4c0fcdee495b45eb18d377b68a7f2254b84306b` |
> | tabela analítica (stdout do gerador sobre a grade; duas execuções byte-idênticas) | `data/prereg/exponent_analytic_table.txt` (cópia byte a byte do original privado) | `4cd78db2bd03b558d522053945e052827d2c529b377f8b3fdd5880cba107556a` |
> | rascunho-fonte (§0, §1 l.90–333, §5 achados 1–8) | [nota privada, não distribuída] | `99641618b4471a54fb8974d789f3fb0eb0e42062a8ff0a71240817815987956e` |
>
> Caminhos sem prefixo = este repositório, com os nomes fixos do desenho do repositório [nota privada, não distribuída] (sha256
> `6fc3c6df953d1b3740d11dadf8ccf59029b142cf7327edab6df3791d26cba95b`; §Workflow B e apêndice A.1/A.2). A grade e a
> tabela analítica são artefatos de pré-registro, sem sorteio; nenhuma simulação de desfecho foi rodada sobre esta grade.
>
> **Marcas `[B-crit n]`** remetem à tabela de achados da §5 do rascunho-fonte (sha256 acima); os achados 1–8 cobrem esta
> família. Decisões operacionais seguidas: [registro privado de estado].
>
> **Não altera nenhuma folha selada:** pré-registro original `data/prereg/01-displacement-replication.md`
> (`b1563d973d090bc08a9dd7495f74264ce98c629b1d355bd45fe371f2ab815368`), adendo KAT `data/prereg/02-token-kat-addendum.md`
> (`6c2213caa487eedac7a78ce8b29951ac69eb2318c0167fdf76f72a0c369dce93`), desvios
> `data/prereg/03-token-kat-deviations.md` (`4ceba2bb20069f0215395b2fce991ddd3571a9be50b9fe9bc2763f00f2d36e15`)
> e desvios-26b `data/prereg/04-token-kat-deviations-b.md`
> (`e83f23aa3908446d8ab86250c88782cdf1efd55fd43fccb317e2eefb2ca909a5`). Células mistas do KAT são citadas pelo nome do
> repositório (MIX1: `λ_S = 0,6`; MIX2: `λ_S = 6`).
>
> **Mudanças declaradas em relação ao rascunho-fonte (nenhuma altera pergunta, previsão, critério ou célula):**
>
> 1. Grade: o rascunho [nota privada, não distribuída] (sha256
>    `8aa03c4be0c31d2f869131e93e4e1151e5e108cc2f002fdd36ed3b553e8d002a`) gravava 5 na chave `tag_r3` e trazia `_tag`
>    em PT; a congelada tem `tag = 5`, sem `tag_r3` `[B-crit 4]`, comentários (`_fonte`, `_custos`, `_desenho`, `_tag`)
>    em inglês e sem caminho privado (vai byte a byte para o repo; juiz de vazamento G5: exit 0) e três chaves de
>    critério de desenho acrescidas, para que o sha da grade cubra os critérios e não só as células:
>    `faixa_troca_baixo = [1.55, 1.65]`, `faixa_troca_alto = [2.45, 2.55]`, `vies_max_sobre_tolD = 0.25`. As 6 células
>    (ids, `bloco`, `familia`, `lado`, `T`, `R`, `S`) são idênticas às do rascunho (conferido por código). A chave
>    descritiva `_tag` fica na grade congelada (string no topo, em inglês; o gerador não a lê): desvio da letra da
>    decisão que mirava o `_tag` duplicado em PT do rascunho, aceito como aviso por decisão posterior registrada no
>    [registro privado de estado], que não recongela a grade por chave de comentário.
> 2. Ponto de troca do rival: a tabela congelada imprime o 1º ponto após a troca na grade de passo 0,0005 (porte literal
>    do rascunho) e a raiz exata (Brent); vale a **raiz exata a 3 casas**. Em EXP-D2 isso dá `p = 2,510` (raiz
>    2,510121), não 2,511 do rascunho (ponto 2,5105 da grade, arredondado); por consequência o intervalo report-only da
>    §1.9 para a família D é `[1,591; 2,510]`. Nenhum critério muda (2,510 segue na faixa `[2,45; 2,55]`).
> 3. Seções de selo (§0.2 e §1.14) REESCRITAS por decisão registrada no [registro privado de estado]: código, testes e saídas desta família nascem
>    só neste repositório; nenhum selo privado novo.
> 4. Referências em APA 7, copiadas do campo `apa7` de [nota privada, não distribuída]; entra Mann & Whitney
>    (1947), porque o texto usa a AUC de Mann–Whitney.
> 5. O gerador confere, além dos critérios da §1.7, as leituras de rivais (§1.8) e onde morre cada mutante de leitor
>    (§1.12), por assert nomeado.

## 0. Decisões transversais que valem para esta família

### 0.1 Um fluxo aleatório por família `[B-crit 1]`

Os quatro rascunhos usavam o mesmo tag `5` em `numpy.random.default_rng([semente, i_celula, i_combo, tag, i_bloco])`:
para o mesmo `(semente, índice, bloco)`, famílias diferentes leriam os mesmos bits, e os quatro veredictos ficariam
correlacionados sem declaração. Tags fixados (registrados no [registro privado de estado]):

| Família | Tag | Observação |
|---|---|---|
| EXP (expoente de `d`) | 5 | — |
| OCC (ocupação × taxa) | 6 | — |
| CMP (fusão, Corolário 4(b)) | 7 | `i_fluxo` no lugar de `i_combo` (0 = `R`; 1 = sorteio partilhado por `RS`/`RF`/`RP`) |
| C5 (cotas, Corolário 5) | 8 | só KNP3 e FIX1; KNP1, KNP2, NUL1 e DEC1 usam, de propósito e declarado, fluxos do KAT (tag 3) |

Tag 3 (r3) e o fluxo de três entradas do r1 ficam reservados. O teste de pinos de cada família assere o seu tag e que
ele difere de 3 e dos outros três.

### 0.2 Selo e prova de proveniência — reescrito por decisão registrada no [registro privado de estado] `[B-crit 2]`

O rascunho propunha "selo r5 com `--prev`" na cadeia privada; **vale o desenho do repo, não o selo privado.** Código de
simulação, testes e saídas desta família nascem SÓ neste repositório, quando o workflow B rodar (depois do workflow A verde).
A prova é `make_provenance.py` (build, depois `--verify` com exit 0), com folhas novas nos estágios correspondentes
de `configs/stages.json`:

| Estágio | Folhas novas da família EXP |
|---|---|
| `prereg` | grade `data/exponent_grid.json` (cópia byte a byte da grade congelada, mesmo sha256), tabela `data/prereg/exponent_analytic_table.txt`, pré-registro sanitizado `data/prereg/05-exponent-addendum.md` |
| `code` | runner partilhado `code/run_grid.py`, gerador portado `code/exponent_analytic_table.py`, testes `tests/test_exponent.py` |
| `data` | `output/exponent/celulas.csv` |
| `scores` | `output/exponent/resumo.json` |

Nada entra na [cadeia privada de selos]; nenhum [selo privado, não distribuído] novo; nenhum `--prev`; o G9
privado fica em 88 testes (cresce só a contagem de testes do repo); o contrato de regeneração G7 não muda (as saídas
desta família não têm contraparte selada no privado); os selos r1–r4 ficam intactos. O relatório de mutação é privado
(§1.12) e o repo cita o resultado só em `REPRODUCIBILITY.md`. A cópia da grade, da tabela e do pré-registro
sanitizado para este repositório e a emenda datada em `data/PREREGISTRATION.md` acontecem só depois do workflow A verde
([registro privado de estado]).

### 0.3 Limite comum, declarado uma vez `[B-crit 3]`

Com o gerador fixado (Poisson, `x ~ N(d_s·y, 1)`) e o leitor oráculo `Σ d_s(x_i − d_s/2)`, o expoente 2 de `d`, a
ponderação pela ocupação, a suficiência de `Σx` na fusão e a dominância usuário a usuário das cotas por `ρ` são
**identidades algébricas** do modelo. Nenhuma das quatro famílias pode falsificar essa álgebra. O que cada uma pode
falsificar: (a) a aproximação fluida (hipótese iii), e a previsão exata onde ela é usada; (b) a implementação literal
(janela, fusão, políticas, leitor). As regras rivais são regras de bolso, não mecanismos que o gerador realize: a
simulação só se comportaria como um rival se o código tivesse o defeito correspondente (leitor sem peso por `d`; janela
por contagem; evento fundido sem a soma). Consequência obrigatória em todo produto de texto: **"conferido por simulação
literal" = a forma fechada bate com a simulação literal**; proibido "estabelecido/medido empiricamente" para expoente,
peso, fator de fusão ou ordem de políticas.

### 0.4 Maquinário partilhado, perguntas separadas `[B-crit 4]` `[B-crit 6]`

As quatro perguntas são distintas e NÃO se fundem (vereditos independentes; um desfecho não arrasta o outro). O
maquinário, sim:

- EXP e OCC rodam pelo mesmo caminho (`run_token_kat._uma_tarefa` + `token_kat.avaliar_kat`, sem editar nada selado):
  **um único runner fino** `code/run_grid.py --grid <json> --out <dir>` serve às duas (escada ponytail: segundo
  uso concreto já existe). As grades novas guardam o tag na chave `tag`; o runner passa a `_uma_tarefa` o adaptador
  `{**grade, "tag_r3": grade.get("tag", grade.get("tag_r3"))}`, que aceita a grade nova (só `tag`) e a do KAT (só
  `tag_r3`, usada no OCCT1). **Nenhuma grade nova tem a chave `tag_r3`** (o rascunho EXP gravava 5 numa chave chamada
  `tag_r3`, nome que engana sobre o valor).
- Parâmetros repetidos entre famílias, declarados: `R ∪ S` de CMP1 (braço `RS`) = `R ∪ S` do KAT S1b; `R ∪ S` de CMP4
  (braço `RS`) = `R ∪ S` do KAT S2b = mistura de KNP2 do C5; mistura de KNP1 = `R ∪ S` do KAT S1a. Só o C5 reusa os
  DADOS selados do KAT (âncoras); o CMP reusa só como teste de identidade (FU1c), fora do veredito.
- Observação do congelamento (conferida por código contra `data/kat_token_grid.json`): o `R` de EXP-C1 e EXP-C3
  (`A` = 1,2; 0,120; 14) é o `R` do KAT S1a/S1b, e o `R` de EXP-C2 e EXP-C4 (`A` = 0,4; 0,230; 55) é o do KAT S2a/S2b;
  com tag 5, os sorteios são independentes dos selados. Nenhum dado do KAT entra no veredito EXP.

### 0.5 Referências — fechado (decisão registrada no [registro privado de estado]; achado 20) `[B-crit 5]`

Norma: APA 7 (D2). Fonte única: [nota privada, não distribuída] (sha256
`7e8ed08ff21c773917f06eec03c13c23cb0aa949f501fc480c0d860c09fad6bd`), linhas verificadas por código a partir dos crus do
Crossref em [nota privada, não distribuída]. Neyman–Pearson mantém o prefixo "IX." do título como publicado. Lista
desta família na §1.15.

### 0.6 Tempo (viabilidade)

Base medida: KAT = 1,476·10⁹ eventos gerados em 76 s com 8 processos (1,94·10⁷ eventos/s de parede). Recontagem de
eventos gerados (N = 100.000, 5 sementes):

| Família | Eventos gerados | Parede estimada (8 processos) | Maior simulação isolada (célula × combo × semente) |
|---|---|---|---|
| EXP | 1,962·10⁹ | ~101 s | ~3 s |
| OCC | 4,123·10⁹ | ~212 s | ~3 s |
| CMP | 1,676·10⁹ (+ fusão, ~+50%) | ~130–150 s | ~5 s |
| C5 | 8,42·10⁸ (+ 5–6 políticas, fator ~2) | ~90–120 s | ~3 s |

Todas muito abaixo de 5 min por simulação; o conjunto cabe em ~10 min de parede. Estimativas por escala linear,
**não medições**; pico de memória do CMP (~0,7 GB/processo com 576 eventos/usuário) cabe com 8–12 processos na máquina
de 14 CPUs. A linha EXP é recalculada pela tabela congelada (`1.962e+09`, `~101 s`).

## 1. EXP — expoente de `d` na separabilidade por token (limite (a))

> Fecha o limite (a) dos desvios do KAT (itens 4–5): "o KT-N é frouxo e confere a forma fluida, não discrimina o
> expoente de `d`". Não altera o pré-registro original, o adendo KAT, os desvios nem os desvios-26b (sha256 no
> cabeçalho). O sha256 deste arquivo, da grade, do gerador e da tabela analítica vai ao [registro privado de estado] antes de existir qualquer
> código da família no repo: `code/run_grid.py`, `code/exponent_analytic_table.py`,
> `tests/test_exponent.py`, `data/exponent_grid.json`, `output/exponent/`. O gerador privado
> (original de `code/exponent_analytic_table.py`) já existe e é artefato de pré-registro (aritmética sem sorteio), congelado
> junto. Resultado em `output/exponent/resumo.json` e no bloco EXP de `output/results.json`; desvio, se
> houver, em arquivo próprio datado.

### 1.1 Pergunta

**Com a janela já saturada antes da fonte nova** (`T·W_R ≥ K`, a condição do Corolário 1) `[B-crit 7]`: nas células em
que a regra LINEAR em `d` (valor por token `d/k`) e a CÚBICA (`d³/k`) preveem o sinal OPOSTO ao da teoria
(`ρ = d²/k`), a simulação literal por orçamento de tokens segue o sinal de `d²/k`? E, separadamente: o que a grade
identifica é o expoente de `d` sozinho ou só a razão entre o expoente de `d` e o de `k`?

As 8 células do KAT refutaram a regra por evento, a `ρ̄` pela taxa, o Corolário 1 fora da saturação e a monotonia, mas
foram desenhadas contra essas regras, não contra o expoente: na leitura "Corolário 1 aplicado sem checar o regime",
`d/k` e `d²/k` dão o mesmo sinal nas 8 (desvios, item 5).

### 1.2 O que a teoria prevê (forma fechada; especificação do outline, bloco 2.3a)

Forma fluida: `W = Σ λ_s k_s`, `h = min(T, K/W)`, `Δ² = h·Σ λ_s d_s²`, `AUC = Φ(√Δ²/√2)`.
Com a janela já saturada antes da fonte nova, Proposição 1 e Corolário 1: `Δ² = K·Σ φ_s ρ_s`, `ρ_s = d_s²/k_s`, e adicionar `S` aumenta a AUC se e
somente se `ρ_S > ρ̄ = Σ_R λ_r d_r² / W_R`.

**De onde vem o expoente 2.** Sob `x ~ N(d_s·y, 1)` e o leitor ótimo (razão de verossimilhança, hipótese iv; Neyman &
Pearson, 1933), a contribuição de cada evento é `d_s(x − d_s/2)`: média `±d_s²/2` por classe, variância `d_s²`; somada
na janela, `Δ² = Σ n_s d_s²`. **O expoente 2 é identidade algébrica do modelo gerador com o leitor ótimo, não fato
empírico a descobrir** (ver §0.3).

Limiares nas duas famílias (ambas com `R` já saturada):

- **Família C** (`R` de fonte única `A`, `S` com custo diferente; `κ = k_S/k_A`, `r = d_S/d_A`): melhora se e só se `r² > κ`.
- **Família D** (custo homogêneo `k = 14`; `R` com uma fonte rara e forte e uma frequente e fraca; pesos
  `w_r = λ_r/Σ_R λ`): melhora se e só se `d_S > μ_2`, com `μ_p = (Σ_R w_r d_r^p)^(1/p)`.

### 1.3 Hipóteses rivais (família que só troca expoentes)

**Rival `H(p, q)`:** valor por token `d^p/k^q`, comparado com a sua média ponderada pela ocupação; com `q = 1` equivale a
`V_p = h·Σ λ_s d_s^p` com o MESMO `h = min(T, K/W)` da teoria. A teoria é `H(2, 1)`. Nomeados: `d/k = H(1, 1)`,
`d³/k = H(3, 1)`, `d/√k = H(1, ½)`, `d²/k² = H(2, 2)`.

- **Por que `d/k` é um rival real.** O Gini de um evento (`2·AUC − 1`, `AUC = Φ(d/√2)`) vale `≈ d/√π` para `d` pequeno:
  ordenar fontes por "ganho de Gini por token" é a regra linear. Realização mecânica: o leitor que soma os atributos SEM
  pesá-los por `d_s` tem separação `(Σ n_s d_s)²/Σ n_s`; com custo homogêneo, adicionar `S` melhora esse leitor se e só
  se `d_S > μ_1` — a regra linear. É o mutante-controle positivo (§1.12). **Nota `[B-crit 3]`:** é esse o sentido exato
  do "poder discriminante" deste teste: a grade detecta um pipeline cujo leitor NÃO pesa por `d` (ou pesa por outra
  potência); não detecta nada sobre o expoente fora do modelo gaussiano com leitor ótimo.
- **Por que duas famílias.** Na família C o limiar do rival é `r^p > κ^q`: identifica só a razão `e = p/q` (`d/√k`
  passaria em todas as C, `e = 2`). Na família D `q` se cancela e o limiar é `d_S^p > Σ w_r d_r^p`: identifica `p`
  sozinho (`d²/k²` passaria em todas as D). Juntas, refutam os quatro rivais nomeados.
- **Direções.** Pela desigualdade das médias de potência (`μ_1 < μ_2 < μ_3` com `d_r` distintos), na família D o lado
  baixo só admite teoria PIORA e rival MELHORA, e o lado alto o contrário — desbalanço imposto pela matemática. Na
  família C cada lado tem uma célula em cada direção. Total: 3 MELHORA e 3 PIORA.
- **Por que sinal e não ordem de `ΔAUC`.** O rival não tem modelo de magnitude (prevê um valor `V`, não AUC); o sinal de
  `ΔV` é invariante a qualquer ligação monótona entre `V` e AUC.

### 1.4 Achado prévio — POST HOC, NÃO confirmatório — sobre os sinais já selados no KAT

Com o rival `H(p, 1)` coerente com a teoria (mesmo `h = min`), os 8 sinais selados do KAT (original privado,
sha256 `389884f760648e851c5a378b95b23930e5bd52bffcfedef5089a0f29f94fa994`; no repo, `output/kat_token/resumo.json`,
com MIX1/MIX2) já excluem `p ≤ 1,39` e `p ≥ 3,41`: o lado baixo SÓ pela célula MIX2 (exclui `p ∈ [0,25; 1,39]`), o lado
alto por MIX1 (`p ≥ 3,41`) e por S1a/S1b (`≥ 3,93`) e S2a/S2b (`≥ 3,77`); S3 e N1 não excluem nada. **Reproduzido pela
crítica** ([verificação adversarial privada], sha256
`c4413a7be352cb2f2307bbe6ab8c55314359408c38bf3734b41303d8f7c62fb3`, bloco 1, varredura `p ∈ [0,25; 5]`; saída
[verificação adversarial privada] (`run1` = `run2`), sha256 `7a33da0912f4604c3781c0f81e58a6d9abaad3ed4f2efb1a3e6799559090451c`, onde as
células mistas aparecem pelos nomes privados). Conferido por código no congelamento: os sete limites acima batem com essa
saída. Três qualificadores obrigatórios: (1) rival definido DEPOIS dos dados; (2) lado baixo sustentado por UMA célula,
em regime misto; (3) não pré-registrado como teste de expoente. O item 5 dos desvios é verdadeiro na leitura "Corolário
1 sem checar o regime" e falso na leitura coerente em uma célula. Vai em nota datada (feita depois pela sessão
principal); **nunca editar os desvios** (folha do selo r4). Este achado não entra em nenhum critério desta família.

### 1.5 O que NÃO se afirma (escopo)

- A simulação **não descobre** o expoente (§0.3). Confere que o pipeline literal (truncamento por orçamento de tokens,
  chegadas Poisson, eventos inteiros, escore do oráculo, AUC de Mann–Whitney (Mann & Whitney, 1947)) realiza a
  contabilidade `d²` e que a aproximação fluida (iii) não a distorce, nas células em que as regras rivais preveem o
  oposto.
- Ilustrativo, ordens de grandeza; **não é replicação do nuFormer**; nada sobre o `ρ_s` real (hipótese vi). Do case:
  `K = 2.048` e `k ∈ {14, 55}` (entradas E1).
- Só com a janela já saturada antes da fonte nova. Regime misto sem célula dedicada.
- **Não** testa ocupação × taxa (limite (b)): nas 6 células as duas ponderações coincidem por construção. **Não** cobre
  Corolários 4(b) e 5.
- **Resolução:** separa `p` e `p/q` de valores fora de `[1,60; 2,50]`; dentro dessa faixa (ex.: 1,8 ou 2,3) não
  discrimina.
- **Produto** `[B-crit 8]`: no máximo uma oração, com destino padrão `docs/THEORY.md` (não os ~170 palavras do
  corpo), porque o conteúdo é verificação de implementação, não resultado novo (ver §1.10). Nenhum número deste teste
  vai ao corpo.
- Sinal na contagem e no tempo de chegada segue excluído (hipótese v).

### 1.6 Modelo gerador (herda o KAT sem mudança)

`π = 0,2`; eventos da fonte `s` por Poisson de taxa `λ_s` em `T` dias, independentes de `y`; `x ~ N(d_s·y, 1)`; leitor =
oráculo `score = Σ_visíveis d_s·(x_i − d_s/2)`; AUC de Mann–Whitney com postos médios; janela = maior sufixo de eventos
mais recentes com custo `≤ K = 2.048`, só eventos inteiros, empate por ordem de entrada (regra fixada pelos testes
KT1/KT2). Ordem de sorteio = a de `simular_literal_tokens`. Fluxo
`numpy.random.default_rng([semente, i_celula, i_combo, 5, i_bloco])` — **tag 5, exclusivo desta família** `[B-crit 1]`;
`i_combo` = 0 para `R`, 1 para `R ∪ S`; blocos de 10.000 usuários; `R` e `R ∪ S` em fluxos independentes.

### 1.7 Grade (fixada aqui)

Fonte única: a grade congelada (original privado, sha256
`5a365aee2307ee2fb568f2221bbdf252ffe7c9e2c389b4082de8c9f928a04dda`), copiada BYTE A BYTE para `data/exponent_grid.json`
depois do workflow A verde; chave `tag = 5` e SEM chave `tag_r3` `[B-crit 4]` (diferenças em relação ao rascunho da
grade no cabeçalho, item 1). `K = 2.048`; `N = 100.000` por (célula, combo, semente); sementes `0..4`; `T = 180`;
6 células × 2 combos × 5 sementes = **60 simulações**.

| célula | família | lado | `R` (λ, d, k) | `S` (λ, d, k) | limiar da teoria | ponto de troca do rival |
|---|---|---|---|---|---|---|
| EXP-C1 | C | baixo | A (1,2; 0,120; 14) | C (1,0; 0,282; 55) | `r = 2,350 > √κ = 1,982`: melhora | `p/q = 1,601` |
| EXP-C2 | C | baixo | A (0,4; 0,230; 55) | C (2,5; 0,098; 14) | `r = 0,426 < √κ = 0,505`: piora | `p/q = 1,604` |
| EXP-C3 | C | alto | A (1,2; 0,120; 14) | C (1,0; 0,207; 55) | `r = 1,725 < 1,982`: piora | `p/q = 2,510` |
| EXP-C4 | C | alto | A (0,4; 0,230; 55) | C (2,5; 0,133; 14) | `r = 0,578 > 0,505`: melhora | `p/q = 2,498` |
| EXP-D1 | D | baixo | A (0,18; 0,294; 14) + B (1,02; 0,029; 14) | C (1,8; 0,097; 14) | `d_S = 0,097 < μ_2 = 0,1170`: piora | `p = 1,591` |
| EXP-D2 | D | alto | A (0,18; 0,294; 14) + B (1,02; 0,029; 14) | C (1,8; 0,139; 14) | `d_S = 0,139 > μ_2 = 0,1170`: melhora | `p = 2,510` (ver nota) |

Ponto de troca = raiz exata a 3 casas (Tabela 3 da tabela congelada; na família C coincide com `ln κ/ln r` a `10⁻⁶`).
**Nota (divergência declarada no congelamento):** o rascunho dava `p = 2,511` para EXP-D2, que é o 1º ponto após a troca
na grade de passo 0,0005 (2,5105) arredondado; a raiz exata é 2,510121. Nas outras cinco células o rascunho já trazia a
raiz exata a 3 casas (em EXP-C1 a grade dá 1,6015 e a raiz, 1,601418).

Família C: `κ = 55/14 = 3,9286` (C1, C3) ou `14/55` (C2, C4); `d_S = d_A·κ^(1/e*)` com `e* = 1,6` (baixo) e `2,5`
(alto), 3 casas. Família D: pesos de taxa `(0,15; 0,85)`, `d_B = 0,1·d_A`, `d_A` para `AUC(R) ≈ 0,84`;
`μ_1 = 0,0688`, `μ_1,6 = 0,0975`, `μ_2 = 0,1170`, `μ_2,5 = 0,1386`, `μ_3 = 0,1565`. Bracket `(1,6; 2,5)` simétrico em log
em torno de 2.

**Critérios de desenho (conferidos por código antes de simular; exit ≠ 0 com assert nomeado se falhar):** `R` e
`R ∪ S` saturadas a `z ≥ 4`; `≤ 600` eventos por usuário; `|ΔAUC fluido| ≥ 2,5·tolΔ` E `≥ 1,2·tol de nível do KAT`;
sinal da teoria oposto ao de `d/k` no lado baixo e ao de `d³/k` no lado alto; ponto de troca em `[1,55; 1,65]` (baixo) e
`[2,45; 2,55]` (alto); viés previsto `|ΔAUC exato − ΔAUC fluido| ≤ 0,25·tolΔ`; família C com `R` de fonte única e
`k_S ≠ k_A`; família D com `k = 14` em todas as fontes e `R` com duas fontes de `d` diferente. Todos os limiares são
chaves da grade congelada (`z_minimo_regime`, `eventos_max_por_usuario`, `margem_tolD`, `margem_tol_nivel`,
`faixa_troca_baixo`, `faixa_troca_alto`, `vies_max_sobre_tolD`). O gerador congelado assere também: tag 5 sem `tag_r3`
e diferente de 3, 6, 7, 8; ids exatamente os 6 acima; sinal da forma fechada = Corolário 1 = limiar da família (`r²`
contra `κ`; `d_S` contra `μ_2`); 3 melhora e 3 piora; as leituras de rivais da §1.8; e onde morre cada mutante de leitor
(§1.12). **Estado:** exit 0 sobre a grade congelada (última linha da tabela: `CRITÉRIOS DE DESENHO: todos passaram`).
Controle negativo feito no congelamento, em cópias descartáveis: grade com tag 3, com `tag_r3`, com `k_S = 55` em
EXP-D1, com `d_S` de EXP-C1 em 0,24 e com a faixa alta estreitada para `[2,45; 2,50]` saem, cada uma, com exit 1 e assert
nomeado.

### 1.8 Tabela analítica — calculada ANTES de simular (sem sorteio)

Gerador: original privado de `code/exponent_analytic_table.py` (sha256 `e98d707fb21ecc27ff9f22e9d4c0fcdee495b45eb18d377b68a7f2254b84306b`),
que porta sem mudança de resultado a aritmética de `tabela_final.py`, `desenho_expoente.py`, `busca_celulas.py` e
`mutantes_nivel.py` do scratch persistido [nota privada, não distribuída] e só importa (nunca edita) as
primitivas do original privado de `code/token_kat_analytic_table.py` (folha selada, sha256
`2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`). Duas execuções byte-idênticas (`cmp`); saída
congelada (original privado, byte a byte igual a `data/prereg/exponent_analytic_table.txt`; sha256
`4cd78db2bd03b558d522053945e052827d2c529b377f8b3fdd5880cba107556a`), cuja 1ª linha é
`grade sha256 5a365aee… · K = 2048 · N = 100000 · sementes = 5 · tag = 5 · …`; saída limpa no juiz de vazamento (G5, exit 0).
No repo, o workflow B porta o gerador para `code/exponent_analytic_table.py` (importa `token_kat_analytic_table` no
lugar do módulo privado) e grava `data/prereg/exponent_analytic_table.txt`, que tem de sair **byte a byte igual**
à tabela congelada (a grade vai byte a byte, logo a 1ª linha coincide).

"Exato" = AUC da população infinita por enumeração da composição da janela saturada (marcas iid da superposição
Poisson), `AUC = E[Φ(√(Δ²_i + Δ²_j)/2)]`. **O critério usa a previsão FLUIDA**; o exato é critério de desenho e coluna
report-only. **Conferido pela crítica:** z, eventos, AUC fluidas, ΔAUC, `tolΔ`, razões, sinais dos quatro rivais e
pontos de troca (dentro do passo 0,00225 da varredura da crítica, que imprime o ponto da grade anterior à troca) batem
com o recálculo independente. **Conferido no congelamento, por código:** 155 números e 48 rótulos
(sinais, família, lado, sentido) das tabelas e textos analíticos da §1 do rascunho contra a grade e a tabela congeladas;
única divergência, o ponto de troca de EXP-D2 (nota da §1.7), que se repete no intervalo da §1.9.

| célula | z(R) | z(R∪S) | eventos/usuário | AUC(R) | AUC(R∪S) | ΔAUC fluido | ΔAUC exato | EP_Δ | tolΔ | ΔAUC/tolΔ | tol nível KAT | ΔAUC/tol nível | teoria | d/k | d³/k | d/√k | d²/k² |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-C1 | 4,74 | 14,20 | 396 | 0,8476 | 0,8800 | +0,0324 | +0,0313 | 0,00108 | 0,0052 | 6,19 | 0,0132 | 2,45 | melhora | piora | melhora | melhora | piora |
| EXP-C2 | 4,10 | 14,85 | 522 | 0,8395 | 0,8162 | −0,0233 | −0,0235 | 0,00118 | 0,0055 | 4,21 | 0,0137 | 1,71 | piora | melhora | piora | piora | melhora |
| EXP-C3 | 4,74 | 14,20 | 396 | 0,8476 | 0,8228 | −0,0248 | −0,0257 | 0,00116 | 0,0055 | 4,53 | 0,0137 | 1,82 | piora | piora | melhora | piora | piora |
| EXP-C4 | 4,10 | 14,85 | 522 | 0,8395 | 0,8608 | +0,0213 | +0,0214 | 0,00112 | 0,0054 | 3,97 | 0,0136 | 1,56 | melhora | melhora | piora | melhora | melhora |
| EXP-D1 | 4,74 | 16,94 | 540 | 0,8414 | 0,8164 | −0,0250 | −0,0245 | 0,00118 | 0,0055 | 4,52 | 0,0113 | 2,22 | piora | melhora | piora | melhora | piora |
| EXP-D2 | 4,74 | 16,94 | 540 | 0,8414 | 0,8680 | +0,0266 | +0,0274 | 0,00110 | 0,0053 | 5,01 | 0,0112 | 2,39 | melhora | melhora | piora | melhora | melhora |

Leitura dos rivais: `d/k` oposto em C1, C2, D1; `d³/k` oposto em C3, C4, D2; `d/√k` só em D1; `d²/k²` só em C1 e C2 —
as duas famílias são necessárias. A tabela congelada traz ainda, por célula, a ocupação da fonte nova `φ′_S`, `ρ_S`,
`ρ̄` (ocupação), o viés `ΔAUC exato − ΔAUC fluido` (Tabela 1), os sinais dos leitores lineares sem peso e com peso `d²`
(Tabela 2), os limiares com `κ` e `ln κ/ln r` e as médias `μ_p` (Tabela 3) e os mutantes de leitor (Tabela 4).

### 1.9 Métrica, tolerância e critério de aprovação

- **Métrica:** `Δ̄ = média(AUC(R∪S)) − média(AUC(R))` nas 5 sementes; `EP_emp = √(var_RS/5 + var_R/5)`, `ddof = 1`.
  `EP_Δ` de desenho = Hanley & McNeil (1982) com `N = 100.000`, `π = 0,2`, por combo, em quadratura, `/√5` (congelado).
- **Tolerância:** `tolΔ = 0,0020 + 3·EP_Δ` (por célula, congelada). `0,0020` = maior `|dif_emp − dif_prev|` das 8
  células do KAT (0,001906, S1a; conferido por código contra o `resumo.json` selado) arredondado para cima; ~0,0009 disso
  é sistemático e o resto é ruído a ~1 EP, de modo que somar `3·EP_Δ` conta o ruído duas vezes — **conservador de
  propósito**; o poder vem das margens de 4–6 `tolΔ`. Tolerância fixa, não recalculada dos dados.
- **Critério (passa se, e só se, EX1–EX5 verdes e):**
  - **EXS (sinal):** nas 6 células, sinal de `Δ̄` = o da teoria. Uma discordância reprova. Se
    `|ΔAUC previsto| < 3·EP_emp`, empate: reprova por falta de poder.
  - **EXN (nível da diferença):** nas 6 células, `|Δ̄ − ΔAUC fluido| ≤ tolΔ`. Um estouro reprova. É critério, não
    relatório: é ele que mata os mutantes de peso do leitor que preservam o sinal.
- Report-only: sinal por semente; `|Δ̄ − ΔAUC exato|` em EP; nível por combo com a tolerância do KAT; `Δ²` recuperado
  (`2·Φ⁻¹(AUC)²`); ociosos e fração saturada; e, se EXS passar, o intervalo implicado `p ∈ [1,591; 2,510]` (D; o
  rascunho dizia 2,511, ver nota da §1.7) e `p/q ∈ [1,604; 2,498]` (C) — **para o pipeline**, não para o mundo (§0.3).

### 1.10 Critério de quebra e o que muda no artigo

Uma reprovação **não falsifica Neyman–Pearson**: falsifica que o pipeline literal realiza a contabilidade `d²` (defeito
do leitor ou do truncamento) ou que (iii) preserva o sinal na célula. Leituras fixadas antes do dado: EXS reprovado em
C1 ou C2 -> o simulado se comporta como razão `p/q ≤ 1,6`; em D1 -> como `p ≤ 1,6` (assinatura do leitor sem peso por
`d`); em C3, C4 ou D2 -> expoente acima de 2,5. Qualquer um: nada entra no texto, o limite (a) segue declarado,
investigação da célula antes de qualquer texto. EXN reprovado com EXS aprovado -> sinal certo, magnitude da diferença
errada; o texto não usa magnitude. Empate -> reprova por poder.

| desfecho | texto | fórmula | tabela | figura | ledger / repo |
|---|---|---|---|---|---|
| **passa** (EXS 6/6 e EXN 6/6) | `[B-crit 7]` `[B-crit 8]` Oração licenciada, destino padrão `docs/THEORY.md`: *"com a janela já saturada antes da fonte nova, a contabilidade `ρ_s = d_s²/k_s` do leitor ótimo (expoente 2 analítico, sob `x` gaussiano) é preservada pela janela literal por orçamento de tokens em células em que as regras `d/k` e `d³/k` preveem o sinal oposto, com custo heterogêneo e homogêneo; conferido por simulação literal"*. No corpo, só por decisão do operador e dentro dos ~170. Proibido "expoente medido/estabelecido empiricamente" e "expoente 2 conferido" sem "do leitor ótimo". Outline: linha de limites passa a "contabilidade `d²` conferida contra rivais `d/k`, `d³/k` (EXP)" por desvio datado, nunca editando os desvios selados | nenhuma (`ρ = d²/k` fica) | tabela das 6 células no `docs/THEORY.md` (EN) | nenhuma (Fig. 3 intocada) | linha `[EXP-expoente-resultado]` no ledger; nota datada sobre o item 5 dos desvios; repo: emenda datada em `data/PREREGISTRATION.md`, bloco EXP em `output/results.json`, `tests/test_paper_numbers.py` assere "EXS 6/6, EXN 6/6", folhas novas em `configs/stages.json` (§0.2) com `make_provenance.py --verify` exit 0; cresce só a contagem de testes do repo; G7 não muda; G9 privado fica 88 |
| **reprova EXS** | 2.3a fica com "expoente 2 analítico (leitor ótimo, Neyman–Pearson, sob `x` gaussiano)"; limite (a) segue | nenhuma | nenhuma | nenhuma | desvio datado com a célula e a leitura acima; ledger com o negativo; `output/results.json` registra a reprovação |
| **reprova só EXN** | a oração entra sem alusão a magnitude | nenhuma | `docs/THEORY.md` mostra o sinal, não o nível | nenhuma | desvio datado; ledger "sinal conferido, nível da diferença não" |

O gate de redação (D10 do desenho do repositório, [nota privada, não distribuída]) só abre com o laudo de impacto do Workflow B em disco.

### 1.11 Testes de unidade (antes de qualquer número da grade)

Em `tests/test_exponent.py`, escritos e vermelhos antes do runner (TDD):

- **EX1 — pinos da grade.** sha256 de `data/exponent_grid.json` = `5a365aee2307ee2fb568f2221bbdf252ffe7c9e2c389b4082de8c9f928a04dda`;
  `z ≥ 4` nos dois combos; `≤ 600` eventos; família C = fonte única e `k_S ≠ k_A`; família D = `k = 14` e duas fontes em
  `R`; `grade["tag"] == 5`, `5 ∉ {3, 6, 7, 8}` e ausência da chave `tag_r3` `[B-crit 1]` `[B-crit 4]`; ids exatamente
  `{EXP-C1, EXP-C2, EXP-C3, EXP-C4, EXP-D1, EXP-D2}` e nenhum casa com a regra de vazamento.
- **EX2 — previsão.** A tabela analítica reproduz AUC fluidas e sinais (contra `token_kat.auc_fluida`); `d/k` oposto em
  C1, C2, D1; `d³/k` em C3, C4, D2; ponto de troca dentro das faixas; o stdout de `code/exponent_analytic_table.py`
  é byte a byte `data/prereg/exponent_analytic_table.txt`.
- **EX3 — identificação.** `d/√k` com o sinal da teoria nas 4 C e oposto em D1; `d²/k²` oposto em C1 e C2 e igual nas D.
- **EX4 — reuso fiel.** O `auc` do runner partilhado `code/run_grid.py` (via adaptador) = `auc_mann_whitney` dos
  escores de `simular_literal_tokens` chamada à mão com `default_rng([semente, i_celula, i_combo, 5, i_bloco])`, numa
  célula pequena.
- **EX5 — critérios.** Linhas fabricadas: discordância reprova; empate reprova; EXN usa valor absoluto e a `tolΔ`
  congelada da célula (não a do KAT).

Pytest sempre com `--color=no`.

### 1.12 Mutação (antes de valer)

Harness PRIVADO [verificação adversarial privada], sobre cópia descartável do repo fora dele (cópia descartável temporária; nunca dentro
deste repositório); relatório [verificação adversarial privada]; o repo cita o resultado só em
`REPRODUCIBILITY.md`. Cada mutante tem de morrer e a **mensagem do assert que o matou** é impressa e conferida
(`--color=no`). Onde cada um morre foi calculado por aritmética fluida (Tabela 4 da tabela congelada; origem
[nota privada, não distribuída]):

1. **Leitor sem peso por `d`** (`score = Σ x_i`) — controle positivo: morre por SINAL em EXP-D1 (previsto `+0,0465` contra
   `−0,0250`) e por EXN nas outras 5.
2. **Leitor com peso `d²`** — mesmo sinal da teoria nas 6; morre por EXN nas 6, com folga em EXP-D1 (`0,0246` contra
   `tolΔ = 0,0055`) e EXP-C2 (`0,0186`); em EXP-C3 no limite (`0,0055` contra `0,0055`; desvio/tolΔ = 1,00 na tabela
   congelada): não contar com ela.
3. **Leitor com peso `√d`** — morre por EXN em EXP-D1 e EXP-D2 (sobrevive nas C: registrado).
4. Forma fechada com `d` no lugar de `d²` — morre no EX2.
5. Tag 3 ou tag de outra família (6, 7, 8) — morre no EX1 `[B-crit 1]`.
6. EXN sem valor absoluto — morre no EX5.
7. Célula D com `k_S = 55` — morre no EX1.
8. Grade com a chave `tag_r3` no lugar de `tag` — morre no EX1 `[B-crit 4]`.

**Margens finas (Tabela 4 da tabela congelada):** morte por EXN com desvio/tolΔ < 1,5 não é garantida sob ruído — sem
peso em EXP-C4 (1,14), peso `d²` em EXP-C1 (1,32) e em EXP-C3 (1,00). Cada mutante de leitor vale pela morte robusta:
1 — sinal em EXP-D1 (12,92); 2 — EXN em EXP-D1 (4,45) e EXP-C2 (3,36); 3 — EXN em EXP-D1 (1,66) e EXP-D2 (2,73). O
harness assere que o mutante morre, não a célula exata em que morre.

Os mutantes 1–3 editam o leitor, que vive em `code/token_kat.py` (porte da folha selada privada):
só na cópia descartável.

### 1.13 Funções reusadas (importadas; nenhuma editada) e arquivos novos

Nomes do repo; identificadores Python verbatim do privado (desenho do repositório [nota privada, não distribuída], A.1); `code/` sem `__init__.py`, entra no
`sys.path` (nunca `import code`). Entre parênteses, o sha256 da folha selada do original privado:

- `code/run_token_kat.py` (original privado, `fe1b61cbee6ba6b8a4628ddaa742f820f4120b4b4adf48f71b17a5669a803efc`):
  `_uma_tarefa` (via o adaptador do runner partilhado, §0.4) e `tolerancias(grade)` (report-only).
- `code/token_kat.py` (original privado, `b70c6a2e729d3b6ecd58b59dc79c9e74697fcd6ce51b606e170b540497c245af`):
  `carregar_grade`, `fontes_da_celula`, `simular_literal_tokens`, `delta2_fluido`, `auc_fluida`, `avaliar_kat` (EXS = o
  seu `KT_S`, com a regra de empate; EXN sai de `dif_empirica`/`dif_prevista` do `por_celula`).
- `code/displacement.py` (original privado, `616b2445a6479f1fde7c1ff6d980dca12887be9743633484bfad21925b36a4ec`):
  `auc_mann_whitney`, `se_hanley_mcneil`, `PI`.
- `code/token_kat_analytic_table.py` (original privado, `2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`):
  só `fontes`, `W`, `delta2`, `auc`, `z_saturacao`, `ep_hanley_mcneil`, `tolerancia` (não `analisar`/`conferir`: o
  dicionário de regras ingênuas é fechado e daria `KeyError` nos rivais novos).
- Saídas seladas do KAT no repo: `output/kat_token/celulas.csv` e `resumo.json` (células mistas MIX1/MIX2; o sha do
  arquivo difere do privado `aea196a288494455720aa8117780836942632cc36827510fd01c8468b37ceae6`, logo teste de identidade
  compara as LINHAS da célula, não o sha do arquivo). Não entram no veredito EXP.

Arquivos novos, todos no repo (workflow B): `data/exponent_grid.json`, `code/run_grid.py` (partilhado com OCC),
`code/exponent_analytic_table.py`, `data/prereg/exponent_analytic_table.txt`, `tests/test_exponent.py`,
`output/exponent/` (`celulas.csv`, `resumo.json`), `data/prereg/05-exponent-addendum.md`, bloco EXP em
`output/results.json`, emenda datada em `data/PREREGISTRATION.md`. No privado, só o gerador já congelado
(original de `code/exponent_analytic_table.py`) e o harness de mutação [verificação adversarial privada] (fora de todo glob selado:
os selos cobrem [verificação adversarial privada] e, em `tests/`, `test_displacement*.py` e os `test_token_kat*.py`).
Nenhum arquivo novo no código privado selado.

### 1.14 Selo e tempo — reescrito por decisão registrada no [registro privado de estado] `[B-crit 2]`

Sem selo privado: a prova é a do repo (§0.2). Estágios de `configs/stages.json` que recebem folhas desta família:
`prereg` = `data/exponent_grid.json` + `data/prereg/exponent_analytic_table.txt` +
`data/prereg/05-exponent-addendum.md`; `code` = `code/run_grid.py` + `code/exponent_analytic_table.py` +
`tests/test_exponent.py` (os módulos reusados já estão selados no repo, hash inalterado); `data` =
`output/exponent/celulas.csv`; `scores` = `output/exponent/resumo.json`. `make_provenance.py` build e
`--verify` exit 0 depois do run; nenhum `--prev`, nenhum [selo privado, não distribuído], nada na
[cadeia privada de selos]; G9 privado fica 88; G7 não muda; r1–r4 intactos. O relatório de mutação fica no privado.

Tempo: `1,962·10⁹` eventos gerados (conferido; tabela congelada) -> **~101 s** com 8 processos (escala linear sobre o
KAT; estimativa). Mutantes de leitor: no máximo um run cada; o 1 só precisa de EXP-D1 (~20 s).

### 1.15 Referências (só as usadas aqui)

- Hanley, J. A., & McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology, 143*(1), 29–36. https://doi.org/10.1148/radiology.143.1.7063747
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491
- Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient tests of statistical hypotheses. *Philosophical Transactions of the Royal Society of London. Series A, Containing Papers of a Mathematical or Physical Character, 231*(694–706), 289–337. https://doi.org/10.1098/rsta.1933.0009

Fonte: campo `apa7` de [nota privada, não distribuída] (sha256 no §0.5), copiado verbatim; ordem alfabética.

## Estado: congelado

Grade, gerador, tabela analítica e este pré-registro estão congelados, nesta ordem, antes de qualquer código da família
no repo. O que o workflow B faz depois, só no repo e só depois do workflow A verde:

1. **Cópia** da grade (byte a byte), porte do gerador (`code/exponent_analytic_table.py`, stdout byte a byte =
   tabela congelada), pré-registro sanitizado `data/prereg/05-exponent-addendum.md` e emenda datada em
   `data/PREREGISTRATION.md` (G5 limpo).
2. **TDD:** EX1–EX5 em `tests/test_exponent.py`, vermelhos antes do runner; depois `code/run_grid.py`.
3. **Run:** `run_grid.py --grid data/exponent_grid.json --out output/exponent` (60 simulações, tag 5).
4. **Mutação:** harness privado [verificação adversarial privada] sobre cópia descartável, os 8 mutantes da §1.12, mensagem
   do assert impressa; relatório [verificação adversarial privada].
5. **Results:** bloco EXP em `output/results.json`, `tests/test_paper_numbers.py` trava o veredito, folhas em
   `configs/stages.json`, `make_provenance.py` build + `--verify` exit 0, laço verde dos portões do repo.
6. **Laudo de impacto:** o que muda em texto, fórmula, tabela e figura segundo a §1.10; quem aplica no outline e no
   ledger é a sessão principal, com `conferir_outline` e verify. A nota datada sobre o item 5 dos desvios (§1.4) também
   é da sessão principal.
