# Compilador

Trabalho da disciplina de **Compiladores** (2026/1) — turma ESW-NOT-PIT-7S-T2 (53334),
profa. Sheila Tirony. É um compilador feito em Python (sem usar bibliotecas prontas de
compilador). Ele passa pelas fases de análise léxica, sintática, semântica, gera código
intermediário (TAC) e código final (bytecode), e no fim executa o programa numa máquina
virtual de pilha.

## Como rodar

```
python3 main.py exemplos/condicional.txt
```

Para ver as fases (tokens, AST, tabela de símbolos, TAC e bytecode):

```
python3 main.py exemplos/condicional.txt --debug
```

Programas que usam `read` leem da entrada padrão:

```
echo 5 | python3 main.py exemplos/soma.txt
```

## A linguagem

- Tipos: `int` e `bool`
- Controle: `if / else` e `while`
- Operadores: `+ - * /` e `== != < >`
- Entrada/saída: `print` e `read`
- Comentários começam com `//`

Exemplo:

```
int n;
read n;
int soma;
soma = 0;
int i;
i = 1;
while (i < n + 1) {
    soma = soma + i;
    i = i + 1;
}
print soma;
```

## Arquivos

- `token_model.py` - classe Token
- `tokens_def.py` - tipos de token e palavras reservadas
- `scanner.py` - análise léxica
- `ast_nodes.py` - nós da árvore (AST)
- `parser.py` - análise sintática (parser descendente recursivo)
- `semantic.py` - análise semântica e tabela de símbolos
- `ir.py` - geração do código de três endereços (TAC)
- `codegen.py` - geração do bytecode e a máquina virtual
- `main.py` - junta tudo
- `exemplos/` - programas de teste

## Observação

A análise semântica rejeita variável usada fora do escopo. Na execução, porém, a VM
guarda as variáveis pelo nome num único dicionário, então duas variáveis de mesmo nome
em escopos diferentes usariam o mesmo espaço. Não tratei esse caso por ser fora do
escopo do trabalho.
