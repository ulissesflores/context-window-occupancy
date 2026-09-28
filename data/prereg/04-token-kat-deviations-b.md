# Desvios pós-selo r4 — frase licenciada do KAT-token (segunda correção)

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

> Datado de 2026-09-26 (tarde), escrito DEPOIS do selo r4. Os desvios anteriores
> `data/prereg/03-token-kat-deviations.md` (sha256 `4ceba2bb20069f0215395b2fce991ddd3571a9be50b9fe9bc2763f00f2d36e15`)
> ficam intocados (folha do selo r4): o que eles dizem e que precisou de correção está aqui. Origem: verificação
> adversarial da fonte 12 do ledger [verificação adversarial privada]
> (sha256 `4f8a953df19aa03afe8b6f4a8611970b6058bae405375aeabc1805c2751de764`; 4 lentes + crítico; veredito FECHADO
> COM CORREÇÕES, achado A02+B-01+A03). **Nenhum dado, resultado ou selo muda:** KT-S 8/8 (40/40 por semente, 0 empates),
> KT-N 16/16.

1. **Frase licenciada com os dois qualificadores de regime (supera a frase do item 2 dos desvios).** A frase anterior
   dizia "com a janela já saturada" sem "antes da fonte nova" e "sem saturação" sem "mesmo com a fonte nova" — a mesma
   perda de qualificador que o pré-registro sofreu ao ser reenunciado como corolário. A própria grade traz o
   contraexemplo de cada leitura errada: MIX1 (`R` não satura, `R ∪ S` satura, `ρ_S < ρ̄`) MELHORA nas 5 sementes; MIX2
   (`R` não satura, `d_S > 0`) PIORA nas 5. Frase vigente, que o mesmo resultado selado sustenta: *"com a janela já
   saturada antes da fonte nova e custo `k_s` heterogêneo, a separabilidade relevante é `ρ_s = d_s²/k_s`, comparada à
   média ponderada pela ocupação (no regime misto o limiar cai para `θ·ρ̄`; sem saturação mesmo com a fonte nova,
   qualquer fonte com `d_S > 0` ajuda); conferido por simulação literal por orçamento de tokens com dois custos (14 e
   55)"*.

2. **Condição de uso no corpo.** A frase cita `θ·ρ̄`: o texto só a usa depois de definir o regime misto (`R` não satura
   e `R ∪ S` satura) e `θ`. Sem essa definição antes dela, a leitura correta da partição em três regimes deixa de estar
   garantida.
