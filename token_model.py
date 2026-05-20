from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    lexema: str
    literal: object
    linha: int
    coluna: int
