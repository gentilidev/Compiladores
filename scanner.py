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
        self.had_error = False

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        if c == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def match(self, expected):
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def add_token(self, type, literal=None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(type, lexeme, literal, self.line, self.column))

    def error(self, message):
        self.had_error = True
        print(f"[linha {self.line}] Erro lexico: {message}")

    def scan_token(self):
        c = self.advance()

        if c in tokens_def.SINGLE_CHAR_TOKENS:
            self.add_token(tokens_def.SINGLE_CHAR_TOKENS[c])
        elif c == "=":
            if self.match("="):
                self.add_token(tokens_def.EQUAL_EQUAL)
            else:
                self.add_token(tokens_def.EQUAL)
        elif c == "!":
            if self.match("="):
                self.add_token(tokens_def.BANG_EQUAL)
            else:
                self.error("caractere inesperado '!'")
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(tokens_def.SLASH)
        elif c in (" ", "\r", "\t", "\n"):
            pass
        elif c == '"':
            self.string()
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == "_":
            self.identifier()
        else:
            self.error(f"caractere inesperado '{c}'")

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            self.advance()
        if self.is_at_end():
            self.error("string nao terminada")
            return
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(tokens_def.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        value = int(self.source[self.start:self.current])
        self.add_token(tokens_def.NUMBER, value)

    def identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.source[self.start:self.current]
        type = tokens_def.KEYWORDS.get(text, tokens_def.IDENTIFIER)
        self.add_token(type)

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(tokens_def.EOF, "", None, self.line, self.column))
        return self.tokens
