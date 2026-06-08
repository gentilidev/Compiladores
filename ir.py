from dataclasses import dataclass
import tokens_def as T
import ast_nodes as ast


@dataclass
class Const:
    value: object


@dataclass
class Instr:
    op: str
    arg1: object = None
    arg2: object = None
    result: object = None


OP_SYMBOLS = {
    T.PLUS: "+",
    T.MINUS: "-",
    T.STAR: "*",
    T.SLASH: "/",
    T.LESS: "<",
    T.GREATER: ">",
    T.EQUAL_EQUAL: "==",
    T.BANG_EQUAL: "!=",
}


class IRGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, arg1=None, arg2=None, result=None):
        self.code.append(Instr(op, arg1, arg2, result))

    def generate(self, statements):
        for stmt in statements:
            self.gen_stmt(stmt)
        return self.code

    def gen_stmt(self, stmt):
        if isinstance(stmt, ast.VarDecl):
            if stmt.initializer is not None:
                value = self.gen_expr(stmt.initializer)
            else:
                value = Const(0) if stmt.var_type == "int" else Const(False)
            self.emit("=", value, None, stmt.name.lexeme)

        elif isinstance(stmt, ast.ExpressionStmt):
            self.gen_expr(stmt.expression)

        elif isinstance(stmt, ast.Print):
            value = self.gen_expr(stmt.expression)
            self.emit("print", value)

        elif isinstance(stmt, ast.Read):
            self.emit("read", None, None, stmt.name.lexeme)

        elif isinstance(stmt, ast.If):
            self.gen_if(stmt)

        elif isinstance(stmt, ast.While):
            self.gen_while(stmt)

        elif isinstance(stmt, ast.Block):
            for s in stmt.statements:
                self.gen_stmt(s)

    def gen_if(self, stmt):
        cond = self.gen_expr(stmt.condition)
        if stmt.else_branch is None:
            end_label = self.new_label()
            self.emit("if_false", cond, None, end_label)
            self.gen_stmt(stmt.then_branch)
            self.emit("label", None, None, end_label)
        else:
            else_label = self.new_label()
            end_label = self.new_label()
            self.emit("if_false", cond, None, else_label)
            self.gen_stmt(stmt.then_branch)
            self.emit("goto", None, None, end_label)
            self.emit("label", None, None, else_label)
            self.gen_stmt(stmt.else_branch)
            self.emit("label", None, None, end_label)

    def gen_while(self, stmt):
        start_label = self.new_label()
        end_label = self.new_label()
        self.emit("label", None, None, start_label)
        cond = self.gen_expr(stmt.condition)
        self.emit("if_false", cond, None, end_label)
        self.gen_stmt(stmt.body)
        self.emit("goto", None, None, start_label)
        self.emit("label", None, None, end_label)

    def gen_expr(self, expr):
        if isinstance(expr, ast.Literal):
            return Const(expr.value)

        if isinstance(expr, ast.Variable):
            return expr.name.lexeme

        if isinstance(expr, ast.Grouping):
            return self.gen_expr(expr.expression)

        if isinstance(expr, ast.Assign):
            value = self.gen_expr(expr.value)
            self.emit("=", value, None, expr.name.lexeme)
            return expr.name.lexeme

        if isinstance(expr, ast.Unary):
            value = self.gen_expr(expr.right)
            temp = self.new_temp()
            self.emit("neg", value, None, temp)
            return temp

        if isinstance(expr, ast.Binary):
            left = self.gen_expr(expr.left)
            right = self.gen_expr(expr.right)
            temp = self.new_temp()
            self.emit(OP_SYMBOLS[expr.operator.type], left, right, temp)
            return temp

        return None


def fmt_operand(x):
    if isinstance(x, Const):
        if isinstance(x.value, bool):
            return "true" if x.value else "false"
        if isinstance(x.value, str):
            return '"' + x.value + '"'
        return str(x.value)
    return str(x)


def format_instr(instr):
    op = instr.op
    if op == "label":
        return f"{instr.result}:"
    if op == "goto":
        return f"    goto {instr.result}"
    if op == "if_false":
        return f"    ifFalse {fmt_operand(instr.arg1)} goto {instr.result}"
    if op == "print":
        return f"    print {fmt_operand(instr.arg1)}"
    if op == "read":
        return f"    read {instr.result}"
    if op == "=":
        return f"    {instr.result} = {fmt_operand(instr.arg1)}"
    if op == "neg":
        return f"    {instr.result} = -{fmt_operand(instr.arg1)}"
    return f"    {instr.result} = {fmt_operand(instr.arg1)} {op} {fmt_operand(instr.arg2)}"
