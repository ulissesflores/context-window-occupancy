# Desvios e registros pós-run — adendo KAT-token

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

> Datado de 2026-09-26 (tarde), escrito DEPOIS do run e do selo r3. O adendo
> `data/prereg/02-token-kat-addendum.md` (sha256 `6c2213caa487eedac7a78ce8b29951ac69eb2318c0167fdf76f72a0c369dce93`)
> fica intocado: o que ele diz e que precisou de correção está aqui. Origem: verificação adversarial
> [verificação adversarial privada] (sha256 `5bdbe5c0bd51c3f60abfc38fe76b79534bb1a1253bcf860c943b6eca60639a24`;
> 4 lentes + crítico; veredito FECHADO COM CORREÇÕES). **Nenhum item muda o veredito:** KT-S 8/8 (40/40 por semente,
> 0 empates), KT-N 16/16, dados e selo r3 inalterados.

1. **Selo r3 com dois arquivos a mais que o §Selo r3 declarava (A01).** O estágio `code` inclui
   [verificação adversarial privada]; o estágio `scores` inclui [verificação adversarial privada].
   Desvio aditivo (mais proveniência), sem efeito no critério.

2. **Frase licenciada com o qualificador de regime (B01).** A frase do §Escopo do adendo omitia o regime, e a célula N1
   do próprio KAT a desmente fora da saturação. Frase vigente, que o mesmo resultado selado sustenta: *"com a janela já
   saturada e custo `k_s` heterogêneo, a separabilidade relevante é `ρ_s = d_s²/k_s`, comparada à média ponderada pela
   ocupação (no regime misto o limiar cai para `θ·ρ̄`; sem saturação, qualquer fonte com `d_S > 0` ajuda); conferido por
   simulação literal por orçamento de tokens com dois custos (14 e 55)"*.

3. **Mecanismo da tolerância base corrigido (B02).** O número (0,0079 = 0,007801 arredondado para cima) e o critério
   não mudam. O que muda é a explicação: o pior desvio do r1 está na célula 590/AC (`T = 365`, `λ_A = 0,1`, `λ_C = 6`,
   `d_C = 0`), a `z = 44` do limiar, ou seja, em saturação profunda. É dispersão da composição da janela (contagem
   pequena de uma fonte rara e forte), não Jensen perto da quina `h = min`, onde o máximo (`|z| < 2,5`) é 0,0049.
   Conferido por execução na sessão 9.

4. **Poder do KT-N (B03).** As tolerâncias (~0,010 a 0,0137 em AUC) aceitam ~8–12% de erro em `Δ²`. O observado ficou
   0,3–1,6% abaixo do fluido, com maior `|desvio|` de 0,0019 AUC. O KT-N só pegaria erro grosseiro de nível: a
   simulação confere a FORMA FLUIDA (uma janela por contagem com `L = ⌊K/k̄⌋` passaria KT-S e KT-N), e a regra
   literal de truncamento é fixada pelos testes de unidade KT1/KT2. Relatar nesses termos.

5. **Limites de discriminação (B04, B05).** As 8 células refutam a regra por evento, a `ρ̄` ponderada pela taxa, o
   Corolário 1 aplicado fora da saturação e a monotonia. Elas **não** discriminam o expoente (`d/k` e `d²/k` dão o mesmo
   sinal nas 8), a comparação ocupação × taxa depende de uma célula só (S3, `z(R) = 2,87`), e `θ` fica localizado só no
   intervalo `λ_S ∈ (0,6; 6,0)`. Corolário 4(a): consequência algébrica da forma fechada, que o KT-N confere de forma
   frouxa; "`d` preservado entre tokenizações" segue suposição analítica.

6. **Integridade das configs de selo (D01).** O `verify` protege só o bloco `stages` de cada `stages-*.json`; os campos
   `_raiz`, `_ordem` e `_nota_*` são metadado sem integridade. A nota do r3 que diz "editar este arquivo tornaria o
   manifesto inverificável" vale só para o bloco `stages`.

7. **Testes complementares (C01, C02, C03, C04, C06, C11, C12, C16).** `tests/test_token_kat.py` é folha selada no r3
   e não foi editado. Os testes que faltavam (estimador média + ddof = 1, limiar 3·EP, tolerância por combo, nível no
   combo R∪S, fronteira de saturação `> K`, desempate fim a fim com tempos empatados, custo não positivo) estão em
   `tests/test_token_kat_extra.py` (8 testes) com o harness [verificação adversarial privada]: **8/8 mortos no
   assert pretendido**. O mutante C16 (`lexsort` sem o índice original) é **equivalente e foi provado assim**:
   `np.lexsort` é estável e sobrevive até ao teste de empate fim a fim, enquanto o desempate invertido (X07) morre.
   Relatório [verificação adversarial privada]. Tudo isso entra no selo r4.

8. **Pendente fora do KAT (D02).** O teste mecânico de disjunção "saídas replicadas × globs selados" (norma
   [nota privada, não distribuída]) fica para o scaffold do repo. A invariante vale hoje:
   `output/replicated/` não está em `configs/stages.json`.
