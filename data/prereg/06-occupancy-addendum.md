# Pré-registro — adendo OCC: ocupação × taxa na média `ρ̄` (limite (b))

> **Translation note (English).** Sanitized copy of a pre-registration addendum frozen in Portuguese on
> 2026-09-26, before any code, test or output of the family it specifies existed. It is the faithful copy of
> the frozen private original whose sha256 is
> `574dccf9065f1860537dab6e5928ea9d1f5f17b6b736b0ac9d78e6639be55c19`; this copy has its own sha256. What
> changed, and nothing else: (1) the title line, which dropped the name of the author's working batch;
> (2) the header sentence giving the root of relative paths, which named the author's local directory and
> defined a `repo/` prefix, and now names the root of this repository; (3) file paths: the `repo/` prefix is
> stripped everywhere (so "só em `repo/`" reads "só neste repositório"); in prose, private paths that have a
> counterpart in this repository were mapped to it (`data/prereg/01`–`04`, `data/prereg/kat_token_analytic_table.txt`,
> `output/kat_token/resumo.json`, `code/token_kat_analytic_table.py`, `code/occupancy_analytic_table.py`,
> `data/prereg/occupancy_analytic_table.txt`); in the table columns that name private origins, and for every
> other pointer to a private file, a bracketed placeholder was used: `[registro privado de estado]` = private
> state log; `[nota privada, não distribuída]` = private note, not distributed; `[arquivo privado, não
> distribuído]` = private file or directory, not distributed; `[verificação adversarial privada]` = private
> adversarial verification; `[cadeia privada de selos]` = private chain of seals; `[selo privado, não
> distribuído]` = private seal configuration, not distributed. No cell id needed renaming (`590/AC` is the
> cell and combo of `output/replication/celulas.csv`). Wording, numbers, criteria and references are otherwise
> verbatim. Every sha256 quoted below refers to the private original of the file it names, except the grid
> (`data/occupancy_grid.json`, `64ae62f9…`) and the analytic table (`data/prereg/occupancy_analytic_table.txt`,
> `40d922b5…`), which are byte-identical in this repository. Names kept from the original: "rascunho-fonte" =
> the private source draft; "desenho" = the private design note of this repository; "outline", "ledger" and
> "STATE" = the author's private working documents; "workflow A" and "workflow B" = the author's two
> build-and-verification batches; `[B-crit n]` = finding n of the critique table in the source draft; "16b.x"
> and "D2" = numbered decisions in the private state log; G7 and G9 = private gates (regeneration contract;
> private test suite of 88 tests). Glossary: pré-registro = pre-registration; adendo = addendum; grade = grid;
> tabela analítica = analytic table; gerador = generator; célula = cell; semente = seed; janela = window;
> ocupação = occupancy; taxa = rate; sobe/desce = upward/downward direction; melhora/piora = improves/worsens;
> concorda/discorda/empate = agrees/disagrees/tie; selo = provenance seal; critério de quebra = falsification
> criterion; desvio = deviation.

> **Status: CONGELADO 2026-09-26 (sha256 registrado no [registro privado de estado], sessão 14, antes de existir qualquer código da família).**
>
> Raiz dos caminhos relativos: a raiz deste repositório, o repositório
> público local do desenho [nota privada, não distribuída] (critério de aceite; §"Workflow B" e apêndice
> A.1/A.2). Este arquivo **não altera** nenhuma folha selada (pré-registro original
> `data/prereg/01-displacement-replication.md`, adendo KAT `data/prereg/02-token-kat-addendum.md`, desvios
> `data/prereg/03-token-kat-deviations.md` e desvios-26b `data/prereg/04-token-kat-deviations-b.md`)
> e **não recebe o resultado** (vai para `output/occupancy/` e para o bloco OCC de `output/results.json`;
> desvio, se houver, em arquivo próprio datado no privado).

**Artefatos congelados deste adendo, na ordem de criação (a ordem é a prova de precedência):**

| # | Artefato | Caminho privado | sha256 | Destino no repo (workflow B) |
|---|---|---|---|---|
| 1 | Grade | [arquivo privado, não distribuído] | `64ae62f966e22e7de03960a6ca11af70cfa553e3892c0b29d7d15e40a3524b0e` | `data/occupancy_grid.json` (byte a byte) |
| 2 | Gerador da tabela analítica | [arquivo privado, não distribuído] | `d0290028feaf01fef73405ca9619451391ec3ce336d0c490129f5b7e1cd35abc` | `code/occupancy_analytic_table.py` (porte; stdout comparado byte a byte) |
| 3 | Tabela analítica (stdout do gerador sobre a grade; duas execuções byte-idênticas) | [arquivo privado, não distribuído] | `40d922b5f3119c32e9ef3990aea312772074d70f87e2ce72663cea79f1d622a3` | `data/prereg/occupancy_analytic_table.txt` |
| — | Rascunho-fonte (§0, §2 e linha 9 da §5; NÃO congelado) | [nota privada, não distribuída] | `99641618b4471a54fb8974d789f3fb0eb0e42062a8ff0a71240817815987956e` | — |

A grade e a tabela saíram limpas no juiz de vazamento ([verificação adversarial privada], exit 0 em cada uma) porque
entram no repo sem edição. Este `.md` é privado; a cópia pública `data/prereg/06-occupancy-addendum.md` é derivada
dele (caminhos privados trocados pelos nomes do repo, sem nomes do workspace) e tem sha próprio.

**Convenção:** as marcas `[B-crit n]` remetem à tabela de achados da §5 do rascunho-fonte (sha256 acima). A numeração
das seções (§0.x, §2.x) é a do rascunho-fonte, para rastrear cada mudança.

**Conferência por código contra o rascunho-fonte:** 354 valores numéricos (tabela §2.7, grade §2.6, linha da S3 e
escalares dos parágrafos) e 51 rótulos comparados na precisão exibida no rascunho; **uma divergência**, declarada onde
ocorre (§2.3: `w − φ`).

## 0. Decisões transversais que valem para esta família

### 0.1 Um fluxo aleatório por família `[B-crit 1]`

Os quatro rascunhos usavam o mesmo tag `5` em `numpy.random.default_rng([semente, i_celula, i_combo, tag, i_bloco])`:
para o mesmo `(semente, índice, bloco)`, famílias diferentes leriam os mesmos bits, e os quatro veredictos ficariam
correlacionados sem declaração. Tags fixados (decisão 16b.2 do STATE):

| Família | Tag | Observação |
|---|---|---|
| EXP (expoente de `d`) | 5 | — |
| OCC (ocupação × taxa) | 6 | — |
| CMP (fusão, Corolário 4(b)) | 7 | `i_fluxo` no lugar de `i_combo` (0 = `R`; 1 = sorteio partilhado por `RS`/`RF`/`RP`) |
| C5 (cotas, Corolário 5) | 8 | só KNP3 e FIX1; KNP1, KNP2, NUL1 e DEC1 usam, de propósito e declarado, fluxos do KAT (tag 3) |

Tag 3 (r3) e o fluxo de três entradas do r1 ficam reservados. O teste de pinos de cada família assere o seu tag e que
ele difere de 3 e dos outros três; cada família tem mutante de tag. Nesta família: `grade["tag"] == 6`, sem a chave
`tag_r3`, conferido pelo gerador congelado.

### 0.2 Onde nascem o código e as saídas, e como se prova (selo) `[B-crit 2]` — reescrita pela decisão 16b.1

O rascunho-fonte selava cada família num novo elo da cadeia privada e, depois da crítica, numa config privada por
família. **As duas versões estão superadas.** Vale o desenho do repo (§"Workflow B"):
o código de simulação, os testes e as saídas desta família nascem **só neste repositório**, e a prova de integridade é o selo
do próprio repo: `make_provenance.py` (build e depois `--verify`, exit 0), com folhas novas nos estágios
correspondentes de `configs/stages.json`:

- `prereg`: `data/occupancy_grid.json`, `data/prereg/occupancy_analytic_table.txt` e o pré-registro
  sanitizado `data/prereg/06-occupancy-addendum.md`;
- `code`: `code/occupancy_analytic_table.py`, `code/run_grid.py` (partilhado com EXP; entra uma vez) e
  `tests/test_occupancy.py`;
- `data`: `output/occupancy/celulas.csv`;
- `scores`: `output/occupancy/resumo.json`.

No privado: nada em [cadeia privada de selos]; nenhum [selo privado, não distribuído] novo; nenhum `--prev`; o G9 privado continua com **88 testes**; o G7 (contrato de regeneração) **não
muda**; os selos r1–r4 ficam intactos (verify exit 0). O harness de mutação é privado (§2.13) e o repo cita o
resultado dele só em `REPRODUCIBILITY.md`.

### 0.3 Limite comum, declarado uma vez `[B-crit 3]`

Com o gerador fixado (Poisson, `x ~ N(d_s·y, 1)`) e o leitor oráculo `Σ d_s(x_i − d_s/2)`, o expoente 2 de `d`, a
ponderação pela ocupação, a suficiência de `Σx` na fusão e a dominância usuário a usuário das cotas por `ρ` são
**identidades algébricas** do modelo. Nenhuma das quatro famílias pode falsificar essa álgebra. O que cada uma pode
falsificar: (a) a aproximação fluida (hipótese iii), e a previsão exata onde ela é usada; (b) a implementação literal
(janela, fusão, políticas, leitor). As regras rivais são regras de bolso, não mecanismos que o gerador realize: a
simulação só se comportaria como um rival se o código tivesse o defeito correspondente (leitor sem peso por `d`;
janela por contagem; evento fundido sem a soma). Consequência obrigatória em todo produto de texto: **"conferido por
simulação literal" = a forma fechada bate com a simulação literal**; proibido "estabelecido/medido empiricamente" para
expoente, peso, fator de fusão ou ordem de políticas.

### 0.4 Maquinário partilhado, perguntas separadas `[B-crit 4]` `[B-crit 6]`

As quatro perguntas são distintas e NÃO se fundem (vereditos independentes; um desfecho não arrasta o outro). O
maquinário, sim:

- EXP e OCC rodam pelo mesmo caminho (`_uma_tarefa` de `code/run_token_kat.py` + `avaliar_kat` de
  `code/token_kat.py`, sem editar nada): **um único runner fino** `code/run_grid.py --grid <json> --out <dir>`
  serve às duas (escada ponytail: segundo uso concreto já existe). As grades novas guardam o tag na chave `tag`; o
  runner passa a `_uma_tarefa` o adaptador `{**grade, "tag_r3": grade.get("tag", grade.get("tag_r3"))}`, que aceita a
  grade nova (só `tag`) e a do KAT (só `tag_r3`, usada no OCCT1). **Nenhuma grade nova tem a chave `tag_r3`** (o
  rascunho EXP gravava 5 numa chave chamada `tag_r3`, nome que engana sobre o valor). `code/` não tem
  `__init__.py`: entra no `sys.path` (nunca `import code`, que sombrearia o módulo da stdlib).
- Parâmetros repetidos entre famílias, declarados: `R ∪ S` de CMP1 (braço `RS`) = `R ∪ S` do KAT S1b; `R ∪ S` de CMP4
  (braço `RS`) = `R ∪ S` do KAT S2b = mistura de KNP2 do C5; mistura de KNP1 = `R ∪ S` do KAT S1a. Só o C5 reusa os
  DADOS selados do KAT (âncoras); o CMP reusa só como teste de identidade (FU1c), fora do veredito. O OCC não reusa
  dado selado: o OCCT1 só confere identidade de maquinário com a S3.

### 0.5 Referências `[B-crit 5]` — fechado

Norma APA 7 (decisão D2; achado 20 da §5 do rascunho-fonte fechado pela decisão 16b.3). Fonte única:
[arquivo privado, não distribuído] (sha256 `7e8ed08ff21c773917f06eec03c13c23cb0aa949f501fc480c0d860c09fad6bd`),
quatro linhas verificadas por código contra os crus Crossref em [arquivo privado, não distribuído]. Cada referência
da §2.14 é o campo `apa7` copiado verbatim (Neyman–Pearson mantém o prefixo "IX." do título e o nome completo da
revista, como publicados).

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
de 14 CPUs. A linha OCC (4,123·10⁹; 2,79× o KAT; ~212 s) é reproduzida pela tabela congelada.

## 2. OCC — ocupação × taxa na média `ρ̄` (limite (b))

> Grade-rascunho de origem: [arquivo privado, não distribuído] (sha256
> `958e7b88f26a7c62f79c7230705509e60d95d6e6433c899d4c4501e983c0c712`); a grade congelada difere dela só no `tag`
> (5 -> 6, `[B-crit 1]`) e no `_fonte` (inglês, só nomes do repo). Recálculo independente da crítica:
> [verificação adversarial privada] (sha256
> `c4413a7be352cb2f2307bbe6ab8c55314359408c38bf3734b41303d8f7c62fb3`), duas execuções byte-idênticas
> ([verificação adversarial privada] = [verificação adversarial privada], sha256
> `7a33da0912f4604c3781c0f81e58a6d9abaad3ed4f2efb1a3e6799559090451c`).

### 2.1 Pergunta

Limite declarado (outline, "Estado de teste"; desvios do KAT, item 5): *"a comparação ocupação × taxa depende de uma
célula só (S3, `z(R) = 2,87`)"*. Agravante calculado: `ρ_S` da S3 fica a 71% do caminho entre `ρ̄_ocup` e `ρ̄_taxa`
(`t = 0,71`); na família de pesos `w_r ∝ λ_r k_r^α` (`α = 1` ocupação, `α = 0` taxa) a S3 só exclui `α < 0,21`, e testa
uma direção só (a teoria prevê MELHORA; "adicionar sempre melhora" passaria nela).

**Pergunta:** numa família de células nas duas direções, **com a janela já saturada antes da fonte nova** e com folga
(`z(R) ≥ 4`), o sinal de `ΔAUC` da simulação literal por orçamento de tokens segue `ρ̄` ponderada pela OCUPAÇÃO
(Corolário 1) em vez de `ρ̄` ponderada pela TAXA?

### 2.2 O que a teoria prevê (forma fechada)

Com `R` saturada (`T·W_R ≥ K`, `W_R = Σ_R λ_r k_r`) — condição do Corolário 1:

```text
ΔΔ² = K · φ′_S · (ρ_S − ρ̄_ocup),   φ′_S = λ_S k_S / (W_R + λ_S k_S),   ρ_S = d_S² / k_S
ρ̄_ocup = Σ_R λ_r d_r² / Σ_R λ_r k_r = Σ_R φ_r ρ_r          (média de ρ sobre os TOKENS da janela)
AUC = Φ(√Δ² / √2)  estritamente crescente  ->  sinal(ΔAUC) = sinal(ρ_S − ρ̄_ocup)
```

Nível por combo: forma fechada fluida `W = Σλk`, `h = min(T, K/W)`, `Δ² = h·Σλd²` (a mesma do KAT).

### 2.3 Hipótese rival (prevê o CONTRÁRIO em toda célula da família)

```text
ρ̄_taxa = Σ_R λ_r ρ_r / Σ_R λ_r          (média de ρ sobre os EVENTOS da janela)
sinal previsto = sinal(ρ_S − ρ̄_taxa)
```

É a regra de quem conta cada evento uma vez (natural na janela por eventos do r1, em que `k ≡ k` fazia as duas médias
coincidirem). Divergem quando `R` mistura custos. Com duas classes (barata `k = 14`, cara `k = 55`):
`ρ̄_taxa − ρ̄_ocup = (w_barata − φ_barata)·(ρ_barata − ρ_cara)`; o afastamento máximo é `0,33·|ρ_barata − ρ_cara|`, em
`λ_barata/λ_cara = √(55/14) ≈ 1,98` (conferido pela tabela congelada: `w − φ = 0,3293` nesse ponto; **divergência
declarada:** o rascunho-fonte trazia `0,3294`, erro de arredondamento na 4ª casa — o valor exato é
`(√(55/14) − 1)/(√(55/14) + 1) = 0,329323`; o arredondamento em duas casas, `0,33`, não muda). **Nota `[B-crit 3]`:** a
regra da taxa não é mecanismo realizável pelo gerador; a família testa (iii) e a implementação em mais células,
profundidades e nas duas direções — reduz a dependência de uma célula rasa (S3), não descobre o peso.

| Direção | Composição de `R` | Ordem | Ocupação prevê | Taxa prevê |
|---|---|---|---|---|
| **sobe** | fonte barata forte + fonte cara fraca (a cara ocupa 2/3 dos tokens com 1/3 dos eventos) | `ρ̄_ocup < ρ_S < ρ̄_taxa` | MELHORA | PIORA |
| **desce** (nova; nenhuma célula do KAT) | fonte barata frequente quase sem sinal (`d = 0,05`) + fonte cara forte | `ρ̄_taxa < ρ_S < ρ̄_ocup` | PIORA | MELHORA |

**Diagnóstico de localização (fora do critério).** Na família `w ∝ λ k^α`, cada célula tem `α*` com `ρ̄_α* = ρ_S`; com
duas classes de custo, `α* = ln[Λ_14·(ρ_S − ρ̄_14) / (Λ_55·(ρ̄_55 − ρ_S))] / ln(55/14)` (confere com a bissecção nas 12
células, erro `< 1e−6`, assert do gerador congelado; reconferido pela crítica por bissecção independente). O sinal
igual ao da ocupação exclui `α < α*`. O lado `α > 1` **não é testado**.

### 2.4 O que NÃO se afirma (escopo)

- Ilustrativo, ordens de grandeza; **não é replicação do nuFormer**. Do case: `K = 2.048` e `k ∈ {14, 55}`.
- Não testa: expoente de `d` (limite a), Corolários 4(b) e 5 (limites c, d), `α > 1`, pesos fora da família `λ k^α`,
  regime misto ou sem saturação (já cobertos pelo KAT).
- Produto: fechar a oração do limite (b); **nenhum número desta família vai ao corpo; nenhuma figura ou tabela nova no
  artigo**.
- Sinal na contagem e no tempo de chegada segue excluído (hipótese v).

### 2.5 Modelo gerador (idêntico ao KAT; muda só a grade e o tag)

`π = 0,2`; Poisson de taxa `λ_s` em `T` dias, independente de `y`; `x ~ N(d_s·y, 1)`; custo `k_s` fixo; janela = maior
sufixo de eventos inteiros com custo `≤ K = 2.048`; leitor = oráculo `Σ_visíveis d_s·(x_i − d_s/2)` — log-razão de
verossimilhança da janela visível, pelo lema de Neyman e Pearson (1933) o **teto** de AUC de qualquer leitor da mesma
janela (hipótese iv). AUC por Mann–Whitney com postos médios (Mann & Whitney, 1947). Tudo por
`simular_literal_tokens` de `code/token_kat.py` (porte de [arquivo privado, não distribuído]), sem reimplementação.

### 2.6 Grade (fonte única: a grade congelada, copiada byte a byte para `data/occupancy_grid.json`)

`K = 2.048`; `N = 100.000` por (célula, combo, semente); sementes `0..4`; blocos de 10.000; fluxo
`numpy.random.default_rng([semente, i_celula, i_combo, 6, i_bloco])` — **tag 6, exclusivo desta família** `[B-crit 1]`
(o rascunho usava 5, colidindo com EXP, CMP e C5); `i_celula` = índice na grade OCC. 12 células × 2 combos × 5 sementes
= 120 simulações. Chaves de dado = as do KAT, no esquema PT que o runner do KAT lê (`K`, `pi`, `N`, `bloco_usuarios`,
`sementes`, `tol_base_r1`, `margem_minima_sobre_tol`, `z_minimo_regime`, `eventos_max_por_usuario`, `celulas`; por
célula `id`, `bloco`, `regra_ingenua`, `T`, `R`, `S`, com `lam`, `d`, `k` por fonte), **sem `tag_r3`**, + `tag`,
`subbloco`, `direcao`; comentário só no `_fonte` (inglês, sem caminho privado). `bloco = "saturado"` e
`regra_ingenua = "taxa"` em toda célula; `z_minimo_regime = 4.0`; `margem_minima_sobre_tol = 1.5`;
`eventos_max_por_usuario = 600`.

**Critérios de desenho** (função `conferir` CONGELADA da tabela do KAT, `code/token_kat_analytic_table.py`, sha256
`2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`, com as chaves mais duras): `z(R) ≥ 4,0` e
`z(R∪S) ≥ 4,0` (KAT: 2,5; a S3 tinha `z(R) = 2,87`; menor `z(R∪S)` da grade: 8,68, OCC03); `≤ 600` eventos;
`|ΔAUC previsto| ≥ 1,5·tol` (KAT: 1,2); regra da taxa oposta; e, fora do `conferir`,
`|ΔAUC previsto| ≥ 10 × 0,00191` (0,00191 = maior `|ΔAUC empírico − ΔAUC previsto|` do run selado do KAT, 0,0019057,
arredondado para cima) e pares de mesmo `(R, S)` em duas profundidades com previsão fluida idêntica (saturado: `Δ²` não
depende de `T`). O gerador congelado assere ainda: `tag == 6` e `6 ∉ {3, 5, 7, 8}`; ausência de `tag_r3`; direção
coerente com a ordem de `ρ` (tabela da §2.3) e com o sinal de `ΔAUC`; `α*` da bissecção = forma fechada (`< 1e−6`);
8 configurações `(R, S)` distintas; núcleo cobrindo 2 direções × 2 `k_S`; a S3 do KAT passa nos critérios do KAT e é
reprovada sob os desta grade (`z(R) = 2,87 < 4,0`). **Resultado: 12/12 passam** (gerador congelado, exit 0;
reconferido pela crítica).

| Célula | Sub-bloco | Direção | T | R (`λ` · `d` · `k`) | S (`λ` · `d` · `k`) |
|---|---|---|---|---|---|
| OCC01 | núcleo | sobe | 90 | A (1,0 · 0,20 · 14), B (0,5 · 0,05 · 55) | C (1,6 · 0,30 · 55) |
| OCC02 | núcleo | sobe | 180 | idem OCC01 | idem OCC01 |
| OCC03 | núcleo | sobe | 90 | idem OCC01 | C (1,6 · 0,15 · 14) |
| OCC04 | núcleo | sobe | 180 | idem OCC01 | idem OCC03 |
| OCC05 | núcleo | desce | 165 | A (0,8 · 0,05 · 14), B (0,2 · 0,34 · 55) | C (1,3 · 0,19 · 55) |
| OCC06 | núcleo | desce | 250 | idem OCC05 | idem OCC05 |
| OCC07 | núcleo | desce | 165 | idem OCC05 | C (1,3 · 0,10 · 14) |
| OCC08 | núcleo | desce | 250 | idem OCC05 | idem OCC07 |
| OCC09 | três fontes | sobe | 120 | A (0,8 · 0,22 · 14), D (0,4 · 0,10 · 14), B (0,5 · 0,05 · 55) | C (3,2 · 0,14 · 14) |
| OCC10 | três fontes | desce | 220 | A (0,6 · 0,04 · 14), B (0,15 · 0,36 · 55), D (0,1 · 0,20 · 55) | C (1,7 · 0,20 · 55) |
| OCC11 | limiar | sobe | 90 | idem OCC01 | C (4,8 · 0,265 · 55) |
| OCC12 | limiar | desce | 110 | A (1,6 · 0,03 · 14), B (0,2 · 0,36 · 55) | C (3,5 · 0,19 · 55) |

Núcleo = fatorial 2 (direção) × 2 (`k_S` = 14 ou 55) × 2 (profundidade: moderada `z ≈ 4,3–4,6`, funda `z ≈ 8–10`), com
`R` fixa por direção e o mesmo `(R, S)` nas duas profundidades. Oito configurações `(R, S)` distintas, 12 células.
Família principal (veredito) = sub-blocos núcleo + três fontes (OCC01–OCC10); sub-bloco limiar (OCC11–OCC12) = OCC-L,
fora do veredito.

### 2.7 Tabela analítica — calculada ANTES de simular (forma fechada)

Congelada em `data/prereg/occupancy_analytic_table.txt` (sha256
`40d922b5f3119c32e9ef3990aea312772074d70f87e2ce72663cea79f1d622a3`): stdout do gerador `code/occupancy_analytic_table.py`
(sha256 `d0290028feaf01fef73405ca9619451391ec3ce336d0c490129f5b7e1cd35abc`) sobre a grade congelada, 1ª linha = sha256
da grade, duas execuções byte-idênticas. Sem sorteio: o gerador só importa (sem editar) `analisar`, `conferir`,
`fontes`, `tolerancia`, `z_saturacao`, `ep_hanley_mcneil`, `W`, `delta2`, `auc` e `inclinacao` da tabela congelada do KAT. Os 204
valores desta tabela foram conferidos por código contra a tabela congelada (zero divergência); já tinham sido
conferidos dígito a dígito pela crítica.

| Célula | z(R) | z(R∪S) | eventos/usuário | ρ_S | ρ̄ ocupação | ρ̄ taxa | t | α* | AUC(R) | AUC(R∪S) | ΔAUC previsto | tol | ΔAUC/tol | ΔAUC/EP_HM | viés dif. previsto | ocupação | taxa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OCC01 | 4,30 | 12,51 | 279 | 0,001636 | 0,000994 | 0,001920 | 0,69 | 0,31 | 0,8435 | 0,8869 | +0,0434 | 0,0136 | 3,20 | 40,6 | −0,0004 | melhora | piora |
| OCC02 | 9,78 | 19,58 | 558 | 0,001636 | 0,000994 | 0,001920 | 0,69 | 0,31 | 0,8435 | 0,8869 | +0,0434 | 0,0136 | 3,20 | 40,6 | −0,0004 | melhora | piora |
| OCC03 | 4,30 | 8,68 | 279 | 0,001607 | 0,000994 | 0,001920 | 0,66 | 0,34 | 0,8435 | 0,8671 | +0,0236 | 0,0136 | 1,74 | 21,4 | +0,0002 | melhora | piora |
| OCC04 | 9,78 | 15,67 | 558 | 0,001607 | 0,000994 | 0,001920 | 0,66 | 0,34 | 0,8435 | 0,8671 | +0,0236 | 0,0136 | 1,74 | 21,4 | +0,0002 | melhora | piora |
| OCC05 | 4,56 | 15,24 | 380 | 0,000656 | 0,001132 | 0,000563 | 0,84 | 0,20 | 0,8591 | 0,8126 | −0,0466 | 0,0137 | 3,40 | 40,2 | +0,0005 | piora | melhora |
| OCC06 | 8,02 | 19,73 | 575 | 0,000656 | 0,001132 | 0,000563 | 0,84 | 0,20 | 0,8591 | 0,8126 | −0,0466 | 0,0137 | 3,40 | 40,2 | +0,0005 | piora | melhora |
| OCC07 | 4,56 | 11,28 | 380 | 0,000714 | 0,001132 | 0,000563 | 0,73 | 0,32 | 0,8591 | 0,8372 | −0,0219 | 0,0136 | 1,61 | 19,5 | +0,0004 | piora | melhora |
| OCC08 | 8,02 | 15,97 | 575 | 0,000714 | 0,001132 | 0,000563 | 0,73 | 0,32 | 0,8591 | 0,8372 | −0,0219 | 0,0136 | 1,61 | 19,5 | +0,0004 | piora | melhora |
| OCC09 | 7,14 | 16,19 | 588 | 0,001400 | 0,000993 | 0,001808 | 0,50 | 0,52 | 0,8433 | 0,8659 | +0,0226 | 0,0136 | 1,67 | 20,5 | +0,0003 | melhora | piora |
| OCC10 | 6,44 | 20,34 | 561 | 0,000727 | 0,001102 | 0,000582 | 0,72 | 0,30 | 0,8559 | 0,8171 | −0,0388 | 0,0137 | 2,83 | 33,5 | +0,0006 | piora | melhora |
| OCC11 | 4,30 | 21,06 | 567 | 0,001277 | 0,000994 | 0,001920 | 0,31 | 0,69 | 0,8435 | 0,8699 | +0,0265 | 0,0136 | 1,95 | 24,1 | −0,0003 | melhora | piora |
| OCC12 | 5,12 | 20,27 | 583 | 0,000656 | 0,000819 | 0,000319 | 0,33 | 0,75 | 0,8201 | 0,7981 | −0,0221 | 0,0137 | 1,61 | 18,0 | +0,0011 | piora | melhora |

`t = (ρ_S − ρ̄_ocup)/(ρ̄_taxa − ρ̄_ocup)`. `EP_HM` = Hanley e McNeil (1982) para a diferença de médias de 5 sementes.
"Viés dif. previsto" = estimativa de desenho (método delta calibrado contra r1 e KAT), fora do critério. A mesma rotina
reproduz a S3 da tabela congelada do KAT (`z(R) = 2,87`, `ρ_S = 0,001325`, `ρ̄ = 0,000545 / 0,001641`,
`ΔAUC = +0,0869`, `tol = 0,0137`) — linha de conferência da tabela congelada, cujos 6 números foram conferidos por código
contra a linha S3 de `data/prereg/kat_token_analytic_table.txt`.

**Viés literal × fluido (desenho, não vai ao texto).** Com contagens independentes de `y`, a AUC exata do oráculo é
`E[Φ(√(D₁ + D₀)/2)]`, `D = Σ n_s d_s²`; `viés ≈ g″(2μ)·Var(D)`, `g(u) = Φ(√u/2)`. Calibração: pior célula do r1
(590/AC) modelo −0,0063 contra −0,0078 observado (subestima ~20%, daí fator 1,5 na parte de Jensen; valores do
rascunho-fonte, não reconferidos nesta etapa); KAT: previsto `≤ 0,0015` contra observado máximo 0,0019 (reconferido
por código contra o `output/kat_token/resumo.json` selado: modelo 0,00146, observado 0,00191). Os dois máximos vêm
de células diferentes: o do modelo está na MIX2, onde o observado é −0,00004; o observado está na S1a, onde o modelo dá
−0,00106 (subestima ~1,8×, acima do fator 1,5 justificado só pelo r1); na MIX1 o modelo erra o sinal (−0,00112 contra
+0,00122 observado). Sem impacto no veredito: o piso `10 × 0,00191` não depende do modelo, e a margem mínima das 10
células do veredito (OCC07/OCC08) fica em 5,79× com fator 1,5, 5,53× com fator 2 e 5,07× com fator 3 (cálculo
externo ao gerador congelado, 2026-09-26, com as funções dele importadas; o gerador imprime só o fator 1,5, com uma
casa: 5,8). Na família: viés
da diferença `≤ 0,0011` (OCC12), contra a teoria em 9 das 12. Nas 10 do veredito, `|ΔAUC previsto|` ≥ 5,8× o pior
caso somado (Jensen × 1,5 + ocioso máximo; mínimo em OCC07/OCC08); OCC12 (fora do veredito) 4,5× (OCC11: 7,1×).
Leitura declarada do "pior caso somado" na diferença, impressa pelo gerador congelado:
`|ΔAUC previsto| / (1,5·|viés dif.| + max(|ocioso de R|, |ocioso de R ∪ S|))`, com ocioso = viés de `k_max` tokens
ociosos no regime saturado (`(dAUC/dΔ²)·Δ²·k_max/K`); é a leitura conservadora (usar só o ocioso de `R` dá os mesmos
5,8 e 4,5). Fonte forte esparsa na janela de `R ∪ S` (`E[n] < 3`, reconferido): OCC10 (B 2,66; D 1,77) e OCC12
(B 1,81) — o viés vai CONTRA a teoria, logo o risco é falso "reprova", não falsa confirmação.

**N, sementes e poder.** `EP_emp/EP_HM ∈ [0,50; 1,15]` no KAT (4 graus de liberdade; reconferido por código contra o
selado); com EP verdadeiro = 1,3·`EP_HM` e o pior `ΔAUC/EP_HM` (18,0): `P(algum empate nas 12) ≤ 1,4e−17`;
`P(algum sinal trocado por ruído) ≤ 7e−44` (limite da união nas 12 células, `r = ΔAUC/EP_HM`:
`Σ P(χ²₄ > 4·(r/(3·1,3))²)` e `Σ P(N(0, 1) > r/1,3)`, impressos pelo gerador congelado). O risco real é sistemático
(literal ≠ fluido), e é isso que a família mede.

### 2.8 Métrica e regra de decisão (fixa)

Por (célula, combo, semente): AUC de Mann–Whitney. Por célula: `ΔAUC_emp = média₅(AUC(R∪S)) − média₅(AUC(R))`;
`EP_emp = √(s²_{R∪S}/5 + s²_R/5)`, `ddof = 1`. Nível por combo: `|média(AUC) − AUC fluida|`.

A família **passa** se, e só se, OCCT1–OCCT3 verdes e:

- **OCC-S (sinal; família principal OCC01–OCC10):** `empate` se `|ΔAUC previsto| < 3·EP_emp`; `discorda` se o sinal
  difere; senão `concorda`. **Passa com 10/10 `concorda`. Uma discordância reprova; um empate reprova por falta de
  poder.** OCC-S aprovado = taxa refutada nas 10.
- **OCC-N (nível, 20 combos de OCC01–OCC10):** `|média(AUC) − AUC fluida| ≤ tol` do combo
  (`tol = 0,0079 + disc + 3·EP_HM/√5`, função `tolerancia` congelada do KAT). Um estouro reprova. Declarado: só pega
  erro grosseiro de nível (frouxidão do KT-N, desvios item 4).
- **OCC-L (limiar, OCC11–OCC12): FORA do veredito**, fixado agora: mesma regra de sinal, reportada à parte; perto do
  limiar uma discordância indicaria `α` pouco diferente de 1 ou viés residual, não a vitória da taxa. Só localiza `α`.

Report-only: sinal por semente; limite inferior de `α` (máximo de `α*` nas concordantes: 0,52 com OCC01–OCC10; 0,75 se
OCC-L também concordar; a S3 sozinha dava 0,21); invariância em `T` nos 4 pares
(`|ΔAUC_emp(T moderado) − ΔAUC_emp(T fundo)| ≤ 3·√(EP²₁ + EP²₂)`); viés observado × previsto; `Δ²` empírico; ociosos e
fração saturada; a regra "por evento" do KAT prevê o oposto da ocupação em 7 das 12 (OCC03, 04, 05, 06, 09, 10, 12 —
reconferido pela tabela congelada) e é reportada como refutada ou não.

### 2.9 Critério de quebra

- **Falsifica a ponderação pela ocupação na simulação literal:** uma célula de OCC01–OCC10 em `discorda`. A taxa só é
  declarada suportada se as 10 discordarem; padrão misto = ocupação falsificada naquelas células, taxa não vindicada
  (lê-se pelo `α*` de cada uma).
- Com OCCT1–OCCT3 e a mutação verdes, discordância aponta para (iii), não para a álgebra (§0.3). Discordância só em
  OCC10 (fonte forte com `E[n] < 3`) lê-se como "(iii) falha com janela esparsa".
- Empate: reprova por poder; nada muda no texto.

### 2.10 O que muda no artigo em cada desfecho

| Desfecho | Corpo (2.3a) | Fórmula | Tabela / figura | Outline, ledger, STATE | Repo |
|---|---|---|---|---|---|
| **Passa** (OCC-S 10/10, OCC-N 20/20) | frase licenciada (desvios-26b, item 1) **fica igual** — já diz "com a janela já saturada antes da fonte nova" e "comparada à média ponderada pela ocupação"; nenhum número | inalterada | nenhuma nova | cai a oração "ocupação × taxa depende de uma célula (S3)"; superação do item 5 dos desvios em arquivo novo datado + linha `[OCC-resultado]`; "Estado de teste" cita a família | `docs/THEORY.md` (EN) `[B-crit 9]`: *"with the window already saturated before the new source, the weight is token occupancy, not event rate; checked by literal simulation on a 10-cell family in both directions"*; emenda datada em `data/PREREGISTRATION.md`; bloco OCC em `output/results.json`; `tests/test_paper_numbers.py` trava 10/10 |
| **Passa + OCC-L concorda** | idem | idem | idem | idem, com `α ≥ 0,75` no `docs/THEORY.md` e no ledger (report-only) | idem |
| **Passa + OCC-L discorda** | idem | idem | idem | idem, com `α ≥ 0,52` e a discordância perto do limiar declarada como limite | limite no `docs/THEORY.md` |
| **OCC-S reprova por discordância** | a frase licenciada perde "comparada à média ponderada pela ocupação" como conferida; vira "`ρ_s = d_s²/k_s` conferido com `k` heterogêneo, com a janela já saturada antes da fonte nova; a ponderação pela ocupação é do modelo fluido e a simulação literal a contradiz em [células]" | Corolário 1 inalterado como teorema do modelo fluido; hipótese (iii) ganha qualificador de escopo | nenhuma | desvio novo datado; "Estado de teste" restringe a ponderação a "analítica + S3" | `docs/THEORY.md` registra a contradição; nenhum teste afrouxado |
| **OCC-S reprova por empate** | nada muda | nada | nada | limite (b) segue; desvio datado | nada |
| **OCC-S passa, OCC-N reprova** | nada muda (o corpo não usa nível) | nada | nada | "sinal conferido, nível não" | idem |

### 2.11 Funções reusadas (nenhum arquivo selado é editado)

| Origem privada (sha256) | Porte no repo | Função | Uso |
|---|---|---|---|
| [arquivo privado, não distribuído] (`b70c6a2e729d3b6ecd58b59dc79c9e74697fcd6ce51b606e170b540497c245af`) | `code/token_kat.py` | `carregar_grade`, `fontes_da_celula`, `delta2_fluido`, `auc_fluida`, `simular_literal_tokens`, `avaliar_kat` | `avaliar_kat` chamada duas vezes: `{**grade, "celulas": núcleo + três fontes}` e `{**grade, "celulas": limiar}` |
| [arquivo privado, não distribuído] (`fe1b61cbee6ba6b8a4628ddaa742f820f4120b4b4adf48f71b17a5669a803efc`) | `code/run_token_kat.py` | `_uma_tarefa`, `tolerancias`, `_celula_csv`, `CAMPOS_CSV` | pelo runner partilhado `code/run_grid.py` (§0.4), adaptador `{**grade, "tag_r3": grade.get("tag", grade.get("tag_r3"))}`; as tarefas preservam o `i_celula` ORIGINAL mesmo filtradas |
| [arquivo privado, não distribuído] (`616b2445a6479f1fde7c1ff6d980dca12887be9743633484bfad21925b36a4ec`) | `code/displacement.py` | `PI`, `auc_mann_whitney` (via `_uma_tarefa`) | — |
| [arquivo privado, não distribuído] (`2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`) | `code/token_kat_analytic_table.py` | `analisar` (`regra_ingenua = "taxa"` já existe), `conferir`, `fontes`, `tolerancia`, `z_saturacao`, `ep_hanley_mcneil`, `W`, `delta2`, `auc`, `inclinacao` | no privado, import por caminho com `sys.dont_write_bytecode = True` (gerador congelado); no repo, `import token_kat_analytic_table` com `code/` no `sys.path`; o `main` do KAT não é reusado |

Identificadores Python dos módulos portados ficam verbatim do privado (desenho A.1). Código novo desta família, todo no
repo e nenhum em glob selado: `data/occupancy_grid.json` (cópia byte a byte da grade congelada),
`code/occupancy_analytic_table.py` (porte do gerador congelado; o stdout sobre a grade do repo tem de ser igual,
byte a byte, a `data/prereg/occupancy_analytic_table.txt`, cópia da tabela congelada), `code/run_grid.py`
(partilhado com EXP), `tests/test_occupancy.py`. Saída em `output/occupancy/` (`celulas.csv`, `resumo.json`).
No privado, só o gerador congelado e o harness de mutação (§2.13).

### 2.12 Testes de unidade (antes de qualquer número da grade)

- **OCCT1 — identidade com o selado.** O runner partilhado `code/run_grid.py`, alimentado com a grade do KAT do repo
  (`data/kat_token_grid.json`, que tem só `tag_r3 = 3`; o adaptador aceita as duas formas) e filtrado para a S3
  com o `i_celula` original (4), reproduz, **byte a byte**, as 10 linhas da S3 (texto das linhas `4,S3,…` do CSV,
  terminador CRLF incluído) em `output/kat_token/celulas.csv` (origem: [arquivo privado, não distribuído], sha256
  `aea196a288494455720aa8117780836942632cc36827510fd01c8468b37ceae6`; o arquivo do repo difere do privado pela
  renomeação das células mistas para MIX1/MIX2, logo o teste compara as linhas da célula, não o sha do arquivo).
  Conferido em 2026-09-26: as 10 linhas `4,S3,…` são byte-idênticas entre o CSV privado e o do repo. Escreve em
  diretório temporário, **nunca** em `output/kat_token/`.
- **OCCT2 — tabela.** `α*` da bissecção = forma fechada de duas classes (`< 1e−6`); a S3 reproduz a linha congelada do
  KAT; `conferir` passa nas 12 e FALHA na S3 sob `z_minimo_regime = 4.0`; `grade["tag"] == 6`, `6 ∉ {3, 5, 7, 8}` e sem
  a chave `tag_r3` `[B-crit 1]`; o stdout de `code/occupancy_analytic_table.py` sobre `data/occupancy_grid.json`
  é igual, byte a byte, a `data/prereg/occupancy_analytic_table.txt`.
- **OCCT3 — previsão.** A forma fechada reproduz `AUC(R)`, `AUC(R∪S)` e o sinal da tabela; os 4 pares têm previsão
  idêntica.

### 2.13 Mutação (antes de valer; `--color=no`, mensagem do assert impressa e conferida)

Harness PRIVADO [arquivo privado, não distribuído], sobre cópia descartável do repo FORA dele; relatório
[verificação adversarial privada] (data do dia do run); o repo cita o resultado só em
`REPRODUCIBILITY.md`. Obrigatórios: (X01) `ρ̄` pela taxa na previsão — tem de morrer em **todas** as 12 pelo análogo do
KT3; (X02) tag 3 ou tag de outra família (5, 7, 8) `[B-crit 1]`; (X03) `z_minimo_regime` de volta a 2,5; (X04)
`margem_minima_sobre_tol` de volta a 1,2; (X05) OCC-L dentro do veredito; (X06) adaptador do tag ausente; (X07) um par de
profundidade com `T` igual. Mutante morto só vale com a mensagem do assert que o matou impressa.

### 2.14 Selo, tempo e referências

**Selo (reescrito pela decisão 16b.1; ver §0.2).** Sem config privada, sem número de selo privado, sem `--prev`: as
folhas desta família entram nos estágios de `configs/stages.json` — `prereg` = `data/occupancy_grid.json` +
`data/prereg/occupancy_analytic_table.txt` + `data/prereg/06-occupancy-addendum.md`; `code` =
`code/occupancy_analytic_table.py` + `code/run_grid.py` + `tests/test_occupancy.py`; `data` =
`output/occupancy/celulas.csv`; `scores` = `output/occupancy/resumo.json` — e a prova é
`make_provenance.py` (build, depois `--verify` exit 0). Os módulos reusados já são folhas do estágio `code` do
repo (portados pelo workflow A). No privado: [cadeia privada de selos] intocado, G9 = 88 testes, G7 sem mudança, r1–r4
com verify exit 0.

Tempo: `4,123·10⁹` eventos (2,79× o KAT; reconferido pela tabela congelada) -> **~212 s** com 8 processos (estimativa
linear, não medição). Memória por bloco `≤ 588 × 10.000` eventos: abaixo do teto de 600/usuário, ~5% acima do máximo que
o KAT exercitou (562; a tabela congelada imprime +4,5%).

Referências (campo `apa7` de [arquivo privado, não distribuído], verbatim). Dantzig (1957) entra porque
`ρ = d²/k` é a razão valor/peso da mochila fracionária; este adendo não testa o Corolário 5.

- Dantzig, G. B. (1957). Discrete-variable extremum problems. *Operations Research, 5*(2), 266–288. https://doi.org/10.1287/opre.5.2.266
- Hanley, J. A., & McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology, 143*(1), 29–36. https://doi.org/10.1148/radiology.143.1.7063747
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491
- Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient tests of statistical hypotheses. *Philosophical Transactions of the Royal Society of London. Series A, Containing Papers of a Mathematical or Physical Character, 231*(694–706), 289–337. https://doi.org/10.1098/rsta.1933.0009

## 3. Estado: congelado — o que o workflow B faz depois

Este adendo, a grade e a tabela analítica estão congelados; nenhum byte deles muda (adendo novo = arquivo novo). A
família OCC entra no workflow B (fila por impacto no corpo: C5 > CMP > OCC > EXP), só depois do workflow A verde, nesta
ordem:

1. **Cópia dos artefatos de pré-registro para o repo, antes de qualquer código da família:** grade byte a byte para
   `data/occupancy_grid.json`; tabela para `data/prereg/occupancy_analytic_table.txt`; pré-registro
   sanitizado `data/prereg/06-occupancy-addendum.md` (limpo no juiz de vazamento); emenda datada em
   `data/PREREGISTRATION.md`.
2. **TDD:** `tests/test_occupancy.py` com OCCT1–OCCT3 escritos e vermelhos antes do runner e do porte do gerador;
   depois `code/run_grid.py` e `code/occupancy_analytic_table.py` até verde (`pytest --color=no`).
3. **Run:** `code/run_grid.py --grid data/occupancy_grid.json --out output/occupancy` (8 processos,
   120 simulações, tag 6). Este 1º run é o ato de publicação (antes do `make_provenance.py` build; desenho A.6,
   "Alvos de escrita"). A regeneração posterior passa a ser entregável do workflow B: o `run_all.py` estendido
   regenera a família em `output/replicated/occupancy/` e compara byte a byte com `output/occupancy/` (nota
   `_note_replicated` de `configs/stages.json`; disjunção conferida por `tests/test_stages_disjoint.py`).
4. **Mutação:** [arquivo privado, não distribuído] (§2.13), relatório em [verificação adversarial privada].
5. **Results:** bloco OCC em `output/results.json`; `tests/test_paper_numbers.py` trava o veredito;
   `make_provenance.py` build + `--verify` exit 0; G9 privado = 88, G7 igual, r1–r4 intactos.
6. **Laudo de impacto:** o que muda em texto, fórmula, tabela e figura pela §2.10 — aplicado no outline e no ledger
   pela sessão principal (com `conferir_outline` e verify r1–r4), nunca por este arquivo. Reenunciar o resultado copia o
   qualificador de regime literal: "com a janela já saturada antes da fonte nova".
