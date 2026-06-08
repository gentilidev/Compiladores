# Guia Completo do Compilador

Este documento explica **o projeto inteiro**: o que cada parte faz, como faz, como
usar e como apresentar. Leia de cima para baixo; ao final você consegue defender
qualquer pedaço do código.

---

## 1. O que é este projeto

É um **compilador** escrito em Python puro (sem PLY, ANTLR, Lark ou `re`). Ele recebe
um programa escrito numa linguagem simples (com `int`, `bool`, `if`, `while`, etc.),
passa por todas as etapas clássicas de tradução e, no final, **executa** o programa
numa máquina virtual própria, mostrando o resultado.

O fluxo é uma esteira (pipeline). Cada etapa recebe a saída da anterior:

```
código-fonte (texto)
      │
      ▼
[ Fase A ] Análise Léxica      → lista de tokens
      ▼
[ Fase B ] Análise Sintática   → AST (árvore)
      ▼
[ Fase C ] Análise Semântica   → AST validada (tipos e escopos checados)
      ▼
[ Fase D ] Código Intermediário→ TAC (código de três endereços)
      ▼
[ Fase E ] Código Final        → bytecode
      ▼
[ Execução ] Máquina Virtual   → saída do programa
```

A ideia de quebrar em fases é o coração da disciplina: cada fase tem uma
responsabilidade única e conversa com a próxima por uma estrutura de dados bem
definida (tokens → árvore → TAC → bytecode).

---

## 2. Como rodar

Só precisa de **Python 3** instalado. Não há nada para instalar (tudo é biblioteca
padrão).

```bash
# compila e executa
python3 main.py exemplos/condicional.txt

# mostra TODAS as fases (tokens, AST, tabela de símbolos, TAC, bytecode)
python3 main.py exemplos/condicional.txt --debug

# programa que usa 'read' (espera você digitar o número e dar Enter)
python3 main.py exemplos/soma.txt

# ou já mandando a entrada pronta
echo 5 | python3 main.py exemplos/soma.txt
```

Exemplos inclusos na pasta `exemplos/`:

| Arquivo | Demonstra | Saída |
|---|---|---|
| `condicional.txt` | `if/else`, `bool`, comparação | `10` |
| `soma.txt` | `while`, `read`, aritmética | soma de 1..n (n=5 → `15`) |
| `fatorial.txt` | `while`, string em `print` | n! (n=5 → `120`) |
| `erros.txt` | detecção de erros semânticos | lista os erros e para |

---

## 3. Revalidação: o que o PDF pediu × o que foi feito

O PDF pede 5 fases obrigatórias e uma linguagem com recursos mínimos. Tabela de
conferência:

### Fases (Seção 2 do PDF)

| Item do PDF | Onde está | Status |
|---|---|---|
| **A. Análise Léxica** — reconhecer palavras reservadas, identificadores, literais (números e strings) e operadores; ignorar espaços e comentários | `scanner.py`, `tokens_def.py`, `token_model.py` | ✅ |
| Teoria: Expressões Regulares e AFD | scanner lê caractere a caractere como um AFD; os laços de leitura equivalem às ER (ver Fase A) | ✅ |
| **B. Análise Sintática** — construir a AST | `parser.py`, `ast_nodes.py` | ✅ |
| Método: Parser Descendente Recursivo | é exatamente o usado | ✅ |
| **C. Análise Semântica** — Tabela de Símbolos | `semantic.py` (classe `SymbolTable`) | ✅ |
| Verificação de tipos (type checking) | `semantic.py` (`check_expr` / `check_binary`) | ✅ |
| Declaração prévia de variáveis e escopo | `SymbolTable` com pilha de escopos | ✅ |
| **D. Código Intermediário (IR)** — Código de Três Endereços (TAC) | `ir.py` | ✅ |
| **E. Código Final** — Assembly ou **Bytecode para uma VM** | `codegen.py` (bytecode + a VM que executa) | ✅ |
| Otimização (Opcional/Bônus) | **não incluído** (era opcional) | ➖ |

### Linguagem-alvo (Seção 3 do PDF)

| Recurso exigido | Como aparece na linguagem | Status |
|---|---|---|
| Tipos: Inteiros e Booleanos | `int` e `bool` | ✅ |
| Estruturas de controle: `if-else` e `while` | implementadas | ✅ |
| Aritméticas: `+ - * /` | implementadas (`/` é divisão inteira) | ✅ |
| Lógicas: `== != < >` | implementadas | ✅ |
| E/S: leitura e escrita (`print` e `read`) | implementadas | ✅ |

### Critérios de avaliação (Seção 4 do PDF)

| Critério | Peso | Como o projeto atende |
|---|---|---|
| Corretude léxica/sintática | 30% | aceita programas válidos e rejeita inválidos (testado) |
| Análise semântica | 20% | detecta erro de tipo e variável não declarada (ver `erros.txt`) |
| Geração de código | 30% | o bytecode roda na VM e produz o resultado certo |
| Documentação/código | 20% | este guia + `README.md` + comentários no código |

**Conclusão:** todas as exigências obrigatórias estão cobertas. O único item ausente é
a otimização, que o próprio PDF marca como opcional/bônus.

---

## 4. A linguagem que o compilador entende

### Recursos
- **Tipos:** `int` (inteiros) e `bool` (`true` / `false`)
- **Declaração:** `int x;` ou já com valor: `int x = 5;`
- **Atribuição:** `x = expressão;`
- **Controle:** `if (cond) { ... } else { ... }` e `while (cond) { ... }`
- **Aritmética:** `+  -  *  /` (divisão inteira) e `-` unário (negativo)
- **Comparação:** `==  !=  <  >`
- **Entrada/Saída:** `print expressão;` e `read variavel;`
- **Comentários:** `// até o fim da linha`
- **Strings:** `"texto"` — só podem ser usadas dentro de `print`

### Gramática (resumida)

A gramática é a "regra de formação" das frases válidas. Cada linha vira uma função no
parser:

```
program     → declaração*
declaração  → varDecl | comando
varDecl     → ("int" | "bool") IDENT ( "=" expressão )? ";"
comando     → ifStmt | whileStmt | printStmt | readStmt | bloco | exprStmt
ifStmt      → "if" "(" expressão ")" comando ( "else" comando )?
whileStmt   → "while" "(" expressão ")" comando
printStmt   → "print" expressão ";"
readStmt    → "read" IDENT ";"
bloco       → "{" declaração* "}"
exprStmt    → expressão ";"

expressão   → atribuição
atribuição  → IDENT "=" atribuição | igualdade
igualdade   → comparação ( ("==" | "!=") comparação )*
comparação  → soma ( ("<" | ">") soma )*
soma        → produto ( ("+" | "-") produto )*
produto     → unário ( ("*" | "/") unário )*
unário      → "-" unário | primário
primário    → NÚMERO | STRING | "true" | "false" | IDENT | "(" expressão ")"
```

> **Por que a expressão é dividida em tantos níveis?** Isso codifica a **precedência**.
> Quem está "mais embaixo" (produto, `*` e `/`) é avaliado primeiro. Por isso
> `2 + 3 * 4` dá 14 e não 20 — explicado no exemplo da Seção 12.

---

## 5. Visão geral dos arquivos

| Arquivo | Papel |
|---|---|
| `token_model.py` | a classe `Token` (a "peça" que o scanner produz) |
| `tokens_def.py` | nomes dos tipos de token e a lista de palavras reservadas |
| `scanner.py` | **Fase A** — transforma texto em tokens |
| `ast_nodes.py` | as classes que formam a árvore (AST) |
| `parser.py` | **Fase B** — transforma tokens em AST |
| `semantic.py` | **Fase C** — checa tipos e escopos |
| `ir.py` | **Fase D** — gera o código de três endereços |
| `codegen.py` | **Fase E** — gera o bytecode e contém a máquina virtual |
| `main.py` | o "maestro": chama as fases em ordem |

---

## 6. Fase A — Análise Léxica (Scanner)

**Arquivos:** `scanner.py`, `tokens_def.py`, `token_model.py`

### O que faz
Lê o código fonte caractere por caractere e o quebra em **tokens** — as menores
unidades com significado. Por exemplo, `x = 10;` vira:
`IDENTIFIER(x)`, `EQUAL(=)`, `NUMBER(10)`, `SEMICOLON(;)`.
Espaços, quebras de linha e comentários são jogados fora.

### Como faz
O scanner funciona como um **Autômato Finito Determinístico (AFD)**: ele olha o
caractere atual e decide o que fazer.

- Se for um símbolo de um caractere só (`+ - * ; ( ) { } < >`), cria o token direto
  usando o dicionário `SINGLE_CHAR_TOKENS`.
- Se for `=`, ele "espia" o próximo: se for outro `=`, é `==` (`EQUAL_EQUAL`); senão é
  `=` (`EQUAL`). O mesmo truque vale para `!=`.
- Se for `/`, espia: `//` é comentário (ignora até a quebra de linha); senão é divisão.
- Se for um dígito, chama `number()` e continua lendo enquanto houver dígitos.
- Se for uma letra, chama `identifier()` e lê o "nome" inteiro; depois checa no
  dicionário `KEYWORDS` se aquele nome é uma palavra reservada (`if`, `while`, `int`...)
  ou um identificador comum.
- Se for `"`, chama `string()` e lê até a próxima aspa.

> **Ligação com Expressões Regulares:** os laços de leitura são a ER na prática.
> `while self.peek().isdigit()` é o mesmo que a ER `[0-9]+` (um número). E
> `while self.peek().isalnum()` é `[a-zA-Z0-9_]*` (um identificador). Essa estratégia de
> "ler o máximo que casa" se chama **maximal munch**.

### Métodos-chave
- `advance()` — consome um caractere e o devolve (e conta linhas/colunas).
- `peek()` — olha o caractere atual **sem** consumir.
- `match(c)` — consome o próximo caractere só se ele for igual a `c` (usado para `==`, `!=`, `//`).
- `add_token(tipo, literal)` — cria um `Token` e guarda na lista.
- `scan_tokens()` — laço principal; no fim adiciona o token `EOF` (fim de arquivo).

### Saída
Uma lista de objetos `Token`. Cada `Token` (em `token_model.py`) guarda: o `type`, o
`lexeme` (texto exato), o `literal` (valor já convertido, ex.: o número `10`), e a
`line`/`column` (para mensagens de erro).

### Erros que detecta
Caractere inválido (ex.: `@`) e string não terminada. Ele imprime a linha do erro e
marca `had_error = True`.

---

## 7. Fase B — Análise Sintática (Parser)

**Arquivos:** `parser.py`, `ast_nodes.py`

### O que faz
Pega a lista de tokens e verifica se eles formam frases válidas segundo a gramática.
Se sim, monta a **AST (Árvore de Sintaxe Abstrata)** — uma árvore que representa a
estrutura do programa. Se a ordem dos tokens estiver errada (ex.: faltou `;`), reporta
erro de sintaxe.

### Como faz
Usa a técnica de **Parser Descendente Recursivo**: existe **uma função para cada regra
da gramática**, e elas se chamam umas às outras. Começa em `parse()` → `declaration()`
→ `statement()` → ... → `expression()` → ... → `primary()`.

A **precedência dos operadores** está embutida na ordem das chamadas:
`equality → comparison → term → factor → unary → primary`. Como `factor` (`*`, `/`)
está mais "fundo" que `term` (`+`, `-`), a multiplicação é agrupada primeiro.

### Ferramentas internas do parser
- `peek()` / `previous()` — token atual / token anterior.
- `check(tipo)` — o token atual é desse tipo?
- `match(tipos...)` — se o token atual for um dos tipos, consome e devolve `True`.
- `consume(tipo, msg)` — exige um token específico; se não vier, dispara erro (ex.: exigir `;`).

### A AST (`ast_nodes.py`)
Cada construção vira uma classe simples de dados (dataclass):
- **Expressões:** `Literal` (valor fixo), `Variable`, `Assign`, `Unary`, `Binary`, `Grouping`.
- **Comandos:** `VarDecl`, `ExpressionStmt`, `Print`, `Read`, `If`, `While`, `Block`.

Exemplo: `x = 2 + 3` vira
`Assign(x, Binary(Literal(2), +, Literal(3)))`.

### Saída
Uma lista de nós de comando (a AST). Erros de sintaxe são reportados com a linha e o
parser para (lança `ParseError`).

---

## 8. Fase C — Análise Semântica

**Arquivo:** `semantic.py`

### O que faz
A gramática garante que o programa está "bem escrito", mas não que ele "faz sentido".
A análise semântica checa o sentido:
1. **Variável declarada antes de usar** — usar `y` sem declarar é erro.
2. **Não declarar a mesma variável duas vezes** no mesmo escopo.
3. **Tipos compatíveis (type checking)** — não dá para fazer `int x = true;`, nem somar
   um `bool` com `int`.
4. **Condição de `if`/`while` precisa ser `bool`** — `if (x + 1)` é erro.

### Como faz
**Tabela de Símbolos (`SymbolTable`)** é uma **pilha de escopos**. Cada escopo é um
dicionário `nome → tipo`.
- Entrar num bloco `{ }` → `begin_scope()` empilha um dicionário novo.
- Sair do bloco → `end_scope()` desempilha.
- `declare(nome, tipo)` registra a variável no escopo do topo (e recusa se já existir lá).
- `lookup(nome)` procura do escopo mais interno para o mais externo (é assim que o
  escopo funciona: o de dentro "enxerga" o de fora).

O **type checking** é feito por `check_expr`, que percorre a expressão e **devolve o
tipo dela** (`"int"`, `"bool"`, `"string"` ou `"erro"`). Por exemplo, em `check_binary`:
- `+ - * /` exigem dois `int` e resultam em `int`;
- `< >` exigem dois `int` e resultam em `bool`;
- `== !=` exigem os dois lados do mesmo tipo e resultam em `bool`.

O tipo especial `"erro"` evita avalanche de mensagens: quando algo já deu erro, ele se
propaga silenciosamente para não acusar o mesmo problema várias vezes.

### Saída
Não transforma a árvore; apenas **valida**. Devolve `True` (tudo certo) ou `False` (teve
erro). Se houver erro, o `main` aborta a compilação.

---

## 9. Fase D — Código Intermediário (TAC)

**Arquivo:** `ir.py`

### O que faz
Traduz a AST para o **Código de Três Endereços (TAC)** — uma lista linear de instruções
bem simples, cada uma com no máximo três "endereços" (operandos). É uma representação
**independente de máquina**: não é Python nem Assembly, é um meio-termo que facilita a
geração do código final.

Exemplo: `x = 2 + 3 * 4` vira
```
t1 = 3 * 4
t2 = 2 + t1
x = t2
```
Os `t1`, `t2` são **temporários** criados pelo gerador para guardar resultados parciais.

### Como faz
A classe `IRGenerator` percorre a árvore (`gen_stmt` para comandos, `gen_expr` para
expressões). A sacada está em `gen_expr`: **toda expressão devolve o "lugar" onde seu
resultado ficou** — pode ser uma constante, o nome de uma variável, ou um temporário
novo. Esse lugar é usado pela operação de cima.

- `new_temp()` cria `t1`, `t2`, ... (resultados parciais).
- `new_label()` cria `L1`, `L2`, ... (alvos de desvio).
- Um valor literal é embrulhado em `Const(valor)` para diferenciá-lo do nome de uma
  variável (ambos poderiam ser texto; o `Const` desfaz a ambiguidade).

### `if` e `while` viram desvios (jumps)
Não existe "bloco" no TAC; tudo é desvio condicional + rótulo:

`if (cond) A else B` vira:
```
    ifFalse cond goto L1   # se a condição for falsa, pula o A
    <A>
    goto L2
L1:
    <B>
L2:
```

`while (cond) C` vira:
```
L1:
    ifFalse cond goto L2   # condição falsa → sai do laço
    <C>
    goto L1                # volta a testar
L2:
```

### Saída
Uma lista de instruções `Instr(op, arg1, arg2, result)`. A função `format_instr` serve
só para imprimir bonito no modo `--debug`.

---

## 10. Fase E — Código Final (Bytecode) + Máquina Virtual

**Arquivo:** `codegen.py`

### O que faz
Rebaixa o TAC para o **código final**: um **bytecode** para uma **máquina de pilha**. E
inclui a própria **máquina virtual (VM)** que executa esse bytecode e produz a saída.
(O PDF permite escolher Assembly **ou** bytecode para uma VM — escolhemos o bytecode,
porque assim conseguimos rodar de verdade e mostrar o resultado.)

### Por que máquina de pilha?
Numa máquina de pilha, contas são feitas empilhando operandos e aplicando operações.
`2 + 3` vira: `PUSH 2`, `PUSH 3`, `ADD` (desempilha 2 e 3, empilha 5). É o modelo mais
simples de gerar e de executar — é o mesmo princípio da JVM e da CPython.

### A tradução (`CodeGenerator.generate`)
Cada instrução TAC vira algumas instruções de bytecode. Para uma operação binária
`t = a op b`:
```
LOAD/PUSH a     # coloca a no topo da pilha
LOAD/PUSH b     # coloca b no topo
<OP>            # desempilha os dois, opera, empilha o resultado
STORE t         # tira o resultado e guarda na memória, no nome t
```
`push_operand` decide: se for `Const`, gera `PUSH valor`; se for um nome, gera
`LOAD nome` (carrega da memória).

Os rótulos (`L1`, `L2`) viram `LABEL`, e os desvios viram `JMP` (incondicional) e `JMPF`
(jump-if-false: desempilha e pula se for falso).

### Opcodes (instruções da VM)
`PUSH, LOAD, STORE, ADD, SUB, MUL, DIV, LT, GT, EQ, NEQ, NEG, PRINT, READ, JMP, JMPF,
LABEL, HALT`.

### A máquina virtual (`VM`)
Tem duas estruturas:
- **`stack`** (pilha) — onde as contas acontecem.
- **`memory`** (dicionário) — onde ficam variáveis e temporários, guardados pelo nome.

Antes de rodar, ela faz uma passada mapeando cada `LABEL` para o índice da instrução
(assim o `JMP L1` sabe para onde pular). Depois roda num laço com um "ponteiro de
programa" `pc`:
- `PUSH v` → empilha `v`; `LOAD n` → empilha `memory[n]`; `STORE n` → desempilha para `memory[n]`.
- `ADD/SUB/...` → desempilha dois, opera, empilha.
- `PRINT` → desempilha e imprime (booleanos saem como `true`/`false`).
- `READ n` → lê uma linha da entrada e guarda em `memory[n]`.
- `JMP`/`JMPF` → mudam o `pc` (desvios).
- `HALT` → fim.

### Saída
A própria execução do programa (o que aparece na tela). Detalhes: `/` é divisão inteira
e divisão por zero gera um erro de execução claro.

---

## 11. O driver — `main.py`

É quem **liga as fases em ordem**. Ele:
1. lê o arquivo passado na linha de comando;
2. roda Fase A (scanner) — se deu erro léxico, para;
3. roda Fase B (parser) — se deu erro de sintaxe, para;
4. roda Fase C (semântica) — se deu erro semântico, para;
5. roda Fase D (TAC) e Fase E (bytecode);
6. executa o bytecode na VM.

Com `--debug`, ele imprime a saída de cada fase (tokens, AST, tabela de símbolos, TAC,
bytecode) antes de executar. A função `dump_ast` desenha a árvore indentada.

---

## 12. Exemplo completo, ponta a ponta

Programa (`mini.txt`):
```
int x;
x = 2 + 3 * 4;
print x;
```

**Fase A — Tokens:**
```
INT 'int' · IDENTIFIER 'x' · SEMICOLON ';'
IDENTIFIER 'x' · EQUAL '=' · NUMBER '2' · PLUS '+' · NUMBER '3' · STAR '*' · NUMBER '4' · SEMICOLON ';'
PRINT 'print' · IDENTIFIER 'x' · SEMICOLON ';' · EOF
```

**Fase B — AST** (repare que `3 * 4` fica *dentro* do `+`, por causa da precedência):
```
VarDecl int x
Assign x
  Binary +
    Literal 2
    Binary *
      Literal 3
      Literal 4
Print
  Variable x
```

**Fase C — Tabela de Símbolos:** `x : int` (escopo 0). Tipos batem, sem erros.

**Fase D — TAC** (o `*` é resolvido antes do `+`):
```
x = 0          # valor padrão da declaração
t1 = 3 * 4
t2 = 2 + t1
x = t2
print x
```

**Fase E — Bytecode:**
```
 0: PUSH 0      \
 1: STORE x      } int x;  (inicializa x com 0)
 2: PUSH 3      \
 3: PUSH 4       } t1 = 3 * 4
 4: MUL          |
 5: STORE t1    /
 6: PUSH 2      \
 7: LOAD t1      } t2 = 2 + t1
 8: ADD          |
 9: STORE t2    /
10: LOAD t2     \
11: STORE x      } x = t2
12: LOAD x      \
13: PRINT        } print x
14: HALT
```

**Execução:** imprime `14`.

> Esse exemplo é ótimo para apresentar: ele mostra a **precedência** sobrevivendo por
> todas as fases (na AST, no TAC e no bytecode `3*4` sempre vem antes do `+`).

---

## 13. Roteiro de apresentação (sugestão)

1. **Mostre o código-fonte** de um exemplo (`condicional.txt` ou `mini.txt`). Diga: "essa
   é a linguagem que o meu compilador entende".
2. **Rode com `--debug`** e explique fase por fase, de cima para baixo, usando a saída na
   tela: "aqui o texto virou tokens; aqui os tokens viraram árvore; aqui validei tipos;
   aqui gerei o código intermediário; aqui o código final; e aqui executou".
3. **Mostre a precedência** com `mini.txt` (`2 + 3 * 4 = 14`): aponte que `3*4` está
   aninhado dentro do `+` na AST.
4. **Mostre a detecção de erros** rodando `erros.txt`: o compilador rejeita programa
   inválido (erro de tipo e variável não declarada) — isso é a parte semântica.
5. **Mostre executando de verdade** com entrada: `python3 main.py exemplos/fatorial.txt`
   e digite um número. Prova que o código final roda e dá o resultado certo.

---

## 14. Perguntas que o professor pode fazer (com respostas)

**"Como você trata a precedência dos operadores?"**
Pela ordem das funções no parser: `equality → comparison → term → factor → unary →
primary`. As que ficam mais embaixo (multiplicação/divisão) são agrupadas primeiro.

**"O que é a AST e por que usar?"**
É a árvore que representa a estrutura do programa, sem detalhes de pontuação. Ela
facilita as próximas fases (semântica e geração de código) porque trabalhar numa árvore
é muito mais fácil que numa lista de tokens.

**"Como funciona a tabela de símbolos e o escopo?"**
É uma pilha de dicionários (`nome → tipo`). Cada bloco `{ }` empilha um escopo novo. A
busca por uma variável vai do escopo mais interno para o mais externo.

**"O que é código de três endereços?"**
Uma representação intermediária linear, com instruções simples de no máximo três
operandos (ex.: `t1 = a + b`). É independente de máquina e serve de ponte para o código
final.

**"Por que máquina de pilha em vez de Assembly real?"**
O PDF permite bytecode para uma VM. A máquina de pilha é simples de gerar e, como eu
mesmo escrevi a VM, consigo executar o programa e mostrar o resultado na hora.

**"Como o `while` é traduzido?"**
Em desvios: um rótulo no início, um `ifFalse` que sai do laço quando a condição é falsa,
o corpo, e um `goto` que volta para o início.

**"O que acontece se eu usar uma variável não declarada?"**
A Fase C detecta com `lookup` retornando `None` e reporta erro semântico, abortando
antes de gerar código.

---

## 15. Glossário

- **Token:** menor unidade com significado (palavra reservada, número, operador...).
- **Lexema:** o texto exato de um token (ex.: o lexema do token `NUMBER` é `"10"`).
- **AFD (Autômato Finito Determinístico):** máquina de estados que lê símbolos e decide;
  é o modelo por trás do scanner.
- **AST (Árvore de Sintaxe Abstrata):** árvore que representa a estrutura do programa.
- **Parser Descendente Recursivo:** parser com uma função por regra da gramática.
- **Tabela de Símbolos:** estrutura que guarda as variáveis e seus tipos por escopo.
- **Type checking:** verificação de que os tipos das operações são compatíveis.
- **TAC (Three-Address Code):** código intermediário com instruções de até 3 operandos.
- **Temporário:** variável auxiliar criada pelo compilador (`t1`, `t2`...).
- **Bytecode:** código de baixo nível executado por uma máquina virtual.
- **Máquina de pilha:** VM que faz contas empilhando e desempilhando valores.
- **Opcode:** o "verbo" de uma instrução de bytecode (`PUSH`, `ADD`, `JMP`...).
