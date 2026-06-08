import ir


BINOPS = {
    "+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV",
    "<": "LT", ">": "GT", "==": "EQ", "!=": "NEQ",
}


class CodeGenerator:
    def __init__(self):
        self.code = []

    def push_operand(self, operand):
        if isinstance(operand, ir.Const):
            return ("PUSH", operand.value)
        return ("LOAD", operand)

    def generate(self, tac_code):
        for instr in tac_code:
            op = instr.op

            if op == "=":
                self.code.append(self.push_operand(instr.arg1))
                self.code.append(("STORE", instr.result))
            elif op == "neg":
                self.code.append(self.push_operand(instr.arg1))
                self.code.append(("NEG",))
                self.code.append(("STORE", instr.result))
            elif op in BINOPS:
                self.code.append(self.push_operand(instr.arg1))
                self.code.append(self.push_operand(instr.arg2))
                self.code.append((BINOPS[op],))
                self.code.append(("STORE", instr.result))
            elif op == "print":
                self.code.append(self.push_operand(instr.arg1))
                self.code.append(("PRINT",))
            elif op == "read":
                self.code.append(("READ", instr.result))
            elif op == "label":
                self.code.append(("LABEL", instr.result))
            elif op == "goto":
                self.code.append(("JMP", instr.result))
            elif op == "if_false":
                self.code.append(self.push_operand(instr.arg1))
                self.code.append(("JMPF", instr.result))

        self.code.append(("HALT",))
        return self.code


class VM:
    def __init__(self, code):
        self.code = code
        self.stack = []
        self.memory = {}
        self.labels = {}
        for i, instr in enumerate(code):
            if instr[0] == "LABEL":
                self.labels[instr[1]] = i

    def format_value(self, value):
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def parse_input(self, line):
        line = line.strip()
        if line == "true":
            return True
        if line == "false":
            return False
        return int(line)

    def run(self):
        pc = 0
        while pc < len(self.code):
            instr = self.code[pc]
            op = instr[0]

            if op == "PUSH":
                self.stack.append(instr[1])
            elif op == "LOAD":
                self.stack.append(self.memory.get(instr[1], 0))
            elif op == "STORE":
                self.memory[instr[1]] = self.stack.pop()
            elif op == "ADD":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a + b)
            elif op == "SUB":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a - b)
            elif op == "MUL":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a * b)
            elif op == "DIV":
                b = self.stack.pop(); a = self.stack.pop()
                if b == 0:
                    raise RuntimeError("divisao por zero")
                self.stack.append(a // b)
            elif op == "LT":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a < b)
            elif op == "GT":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a > b)
            elif op == "EQ":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a == b)
            elif op == "NEQ":
                b = self.stack.pop(); a = self.stack.pop(); self.stack.append(a != b)
            elif op == "NEG":
                a = self.stack.pop(); self.stack.append(-a)
            elif op == "PRINT":
                print(self.format_value(self.stack.pop()))
            elif op == "READ":
                self.memory[instr[1]] = self.parse_input(input())
            elif op == "JMP":
                pc = self.labels[instr[1]]
                continue
            elif op == "JMPF":
                if not self.stack.pop():
                    pc = self.labels[instr[1]]
                    continue
            elif op == "LABEL":
                pass
            elif op == "HALT":
                break

            pc += 1


def format_bytecode(code):
    linhas = []
    for i, instr in enumerate(code):
        if len(instr) == 1:
            texto = instr[0]
        else:
            texto = f"{instr[0]} {instr[1]}"
        linhas.append(f"{i:>3}: {texto}")
    return "\n".join(linhas)
