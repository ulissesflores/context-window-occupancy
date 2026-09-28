# Pré-registro — adendo C5 (cotas por `ρ` contra o corte por recência; Corolário 5; limite (d))

> **Translation note (English).** Sanitized copy of a pre-registration document that was frozen in
> Portuguese before any code of the family it specifies existed (sha256 of the private original:
> `6e30e20d4ddc0283743366ee13c7cf5e1319476fd147489059dde13f55fdf807`). Only file paths changed: the `repo/` prefix was dropped
> (paths are relative to the root of this repository; a bare `repo/` became "neste repositório" = in this
> repository), the line giving the root of the private paths was removed, private paths that have a fixed name in
> this repository were mapped to it (`code/`, `tests/`, `data/`, `output/`, `docs/`), and pointers to private files
> were replaced by bracketed placeholders: `[registro privado de estado]` = private state log;
> `[nota privada, não distribuída]` = private note, not distributed; `[verificação adversarial privada]` = private
> adversarial verification; `[script privado, não distribuído]` = private script, not distributed;
> `[cadeia privada de selos]` = private seal chain; `[selo privado, não distribuído]` = private seal configuration,
> not distributed; `[original privado]` = private original of a file whose name in this repository appears in the
> same sentence; `[arquivo privado de desvios, datado; …]` = dated private deviations file, whose sanitized copy goes
> under `data/prereg/`. The private temporary directory is described as temporary. The token-KAT cells of the mixed
> regime already appear under this repository's names (`MIX1`/`MIX2`). Wording, numbers and criteria are otherwise
> verbatim. Every sha256 quoted below refers to the private original of the file it names, except those of the grid
> (`data/quotas_grid.json`, `b0a82de2…`) and of the analytic table (`data/prereg/quotas_analytic_table.txt`,
> `a206f155…`), which are byte-identical in this repository. Glossary: pré-registro = pre-registration; adendo =
> addendum; desvio = deviation; grade = grid; gerador = generator; tabela analítica = analytic table; congelado =
> frozen; rascunho = draft; célula = cell; semente = seed; janela = window; fonte = source; cotas = quotas; corte por
> recência = recency cut; saturado = saturated; decaimento = decay; rival = rival hypothesis; selo = provenance seal;
> critério de quebra = falsification criterion.

> **Status: CONGELADO 2026-09-26 (sha256 registrado no [registro privado de estado], sessão 14, antes de existir qualquer código da família).**
>
> Fecha, para o Corolário 5, o limite (d) dos desvios do KAT-token ("Corolários 4(b) e 5: analíticos"). Não altera
> nenhuma folha selada: pré-registro original `data/prereg/01-displacement-replication.md` (sha256 `b1563d97…`), adendo
> KAT `data/prereg/02-token-kat-addendum.md` (`6c2213ca…`), desvios (`4ceba2bb…`) e desvios-26b (`e83f23aa…`).
> Desvio, se houver, vai a arquivo NOVO datado ([arquivo privado de desvios, datado; cópia sanitizada em `data/prereg/`]) + emenda datada
> em `data/PREREGISTRATION.md`; nunca edição deste arquivo, da grade, do gerador ou da tabela.

## Artefatos congelados (a ordem de criação é a prova de precedência)

| Ordem | Artefato | Caminho | sha256 | Criado (2026-09-26) |
|---|---|---|---|---|
| 1 | Grade (fonte única; vai BYTE A BYTE ao repo como `data/quotas_grid.json`; juiz de vazamento G5 = 0) | `data/quotas_grid.json` | `b0a82de2a4690143996d5bdf196bd91f44e75e9c774c0515b7a9c767ba97a42b` | 18:10:19 |
| 2 | Gerador da tabela analítica (sem sorteio; confere os critérios de desenho com assert nomeado) | `code/quotas_analytic_table.py` | `a6cf81ccd13edf37b9429319d0380ec7f63e816dd7a9e22aecc1d4e097c22a3b` | 18:10:26 |
| 3 | Tabela analítica (stdout do gerador sobre a grade congelada; duas execuções byte-idênticas por `cmp`; G5 = 0) | `data/prereg/quotas_analytic_table.txt` | `a206f1555df554e761b5d9212451ac65ac3bb2082ff765ad7c4b885697569189` | 18:10:38 |
| 4 | Este pré-registro | `data/prereg/08-quotas-addendum.md` | no [registro privado de estado] | depois dos três |
| fonte | Rascunho-fonte (NÃO congelado): §4 (l.850–1131) + §0 + §5 (achados 14–19) | [nota privada, não distribuída] | `99641618b4471a54fb8974d789f3fb0eb0e42062a8ff0a71240817815987956e` | — |

A 1ª linha da tabela congelada é `grade sha256 b0a82de2a4690143996d5bdf196bd91f44e75e9c774c0515b7a9c767ba97a42b · K = 2048 · N = 100000 · sementes = 5 · tag = 8 ·
tol_X = 0.00405`. Evidência auxiliar (não é folha deste pré-registro): o montador da grade
[script privado, não distribuído] (`f68dcf347cd8af2405ac9e64184ae7d1541aff1568b386b285fa538f1c81b2dd`) lê as dez AUC de âncora por código do `celulas.csv` selado do KAT
(nunca redigitadas) e reproduz a grade byte a byte; a conferência por código rascunho × tabela congelada
[script privado, não distribuído] (`6427b4cf733173ed2a70426ee19a7354d2e1492bcecf69ebb464954d0dc28c21`) grava
[nota privada, não distribuída] (`27448bcb887fddeacae752af0198a558f79ae4717cf81479e978052c918b226e`): **172 números conferidos na
precisão exibida pelo rascunho, 169 iguais, 3 divergências** (§14; nenhum número foi ajustado para bater).

> **Convenções.** A marca `[B-crit n]` remete à tabela de achados da §5 do rascunho-fonte (sha256 acima); os achados
> 14–19, que são do C5, estão transcritos no Apêndice A. Caminhos `code/…`, `data/…`, `tests/…`, `output/…` e `docs/…` são os nomes FIXOS do repositório público
> (desenho [nota privada, não distribuída], §"Workflow B" e apêndices A.1/A.2), que o workflow B cria depois do
> workflow A verde; no congelamento nenhum arquivo da família existe neste repositório (§12). Módulos selados são citados pelo
> nome no repo e pela origem privada + sha256. Células mistas do KAT são citadas pelo nome do repositório (MIX1:
> `λ_S = 0,6`; MIX2: `λ_S = 6`). Os scripts do rascunho vivem no scratch persistido
> [nota privada, não distribuída] (lista e sha256 em [nota privada, não distribuída]).

## 0. Decisões transversais que valem para esta família

### 0.1 Um fluxo aleatório por família `[B-crit 1]`

Os quatro rascunhos usavam o mesmo tag `5` em `numpy.random.default_rng([semente, i_celula, i_combo, tag, i_bloco])`:
para o mesmo `(semente, índice, bloco)`, famílias diferentes leriam os mesmos bits, e os quatro veredictos ficariam
correlacionados sem declaração. Tags fixados (registrados no [registro privado de estado], sessão 14, decisão 16b item 2):

| Família | Tag | Observação |
|---|---|---|
| EXP (expoente de `d`) | 5 | — |
| OCC (ocupação × taxa) | 6 | — |
| CMP (fusão, Corolário 4(b)) | 7 | `i_fluxo` no lugar de `i_combo` (0 = `R`; 1 = sorteio partilhado por `RS`/`RF`/`RP`) |
| C5 (cotas, Corolário 5) | 8 | só KNP3 e FIX1; KNP1, KNP2, NUL1 e DEC1 usam, de propósito e declarado, fluxos do KAT (tag 3) |

Tag 3 (KAT) e o fluxo de três entradas da réplica ficam reservados. O teste de pinos de cada família assere o seu tag e
que ele difere de 3 e dos outros três. Nesta família o gerador congelado já assere `tag = 8 ∉ {3, 5, 6, 7}`, a ausência
da chave `tag_r3` e cada fluxo declarado (§9).

### 0.2 Selo e prova — só no repositório (reescrita pela decisão 16b item 1) `[B-crit 2]`

O rascunho propunha um selo privado numerado, na ordem de conclusão, encadeado por `--prev` ao `chain_head` vigente.
**Superado: vale o desenho do repo.** Código de simulação, testes e saídas desta família nascem SÓ neste repositório, e a prova
é a cadeia do próprio repo:

- `make_provenance.py` (build + `--verify`, exit 0) é a prova; as folhas novas entram nos estágios já existentes de
  `configs/stages.json`: **prereg** ← `data/quotas_grid.json` (a grade congelada, byte a byte),
  `data/prereg/quotas_analytic_table.txt` (a tabela congelada) e `data/prereg/08-quotas-addendum.md` (este
  pré-registro, sanitizado); **code** ← `code/quotas.py`, `code/run_quotas.py`,
  `code/quotas_analytic_table.py` e `tests/test_quotas.py`; **data** ← `output/quotas/celulas.csv`;
  **scores** ← `output/quotas/resumo.json` (o bloco da família em `output/results.json` já está no estágio).
- NADA na [cadeia privada de selos]; nenhum [selo privado, não distribuído] novo; nenhum `--prev`; nenhum
  número de selo privado.
- Portões que NÃO mudam: G9 (pytest privado) continua **88** testes; G7 (regeneração módulo mapa) não muda; os selos
  privados r1–r4 ficam intactos (verify exit 0 antes e depois).
- Invariante de replicação: o run completo escreve em diretório NÃO selado; só um passo explícito de publicação grava em
  `output/quotas/` antes do build; `tests/test_stages_disjoint.py` assere a disjunção.

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

- EXP e OCC rodam pelo caminho do KAT (`_uma_tarefa` de `code/run_token_kat.py` + `avaliar_kat` de
  `code/token_kat.py`, sem editar nada) por um único runner fino partilhado, `code/run_grid.py --grid <json>
  --out <dir>`, com o adaptador `{**grade, "tag_r3": grade.get("tag", grade.get("tag_r3"))}`. **O C5 não usa esse
  runner:** as suas políticas leem a história inteira de cada usuário, e o runner é o da família
  (`code/run_quotas.py`). **Nenhuma grade nova tem a chave `tag_r3`**; a do C5 guarda o tag na chave `tag` (o
  gerador assere).
- Parâmetros repetidos entre famílias, declarados: `R ∪ S` de CMP1 (braço `RS`) = `R ∪ S` do KAT S1b; `R ∪ S` de CMP4
  (braço `RS`) = `R ∪ S` do KAT S2b = mistura de KNP2 do C5; mistura de KNP1 = `R ∪ S` do KAT S1a. Só o C5 reusa os
  DADOS selados do KAT (âncoras); o CMP reusa só como teste de identidade, fora do veredito.

### 0.5 Referências

Fechado: ver §13 (`[B-crit 5]` e `[B-crit 20]`).

### 0.6 Tempo (viabilidade)

Base medida: KAT = 1,476·10⁹ eventos gerados em 76 s com 8 processos (1,94·10⁷ eventos/s de parede). Recontagem de
eventos gerados (N = 100.000, 5 sementes):

| Família | Eventos gerados | Parede estimada (8 processos) | Maior simulação isolada (célula × combo × semente) |
|---|---|---|---|
| EXP | 1,962·10⁹ | ~101 s | ~3 s |
| OCC | 4,123·10⁹ | ~212 s | ~3 s |
| CMP | 1,676·10⁹ (+ fusão, ~+50%) | ~130–150 s | ~5 s |
| C5 | 8,42·10⁸ (+ 5–6 políticas, fator ~2) | ~90–120 s | ~3 s |

Todas muito abaixo de 5 min por simulação; o conjunto cabe em ~10 min de parede. Estimativas por escala linear, **não
medições**; pico de memória do CMP (~0,7 GB/processo com 576 eventos/usuário) cabe com 8–12 processos na máquina de 14
CPUs. A tabela analítica congelada do C5 roda em ~12 s (medido: duas execuções).

## 1. Pergunta

O Corolário 5 (outline, bloco 2.3a) é hoje **só analítico**: maximizar `Σ_s n_s d_s²` sujeito a `Σ_s n_s k_s ≤ K` e
`0 ≤ n_s ≤ λ_s T` é a relaxação contínua da mochila; preencher por `ρ_s = d_s²/k_s` decrescente, cada fonte até `λ_s T`,
é ótimo (Dantzig, 1957); a janela por recência é ponto viável do mesmo problema, logo `Δ²_ótimo − Δ²_recência ≥ 0`; sob
(ii), cotas por fonte (os `n_s` mais recentes de cada uma) implementam o ótimo.

Pergunta: numa janela de `K = 2.048` tokens **saturada**, com eventos inteiros e contagens Poisson, a simulação LITERAL
confirma (a) a ordem cotas-por-`ρ` > recência, com o tamanho previsto; (b) que ordenar pela separabilidade POR EVENTO
(`d_s²`, ignora `k`) fica abaixo, podendo ficar abaixo da própria recência; (c) onde as cotas NÃO ganham: com `ρ`
homogêneo (equivalência), com cota FIXA arredondada numa fonte rara (perde) e com decaimento por idade, fora da
hipótese (ii) (perde para a recência)? O caso "sem saturação" (todas devolvem a história inteira) é identidade por
construção e fica no teste de unidade UT-2, não na simulação `[B-crit 17]`.

## 2. O que NÃO se afirma (escopo)

- Ilustrativo; **não é replicação do nuFormer**. Do case: `K = 2.048` e `k ∈ {14, 55}`. `ρ_s` real segue não estimável
  (hipótese vi).
- O Corolário 5 é um fato de programação linear; a simulação **não** o prova (§0.3). O que ela pode falsificar: que a
  implementação literal (eventos inteiros, contagens Poisson, orçamento em tokens) realiza o ganho previsto; que as
  regras ingênuas perdem; e as fronteiras (cota fixa, decaimento). As previsões são EXATAS (não fluidas) em KNP1–KNP3,
  FIX1 e NUL1: esta família testa sobretudo a implementação das políticas e o preditor exato; só DEC1 depende do fluido.
- Todas as políticas dependem só de fonte, tempo e contagens — **nunca** de `x` realizado —, dentro do escopo
  "alocações por fonte, independentes dos atributos realizados". Contagens não dependem de `y` (hipótese v).
- **Produto:** licenciar UMA frase do Corolário 5 e corrigir a PROP (§10). **Nenhum número no corpo; nenhuma figura
  nova no artigo.**

## 3. Modelo gerador (herda o KAT; muda só a política de janela)

`π = 0,2`; Poisson de taxa `λ_s` em `T` dias, independente de `y`; tempos uniformes em `[0, T)`; `x ~ N(d_s·y, 1)`;
custo inteiro `k_s`; leitor = oráculo `Σ_visíveis d_i·(x_i − d_i/2)`, teto de qualquer leitor da mesma janela (Neyman &
Pearson, 1933); AUC por Mann–Whitney com postos médios (Mann & Whitney, 1947). Ordem de sorteio idêntica a
`simular_literal_tokens` de `code/token_kat.py` (origem [original privado]): `y`; contagens Poisson usuários ×
fontes na ordem A, C da grade; tempos; atributos.

**Único desvio do gerador (só em DEC1):** `d_i = d_s·e^{−a_i/τ}`, `a_i = T − t_i`; `x_i ~ N(d_i·y, 1)` e o oráculo usa o
mesmo `d_i`. Com `τ = ∞`, byte-idêntico ao sem decaimento (UT-5). Viola (ii) de propósito.

**Uma história por (célula, semente), lida por TODAS as políticas (pareamento).**

## 4. Políticas (definição literal, fixada aqui; também na chave `_politicas` da grade)

| Id | Política | Regra por usuário (eventos inteiros, orçamento `K`) |
|---|---|---|
| REC | corte por recência | maior sufixo de eventos mais recentes com custo `≤ K`; o evento que estoura cai com os mais antigos (`janela_tokens` de `code/token_kat.py`) |
| RHO | cotas adaptativas por `ρ` | fontes em `ρ_s` decrescente (empate: ordem da grade); `n_s = min(N_s, ⌊resto/k_s⌋)` eventos mais recentes; `resto −= n_s·k_s`; **continua** na fonte seguinte — Dantzig sobre as contagens realizadas |
| FIXf | cotas fixas, piso | `q_s` = guloso por `ρ` sobre as contagens ESPERADAS: `q_s = min(⌊λ_s T⌋, ⌊resto/k_s⌋)`; `n_s = min(N_s, q_s)`; sobra NÃO realocada |
| FIXc | cotas fixas, teto | idem com `⌈λ_s T⌉` |
| TAX | proporcional à taxa | cota fixa `q_s = ⌊λ_s·K/W⌋`, `W = Σ_r λ_r k_r`; `n_s = min(N_s, q_s)` |
| EVT | regra por evento | como RHO, ordem `d_s²` decrescente (ignora `k`) |
| RHOidade | cotas por `ρ` na idade (só DEC1) | prioridade por evento `d_i²/k_s`; varre em ordem decrescente, inclui se couber, senão pula |

**Identidade declarada.** Saturada, a recência aloca `n_s = λ_s·K/W` na forma fluida: já É a proporcional à taxa. TAX é
**controle de equivalência** (estratificar por si não ganha). Com fonte rara o piso corta a fonte (FIX1: cota 1 contra
1,26 esperados na janela) e a identidade quebra por arredondamento — registrado, não testado como equivalência.

## 5. O que a teoria prevê

**Fluida.** Recência: `h = min(T, K/W)`, `Δ²_rec = h·Σ_s λ_s d_s²`. Ótimo (Dantzig), com `c` o item crítico:
`Δ²_ótm = Σ_{s<c} λ_s T d_s² + ρ_c·(K − Σ_{s<c} λ_s T k_s)`. `G = Δ²_ótm − Δ²_rec ≥ 0`, com `G = 0` se, e só se, a janela
não satura ou todos os `ρ_s` são iguais.

**Por usuário (usada como previsão).** Com contagens `N_s`, a janela da REC é ponto viável do PL com tetos `N_s`, cujo
ótimo o guloso RHO atinge a menos do arredondamento do item crítico (`≤ k_max − 1` tokens ociosos). Como
`score | y, D ~ N((y − ½)·D, D)`, `D = Σ_visíveis d_i²` independente de `y`: `AUC = E[Φ(√(D₁ + D₀)/2)]`, `D₁, D₀` iid.

**Previsão exata, sem simulação.** RHO, FIXf, FIXc, TAX e EVT: `D` determinístico nas contagens — soma sobre o suporte
Poisson. REC com duas fontes: composição hipergeométrica do sufixo, com a regra de parada do orçamento. **Conferência
independente da crítica:** um segundo preditor (REC por marcas iid da superposição Poisson, DP sobre a composição; as
demais políticas por soma sobre `±10` desvios do suporte) reproduz as AUC exatas das 5 células na 5ª casa
([verificação adversarial privada], sha256 `c4413a7b…`, bloco 4; saída
[verificação adversarial privada], `7a33da09…`, duas execuções idênticas). Calibração do preditor exato contra as 14 médias
SELADAS do KAT com uma ou duas fontes ([original privado], `389884f7…`; no repo,
`output/kat_token/resumo.json`): erro máximo **0,00133** (sinais mistos), contra 0,00178 da forma fluida (quase
sempre para baixo) — reconferida na congelação por código ([script privado, não distribuído],
`02c74593…`, rodado sobre cópia descartável temporária: `max |média − exata| = 0.00133`, `max |média − fluida| =
0.00178`). Por decisão de desenho, a calibração NÃO entra no gerador congelado (dependeria do `resumo.json` selado e
imprimiria ids de célula que casam o juiz de vazamento): é justificativa da `tol_X`, não previsão congelada.

**Decaimento (DEC1, fluida).** Fonte `s` coberta até a idade `a_s`: `V_s = λ_s d_s² (τ/2)(1 − e^{−2a_s/τ})`. REC:
`a_s = h`. RHO (`ρ` nominal): a fonte de maior `ρ` vai até `min(T, K/(λ_s k_s))`, a seguinte recebe o resto. Ótimo com
idade (enchimento d'água): `a_s = clip((τ/2)·ln(ρ_s/μ), 0, T)` com `Σ_s λ_s k_s a_s = K`. `AUC = Φ(√(ΣV/2))`.

## 6. Hipóteses rivais

| Id (na grade) | Rival | Prevê |
|---|---|---|
| H-REC (`H-REC`) | "a recência já é ótima / qualquer janela cheia empata" | RHO ≤ REC |
| H-EVT (`H-EVT`) | "priorizar a fonte mais informativa por evento" | EVT ≥ RHO e EVT ≥ REC |
| H-FIX (`H-FIX`) | "cota fixa tirada da solução fluida implementa o ótimo" (a PROP lida ao pé da letra) | FIXf ≈ FIXc ≈ RHO > REC |
| H-EST (`H-EST`) | "estratificar por fonte ajuda por si" | TAX > REC |
| H-(ii) (`H-ii`) | "o Corolário 5 vale com decaimento por idade" | RHO > REC também em DEC1 |
| "nenhum canal remove o dano" (`H-CONS`) | rival da Consequência (KNP1) | `ΔAUC_RHO(R -> R ∪ S) < 0` |

`[B-crit 14]` **Nenhum rival é refutável em NUL1.** A previsão exata da teoria em NUL1 dá EVT − REC = +0,0004 e
TAX − REC = +0,0004: o MESMO sinal que H-EVT e H-EST preveem, e nenhum rival declara magnitude. O rascunho listava
"H-EVT: EVT − REC > 0" como rival de NUL1; retirado. NUL1 é **controle de equivalência puro** (`±tol_X`).

## 7. Grade (fixada aqui; fonte única = a grade congelada)

Fonte única: [original privado] (sha256 acima), que vai byte a byte a
`data/quotas_grid.json`. Chave `tag = 8`, sem `tag_r3`; esquema de dados do KAT (`id`, `bloco`, `T`, `R = {A}`,
`S = {C}`, fontes `lam`, `d`, `k`); a história lida por toda política é `R ∪ S` na ordem A, C, e `R` sozinha é a
mistura atual da Consequência. Texto livre da grade em inglês (limpa no juiz de vazamento). `K = 2.048`; `N = 100.000`
por (célula, semente); sementes `0..4`; blocos de 10.000; 6 células = 30 histórias, cada uma lida por todas as políticas.
Critérios de desenho (conferidos por código no gerador congelado, antes de qualquer simulação; todos passaram):
saturado a `z ≥ 2,5`; `≤ 600` eventos por usuário; `|ΔAUC previsto| ≥ 1,2·tol` em toda comparação estrita; o rival
nomeado com previsão oposta (o rival "≈ 0" de FIX1 é refutado por tamanho, C5-G); equivalência prevista dentro de
`tol_X`; `tol_X = 3·ep_dif_kat_max`; fluxos declarados = fluxos selados do KAT nas âncoras; Consequência com `R` já
saturada.

| Célula | Bloco | `T` | Fontes (`λ`, `d`, `k`) | Fluxo `[semente, i_celula, i_combo, tag, i_bloco]` | O que discrimina |
|---|---|---|---|---|---|
| KNP1 | dentro de (i)–(v) | 180 | A (1,2; 0,12; 14) · C (0,5; 0,17; 55) — = `R ∪ S` de S1a (KAT) | `[s, 0, 1, 3, b]` = S1a `R ∪ S` do KAT (âncora) | `ρ_A > ρ_C` mas `d_C² > d_A²`: H-EVT prevê EVT > REC; a teoria, RHO > REC > EVT. Sub-teste da Consequência |
| KNP2 | dentro de (i)–(v) | 180 | A (0,4; 0,23; 55) · C (1,5; 0,16; 14) — = `R ∪ S` de S2b (KAT) | `[s, 3, 1, 3, b]` = S2b `R ∪ S` do KAT (âncora) | espelho: texto forte por evento × compacta forte por token |
| KNP3 | dentro de (i)–(v) | 180 | A (0,2; 0,20; 14) · C (1,0; 0,25; 55) | `[s, 2, 0, 8, b]` | ótimo INTERIOR (teto de A liga): H-EVT prevê EVT ≥ RHO; a teoria, RHO > REC > EVT |
| FIX1 | dentro de (i)–(v) | 90 | A (0,02; 1,0; 14) · C (2,3; 0,08; 14) | `[s, 3, 0, 8, b]` | fonte rara e forte (`λ_A T = 1,8`): H-FIX prevê FIXf ≈ RHO > REC; a teoria, RHO > FIXc > REC > FIXf |
| NUL1 | equivalência | 180 | A (1,2; 0,12; 14) · C (0,5; 0,12·√(55/14) = 0,2378475; 55) | `[s, 0, 1, 3, b]` = o do KNP1 | `ρ_A = ρ_C`: todas dentro de `±tol_X`; **sem rival refutável** `[B-crit 14]` |
| DEC1 | fronteira (viola ii) | 180 | fontes do KNP1, `τ = 60` d (meia-vida de `d` = 41,6 d) | `[s, 0, 1, 3, b]` = o do KNP1 | H-(ii) prevê RHO > REC (+0,0435 na forma fluida, o ganho sem decaimento); a teoria com decaimento prevê REC > RHO |

`d_C` de NUL1 está na grade com precisão completa de float (`0.23784749015162757`), de modo que `ρ_A = ρ_C` vale até a
última casa (o gerador assere com tolerância relativa `10⁻¹²`); o rascunho grafava `0,237846` (truncado, §14). O
`i_celula` de KNP3 e FIX1 é o índice da célula na grade do C5; o de KNP1 e KNP2 é o índice de S1a e S2b na grade do
KAT (o gerador confere contra a grade do KAT: fontes, `T`, índice, `i_combo = 1` e tag 3 = `tag_r3`).

**Células discriminantes: 4** (KNP1, KNP2, KNP3, FIX1), cada uma com rival nomeado que prevê o sinal OPOSTO numa
comparação estrita. NUL1 é equivalência sem rival; DEC1 é fronteira com veredito próprio.

**Sub-teste da Consequência (KNP1)** `[B-crit 18]`. **Com a janela já saturada antes da fonte nova** (`R = {A}` satura
sozinha: `z(R) = 4,74`), a história de `R` é a de `R ∪ S` sem os eventos de C (pareamento). Previsto:
`ΔAUC_RHO(R -> R ∪ S) = 0` (com `N_A ≥ 146` as janelas coincidem evento a evento; `P(N_A < 146) = 1,8·10⁻⁷` para
`N_A ~ Poisson(216)` — o rascunho original dizia `≈ 10⁻⁶`) e `ΔAUC_REC(R -> R ∪ S) = −0,04407` (o dano do Corolário 1).
Declarado: sob o pareamento, `ΔRHO = 0` é quase tautológico (mesmos eventos visíveis, mesmos escores) — confere código,
não conteúdo. Toca a frase "só o desenho do canal remove (…cotas…)" da Consequência.

## 8. Tabela analítica — congelada ANTES de qualquer simulação

**Estado: congelada.** Gerador [original privado] (sha256 `a6cf81ccd13edf37b9429319d0380ec7f63e816dd7a9e22aecc1d4e097c22a3b`), saída
[original privado] (`a206f1555df554e761b5d9212451ac65ac3bb2082ff765ad7c4b885697569189`); no repo, `code/quotas_analytic_table.py`
(porte) e `data/prereg/quotas_analytic_table.txt` (= a tabela congelada, comparada byte a byte). O gerador porta,
sem mudar resultado, a aritmética dos scripts do rascunho no scratch persistido [nota privada, não distribuída]:
[script privado, não distribuído] (`60fc24ec…`), [script privado, não distribuído] (`650732b3…`), [script privado, não distribuído] (`ff8c54c9…`), [script privado, não distribuído] (`63f5c6d3…`) e
[script privado, não distribuído] (`0c55c480…`); saída de referência [nota privada, não distribuída] (`f012454f…`, duas execuções idênticas) e
[nota privada, não distribuída] (`cc5c4b15…`). Diferenças de forma, não de número: o gerador imprime só stdout em precisão fixa
(sem o JSON lateral), calcula a varredura de `τ` deliberadamente (no rascunho ela saía como efeito colateral de import do
[script privado, não distribuído]) e usa as formas fechadas sem decaimento no caso `τ = ∞` (no lugar de `τ = 10⁹`). **Reconferido pela
crítica por método independente (5ª casa) e, na congelação, por código contra este texto (172 números; 3 divergências,
§14).**

| Célula | z | eventos/usuário | REC | RHO | EVT | TAX | FIXf | FIXc | cotas FIXf · FIXc · TAX |
|---|---|---|---|---|---|---|---|---|---|
| KNP1 | 10,57 | 306 | 0,80332 | 0,84738 | 0,76767 | 0,80329 | 0,84738 | 0,84738 | [146, 0] · [146, 0] · [55, 23] |
| KNP2 | 10,94 | 342 | 0,88238 | 0,91419 | 0,83873 | 0,88258 | 0,91419 | 0,91419 | [0, 146] · [0, 146] · [19, 71] |
| KNP3 | 11,25 | 216 | 0,86645 | 0,89578 | 0,85888 | 0,86666 | 0,89316 | 0,89316 | [36, 28] · [36, 28] · [7, 35] |
| FIX1 | 4,33 | 209 | 0,84395 | 0,86993 | 0,86993 | 0,82467 | 0,82467 | 0,85400 | [1, 145] · [2, 144] · [1, 145] |
| NUL1 | 10,57 | 306 | 0,84645 | 0,84738 | 0,84685 | 0,84685 | 0,84738 | 0,84738 | [146, 0] · [146, 0] · [55, 23] |
| DEC1 (fluida) | 10,57 | 306 | 0,72959 | 0,69312 (`ρ` nominal) | — | — | — | — | RHOidade 0,73106 |

**Comparações declaradas** (`tol_X = 0,00405` fixo `[B-crit 15]`; razão = previsto/tol; EP plan. = Hanley–McNeil NÃO
pareado, cota superior do pareado; na grade, chave `comparacoes` de cada célula, com `tipo`, `criterios`, `rival`,
`rival_preve` e `refuta_rival`):

| Célula | Comparação | Tipo | Previsto | tol | Razão | EP plan. | Rival prevê | Critério que refuta o rival |
|---|---|---|---|---|---|---|---|---|
| KNP1 | RHO − REC | estrita | +0,04407 | 0,00405 | 10,9 | 0,00119 | H-REC: ≤ 0 | C5-O |
| KNP1 | REC − EVT | estrita | +0,03565 | 0,00405 | 8,8 | 0,00128 | H-EVT: < 0 | C5-O |
| KNP1 | RHO − EVT | estrita | +0,07971 | 0,00405 | 19,7 | 0,00122 | H-EVT: ≤ 0 | C5-O |
| KNP1 | TAX − REC | equivalência | −0,00003 | 0,00405 | — | 0,00124 | H-EST: > 0 (sem magnitude) | C5-G (só se o rival previsse ≥ 0,004) |
| KNP2 | RHO − REC | estrita | +0,03182 | 0,00405 | 7,9 | 0,00095 | H-REC: ≤ 0 | C5-O |
| KNP2 | REC − EVT | estrita | +0,04364 | 0,00405 | 10,8 | 0,00109 | H-EVT: < 0 | C5-O |
| KNP2 | RHO − EVT | estrita | +0,07546 | 0,00405 | 18,6 | 0,00103 | H-EVT: ≤ 0 | C5-O |
| KNP2 | TAX − REC | equivalência | +0,00021 | 0,00405 | — | 0,00101 | H-EST: > 0 (sem magnitude) | idem |
| KNP3 | RHO − REC | estrita | +0,02933 | 0,00405 | 7,2 | 0,00102 | H-REC: ≤ 0 | C5-O |
| KNP3 | REC − EVT | estrita | +0,00757 | 0,00405 | 1,9 | 0,00108 | H-EVT: < 0 | C5-O |
| KNP3 | RHO − EVT | estrita | +0,03690 | 0,00405 | 9,1 | 0,00103 | H-EVT: ≤ 0 | C5-O |
| FIX1 | RHO − FIXc | estrita | +0,01593 | 0,00405 | 3,9 | 0,00108 | H-FIX: ≈ 0 | **C5-G** `[B-crit 19]` (o sinal sozinho não refuta "≈ 0") |
| FIX1 | FIXc − REC | estrita | +0,01005 | 0,00405 | 2,5 | 0,00112 | — | — |
| FIX1 | REC − FIXf | estrita | +0,01929 | 0,00405 | 4,8 | 0,00116 | H-FIX: < 0 (FIXf ganha) | C5-O |
| FIX1 | RHO − REC | estrita | +0,02598 | 0,00405 | 6,4 | 0,00110 | H-REC: ≤ 0 | C5-O |
| NUL1 | RHO − REC · EVT − REC · TAX − REC · RHO − EVT | equivalência | +0,00093 · +0,00040 · +0,00040 · +0,00053 | 0,00405 | — | 0,00113 | — `[B-crit 14]` | — |
| DEC1 | REC − RHO | estrita | +0,03647 | 0,01467 (report-only) | 2,5 | 0,00139 | H-(ii): −0,0435 | C5-D (sinal) |
| DEC1 | RHOidade − RHO | estrita | +0,03794 | 0,01467 (report-only) | 2,6 | 0,00139 | — | C5-D (sinal) |
| DEC1 | RHOidade − REC | report-only `[B-crit 16]` | +0,00147 | 0,01467 | — | 0,00137 | — | — |
| KNP1 | Consequência: ΔRHO(R -> R∪S) · ΔREC(R -> R∪S) | equivalência · estrita | 0 · −0,04407 | 0,00405 | — · 10,9 | 0,00113 · 0,00119 | "nenhum canal remove o dano": ΔRHO < 0 | C5-C |

**Varredura do FIX1 (cota da fonte rara, `q_A = 0..6`; C recebe `⌊(K − q_A·k_A)/k_C⌋`, sem realocação):** FIX − REC =
−0,0911 · **−0,0193** · **+0,0101** · +0,0207 · +0,0239 · +0,0246 · +0,0245. Com piso (`q_A = 1`) a cota fixa perde da
recência; com teto (`q_A = 2`) ganha; com `q_A ≥ 3` fica a menos de 0,006 da RHO (RHO − FIX = 0,00525 · 0,00205 ·
0,00140 · 0,00149). Leitura licenciada: "sensível à cota da fonte rara", nunca "cota fixa perde".

**Varredura do DEC1 (`τ` em dias; REC − RHO):** 30 -> +0,0426 · 45 -> +0,0415 · **60 -> +0,0365** · 90 -> +0,0243 ·
120 -> +0,0138 · 180 -> −0,0007 (cruzamento perto de `τ ≈ 180`) · ∞ -> −0,0435 (sem decaimento; a AUC exata dá +0,0441
em RHO − REC). O ótimo com idade fica a ≤ 0,0051 da REC para `τ ≤ 120` (RHOidade − REC = +0,00022 · +0,00075 · +0,00147
· +0,00317 · +0,00501; o rascunho dizia "≤ 0,005", que falha por 0,00001 em `τ = 120`, §14).

## 9. N, fluxos, métrica e regra de decisão

- `N = 100.000` por (célula, semente), sementes `0..4`, blocos de 10.000 (até 342 eventos/usuário).
- **Âncoras byte a byte:** KNP1 usa o fluxo do KAT S1a/`R ∪ S`, `default_rng([semente, 0, 1, 3, i_bloco])`; KNP2 o do
  KAT S2b/`R ∪ S`, `default_rng([semente, 3, 1, 3, i_bloco])`. A AUC da REC nessas células reproduz, por semente, a
  coluna `auc` das LINHAS da célula (S1a ou S2b), combo `RS`, de `output/kat_token/celulas.csv`, com igualdade de
  `repr`. A comparação é POR LINHA, nunca pelo sha256 do arquivo: o `celulas.csv` do repo difere do
  [original privado] (sha256 `aea196a2…`) pela renomeação MIX1/MIX2, que não toca S1a nem S2b. S1a:
  0,8011109275687086 · 0,8013735035676965 · 0,8034060967389719 · 0,803637877619022 · 0,8033566394616265. S2b (acréscimo
  da congelação, lido por código do arquivo selado, nunca redigitado): 0,8815576561089443 · 0,880261843817808 ·
  0,8825051777122616 · 0,8829188003895213 · 0,8826501920909554. Os dez valores estão na grade
  (`ancora.auc_rec_por_semente`). Falha aborta o run antes de qualquer critério. **Declarado:** o nível da REC nessas
  duas células já é conhecido (selado); a evidência nova é das outras políticas sobre as mesmas histórias.
- DEC1 e NUL1 usam o MESMO fluxo do KNP1 (mesmas contagens, tempos e ruído normal padronizado; muda só a média de `x`):
  a inversão de ordem entre KNP1 e DEC1 fica atribuível só a `τ`.
- KNP3 e FIX1: `default_rng([semente, i_celula, 0, 8, i_bloco])`, com `i_celula` = 2 (KNP3) e 3 (FIX1), declarados na
  chave `fluxo` de cada célula — **tag 8, exclusivo desta família** `[B-crit 1]` (o rascunho usava 5).
- **Métrica:** AUC de Mann–Whitney por (célula, semente, política); diferença pareada por semente; média das 5;
  `EP_par` = desvio-padrão entre sementes (`ddof = 1`)/√5. Report-only: sinal por semente; fração de usuários com
  `D_RHO < D_REC` (esperado ≈ 0); ociosos por política; fração saturada; na Consequência, usuários cuja janela RHO
  difere entre `R` e `R ∪ S`.

**Tolerância `[B-crit 15]`.** `tol_X = 0,00405` **fixo** (3 × 0,00135, o maior `ep_dif` NÃO pareado do KAT: S1a,
0,0013467…, arredondado a 5 casas; chaves `ep_dif_kat_max` e `tol_X` da grade). O rascunho original usava
`max(0,00405; 3·EP_emp)`, tolerância que cresce com o ruído do próprio run (um run ruidoso ou defeituoso afrouxaria o
próprio critério). Agora: se `3·EP_par > 0,00405` numa comparação, ela é **sem poder** e reprova (regra do KAT).
Calibração retro: erro máximo 0,00133 da previsão exata nas médias seladas do KAT, ~3× abaixo de `tol_X` (§5).

O teste **passa** se, e só se, UT-1 a UT-6 verdes, as âncoras batem e:

- **C5-O (ordem):** em cada comparação ESTRITA de KNP1, KNP2, KNP3 e FIX1, o sinal da média pareada é o previsto. Uma
  discordância reprova. `|previsto| < 3·EP_par` = empate: reprova por falta de poder.
- **C5-G (tamanho):** em cada comparação declarada dessas células e de NUL1, `|média pareada − previsto| ≤ tol_X`. Um
  estouro reprova. (É o C5-G que refuta H-FIX em `RHO − FIXc`.)
- **C5-C (Consequência, KNP1):** `|ΔAUC_RHO(R -> R ∪ S)| ≤ tol_X` e `ΔAUC_REC(R -> R ∪ S) < 0` com
  `|empírico − (−0,04407)| ≤ tol_X`.
- **C5-N (nível, secundário):** em cada (célula, política) com previsão exata, `|média(AUC) − AUC exata| ≤ tol_X`.
  Reprovado com C5-O/C5-G aprovados -> o texto não usa nível.

**Bloco de fronteira (veredito próprio) `[B-crit 16]`:**

- **C5-D (só sinal):** em DEC1, `REC − RHO > 0` e `RHOidade − RHO > 0`; `|previsto| < 3·EP_par` = empate, reprova o
  bloco. O nível (`|empírico − previsto| ≤ tol_F`, `tol_F = 0,0079 + disc(0,0027) + 0,00405 = 0,01467`, com `disc` = viés
  de eventos inteiros calculado sobre o `Δ²` da REC COM decaimento) e `|RHOidade − REC|` são report-only: a base 0,0079
  foi calibrada no r1 SEM decaimento e não se transfere a uma diferença pareada sob decaimento; o rascunho original usava
  esse nível como critério. (O rascunho grafava `disc(0,0032)`, que é o valor SEM decaimento; o total 0,01467 sempre
  usou o valor com decaimento, §14.)

## 10. Critério de quebra e leitura por desfecho

- **Corolário 5 implementado:** RHO abaixo de REC além de `tol_X` em célula saturada com `ρ` heterogêneo (contradiz a
  dominância usuário a usuário), ou ganho RHO − REC fora de `tol_X` do previsto.
- **Regra por evento:** EVT ≥ REC em KNP1 ou KNP2, ou EVT ≥ RHO em KNP3.
- **Cota fixa:** FIXf ≥ REC ou FIXc ≥ RHO em FIX1.
- **Equivalência:** qualquer política fora de `tol_X` da REC em NUL1.
- **Consequência:** ΔRHO(R -> R ∪ S) < −tol_X em KNP1.
- **Fronteira:** RHO ≥ REC em DEC1.

| Desfecho | Texto (2.3a e Consequência) | Fórmula | Tabela | Figura | Ledger / outline |
|---|---|---|---|---|---|
| **Tudo passa** | `[B-crit 17]` frase licenciada no corpo: *"com a janela saturada e `ρ_s` heterogêneo, cotas por fonte **adaptativas** na ordem de `ρ_s` (Dantzig, 1957) superam o corte por recência, e ordenar pela separabilidade por evento pode ficar abaixo da própria recência; conferido por simulação literal por orçamento de tokens"*. Fica FORA da frase do corpo (vai ao `docs/THEORY.md`, com o status de cada uma): "com `ρ_s` homogêneo, as políticas empatam dentro de ±0,004 AUC (equivalência, NUL1)" e "sem saturação, todas devolvem a história inteira (por construção, UT-2)". PROP: "janela estratificada por fonte com cotas ordenadas por `ρ_s`" -> "cotas por fonte **adaptativas** ordenadas por `ρ_s` (a sobra de uma fonte passa à seguinte)". Consequência: "cotas" -> "cotas adaptativas" | nenhuma nova no corpo; no `docs/THEORY.md`: versão por usuário e `AUC = E[Φ(√(D₁+D₀)/2)]` | nenhuma no artigo; tabela das 6 células no `docs/THEORY.md` / bloco da família em `output/results.json` (EN) | nenhuma no artigo | "Corolários 4(b) e 5: analíticos" -> "Corolário 5: conferido (adendo cotas-c5)" (4(b) conforme o CMP); chave `[C5-cotas-resultado]`; `[TEO-corolario-5]` aponta para ela |
| **C5-D passa** (com o acima) | "com decaimento por idade o objetivo muda e a recência fica em parte justificada" -> "com decaimento por idade a ordem usa `ρ` na idade do evento; o `ρ` nominal pode perder da recência" (sem "perto do ótimo": o nível é report-only) | `V_s(a)` só no `docs/THEORY.md` | — | — | chave `[C5-cotas-decaimento]` |
| **C5-D reprova** | texto do decaimento fica como está, "analítico" | — | — | — | desvio datado |
| **FIX1 reprova** (C5-O/C5-G) | PROP sem "adaptativas" e sem a ressalva da fonte rara; resto vale se KNP1–3 passarem | — | — | — | desvio datado |
| **KNP3 reprova só em REC − EVT** (razão 1,9, a menor margem) | a frase perde "pode ficar abaixo da própria recência"; mantém RHO > EVT se as outras passarem | — | — | — | desvio datado |
| **NUL1 reprova** | o `docs/THEORY.md` perde a linha de equivalência; investigar ociosos antes de qualquer leitura | — | — | — | desvio datado |
| **C5-C reprova** | Consequência fica sem "cotas" testadas | — | — | — | desvio datado |
| **C5-O reprova em KNP1 ou KNP2** | Corolário 5 fica "analítico"; PROP rebaixada a "hipótese de desenho, não conferida"; a frase não entra | — | — | — | desvio datado |
| **Só C5-N reprova** | o texto não usa nível | — | — | — | registro |

"Desvio datado" = arquivo novo [arquivo privado de desvios, datado; cópia sanitizada em `data/prereg/`] + emenda datada em
`data/PREREGISTRATION.md`; o veredito da família fica num bloco próprio de `output/results.json`, travado por
`tests/test_paper_numbers.py`. Orçamento: a frase e "adaptativas" somam ~15–20 palavras à teoria (~170); se
estourar, vale a regra do outline (a Observação do regime misto ou o 4(b) vão à legenda da Figura 3 ou ao
`docs/THEORY.md`).

## 11. Testes de unidade, mutação, tempo e reuso

Testes novos: `tests/test_quotas.py` (nenhum arquivo de teste da família no privado; nunca
`tests/test_displacement*.py` nem `tests/test_token_kat*.py`).

- **UT-1 — identidade com o selado.** Mesmo `rng`: o caminho REC devolve escores byte-idênticos a
  `simular_literal_tokens` (`code/token_kat.py`) numa célula pequena (com empates de tempo forçados).
- **UT-2 — políticas.** Histórias à mão: RHO/EVT pegam os mais recentes, respeitam `≤ K`, passam a sobra, desempatam
  `ρ` pela ordem da grade; FIXf/FIXc/TAX nunca excedem a cota e não realocam; história com custo `≤ K` -> todas devolvem
  tudo (é aqui que "sem saturação, empatam" é conferido); vazia -> janela vazia; custo não positivo -> erro.
- **UT-3 — previsão exata.** O módulo analítico (`code/quotas_analytic_table.py`) reproduz a tabela congelada byte
  a byte; REC hipergeométrica = binomial para `k` homogêneo (`≤ 10⁻⁹`) e = força bruta sobre TODAS as permutações em
  histórias pequenas (`N_A, N_C ≤ 6`, `K` reduzido).
- **UT-4 — pareamento.** Todas as políticas leem o mesmo vetor de eventos; o `R` da Consequência é o `R ∪ S` sem C.
- **UT-5 — decaimento.** `τ = ∞` -> gerador e escores byte-idênticos; `D` do oráculo = `Σ d_i²`.
- **UT-6 — independência de `x` e tag.** Permutar `x` dentro da fonte não muda janela; `grade["tag"] == 8`,
  `8 ∉ {3, 5, 6, 7}` `[B-crit 1]`; fluxos declarados de cada célula = os da §9.

**Mutação** (harness PRIVADO [script privado, não distribuído], sobre cópia descartável do repo FORA dele, em diretório temporário;
relatório [nota privada, não distribuída]; o repo cita o resultado só em
`REPRODUCIBILITY.md`; mensagem do assert que matou cada mutante impressa e conferida; pytest com `--color=no`):
(1) RHO sem passar a sobra; (2) RHO que PARA na primeira fonte que não cabe; (3) ordem por `d²` no lugar de `ρ`; (4)
cotas com os mais ANTIGOS; (5) `<` no lugar de `≤`; (6) TAX com `λ_s k_s`; (7) FIXc com piso; (8) REC hipergeométrica
com `P(próximo = A)` usando `N_C`; (9) pareamento quebrado; (10) oráculo com `d_s` nominal em DEC1; (11) fluxo do KNP1
diferente do KAT (quebra a âncora); (12) `x` influenciando a janela; **(13) `tol_X` recalculado dos dados**
`[B-crit 15]`; **(14) tag 3 ou de outra família nos fluxos de KNP3/FIX1** `[B-crit 1]`.

**Tempo:** 8,42·10⁸ eventos (recontado) -> ~43 s de geração com 8 processos; com as 5–6 políticas (fator ~2), **~90–120 s**
(estimativa; o gerador não foi cronometrado para não rodar simulação). Tabela analítica: ~12 s (medido).

**Reuso (só importado, nunca editado):**

- `code/displacement.py` ← [original privado] (sha256 `616b2445a6479f1fde7c1ff6d980dca12887be9743633484bfad21925b36a4ec`): `auc_mann_whitney`, `PI`, `se_hanley_mcneil`, `janela_ultimos`.
- `code/token_kat.py` ← [original privado] (`b70c6a2e729d3b6ecd58b59dc79c9e74697fcd6ce51b606e170b540497c245af`): `simular_literal_tokens`, `janela_tokens`, `delta2_fluido`, `auc_fluida`.
- `code/token_kat_analytic_table.py` ← [original privado] (`2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`): `tolerancia`, `z_saturacao`, `ep_hanley_mcneil`, `inclinacao` (o gerador congelado do C5 importa também `W`, `delta2`, `auc`).
- Padrão do runner: `code/run_token_kat.py` ← [original privado] (`fe1b61cbee6ba6b8a4628ddaa742f820f4120b4b4adf48f71b17a5669a803efc`).
- Saídas seladas do KAT: `output/kat_token/celulas.csv` e `output/kat_token/resumo.json` (âncoras e calibração).

**Código novo da família (nasce SÓ no repo; `code/` sem `__init__.py`, entra no `sys.path`, nunca `import code`):**
`code/quotas.py` (políticas), `code/run_quotas.py` (runner), `code/quotas_analytic_table.py` (porte do
gerador congelado: `--grade` padrão `data/quotas_grid.json`, `--grade-kat` padrão `data/kat_token_grid.json`,
módulo selado importado como `token_kat_analytic_table`; identificadores verbatim; stdout comparado byte a byte com
`data/prereg/quotas_analytic_table.txt`), `tests/test_quotas.py`; saídas em `output/quotas/`
(`celulas.csv`, `resumo.json`). **Selo:** §0.2 (sem número de selo privado, sem `--prev`).

## 12. Estado: congelado — o que o workflow B faz depois

No congelamento (18:14 BRT, `ls`), NÃO existe `code/quotas.py`, `code/run_quotas.py`,
`code/quotas_analytic_table.py`, `data/quotas_grid.json`, `data/prereg/quotas_analytic_table.txt`,
`data/prereg/08-quotas-addendum.md`, `tests/test_quotas.py` nem `output/quotas/`. O workflow B, depois
do workflow A verde (e na fila C5 > CMP > OCC > EXP), faz, nesta ordem:

1. **Porte do pré-registro:** grade byte a byte -> `data/quotas_grid.json`; gerador -> `code/quotas_analytic_table.py`
   com stdout idêntico à tabela congelada -> `data/prereg/quotas_analytic_table.txt`; este arquivo sanitizado
   (caminhos pelo mapa A.2, nota de tradução) -> `data/prereg/08-quotas-addendum.md`; emenda datada em
   `data/PREREGISTRATION.md`.
2. **TDD:** UT-1 a UT-6 escritos e vermelhos antes de `code/quotas.py` e `code/run_quotas.py`; depois verdes.
3. **Run:** `N = 100.000` × 5 sementes, âncoras conferidas antes de qualquer critério; escrita em diretório não selado;
   publicação explícita em `output/quotas/`.
4. **Mutação:** os 14 mutantes da §11 (`--color=no`, mensagem do assert impressa).
5. **Results:** bloco da família em `output/results.json`; `tests/test_paper_numbers.py` trava o veredito;
   folhas novas nos estágios de `configs/stages.json` (§0.2); `make_provenance.py` build + `--verify` exit 0;
   laço verde do [script privado, não distribuído] (G9 = 88; G7 igual; r1–r4 intactos).
6. **Laudo de impacto:** o que muda em texto/fórmula/tabela/figura/ledger pela §10; quem aplica no outline/ledger é a
   sessão principal ([script privado, não distribuído], [script privado, não distribuído], verify r1–r4). Resultado que contradiga corolário ou frase
   licenciada -> desvio novo datado, nunca edição de selado.

## 13. Referências (APA 7; campo `apa7` de [nota privada, não distribuída], sha256 `7e8ed08f…`, copiado verbatim) `[B-crit 5]` `[B-crit 20]`

- Dantzig, G. B. (1957). Discrete-variable extremum problems. *Operations Research, 5*(2), 266–288. https://doi.org/10.1287/opre.5.2.266
- Hanley, J. A., & McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology, 143*(1), 29–36. https://doi.org/10.1148/radiology.143.1.7063747
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491
- Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient tests of statistical hypotheses. *Philosophical Transactions of the Royal Society of London. Series A, Containing Papers of a Mathematical or Physical Character, 231*(694–706), 289–337. https://doi.org/10.1098/rsta.1933.0009

Nota: Kaul, Yates e Gruteser (2012), chave `kaul2012aoi` de [nota privada, não distribuída] (VERIFICADA,
Crossref), fica FORA desta lista: só entra se o texto do decaimento tocar a ponte com Age of Information, e esse
registro ainda não tem campo `apa7` (a referência não é redigida à mão).

## 14. Divergências rascunho × congelado (conferência por código; nenhum número foi ajustado)

| # | Onde | Rascunho | Congelado | Causa | Tratamento aqui |
|---|---|---|---|---|---|
| 1 | §4.8, varredura do DEC1 | "o ótimo com idade fica a ≤ 0,005 da REC para `τ ≤ 120`" | RHOidade − REC = +0,00501 em `τ = 120` (0,00500999…) | arredondamento do texto: a 5ª casa passa do limite | texto trocado por "≤ 0,0051", com os cinco valores (§8) |
| 2 | §4.7, célula NUL1 | `d_C = 0,237846` | `0,12·√(55/14) = 0,2378474901…` (0,237847 a 6 casas) | valor truncado no texto; os scripts do rascunho sempre usaram a fórmula, então nenhuma AUC muda | grade com o float completo; texto com 0,2378475 (§7) |
| 3 | §4.9, `tol_F` | `0,0079 + disc(0,0032) + 0,00405 = 0,01467` | `disc` = 0,0027 (0,0027173…); total 0,01467 | 0,0032 (0,0031793…) é o `disc` do `Δ²` da REC SEM decaimento; o total sempre usou o `Δ²` COM decaimento | parcela corrigida para 0,0027; total inalterado (§9) |

## Apêndice A — achados da crítica que tocam o C5 (§5 do rascunho-fonte, linhas 14–19, transcritos)

| # | Severidade | Rascunho | Achado | Correção aplicada |
|---|---|---|---|---|
| 14 | ALTA | C5 | NUL1 listava "H-EVT: EVT − REC > 0" como rival, mas a previsão exata da teoria dá EVT − REC = +0,0004 e TAX − REC = +0,0004 (recálculo): mesmo sinal; nenhum rival declara magnitude; NUL1 não refuta nada por sinal | Aplicada: NUL1 = controle de equivalência puro, coluna de rival "—"; "com `ρ` homogêneo, empatam" só no `THEORY.md` como "dentro de ±0,004 AUC" (§4.6, §4.7, §4.10) |
| 15 | MÉDIA | C5 | `tol_X = max(0,00405; 3·EP_emp)`: tolerância que cresce com o ruído do próprio run (grau de liberdade pós-hoc; run ruidoso ou defeituoso afrouxa o próprio critério) | Aplicada: `tol_X = 0,00405` fixo; `3·EP_par > 0,00405` = sem poder -> reprova; mutante 13 (§4.9, §4.11) |
| 16 | MÉDIA | C5 | C5-D usava nível com `tol_F`, cuja base 0,0079 foi calibrada no r1 sem decaimento; não se transfere a diferença pareada sob decaimento | Aplicada: C5-D só por sinal; nível e `RHOidade ≈ REC` report-only; texto do decaimento sem "perto do ótimo" (§4.9, §4.10) |
| 17 | MÉDIA | C5 | "Sem saturação, empatam" estava sob "conferido por simulação literal", mas é identidade por construção (UT-2), sem simulação | Aplicada: tirado da frase do corpo; vai ao `THEORY.md` como "por construção" (§4.1, §4.10) |
| 18 | BAIXA | C5 | Sub-teste da Consequência sem o qualificador literal de regime; `P(N_A < 146)` dada como `≈ 10⁻⁶` (correto: 1,8·10⁻⁷, `N_A ~ Poisson(216)`); `ΔRHO = 0` é quase tautológico sob pareamento | Aplicada: "com a janela já saturada antes da fonte nova" (`z(R) = 4,74`), número corrigido, tautologia declarada (§4.7) |
| 19 | BAIXA | C5 | Em FIX1, H-FIX prevê `RHO − FIXc ≈ 0` — não é sinal oposto; o C5-O sozinho não o refuta | Aplicada: coluna "critério que refuta o rival" na tabela de comparações; em `RHO − FIXc` é o C5-G (§4.8) |

Os achados transversais 1 (tags), 2 (selo; aqui reescrito pela decisão 16b item 1), 3 (limite comum), 4 e 6 (maquinário),
5 (referências, fechado pelo `refs-verificadas-teoria.jsonl`) e 20 (norma de citação = APA 7, decisão D2) estão
aplicados em §0 e §13.
