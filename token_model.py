from dataclasses import dataclass


@dataclass
class Token:
    type: str
    lexeme: str
    literal: object
    line: int
    column: int
