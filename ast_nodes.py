from dataclasses import dataclass


@dataclass
class Literal:
    value: object
    type: str


@dataclass
class Variable:
    name: object


@dataclass
class Assign:
    name: object
    value: object


@dataclass
class Unary:
    operator: object
    right: object


@dataclass
class Binary:
    left: object
    operator: object
    right: object


@dataclass
class Grouping:
    expression: object


@dataclass
class VarDecl:
    var_type: str
    name: object
    initializer: object


@dataclass
class ExpressionStmt:
    expression: object


@dataclass
class Print:
    expression: object


@dataclass
class Read:
    name: object


@dataclass
class If:
    keyword: object
    condition: object
    then_branch: object
    else_branch: object


@dataclass
class While:
    keyword: object
    condition: object
    body: object


@dataclass
class Block:
    statements: list
