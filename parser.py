import tokens_def as T
import ast_nodes as ast


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def is_at_end(self):
        return self.peek().type == T.EOF

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token, message):
        if token.type == T.EOF:
            print(f"[linha {token.line}] Erro de sintaxe no fim do arquivo: {message}")
        else:
            print(f"[linha {token.line}] Erro de sintaxe em '{token.lexeme}': {message}")
        return ParseError(message)

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self):
        if self.match(T.INT, T.BOOL):
            return self.var_declaration()
        return self.statement()

    def var_declaration(self):
        var_type = "int" if self.previous().type == T.INT else "bool"
        name = self.consume(T.IDENTIFIER, "esperado nome de variavel")
        initializer = None
        if self.match(T.EQUAL):
            initializer = self.expression()
        self.consume(T.SEMICOLON, "esperado ';' apos a declaracao")
        return ast.VarDecl(var_type, name, initializer)

    def statement(self):
        if self.match(T.IF):
            return self.if_statement()
        if self.match(T.WHILE):
            return self.while_statement()
        if self.match(T.PRINT):
            return self.print_statement()
        if self.match(T.READ):
            return self.read_statement()
        if self.match(T.LEFT_BRACE):
            return ast.Block(self.block())
        return self.expression_statement()

    def if_statement(self):
        keyword = self.previous()
        self.consume(T.LEFT_PAREN, "esperado '(' apos 'if'")
        condition = self.expression()
        self.consume(T.RIGHT_PAREN, "esperado ')' apos a condicao")
        then_branch = self.statement()
        else_branch = None
        if self.match(T.ELSE):
            else_branch = self.statement()
        return ast.If(keyword, condition, then_branch, else_branch)

    def while_statement(self):
        keyword = self.previous()
        self.consume(T.LEFT_PAREN, "esperado '(' apos 'while'")
        condition = self.expression()
        self.consume(T.RIGHT_PAREN, "esperado ')' apos a condicao")
        body = self.statement()
        return ast.While(keyword, condition, body)

    def print_statement(self):
        value = self.expression()
        self.consume(T.SEMICOLON, "esperado ';' apos o valor de print")
        return ast.Print(value)

    def read_statement(self):
        name = self.consume(T.IDENTIFIER, "esperado nome de variavel apos 'read'")
        self.consume(T.SEMICOLON, "esperado ';' apos o comando read")
        return ast.Read(name)

    def block(self):
        statements = []
        while not self.check(T.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(T.RIGHT_BRACE, "esperado '}' para fechar o bloco")
        return statements

    def expression_statement(self):
        expr = self.expression()
        self.consume(T.SEMICOLON, "esperado ';' apos a expressao")
        return ast.ExpressionStmt(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.equality()
        if self.match(T.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, ast.Variable):
                return ast.Assign(expr.name, value)
            raise self.error(equals, "alvo de atribuicao invalido")
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(T.EQUAL_EQUAL, T.BANG_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = ast.Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(T.LESS, T.GREATER):
            operator = self.previous()
            right = self.term()
            expr = ast.Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(T.PLUS, T.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = ast.Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(T.STAR, T.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = ast.Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(T.MINUS):
            operator = self.previous()
            right = self.unary()
            return ast.Unary(operator, right)
        return self.primary()

    def primary(self):
        if self.match(T.NUMBER):
            return ast.Literal(self.previous().literal, "int")
        if self.match(T.STRING):
            return ast.Literal(self.previous().literal, "string")
        if self.match(T.TRUE):
            return ast.Literal(True, "bool")
        if self.match(T.FALSE):
            return ast.Literal(False, "bool")
        if self.match(T.IDENTIFIER):
            return ast.Variable(self.previous())
        if self.match(T.LEFT_PAREN):
            expr = self.expression()
            self.consume(T.RIGHT_PAREN, "esperado ')' apos a expressao")
            return ast.Grouping(expr)
        raise self.error(self.peek(), "esperado uma expressao")
