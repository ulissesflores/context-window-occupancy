# Pré-registro — adendo CMP: fusão de eventos (Corolário 4(b)) por orçamento de tokens (limite (c))

> **Translation note (English).** Sanitized copy of the CMP pre-registration addendum, frozen in Portuguese on
> 2026-09-26 before any code of this family existed; the private original has sha256
> `f55d02eddf723b0d215759cf2e9f4c2d0296747afab0b1eddb4296eee27c1585`. Only file paths, pointers to private material
> and one table-header word changed. Paths were mapped to the paths of this repository (`code/`, `tests/`, `data/`,
> `output/`, `configs/`, `docs/`; the `repo/` prefix of the original is dropped). Pointers to private material were
> replaced by bracketed placeholders: `[registro privado de estado]` = private state log;
> `[nota privada, não distribuída]` = private note, not distributed; `[verificação adversarial privada]` = private
> adversarial verification (mutation harness and its report); `[selo privado, não distribuído]` = private provenance
> seal and the sealed private code and outputs it covers, not distributed; `[cadeia privada de selos]` = private chain
> of seals; `[portão privado de aceite]` = private acceptance gate of this repository. Bare file names of private
> evidence (draft design and recomputation scripts, the verified-references file, the Crossref captures, the sealed
> modules reused here, the mutation harness) are kept next to their sha256 or their placeholder, so that each can be
> matched to its private original. The header of the second column of the rival-hypotheses table (§4) reads
> `formulação`, a Portuguese synonym of the original header word (both mean "statement"). Wording, numbers, criteria
> and the literal stdout blocks of §7 are otherwise verbatim. Every sha256 quoted below refers to the private original of the file it names, except the grid
> (`data/fusion_grid.json`, `869127a0…`) and the analytic table (`data/prereg/fusion_analytic_table.txt`,
> `a4f55d6b…`), which are byte-identical in this repository; the generator `code/fusion_analytic_table.py` is a port
> whose stdout on that grid reproduces the table byte for byte (FU4(b)), so its own sha256 differs from the private
> `fb06ec6a…` quoted in the header table. Glossary: pré-registro = pre-registration; adendo = addendum; desvio =
> deviation; grade = grid; tabela analítica = analytic table; gerador = generator; célula = cell; braço = arm; semente
> = seed; janela = window; fusão / fundida = fusion / fused; bloco = block; sem perda / com perda = lossless / lossy;
> sat / nao / misto = saturated / unsaturated / mixed; melhora / piora / nulo = improves / worsens / null; critério /
> só reportado = criterion / report-only; selo = provenance seal; outline = private draft of the article, whose block
> 2.3a is rendered in English in `docs/THEORY.md`; corpo = article body; ledger = private claims ledger (its sanitized
> part is `data/claims-ledger.csv`); `[B-crit n]` = finding n of the private adversarial critique of the draft;
> `conferir_outline` + verify = private checks of the outline and of the private seals. The two regime qualifiers
> translate literally:
> "com a janela já saturada antes da fonte nova" = "with the window already saturated before the new source";
> "sem saturação mesmo com a fonte nova" = "without saturation even with the new source".

> [!IMPORTANT]
> **Status: CONGELADO 2026-09-26 (sha256 registrado no [registro privado de estado], sessão 14, antes de existir qualquer código da família).**
> Congelado na ordem grade -> gerador -> tabela analítica (duas execuções byte-idênticas) -> este arquivo. Nenhuma
> simulação de desfecho foi rodada: nenhum `x` sorteado, nenhuma AUC de Mann–Whitney sobre esta grade.

| Artefato congelado | Caminho | sha256 |
|---|---|---|
| grade | `data/fusion_grid.json` | `869127a0cc6aa6e8bbc56840eb6b907ac354d5110521adc87dd69a5869951de6` |
| gerador da tabela analítica | `code/fusion_analytic_table.py` | `fb06ec6ae08726372d40c474627d9f6dfe4a5a7ae5ba72706d5d831305811508` |
| tabela analítica (stdout do gerador sobre a grade) | `data/prereg/fusion_analytic_table.txt` | `a4f55d6bbd3233c4edaa56c86652be1e8d43a5c62e9f0ff889361758146bcb2d` |
| rascunho-fonte (NÃO congelado; §0, §3 e linhas 10–13 da §5) | `rascunho-prereg-B-2026-09-26.md` [nota privada, não distribuída] | `99641618b4471a54fb8974d789f3fb0eb0e42062a8ff0a71240817815987956e` |

- **Raiz dos caminhos:** a raiz deste repositório. Caminhos `code/…`, `tests/…`, `data/…`, `output/…`, `configs/…` e
  `docs/…` = este repositório, com os nomes fixos do desenho (`repo-desenho-2026-09-26.md`, [nota privada, não distribuída], §A.1, sha256
  `6fc3c6df953d1b3740d11dadf8ccf59029b142cf7327edab6df3791d26cba95b`) e da decisão 16b do [registro privado de estado]. No congelamento, nenhum
  deles existe (prova por `ls` registrada no [registro privado de estado]).
- **Não altera nenhuma folha selada:** `data/prereg/01-displacement-replication.md`, `data/prereg/02-token-kat-addendum.md`,
  os dois arquivos de desvios do KAT, nem código ou saída selados em r1–r4. **Este arquivo não recebe o resultado** (vai
  para `output/fusion/` e para o bloco da família em `output/results.json`); desvio, se houver, vai para arquivo
  próprio datado.
- **Marcas `[B-crit n]`:** remetem à tabela de achados da §5 do rascunho-fonte (sha256 acima).
- **Células mistas do KAT** são citadas pelo nome do repositório (MIX1: `λ_S = 0,6`; MIX2: `λ_S = 6`).
- **Evidência herdada do rascunho** (scratch persistido [nota privada, não distribuída]): desenho
  `design_cmp.py` (`d76480a9859f4c14776590005f585687871f3e8ac531a4c5c5e061beb8f11de9`) e `design_cmp_final.py`
  (`ce78cae17aca28ef335be1e89080b662af7abc90f08a60bac5f06f0644a9922c`), grade-rascunho `grade-cmp-rascunho.json`
  (`5adb3b7a518f88f322b555758d5b6115a7f0adaad413c6b6daa6c2f4be4fcb86`), saída `tabela-cmp-rascunho.txt`
  (`46dce7877cec3f9d3f4fe4165a9f0f517203068e98133a6bf0f15814bf87e597`); recálculo independente da crítica
  `critica_B_recalc.py` (`c4413a7be352cb2f2307bbe6ab8c55314359408c38bf3734b41303d8f7c62fb3`), duas execuções
  byte-idênticas (`critica_B_recalc_run1.txt` = `critica_B_recalc_run2.txt` =
  `7a33da0912f4604c3781c0f81e58a6d9abaad3ed4f2efb1a3e6799559090451c`). O gerador congelado é porte do par `design_cmp*`:
  as células da grade congelada são as da grade-rascunho, e o gerador reproduz as grandezas do desenho com igualdade
  exata de float (330 comparações, 0 diferenças, conferido por código no congelamento).
- **Histórico:** o rascunho original do CMP foi escrito em modo degradado (advisor fora por limite de uso); a crítica
  adversarial do rascunho B foi o primeiro escrutínio externo dele; as decisões transversais foram fixadas pelo advisor
  nativo ([registro privado de estado], entrada 16b).

## 0. Decisões transversais que valem para esta família

**0.1 Um fluxo aleatório por família `[B-crit 1]`.** Os quatro rascunhos usavam o mesmo tag `5` em
`numpy.random.default_rng([semente, i_celula, i_combo, tag, i_bloco])`: para o mesmo `(semente, índice, bloco)`, famílias
diferentes leriam os mesmos bits, e os quatro veredictos ficariam correlacionados sem declaração. Tags fixados
(decisão 16b.2 do [registro privado de estado]):

| Família | Tag | Observação |
|---|---|---|
| EXP (expoente de `d`) | 5 | — |
| OCC (ocupação × taxa) | 6 | — |
| CMP (fusão, Corolário 4(b)) | 7 | `i_fluxo` no lugar de `i_combo` (0 = `R`; 1 = sorteio partilhado por `RS`/`RF`/`RP`) |
| C5 (cotas, Corolário 5) | 8 | só KNP3 e FIX1; KNP1, KNP2, NUL1 e DEC1 usam, de propósito e declarado, fluxos do KAT (tag 3) |

Tag 3 (r3) e o fluxo de três entradas do r1 ficam reservados. O teste de pinos de cada família assere o seu tag e que
ele difere de 3 e dos outros três. Nesta família, `i_celula` = posição da célula (base 0) na lista `celulas` da grade
congelada; a grade guarda o tag na chave `tag` (nunca `tag_r3`).

**0.2 Selo: a §0.2 do rascunho NÃO vale `[B-crit 2]`.** O rascunho propunha configs privadas por família
(`stages-*.json`) e o número do selo privado (r5 em diante) com `--prev` na ordem de conclusão. A decisão
16b.1 do [registro privado de estado] a substitui: código de simulação, testes e saídas desta família nascem SÓ neste repositório, e a prova é o
`make_provenance.py` do repositório. A seção de selo reescrita está na §10.

**0.3 Limite comum, declarado uma vez `[B-crit 3]`.** Com o gerador fixado (Poisson, `x ~ N(d_s·y, 1)`) e o leitor
oráculo `Σ d_s(x_i − d_s/2)`, o expoente 2 de `d`, a ponderação pela ocupação, a suficiência de `Σx` na fusão e a
dominância usuário a usuário das cotas por `ρ` são **identidades algébricas** do modelo. Nenhuma das quatro famílias
pode falsificar essa álgebra. O que cada uma pode falsificar: (a) a aproximação fluida (hipótese iii), e a previsão
exata onde ela é usada; (b) a implementação literal (janela, fusão, políticas, leitor). As regras rivais são regras de
bolso, não mecanismos que o gerador realize: a simulação só se comportaria como um rival se o código tivesse o defeito
correspondente (leitor sem peso por `d`; janela por contagem; evento fundido sem a soma). Consequência obrigatória em
todo produto de texto: **"conferido por simulação literal" = a forma fechada bate com a simulação literal**; proibido
"estabelecido/medido empiricamente" para expoente, peso, fator de fusão ou ordem de políticas.

**0.4 Maquinário partilhado, perguntas separadas `[B-crit 4]` `[B-crit 6]`.** As quatro perguntas são distintas e
NÃO se fundem (vereditos independentes; um desfecho não arrasta o outro). O maquinário, sim:

- EXP e OCC rodam pelo mesmo caminho (`_uma_tarefa` de `code/run_token_kat.py` + `avaliar_kat` de
  `code/token_kat.py`, sem editar nada selado): **um único runner fino** `code/run_grid.py --grid <json>
  --out <dir>` serve às duas, com o adaptador `{**grade, "tag_r3": grade.get("tag", grade.get("tag_r3"))}` para
  `_uma_tarefa`. **Nenhuma grade nova tem a chave `tag_r3`.** O CMP não usa esse runner: a fusão é transformação
  pós-sorteio, com runner próprio `code/run_fusion.py` (§5).
- Parâmetros repetidos entre famílias, declarados: `R ∪ S` de CMP1 (braço `RS`) = `R ∪ S` do KAT S1b; `R ∪ S` de CMP4
  (braço `RS`) = `R ∪ S` do KAT S2b = mistura de KNP2 do C5; mistura de KNP1 = `R ∪ S` do KAT S1a. Só o C5 reusa os
  DADOS selados do KAT (âncoras); o CMP reusa só como teste de identidade (FU1c), fora do veredito.

**0.5 Referências e norma `[B-crit 5]` `[B-crit 20]`.** Norma APA 7 (decisão D2; achado 20 fechado pela decisão 16b.3).
Fonte única: `refs-verificadas-teoria.jsonl` ([nota privada, não distribuída]; sha256
`7e8ed08ff21c773917f06eec03c13c23cb0aa949f501fc480c0d860c09fad6bd`), linhas VERIFICADAS por código a partir dos crus
Crossref em [nota privada, não distribuída] (`neyman1933.crossref.json`
`8accca837b78f32cbb796faba830f81e6e6c60d25921c2fc2957ddf266782d3c`; `hanley1982.crossref.json`
`099980ca772d8c001f387876177376a01f216427d034a662ee60524f1d0d39bf`; `mann1947.crossref.json`
`f4ea84643ff6176d8bdeb7884105bc01547b4750d7872e188d1e8f32f0fecaea`). Cada referência da §10 é o campo `apa7` copiado
verbatim; Neyman–Pearson mantém o prefixo "IX." do título como publicado.

**0.6 Tempo (viabilidade).** Base medida: KAT = 1,476·10⁹ eventos gerados em 76 s com 8 processos
(1,94·10⁷ eventos/s de parede). Recontagem de eventos gerados (N = 100.000, 5 sementes):

| Família | Eventos gerados | Parede estimada (8 processos) | Maior simulação isolada (célula × combo × semente) |
|---|---|---|---|
| EXP | 1,962·10⁹ | ~101 s | ~3 s |
| OCC | 4,123·10⁹ | ~212 s | ~3 s |
| CMP | 1,676·10⁹ (+ fusão, ~+50%) | ~130–150 s | ~5 s |
| C5 | 8,42·10⁸ (+ 5–6 políticas, fator ~2) | ~90–120 s | ~3 s |

Todas muito abaixo de 5 min por simulação; o conjunto cabe em ~10 min de parede. Estimativas por escala linear,
**não medições**; pico de memória do CMP (~0,7 GB/processo com 576 eventos/usuário) cabe com 8–12 processos na máquina
de 14 CPUs.

## 1. Pergunta

A especificação (outline, bloco 2.3a) enuncia o **Corolário 4(b)** só analiticamente: fundir `m` eventos adjacentes de
`S` num evento de custo `k′ < m·k_S` **sem perda** (o evento fundido carrega a estatística suficiente dos `m`) dá taxa
`λ_S/m` e `d_S² -> m·d_S²`, multiplica `ρ_S` por `m·k_S/k′`, mantém `λ_S d_S²`, reduz a ocupação e **pode inverter o
sinal do Corolário 1**; o fator é **teto fluido de uma codificação ideal**; **com perda o fator é menor** (`k_S/k′`
quando só um representante é retido).

Este adendo testa, por simulação LITERAL por orçamento de tokens (a do KAT, com a fusão aplicada aos eventos gerados),
se sinal e nível seguem a forma fechada com os parâmetros fundidos: (i) nas células em que a fusão inverte o sinal
(**com a janela já saturada antes da fonte nova**); (ii) na célula em que o fator não basta; (iii) na célula em que a
compactação NÃO ajuda (**sem saturação mesmo com a fonte nova**, crua); (iv) no controle de `d` NÃO preservado (fusão
com perda); (v) na troca de regime (a fusão dessatura a janela).

## 2. O que a teoria prevê (forma fechada)

**Evento fundido sem perda.** Para `m` atributos `x_i ~ N(d_S·y, 1)` independentes dado `y`, a log-razão de
verossimilhança é `Σ_i d_S(x_i − d_S/2) = d_S·Σ_i x_i − m·d_S²/2`: depende só de `Σ_i x_i ~ N(m·d_S·y, m)`, que
padronizado é um atributo com separação `√m·d_S`. Para o leitor ótimo (hipótese iv; Neyman & Pearson, 1933), o evento
fundido é um evento com `d_F² = m·d_S²`. **Com perda (controle):** o bloco retém só o `x` do membro mais recente,
`d_P² = d_S²`.

| braço | `S` entra como | `ρ` da fonte nova | separabilidade por dia | ocupação |
|---|---|---|---|---|
| `R` | ausente | — | — | — |
| `RS` (crua) | `(λ_S, d_S, k_S)` | `ρ_S = d_S²/k_S` | `λ_S d_S²` | `λ_S k_S` |
| `RF` (fundida sem perda) | `(λ_S/m, √m·d_S, k′)` | `ρ_S·m·k_S/k′` | `λ_S d_S²` (igual) | `λ_S k′/m` |
| `RP` (representante; `d` NÃO preservado) | `(λ_S/m, d_S, k′)` | `ρ_S·k_S/k′` | `λ_S d_S²/m` | `λ_S k′/m` |

Forma fechada (a do KAT): `W_X = W_R + λ_X k_X`, `h_X = min(T, K/W_X)`, `Δ²_X = h_X·(Σ_R λ_r d_r² + λ_X d_X²)`,
`AUC = Φ(√(Δ²/2))`. Consequências conferidas:

- **(A) Inversão possível.** Com `R` saturada (logo `R ∪ S_F` satura, porque `W_F ≥ W_R`), o sinal de `RF − R` é o do
  Corolário 1 com `ρ_F = ρ_S·m·k_S/k′` contra `ρ̄`: se `ρ_S < ρ̄ < ρ_S·m·k_S/k′`, `RS` piora e `RF` melhora.
- **(B) Fusão sem perda nunca piora em relação à crua.** `λ_S d_S²` fixo e `W_F < W_S` dão `h_F ≥ h_S`:
  `Δ²_F − Δ²_S = (Σ_R λ d² + λ_S d_S²)·(h_F − h_S) ≥ 0`, estrito se e só se `T·W_S > K`.
- **(C) Sem saturação mesmo com a fonte nova crua (`T·W_S ≤ K`), a fusão sem perda NÃO ajuda:** `h = T` nos dois
  braços e `Δ²_F = Δ²_S`.
- **(D) Com perda.** `RP − R` segue o Corolário 1 com `ρ_P = ρ_S·k_S/k′`. Com `k′ = k_S`, `RP` é `S` afinada por `m`:
  sinal de `RP − R` = sinal de `RS − R` (Corolário 2) e, saturado, `RP − RS` tem o sinal de `ρ̄ − ρ_S`; sem saturação,
  `Δ²_P − Δ²_S = −T·λ_S d_S²(1 − 1/m) < 0`.
- **(E) Troca de regime.** Se `R` não satura, `R ∪ S` crua satura e `R ∪ S_F` não (`T·W_F < K ≤ T·W_S`), `RF − R`
  melhora pelo Corolário 3 **mesmo com `ρ_F < ρ̄`**.

> [!IMPORTANT]
> **Achado analítico (independe do desfecho; reconferido pela crítica).** Sob a hipótese do Corolário 1 (`R`
> saturada) o 4(b) está completo: `R ∪ S_F` satura junto. A lacuna é o regime misto, que o 4(a) cobre e o 4(b) não:
> com `R` sem saturar e `R ∪ S` crua saturada, a fusão reduz a ocupação e pode dessaturar `R ∪ S` (CMP5: `z(RF) =
> −3,15` na tabela congelada; −3,19 no recálculo da crítica, ver `[B-crit 12]` na §7); ali "comparar `ρ_S·m·k_S/k′`
> com `ρ̄`" prevê PIORA e a fórmula geral prevê MELHORA (+0,1203). Recomenda-se acrescentar ao 4(b): "(no regime
> misto, a fonte fundida entra na Observação com os parâmetros fundidos; se a fusão dessatura `R ∪ S`, vale o
> Corolário 3)". **Registrado aqui como achado; o outline NÃO é editado por este pré-registro.** A aplicação é edição de
> outline da sessão principal, na passada única da etapa 6 (decisão 16b.6 do [registro privado de estado]), com `conferir_outline` + verify.

## 3. O que NÃO se afirma (escopo)

- Ilustrativo; **não é replicação do nuFormer**. Do case: `K = 2.048` e os custos `{14, 55}`. O **custo `k′` do evento
  fundido NÃO vem do case**: reusar 14 ou 55 é escolha ilustrativa.
- Testa a **codificação ideal** que o 4(b) chama de teto: blocos ancorados no evento mais recente. **Não cobre** fusão em
  fluxo (bloco mais recente incompleto cru ou atrasado).
- Perda só na forma "um representante".
- Corolário 4(a) ("`d` preservado entre tokenizações") segue suposição: sob o leitor oráculo, `d` é exógeno. Corolário 5
  fica com o limite (d).
- **`[B-crit 10]` Limite comum (§0.3), aqui literal:** o rival `H_tok` aplicado ao braço `RF` é exatamente a previsão do
  braço `RP`, e `H_ideal` aplicado ao `RP` é exatamente a do `RF` (recálculo da crítica, bloco 3 de
  `critica_B_recalc.py`). A diferença `RF` × `RP` é, sob o oráculo, consequência da soma dos `m` membros (suficiência) —
  o que a simulação confere é o **fator fluido sob blocos literais e truncamento**, não a suficiência. Um código que
  perdesse a soma se comportaria como `H_tok`: é esse o poder discriminante real.
- **Produto:** licenciar UMA frase (§9). Nenhum número deste adendo vai ao corpo.

## 4. Hipóteses rivais

| rival | formulação | onde prevê o oposto da forma fechada |
|---|---|---|
| `H_tok` | o evento fundido vale UM evento (`d² = d_S²`) — ≡ modelo do braço `RP` | CMP1 e CMP2 `RF − R` (piora); CMP2 e CMP4 `RF − RS` (piora); CMP6 `RF − RS` (−0,0450) |
| `H_ideal` | a perda não importa; todo bloco vale `m·d_S²` — ≡ modelo do braço `RF` | CMP1 `RP − R` (melhora); CMP2 e CMP4 `RP − RS` (melhora) |
| `H_dia` | a separabilidade por dia `λ_S d_S²` decide; a fusão, que a preserva, não muda nada | CMP1 e CMP3 `RF − RS` (zero; a forma fechada prevê +0,1157 e +0,0447) |
| `H_m` | o fator é `m` (ignora o custo `k′`) | CMP3 `RF − R` (melhora +0,0191; a forma fechada prevê piora) |
| `H_c1` | Corolário 1 com `ρ` fundido, sem checar a saturação | CMP5 `RF − R` (piora) |
| `H_P1` | Proposição 1 (`h = K/W`) sem checar a saturação | CMP6 `RF − RS` (+0,0409) e `RP − RS` (+0,0231) |
| `H_mono` | "fonte com `d_S > 0` nunca piora" (já refutada no KAT, MIX2) | CMP5 `RS − R` (melhora) |

Todas as previsões de rival acima foram reconferidas pelo recálculo independente (bloco 3), dígito a dígito, e batem
com a tabela congelada (§7).

## 5. Modelo gerador e regra literal de fusão (fixados aqui)

**Herdado do KAT sem mudança:** `π = 0,2`; Poisson de taxa `λ_s` em `T` dias, independente de `y`; tempos uniformes em
`[0, T)`; `x ~ N(d_s·y, 1)`; leitor = oráculo; AUC de Mann–Whitney com postos médios (Mann & Whitney, 1947); janela =
maior sufixo de eventos mais recentes com custo `≤ K`, só eventos inteiros, sem pular, desempate por ordem de entrada.

**Regra de fusão (nova):**

1. Os eventos de `S` de cada usuário são ordenados por (tempo, ordem de entrada), estável; posto a partir do mais
   recente: `r = 0` é o mais recente.
2. Bloco `b = ⌊r/m⌋`: o bloco 0 contém os `m` mais recentes. O bloco incompleto, se houver, é o MAIS ANTIGO.
3. Cada bloco vira um evento com o tempo e a ordem de entrada do seu membro mais recente e custo `k′` (inclusive o
   incompleto).
4. `RF`: contribuição = `Σ_membros d_S(x_i − d_S/2)`. `RP`: só `d_S(x_mais-recente − d_S/2)`.
5. `RF` e `RP` têm a mesma janela (regra do KAT sobre `R` + blocos). `RS` é exatamente a simulação do KAT.

**Sorteio (números aleatórios comuns).** Um sorteio para `R` (`i_fluxo = 0`) e UM partilhado por `RS`, `RF` e `RP`
(`i_fluxo = 1`), na ordem de `simular_literal_tokens`; a fusão é transformação pós-sorteio. Fluxo
`numpy.random.default_rng([semente, i_celula, i_fluxo, 7, i_bloco])` — **tag 7, exclusivo desta família**
`[B-crit 1]` (o rascunho original propunha 5); `i_celula` = posição da célula (base 0) na grade congelada; blocos de
10.000 usuários (`bloco_usuarios` da grade).

**Restrições de código.** Nada selado é editado; os módulos novos só importam. Nada desta família nasce no lado
privado: nenhum arquivo em `src/` do [selo privado, não distribuído], nenhum `tests/test_replica_*.py` nem `tests/test_kat_token*.py` do [selo privado, não distribuído]
(globs selados). Nomes fixos no repositório: regra de fusão `code/fusion.py`; runner da grade
`code/run_fusion.py`; tabela analítica portada `code/fusion_analytic_table.py`; testes
`tests/test_fusion.py`; grade `data/fusion_grid.json` (cópia byte a byte da grade congelada); saída
`output/fusion/`. Identificadores Python dos módulos portados ficam verbatim do privado (desenho, §A.1);
`code/` não tem `__init__.py`, entra no `sys.path`, e nunca se escreve `import code`. Colocação: só no repositório,
depois do workflow A verde (decisão 16b.1); selo na §10.

## 6. Grade (fixada aqui)

`K = 2.048`; `N = 100.000` por (célula, braço, semente); sementes `0..4`; 6 células × 4 braços. Critérios de desenho
(conferidos por código antes de simular, exit 0): cada braço a `|z| ≥ 2,5` do lado declarado (variância Poisson também
para a fonte fundida — conservador); `≤ 600` eventos gerados por usuário; contraste no critério só se
`|ΔAUC previsto| ≥ 1,2·tol` e `≥ 3·EP`; todo contraste discriminante com rival de sinal oposto (ou zero, para `H_dia`).

| célula | regime (R · RS · RF) | T | `R` (λ, d, k) | `S` (λ, d, k_S) | m | k′ | o que discrimina |
|---|---|---|---|---|---|---|---|
| CMP1 | sat · sat · sat | 180 | A (1,2; 0,12; 14) | C (1,5; 0,17; 55) | 4 | 55 | inversão: `RS` piora, `RF` melhora (`H_tok`: piora); `RP` com `k′ = k_S` = afinamento, não inverte (`H_ideal`: melhora); `RF > RS` (`H_dia`: zero) |
| CMP2 | sat · sat · sat | 180 | A (1,2; 0,12; 14) | C (2,0; 0,105; 14) | 8 | 55 | inversão com `k′ ≠ k_S` (fator 2,036): `RF` melhora (`H_tok`: piora); `RP` (fator 0,2545) piora mais que `RS` (`H_ideal`: melhora) |
| CMP3 | sat · sat · sat | 180 | A (1,2; 0,12; 14) | C (2,0; 0,06; 14) | 8 | 55 | par de CMP2, só `d_S` muda: o fator não basta, `RF` ainda piora (`H_m`: melhora); `RF > RS` (`H_dia`: zero) |
| CMP4 | sat · sat · sat | 180 | A (0,4; 0,23; 55) | C (1,5; 0,16; 14) | 4 | 14 | fonte boa (`ρ_S > ρ̄`): com perda a compactação PIORA, `RP < RS` (`H_ideal`: melhora); sem perda melhora (`H_tok`: piora) |
| CMP5 | não · sat · não | 90 | A (0,25; 0,3; 14) | C (6,0; 0,09; 14) | 6 | 14 | troca de regime: `RS` piora (misto, `θ = 0,1186`; `H_mono`: melhora); a fusão dessatura e `RF` melhora com `ρ_F < ρ̄` (`H_c1`: piora) |
| CMP6 | não · não · não | 90 | A (0,3; 0,25; 14) | C (0,15; 0,30; 55) | 4 | 55 | a compactação NÃO ajuda: `RF = RS` (nulo; `H_P1`: +0,0409, `H_tok`: −0,0450); com perda PIORA, `RP < RS` (`H_P1`: melhora) |

**Grade congelada (fonte única):** `data/fusion_grid.json` (sha256 na tabela do
topo), objeto JSON com o cabeçalho `K`, `pi`, `N`, `bloco_usuarios`, `sementes`, `tag = 7`, `tol_base_r1 = 0,0079`,
`ep_dif_max_kat` (maior `ep_dif` do resumo selado do KAT, célula S1a), `tol_0 = 0,0041`, os pisos de desenho
(`margem_minima_sobre_tol = 1,2`, `z_minimo_regime = 2,5`, `eventos_max_por_usuario = 600`) e as 6 células; comentários
em inglês, limpa no juiz de vazamento (G5, exit 0), porque entra byte a byte no repositório como
`data/fusion_grid.json`. As células são as da grade-rascunho, sem mudança de valor.

**Parâmetros repetidos, declarados `[B-crit 13]`:** CMP1 (`R` e `RS`) = KAT S1b; CMP4 (`R` e `RS`) = KAT S2b; `RS` de
CMP4 = mistura de KNP2 (C5). O CMP roda nos SEUS fluxos (tag 7); os dados selados do KAT entram só no teste de
identidade FU1c, nunca no veredito.

## 7. Tabela analítica — calculada ANTES de simular

`tol` por braço = `0,0079 + disc + disc_bloco + 3·EP_média` (a do KAT mais `disc_bloco`); `EP` de poder =
Hanley–McNeil (Hanley & McNeil, 1982), braços como independentes (cota superior para números aleatórios comuns).
**Reconferido pela crítica:** AUC fluidas dos 4 braços, `ρ` e contrastes, dígito a dígito; `tol` base (sem
`disc_bloco`) idem.

`[B-crit 12]` **z dos braços fundidos: vale o valor que o gerador congelado imprime** (2 casas): +9,48 (CMP1), +8,23
(CMP2, CMP3), +5,95 (CMP4), −3,15 (CMP5), −11,76 (CMP6). O recálculo da crítica deu +9,44 · +8,17 · +8,17 · +5,94 ·
−3,19 · −11,9 (valores que o rascunho levou, com 1 casa, à coluna z). Causa da diferença: o gerador soma à média de
tokens do braço fundido o meio bloco incompleto esperado, `k′·(m − 1)/(2m)` (blocos = `⌈n/m⌉`), e o recálculo usou a
média sem esse termo; a variância é a Poisson da fonte fundida nos dois (conservadora). O rascunho original, antes da
crítica, imprimia +9,5 · +8,2 · +8,2 · +6,0 · −3,1 · −11,8, consistentes com o gerador congelado. Nenhum cruza o piso
2,5; CMP5/RF fica a 0,65 desvio dele (0,69 no recálculo), o braço mais perto da quina.

As três tabelas abaixo são **cópia literal do stdout congelado** (`data/prereg/fusion_analytic_table.txt`,
sha256 na tabela do topo), com ponto decimal e sinal ASCII como impressos; só se acrescentaram linhas em branco entre
blocos. A 1ª linha do stdout amarra a tabela à grade:

```text
grade sha256 869127a0cc6aa6e8bbc56840eb6b907ac354d5110521adc87dd69a5869951de6 · K = 2048 · N = 100000 · sementes = 5 · tag = 7 · tol_base_r1 = 0.0079 · tol_0 = 0.0041
```

| célula | T | m | k_S -> k′ | regime R · RS · RF · RP | z (R · RS · RF) | eventos/usuário | ρ_S | ρ_S·m·k_S/k′ (RF) | ρ_S·k_S/k′ (RP) | ρ̄ | θ (RS) | AUC fluida R · RS · RF · RP | tol R · RS · RF · RP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CMP1 | 180 | 4 | 55 -> 55 | sat · sat · sat · sat | +4.74 · +17.07 · +9.48 | 486 | 0.000525 | 0.002102 | 0.000525 | 0.001029 | — | 0.8476 · 0.7854 · 0.9011 · 0.8098 | 0.0111 · 0.0137 · 0.0137 · 0.0145 |
| CMP2 | 180 | 8 | 14 -> 55 | sat · sat · sat · sat | +4.74 · +17.90 · +8.23 | 576 | 0.000787 | 0.001604 | 0.000200 | 0.001029 | — | 0.8476 · 0.8285 · 0.8746 · 0.7938 | 0.0111 · 0.0112 · 0.0139 · 0.0154 |
| CMP3 | 180 | 8 | 14 -> 55 | sat · sat · sat · sat | +4.74 · +17.90 · +8.23 | 576 | 0.000257 | 0.000524 | 0.000065 | 0.001029 | — | 0.8476 · 0.7728 · 0.8175 · 0.7825 | 0.0111 · 0.0114 · 0.0146 · 0.0159 |
| CMP4 | 180 | 4 | 14 -> 14 | sat · sat · sat · sat | +4.10 · +10.94 · +5.95 | 342 | 0.001829 | 0.007314 | 0.001829 | 0.000962 | — | 0.8395 · 0.8832 · 0.9327 · 0.8588 | 0.0136 · 0.0132 · 0.0129 · 0.0137 |
| CMP5 | 90 | 6 | 14 -> 14 | nao · sat · nao · nao | -26.10 · +17.55 · -3.15 | 562 | 0.000579 | 0.003471 | 0.000579 | 0.006429 | 0.1186 | 0.8428 · 0.8192 · 0.9632 · 0.8797 | 0.0103 · 0.0113 · 0.0092 · 0.0102 |
| CMP6 | 90 | 4 | 55 -> 55 | nao · nao · nao · nao | -22.96 · -4.32 · -11.76 | 40 | 0.001636 | 0.006545 | 0.001636 | 0.004464 | — | 0.8208 · 0.8858 · 0.8858 · 0.8408 | 0.0104 · 0.0100 · 0.0100 · 0.0124 |

| célula | contraste | ΔAUC previsto | sinal | rival (previsão) | papel | \|Δ\|/tol | \|Δ\|/EP |
|---|---|---|---|---|---|---|---|
| CMP1 | RS − R | -0.0622 | piora | — | critério | 4.54 | 52 |
| CMP1 | RF − R | +0.0535 | melhora | H_tok -0.0378 | critério | 3.92 | 52 |
| CMP1 | RP − R | -0.0378 | piora | H_ideal +0.0535 | critério | 2.61 | 32 |
| CMP1 | RF − RS | +0.1157 | melhora | H_dia +0.0000 | critério | 8.44 | 103 |
| CMP1 | RP − RS | +0.0243 | melhora | — | critério | 1.68 | 19 |
| CMP2 | RS − R | -0.0191 | piora | — | critério | 1.71 | 17 |
| CMP2 | RF − R | +0.0269 | melhora | H_tok -0.0539 | critério | 1.94 | 25 |
| CMP2 | RP − R | -0.0539 | piora | — | critério | 3.49 | 45 |
| CMP2 | RF − RS | +0.0461 | melhora | H_tok -0.0347 | critério | 3.31 | 41 |
| CMP2 | RP − RS | -0.0347 | piora | H_ideal +0.0461 | critério | 2.25 | 28 |
| CMP3 | RS − R | -0.0748 | piora | — | critério | 6.55 | 61 |
| CMP3 | RF − R | -0.0301 | piora | H_m +0.0191 | critério | 2.07 | 26 |
| CMP3 | RP − R | -0.0651 | piora | — | critério | 4.10 | 54 |
| CMP3 | RF − RS | +0.0447 | melhora | H_dia +0.0000 | critério | 3.07 | 36 |
| CMP3 | RP − RS | +0.0097 | melhora | — | só reportado | 0.61 | 8 |
| CMP4 | RS − R | +0.0437 | melhora | — | critério | 3.21 | 40 |
| CMP4 | RF − R | +0.0932 | melhora | — | critério | 6.86 | 94 |
| CMP4 | RP − R | +0.0193 | melhora | — | critério | 1.41 | 17 |
| CMP4 | RF − RS | +0.0495 | melhora | H_tok -0.0243 | critério | 3.76 | 55 |
| CMP4 | RP − RS | -0.0243 | piora | H_ideal +0.0495 | critério | 1.78 | 23 |
| CMP5 | RS − R | -0.0237 | piora | H_mono (sinal): melhora | critério | 2.10 | 20 |
| CMP5 | RF − R | +0.1203 | melhora | H_c1 (sinal): piora | critério | 11.66 | 132 |
| CMP5 | RP − R | +0.0368 | melhora | — | critério | 3.57 | 34 |
| CMP5 | RF − RS | +0.1440 | melhora | — | critério | 12.77 | 152 |
| CMP5 | RP − RS | +0.0605 | melhora | — | critério | 5.37 | 54 |
| CMP6 | RS − R | +0.0650 | melhora | — | critério | 6.22 | 59 |
| CMP6 | RF − R | +0.0650 | melhora | — | critério | 6.22 | 59 |
| CMP6 | RP − R | +0.0200 | melhora | — | critério | 1.61 | 17 |
| CMP6 | RF − RS | +0.0000 | **nulo** | H_P1 +0.0409 · H_tok -0.0450 | critério (nulo) | — | — |
| CMP6 | RP − RS | -0.0450 | piora | H_P1 +0.0231 | critério | 3.64 | 42 |

| célula | regime RF · RP | disc_bloco RF | disc_bloco RP | disc_bloco/tol RF | disc_bloco/tol RP |
|---|---|---|---|---|---|
| CMP1 | sat · sat | 0.0007 | 0.0008 | 5.5% | 5.5% |
| CMP2 | sat · sat | 0.0006 | 0.0017 | 4.5% | 11.2% |
| CMP3 | sat · sat | 0.0009 | 0.0022 | 6.1% | 13.7% |
| CMP4 | sat · sat | 0.0007 | 0.0002 | 5.6% | 1.7% |
| CMP5 | nao · nao | 0.0000 | 0.0001 | 0.0% | 1.4% |
| CMP6 | nao · nao | 0.0000 | 0.0021 | 0.0% | 16.6% |

disc_bloco máximo em valor: 0.0022 (CMP3/RP; 13.7% da tol do braço) · máximo em fração da tol: CMP6/RP (0.0021; 16.6%)

```text
CRITÉRIOS DE DESENHO: todos passaram (tag exclusiva, tol_0 da grade, regime declarado por braço, |z| ≥ z_min do lado declarado, eventos ≤ máximo, forma fechada = corolário do regime, contraste discriminante no critério, rival com sinal oposto ou zero, nulo exato com rivais ≥ margem·tol_0) · contrastes assinados no critério = 28 · nulo = 1
```

Leitura: a 1ª tabela traz, por célula, o regime de cada braço (`sat` = `T·W ≥ K`), `z` de `R`, `RS` e `RF` (o de `RP` é
igual ao de `RF`: mesma taxa e mesmo custo), eventos gerados por usuário, os três `ρ` da fonte nova, `ρ̄`, `θ` (só no
regime misto de CMP5), a AUC fluida e a `tol` dos 4 braços; a 2ª, os 30 contrastes com previsão, rival e papel
(28 "critério", 1 "critério (nulo)", 1 "só reportado": `CMP3 RP − RS`); a 3ª, o `disc_bloco` dos braços fundidos.

**`disc_bloco`.** Saturado: a ancoragem no mais recente põe em média até `(m − 1)/(2m)` bloco a mais no sufixo,
`|ΔΔ²| ≤ (m − 1)/(2m)·k′·|ρ_X − ρ̄|`. Sem saturação (só `RP`): `E[⌈n_S/m⌉] − λ_S T/m` blocos a mais, pela Poisson exata.
Maior valor absoluto: 0,0022 em AUC (CMP3/RP), 13,7% (≈ 14%) da `tol` do braço; maior fração da `tol`: CMP6/RP (0,0021;
16,6%). **Gap de Jensen** da composição com blocos (CMP1/RF): ~0,0002 em AUC, coberto pela base 0,0079.

## 8. N, sementes, métrica e testes de unidade

- `N = 100.000` por (célula, braço, semente); 5 sementes; 120 AUCs de 60 sorteios (30 de `R` + 30 partilhados).
- **Métrica:** AUC de Mann–Whitney (Mann & Whitney, 1947); contraste = diferença das médias de 5 sementes;
  `EP_emp = √(v_a/5 + v_b/5)`, `ddof = 1` (conservadora para braços com números aleatórios comuns). Report-only: sinal
  por semente; `Δ²` empírico; blocos visíveis contra `(λ_S/m)·h`; ociosos; fração saturada; fração com bloco incompleto
  visível; `CMP3 RP − RS`.
- **FU1 — identidade com o selado.** (a) `RS` = `simular_literal_tokens`, escores byte-idênticos com o mesmo gerador;
  (b) com `m = 1` e `k′ = k_S`, `RF` e `RP` byte-idênticos a `RS`; **(c) `[B-crit 13]` o braço `RS`, alimentado com o
  fluxo selado do KAT (`[semente, 1, 1, 3, i_bloco]` para S1b e `[semente, 3, 1, 3, i_bloco]` para S2b: posição da
  célula na grade do KAT, `i_combo = 1` = `R ∪ S`, tag 3), reproduz, por semente, as LINHAS de S1b e S2b (combo `RS`)
  de `output/kat_token/celulas.csv`: `auc` com igualdade de `repr`, `n_pos` e `n_neg` iguais, em diretório
  temporário, fora do veredito.** A comparação é por linha, nunca pelo sha256 do arquivo: o `celulas.csv` do repositório
  difere da origem privada `celulas.csv` do [selo privado, não distribuído] (sha256
  `aea196a288494455720aa8117780836942632cc36827510fd01c8468b37ceae6`) pela renomeação MIX1/MIX2; as linhas de S1b e S2b
  são as mesmas pelo contrato de regeneração (G7).
- **FU2 — regra de fusão.** Bloco 0 = os `m` mais recentes; incompleto = o mais antigo; tempo e ordem do bloco = os do
  membro mais recente; custo `k′` também no incompleto; `RF` soma os membros; `RP` usa só o mais recente (índice
  explícito); empate `R` × bloco no mesmo tempo resolvido pela ordem de entrada do membro mais recente.
- **FU3 — números aleatórios comuns.** Com `K` grande, escores de `RF` = de `RS` (`allclose`, atol 1e−12).
- **FU4 — previsão.** (a) A forma fechada reproduz, célula e braço, AUC e regime da tabela congelada; (b) o stdout de
  `code/fusion_analytic_table.py` sobre `data/fusion_grid.json` é byte-idêntico a
  `data/prereg/fusion_analytic_table.txt` (= a tabela congelada, sha256 do topo).
- **FU5 — critério.** Média + `ddof = 1`, limiar `3·EP`, nulo com `tol_0`, tolerância com `disc_bloco`, papel
  "critério × só reportado" lido de `data/prereg/fusion_analytic_table.txt`; `grade["tag"] == 7` e
  `7 ∉ {3, 5, 6, 8}` `[B-crit 1]`.

## 9. Critério de aprovação, quebra e produto

O adendo CMP **passa** se, e só se, FU1–FU5 verdes e:

- **CMP-S (sinal; 28 contrastes "critério"):** sinal de `média(AUC_a) − média(AUC_b)` = o previsto **e**
  `|diferença| ≥ 3·EP_emp` (exigência a mais que o KAT, porque `H_dia` prevê zero). Se `|ΔAUC previsto| < 3·EP_emp`,
  empate: reprova por falta de poder. Uma discordância reprova.
- **CMP-0 (nulo, CMP6 `RF − RS`):** `|média(AUC_RF) − média(AUC_RS)| ≤ tol_0 = 0,0041` (3 × 0,0013467, o maior
  `ep_dif` do KAT, S1a, arredondado para cima). Rivais: `|Δ| ≥ 0,0409`. Declarado: sob o oráculo e números comuns, os
  escores de `RF` e `RS` são idênticos para todo usuário cujo histórico cabe — contraste quase tautológico, que testa
  a fronteira de regime e o código.
- **CMP-N (nível; 24 combinações):** `|média(AUC) − AUC fluida| ≤ tol` do braço. Um estouro reprova.
- **CMP-T (teto; fora do veredito):** nos `RF` saturados (CMP1–CMP4), `média(AUC_RF) ≤ AUC fluida + disc_bloco +
  3·EP_média`; consequência própria no texto, não reprova.

| se falhar | o que cai |
|---|---|
| CMP1 ou CMP2 `RF − R` | "pode inverter o sinal do Corolário 1" deixa de ter apoio de simulação |
| CMP3 `RF − R` com sinal `+` | o fator `m·k_S/k′` (`H_m` ou a regra por evento ficam de pé) |
| CMP1 `RP − R`, CMP2 ou CMP4 `RP − RS` | a condição "sem perda": com perda o efeito seria o mesmo (`H_ideal`) |
| CMP1 ou CMP3 `RF − RS` sem significância | o mecanismo "reduz a ocupação com `λ_S d_S²` fixo" (`H_dia`) |
| CMP5 `RF − R` | a passagem dos parâmetros fundidos por `h = min` na troca de regime |
| CMP6 `RF − RS` fora de `tol_0` | NÃO falsifica a teoria; indica erro de código e invalida o run |
| CMP-N | o nível fluido (o sinal pode ficar de pé) |
| CMP-T | a palavra "teto" no 4(b) para esta regra literal |

| desfecho | texto | fórmula | tabela | figura |
|---|---|---|---|---|
| **Passa (CMP-S 28/28, CMP-0, CMP-N 24/24) e CMP-T ok** | l. "Estado de teste": "Corolário 4(b): conferido por simulação literal por orçamento de tokens (adendo CMP); Corolário 5: analítico"; ledger `[CMP-resultado]` com a frase `[B-crit 11]`: *"com a janela já saturada antes da fonte nova, fundir `m` eventos de `S` num evento de `k′` tokens que carrega a estatística suficiente multiplica `ρ_S` por `m·k_S/k′` e pode inverter o sinal do Corolário 1; retendo um só representante, o fator cai para `k_S/k′`; sem saturação mesmo com a fonte nova (crua), a fusão sem perda não muda o teto; conferido por simulação literal por orçamento de tokens"* (o rascunho dizia "mesmo com a fonte crua", perdendo o qualificador literal); nenhum número no corpo; 0 palavra se for ao `docs/THEORY.md`, ~6 se "conferido por simulação" entrar na frase do 4(b) | nenhuma | nenhuma no corpo; tabela CMP (EN) no `docs/THEORY.md` e no bloco da família em `output/results.json` | nenhuma |
| Achado analítico (QUALQUER desfecho) | cláusula de regime no 4(b) (§2); ~12 palavras no outline; no corpo só se couber nos ~170 | nenhuma | — | — |
| CMP-T falha, resto passa | 4(b): "teto fluido de uma codificação ideal" -> "aproximação fluida" | nenhuma | — | — |
| CMP-N falha, CMP-S passa | o texto usa só o sinal; o nível do fator fica analítico | nenhuma | `docs/THEORY.md` sem a coluna de nível | — |
| Inversão falha (CMP1/CMP2 `RF − R`) | sai "pode inverter o sinal do Corolário 1" do corpo; 4(b) segue "analítico"; desvio datado | fator analítico | — | — |
| Fator falha (CMP3) | 4(b) sem o fator `m·k_S/k′` no corpo | `m·k_S/k′` não conferido no `docs/THEORY.md` | — | — |
| Controle falha (`RP`) | cai "sem perda" como condição e "com perda o fator é menor" | `k_S/k′` não conferido | — | — |
| Troca de regime falha (CMP5) | 4(b) restrito a "`R ∪ S` fundida saturada" | — | — | — |
| CMP-0 falha | run inválido; corrige-se o código (nunca a expectativa); novo run sob desvio datado | — | — | — |
| Empate (falta de poder) | reprova como no KAT; texto como "Inversão falha" | — | — | — |

O veredito vai para o bloco próprio da família em `output/results.json`, travado por
`tests/test_paper_numbers.py`.

## 10. Mutação, tempo, reuso, selo e referências

**Mutação** (cópia descartável; mensagem do assert impressa e conferida; `--color=no`), ids `FX01…FX13`: (FX01) blocos
ancorados no mais ANTIGO; (FX02) tempo do bloco = membro mais antigo; (FX03) `RF` com `d_S(x̄ − d_S/2)` (perde o fator
`m`); (FX04) custo do bloco `m·k_S`; (FX05) incompleto descartado; (FX06) `RP` guarda o mais antigo (**equivalente no
desfecho**, `x` iid dado `y`; morre só no FU2 com índice explícito, como o C16 do KAT); (FX07) forma fechada com taxa
`λ_S` no lugar de `λ_S/m`; (FX08) forma fechada de `RF` com o fator do representante; (FX09) regime de `RF` com `W` da
fonte crua (quebra FU4 em CMP5); (FX10) `RF` em fluxo próprio (quebra FU3); (FX11) janela por contagem `L = ⌊K/k̄⌋`;
(FX12) desempate invertido entre evento de `R` e bloco no mesmo tempo; **(FX13) tag 3 ou de outra família (5, 6, 8)
`[B-crit 1]`**. Harness PRIVADO `mutacao_fusao_cmp.py` [verificação adversarial privada], sobre cópia descartável do repositório fora dele (diretório
temporário; nunca `rm -rf`); relatório `mutacao-fusao-cmp-2026-09-2x.txt` [verificação adversarial privada]; o repositório cita o resultado
da mutação só em `REPRODUCIBILITY.md`.

**Tempo:** eventos gerados `1,676·10⁹` (recontado; `RS`/`RF`/`RP` partilham o sorteio) -> ~86 s de geração com 8
processos; com fusão (~+50%) e ordenações, **~130–150 s** de parede (estimativa, coerente com a cronometragem de
primitivas do rascunho: 0,07–1,64 s por bloco de 10.000). Pico ~0,7 GB/processo (576 eventos/usuário).

**Reuso (importado, nunca editado; nome no repositório <- origem privada selada, sha256):**

- `code/token_kat.py` <- `kat_token.py` do [selo privado, não distribuído] (`b70c6a2e729d3b6ecd58b59dc79c9e74697fcd6ce51b606e170b540497c245af`):
  `simular_literal_tokens`, `janela_tokens`, `delta2_fluido`, `auc_fluida`, `fontes_da_celula`, `_media_var`;
- `code/displacement.py` <- `replica_deslocamento.py` do [selo privado, não distribuído]
  (`616b2445a6479f1fde7c1ff6d980dca12887be9743633484bfad21925b36a4ec`): `auc_mann_whitney`, `PI`, `se_hanley_mcneil`;
- `code/token_kat_analytic_table.py` <- `kat_token_tabela_analitica.py` do [selo privado, não distribuído]
  (`2b803a7874434304556b9da39edc01925c83d6301979faeff97ddd68abada2af`): `tolerancia`, `ep_hanley_mcneil`, `inclinacao`,
  `z_saturacao`, `W`, `delta2`, `auc`;
- esqueleto de `code/run_token_kat.py` <- `rodar_kat_token.py` do [selo privado, não distribuído]
  (`fe1b61cbee6ba6b8a4628ddaa742f820f4120b4b4adf48f71b17a5669a803efc`);
- saídas seladas do KAT, só no FU1(c): `output/kat_token/celulas.csv` <- `celulas.csv` do [selo privado, não distribuído]
  (`aea196a288494455720aa8117780836942632cc36827510fd01c8468b37ceae6`);
- tabela analítica desta família: `code/fusion_analytic_table.py` <- `fusao_cmp_tabela_analitica.py` privado (este
  congelamento; o porte troca o import do módulo selado por `import token_kat_analytic_table`, o padrão de `--grade`
  por `data/fusion_grid.json` e a docstring por uma em inglês sem caminho privado (desenho, §A.1); aritmética, asserts
  e stdout byte-idênticos, FU4(b)).

Novo e só isto: a transformação de fusão, a janela sobre `R` + blocos, o runner da grade CMP e o critério CMP-S/0/N/T.

**Selo (reescrito pela decisão 16b.1 do [registro privado de estado]; substitui o "Selo" da §3.10 e a §0.2 do rascunho).** Código, testes e
saídas desta família nascem SÓ neste repositório, depois do workflow A verde. Prova = `make_provenance.py` (build +
`--verify`, exit 0), com folhas novas nos estágios de `configs/stages.json`:

| estágio | folhas novas da família |
|---|---|
| `prereg` | `data/fusion_grid.json` (grade congelada, byte a byte), `data/prereg/fusion_analytic_table.txt` (tabela congelada, byte a byte), `data/prereg/07-fusion-addendum.md` (este pré-registro, sanitizado) |
| `code` | `code/fusion.py`, `code/run_fusion.py`, `code/fusion_analytic_table.py`, `tests/test_fusion.py` |
| `data` | `output/fusion/celulas.csv` |
| `scores` | `output/fusion/resumo.json` |

Negativos, que valem como critério: nada na [cadeia privada de selos]; nenhum `stages-*.json`
privado novo (não existe `stages-fusao-cmp.json`); nenhum `--prev`; nenhum selo privado novo (não há r5); selos
privados r1–r4 intactos (verify exit 0); G9 (pytest privado) fica em 88 testes; G7 (contrato de regeneração privado ×
repositório) não muda, porque esta família não tem saída privada a regenerar. Emenda datada da família em
`data/PREREGISTRATION.md`.

**Referências** (APA 7; campo `apa7` de `refs-verificadas-teoria.jsonl` ([nota privada, não distribuída]), verbatim). Neyman & Pearson (1933)
— leitor ótimo = razão de verossimilhança; "sem perda" é sem perda para ESTE leitor. Hanley & McNeil (1982) — EP da
AUC na tolerância. Mann & Whitney (1947) — a métrica (AUC de Mann–Whitney com postos médios), herdada do KAT. Nenhuma
referência nova além dessas: a suficiência de `Σx` é derivada em uma linha (§2). Dantzig (1957) pertence ao limite (d).

- Hanley, J. A., & McNeil, B. J. (1982). The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology, 143*(1), 29–36. https://doi.org/10.1148/radiology.143.1.7063747
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491
- Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient tests of statistical hypotheses. *Philosophical Transactions of the Royal Society of London. Series A, Containing Papers of a Mathematical or Physical Character, 231*(694–706), 289–337. https://doi.org/10.1098/rsta.1933.0009

## 11. Estado: congelado — o que o workflow B faz depois

**Estado: congelado em 2026-09-26**, na ordem grade -> gerador -> tabela analítica (duas execuções byte-idênticas,
`cmp`) -> este arquivo; grade e tabela limpas no juiz de vazamento (G5, exit 0); nenhum arquivo da família neste repositório
(prova por `ls` no [registro privado de estado]). Daqui em diante este arquivo não recebe byte; mudança = arquivo novo datado.

Depois, no workflow B (só com o workflow A verde; fila por impacto C5 > CMP > OCC > EXP):

1. **Cópia para o repositório:** grade -> `data/fusion_grid.json` (byte a byte); gerador portado ->
   `code/fusion_analytic_table.py`, cujo stdout sobre a grade do repositório é byte-idêntico à tabela congelada ->
   `data/prereg/fusion_analytic_table.txt`; pré-registro sanitizado -> `data/prereg/07-fusion-addendum.md`;
   emenda datada em `data/PREREGISTRATION.md`.
2. **TDD:** `tests/test_fusion.py` (FU1–FU5) escrito e vermelho antes de `code/fusion.py` e
   `code/run_fusion.py`; pytest sempre com `--color=no`.
3. **Run:** a grade inteira (6 células × 4 braços × 5 sementes, `N = 100.000`) -> `output/fusion/celulas.csv` +
   `output/fusion/resumo.json`.
4. **Mutação:** FX01–FX13 pelo harness privado (§10), com a mensagem do assert que matou cada mutante impressa e
   conferida.
5. **Results:** bloco da família em `output/results.json`; `tests/test_paper_numbers.py` trava o veredito;
   `make_provenance.py` build + `--verify` exit 0; laço verde do [portão privado de aceite] (G9 = 88, G7 igual).
6. **Laudo de impacto:** o que muda em texto, fórmula, tabela e figura segundo a tabela de desfechos da §9; quem aplica
   no outline e no ledger é a sessão principal (etapa 6, com `conferir_outline` + verify), junto do achado analítico
   da §2. Resultado que contradiga corolário ou frase licenciada -> desvio novo datado, nunca edição deste arquivo.
