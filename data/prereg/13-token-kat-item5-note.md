# Nota datada sobre o item 5 dos desvios do KAT-token — 2026-09-27

> **Translation note (English).** Sanitized copy of a dated note on item 5 of the token-KAT deviations, written in Portuguese on
> 2026-09-27 after the workflow-B runs; it edits neither deviations file it discusses. The private
> original has sha256 `6d054978403f5642eeb96ed1f8e5290f740481d935ec5d69f8790761863c2e24`. What changed,
> and nothing else: (1) file paths were mapped to the names of this repository (`data/prereg/03`,
> `04`, `05`, `06`); (2) the two token-KAT cells of the mixed regime were renamed `MIX1`/`MIX2`, as in
> every file of this repository; (3) item 1 cited a private recomputation script and its two outputs
> by path and sha256: it now cites `[script privado, não distribuído]` = private script, not
> distributed, and says what the two output hashes showed ("duas execuções com saída byte-idêntica" =
> two runs with byte-identical output). Wording is otherwise verbatim. Every sha256 quoted below
> refers to the private original of the file it names. "r4" = the private seal that covers the first
> deviations file; `[EXP-expoente-resultado]` and `[OCC-resultado]` = rows of `data/claims-ledger.csv`.
> Glossary: nota = note; desvio = deviation; adendo = addendum; oração = clause; célula = cell;
> leitura = reading; rival = rival hypothesis; faixa = range; família = family; veredito = verdict;
> segue aberto = remains open.

Esta nota não edita `data/prereg/03-token-kat-deviations.md` (sha256 4ceba2bb…, selado no r4) nem
`data/prereg/04-token-kat-deviations-b.md` (sha256 e83f23aa…). O item 5 continua verdadeiro como
registro do KAT; esta nota registra o que o workflow B fez com duas das suas três orações.

1. "Elas não discriminam o expoente (`d/k` e `d²/k` dão o mesmo sinal nas 8)." Verdadeiro na leitura "Corolário 1
   aplicado sem checar o regime". Na leitura coerente (rival `H(p, 1)` com o mesmo `h = min`), os 8 sinais selados
   excluem uma faixa baixa de `p`, só pela célula mista MIX2, e uma faixa alta, por MIX1 e pelas saturadas; os limites são
   os da saída de [script privado, não distribuído] (duas
   execuções com saída byte-idêntica, reconferidos em 2026-09-27). Três qualificadores obrigatórios: (i) rival definido depois dos dados; (ii) o lado baixo se apoia numa
   célula só, em regime misto; (iii) não foi pré-registrado como teste de expoente. Não entra em critério nenhum. O
   teste pré-registrado do expoente é a família EXP (adendo `data/prereg/05-exponent-addendum.md`, sha256
   9c9fce06…; veredito PASSA; `[EXP-expoente-resultado]`), em células próprias desenhadas contra `d/k` e `d³/k`; as 8
   células do KAT continuam não discriminando o expoente.
2. "A comparação ocupação × taxa depende de uma célula só (S3, …)." SUPERADA pela família OCC (adendo
   `data/prereg/06-occupancy-addendum.md`, sha256 574dccf9…; veredito PASSA; `[OCC-resultado]`): família pré-registrada
   de células nas duas direções, com folga de saturação, em que as duas ponderações preveem sinais opostos. A S3 segue
   a única célula perto da fronteira de saturação.
3. "`θ` fica localizado só no intervalo …" Segue aberto; o workflow B não o testou.
