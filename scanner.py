import tokens_def
from token_model import Token


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(tokens_def.EOF, "", None, self.line, self.column))
        return self.tokens

    def scan_token(self):
        token = self.advance()

        if token in tokens_def.SINGLE_CHAR_TOKENS:
            self.add_token(tokens_def.SINGLE_CHAR_TOKENS[token])
        elif token == "=":
            if self.match("="):
                self.add_token(tokens_def.EQUAL_EQUAL)
            else:
                self.add_token(tokens_def.EQUAL)
        elif token == "!":
            if self.match("="):
                self.add_token(tokens_def.BANG_EQUAL)
            else:
                self.error_unexpected(token)
        elif token == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(tokens_def.SLASH)
        elif token in [" ", "\r", "\t"]:
            pass
        elif token == "\n":
            pass
        else:
            self.error_unexpected(token)

    def add_token(self, tipo, literal=None):
        lexema = self.source[self.start:self.current]
        token = Token(
            tipo=tipo,
            lexema=lexema,
            literal=literal,
            linha=self.line,
            coluna=self.column,
        )
        self.tokens.append(token)

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        self.column += 1

        if c == "\n":
            self.line += 1
            self.column = 1

        return c

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        self.column += 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def is_at_end(self):
        return self.current >= len(self.source)

    def error_unexpected(self, token):
        print(f"Caractere inesperado: {token} na linha {self.line}, coluna {self.column}")
