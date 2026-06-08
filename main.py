import sys

from scanner import Scanner
from parser import Parser, ParseError
from semantic import SemanticAnalyzer
import ir
from codegen import CodeGenerator, VM, format_bytecode
import ast_nodes as ast


def dump_ast(node, indent=0):
    espaco = "  " * indent
    if isinstance(node, ast.VarDecl):
        print(f"{espaco}VarDecl {node.var_type} {node.name.lexeme}")
        if node.initializer is not None:
            dump_ast(node.initializer, indent + 1)
    elif isinstance(node, ast.Print):
        print(f"{espaco}Print")
        dump_ast(node.expression, indent + 1)
    elif isinstance(node, ast.Read):
        print(f"{espaco}Read {node.name.lexeme}")
    elif isinstance(node, ast.ExpressionStmt):
        dump_ast(node.expression, indent)
    elif isinstance(node, ast.If):
        print(f"{espaco}If")
        dump_ast(node.condition, indent + 1)
        dump_ast(node.then_branch, indent + 1)
        if node.else_branch is not None:
            print(f"{espaco}else:")
            dump_ast(node.else_branch, indent + 1)
    elif isinstance(node, ast.While):
        print(f"{espaco}While")
        dump_ast(node.condition, indent + 1)
        dump_ast(node.body, indent + 1)
    elif isinstance(node, ast.Block):
        print(f"{espaco}Block")
        for s in node.statements:
            dump_ast(s, indent + 1)
    elif isinstance(node, ast.Binary):
        print(f"{espaco}Binary {node.operator.lexeme}")
        dump_ast(node.left, indent + 1)
        dump_ast(node.right, indent + 1)
    elif isinstance(node, ast.Unary):
        print(f"{espaco}Unary {node.operator.lexeme}")
        dump_ast(node.right, indent + 1)
    elif isinstance(node, ast.Grouping):
        dump_ast(node.expression, indent)
    elif isinstance(node, ast.Assign):
        print(f"{espaco}Assign {node.name.lexeme}")
        dump_ast(node.value, indent + 1)
    elif isinstance(node, ast.Literal):
        print(f"{espaco}Literal {node.value}")
    elif isinstance(node, ast.Variable):
        print(f"{espaco}Variable {node.name.lexeme}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo> [--debug]")
        return

    path = sys.argv[1]
    debug = "--debug" in sys.argv

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    if scanner.had_error:
        return
    if debug:
        print("--- TOKENS ---")
        for tok in tokens:
            print(tok.type, repr(tok.lexeme))

    parser = Parser(tokens)
    try:
        tree = parser.parse()
    except ParseError:
        return
    if debug:
        print("\n--- AST ---")
        for stmt in tree:
            dump_ast(stmt)

    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(tree):
        return
    if debug:
        print("\n--- TABELA DE SIMBOLOS ---")
        for nome, tipo, escopo in analyzer.symbols.all_symbols:
            print(nome, tipo, "escopo", escopo)

    gen = ir.IRGenerator()
    tac = gen.generate(tree)
    if debug:
        print("\n--- CODIGO INTERMEDIARIO (TAC) ---")
        for instr in tac:
            print(ir.format_instr(instr))

    cg = CodeGenerator()
    bytecode = cg.generate(tac)
    if debug:
        print("\n--- BYTECODE ---")
        print(format_bytecode(bytecode))
        print("\n--- EXECUCAO ---")

    VM(bytecode).run()


if __name__ == "__main__":
    main()
