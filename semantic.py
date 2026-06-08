import tokens_def as T
import ast_nodes as ast


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.all_symbols = []

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name, var_type):
        scope = self.scopes[-1]
        if name in scope:
            return False
        scope[name] = var_type
        self.all_symbols.append((name, var_type, len(self.scopes) - 1))
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()
        self.had_error = False

    def error(self, token, message):
        self.had_error = True
        print(f"[linha {token.line}] Erro semantico: {message}")

    def analyze(self, statements):
        for stmt in statements:
            self.check_stmt(stmt)
        return not self.had_error

    def check_stmt(self, stmt):
        if isinstance(stmt, ast.VarDecl):
            if stmt.initializer is not None:
                init_type = self.check_expr(stmt.initializer)
                if init_type != "erro" and init_type != stmt.var_type:
                    self.error(stmt.name,
                               f"variavel '{stmt.name.lexeme}' e do tipo "
                               f"'{stmt.var_type}' mas recebeu '{init_type}'")
            if not self.symbols.declare(stmt.name.lexeme, stmt.var_type):
                self.error(stmt.name,
                           f"variavel '{stmt.name.lexeme}' ja declarada neste escopo")

        elif isinstance(stmt, ast.Print):
            self.check_expr(stmt.expression)

        elif isinstance(stmt, ast.Read):
            if self.symbols.lookup(stmt.name.lexeme) is None:
                self.error(stmt.name, f"variavel '{stmt.name.lexeme}' nao declarada")

        elif isinstance(stmt, ast.ExpressionStmt):
            self.check_expr(stmt.expression)

        elif isinstance(stmt, ast.If):
            cond = self.check_expr(stmt.condition)
            if cond not in ("erro", "bool"):
                self.error(stmt.keyword, "a condicao do 'if' deve ser booleana")
            self.check_stmt(stmt.then_branch)
            if stmt.else_branch is not None:
                self.check_stmt(stmt.else_branch)

        elif isinstance(stmt, ast.While):
            cond = self.check_expr(stmt.condition)
            if cond not in ("erro", "bool"):
                self.error(stmt.keyword, "a condicao do 'while' deve ser booleana")
            self.check_stmt(stmt.body)

        elif isinstance(stmt, ast.Block):
            self.symbols.begin_scope()
            for s in stmt.statements:
                self.check_stmt(s)
            self.symbols.end_scope()

    def check_expr(self, expr):
        if isinstance(expr, ast.Literal):
            return expr.type

        if isinstance(expr, ast.Variable):
            t = self.symbols.lookup(expr.name.lexeme)
            if t is None:
                self.error(expr.name, f"variavel '{expr.name.lexeme}' nao declarada")
                return "erro"
            return t

        if isinstance(expr, ast.Assign):
            value_type = self.check_expr(expr.value)
            var_type = self.symbols.lookup(expr.name.lexeme)
            if var_type is None:
                self.error(expr.name, f"variavel '{expr.name.lexeme}' nao declarada")
                return "erro"
            if value_type != "erro" and value_type != var_type:
                self.error(expr.name,
                           f"nao e possivel atribuir '{value_type}' a "
                           f"'{expr.name.lexeme}' do tipo '{var_type}'")
            return var_type

        if isinstance(expr, ast.Grouping):
            return self.check_expr(expr.expression)

        if isinstance(expr, ast.Unary):
            right = self.check_expr(expr.right)
            if right not in ("erro", "int"):
                self.error(expr.operator, "operador '-' exige inteiro")
            return "int"

        if isinstance(expr, ast.Binary):
            return self.check_binary(expr)

        return "erro"

    def check_binary(self, expr):
        left = self.check_expr(expr.left)
        right = self.check_expr(expr.right)
        op = expr.operator.type
        has_error = "erro" in (left, right)

        if op in (T.PLUS, T.MINUS, T.STAR, T.SLASH):
            if not has_error and (left != "int" or right != "int"):
                self.error(expr.operator,
                           f"operacao aritmetica exige inteiros, recebeu '{left}' e '{right}'")
            return "int"

        if op in (T.LESS, T.GREATER):
            if not has_error and (left != "int" or right != "int"):
                self.error(expr.operator,
                           f"comparacao exige inteiros, recebeu '{left}' e '{right}'")
            return "bool"

        if op in (T.EQUAL_EQUAL, T.BANG_EQUAL):
            if not has_error and left != right:
                self.error(expr.operator,
                           f"igualdade exige tipos iguais, recebeu '{left}' e '{right}'")
            return "bool"

        return "erro"
