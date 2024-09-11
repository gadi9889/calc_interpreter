INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'EOF'
)

class Token:
    def __init__(self, type: str, value: any) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return 'Token({type}, {value})'.format(
            type=self.type, value=repr(self.value)
        )

    def __repr__(self) -> str:
        return self.__str__()

class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self) -> None:
        raise Exception('Invalid character')

    def advance(self) -> None:
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self) -> int:
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')
            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            self.error()
        return Token(EOF, None)

class AST:
    pass

class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST) -> None:
        self.left = left
        self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value

class UnaryOp(AST):
    def __init__(self, op: Token, expr: AST) -> None:
        self.op = op
        self.expr = expr

class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self) -> None:
        raise Exception('Invalid syntax')

    def eat(self, token_type: str) -> None:
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self) -> AST:
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == MINUS:
            self.eat(MINUS)
            return UnaryOp(token, self.factor())
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self) -> AST:
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self) -> AST:
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def parse(self) -> AST:
        node = self.expr()
        if self.current_token.type != EOF:
            self.error()
        return node

class NodeVisitor:
    def visit(self, node: AST) -> any:
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: AST) -> None:
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def visit_BinOp(self, node: BinOp) -> int:
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Num(self, node: Num) -> int:
        return node.value

    def visit_UnaryOp(self, node: UnaryOp) -> int:
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def interpret(self) -> int:
        tree = self.parser.parse()
        return self.visit(tree)

def main() -> None:
    while True:
        try:
            text = input('spi> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)

if __name__ == '__main__':
    main()
