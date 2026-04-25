from dataclasses import dataclass
from typing import Union
POSTFIX_OPS = {'*', '+', '?'}

@dataclass
class LiteralNode:
    char: str

@dataclass
class UnionNode:
    left: 'ASTNode'
    right: 'ASTNode'

@dataclass
class ConcatNode:
    left: 'ASTNode'
    right: 'ASTNode'

@dataclass
class StarNode:
    child: 'ASTNode'

@dataclass
class PlusNode:
    child: 'ASTNode'

@dataclass
class QuestionNode:
    child: 'ASTNode'

@dataclass
class EpsilonNode:
    pass

ASTNode = Union[LiteralNode, UnionNode, ConcatNode, StarNode, PlusNode, QuestionNode, EpsilonNode]

class RegexParser:
    def __init__(self, regex_str: str):
        self.regex = regex_str
        self.pos = 0

    def peek(self) -> str:
        if self.pos < len(self.regex):
            return self.regex[self.pos]
        return ''

    def consume(self) -> str:
        if self.pos < len(self.regex):
            c = self.regex[self.pos]
            self.pos += 1
            return c
        return ''

    def parse(self) -> ASTNode:
        if not self.regex:
            return EpsilonNode()
        node = self.parse_union()
        if self.pos < len(self.regex):
            raise ValueError(f"Unexpected character at position {self.pos}: '{self.peek()}'")
        return node

    def parse_union(self) -> ASTNode:
        node = self.parse_concat()
        while self.peek() == '|':
            self.consume()
            
            # Check for dangling OR
            if self.pos >= len(self.regex) or self.peek() == ')':
                raise ValueError("Invalid regex: empty operand after '|'")

            right = self.parse_concat()
            node = UnionNode(node, right)
        return node

    def parse_concat(self) -> ASTNode:
        nodes = []
        while self.pos < len(self.regex) and self.peek() not in ['|', ')']:
            c = self.peek()
            if c in POSTFIX_OPS and not nodes:
                raise ValueError(f"Unexpected operator '{c}' at position {self.pos}")
            nodes.append(self.parse_quantified())
        
        if not nodes:
            raise ValueError(f"Invalid regex: empty operand at position {self.pos}")
        
        node = nodes[0]
        for right in nodes[1:]:
            node = ConcatNode(node, right)
        return node

    def parse_quantified(self) -> ASTNode:
        node = self.parse_base()

        while self.pos < len(self.regex) and self.regex[self.pos] in POSTFIX_OPS:
            op = self.regex[self.pos]
            self.pos += 1

            # Catch invalid double postfix like a** or a+?
            if self.pos < len(self.regex) and self.regex[self.pos] in POSTFIX_OPS:
                raise ValueError(
                    f"Invalid regex: consecutive postfix operators "
                    f"'{op}{self.regex[self.pos]}' at position {self.pos - 1}"
                )

            if op == '*':
                node = StarNode(node)
            elif op == '+':
                node = PlusNode(node)
            elif op == '?':
                node = QuestionNode(node)

        return node

    def parse_base(self) -> ASTNode:
        c = self.peek()
        if c == '(':
            self.consume()
            # Catch empty parens ()
            if self.peek() == ')':
                self.consume()
                return EpsilonNode()
            # Ensure not incomplete like `(ab`
            node = self.parse_union()
            if self.consume() != ')':
                raise ValueError(f"Expected ')' at position {self.pos}")
            return node
        elif c == '[':
            self.consume()
            return self.parse_class()
        elif c in ['*', '+', '?', '|', ')', ']']:
            raise ValueError(f"Unexpected operator '{c}' at position {self.pos}")
        elif c == '':
            raise ValueError("Unexpected end of string")
        else:
            self.consume()
            return LiteralNode(c)

    def parse_class(self) -> ASTNode:
        chars = []
        while self.pos < len(self.regex) and self.peek() != ']':
            chars.append(self.consume())
        if self.consume() != ']':
            raise ValueError(f"Expected ']' to close character class at position {self.pos}")
        
        if not chars:
            return EpsilonNode()
        
        node = LiteralNode(chars[0])
        for char in chars[1:]:
            node = UnionNode(node, LiteralNode(char))
        return node


def parse(regex_str: str) -> ASTNode:
    parser = RegexParser(regex_str)
    return parser.parse()


def pretty_print(node: ASTNode, indent: int = 0):
    prefix = '  ' * indent
    if isinstance(node, LiteralNode):
        print(f"{prefix}Literal('{node.char}')")
    elif isinstance(node, EpsilonNode):
        print(f"{prefix}Epsilon()")
    elif isinstance(node, StarNode):
        print(f"{prefix}Star()")
        pretty_print(node.child, indent + 1)
    elif isinstance(node, PlusNode):
        print(f"{prefix}Plus()")
        pretty_print(node.child, indent + 1)
    elif isinstance(node, QuestionNode):
        print(f"{prefix}Question()")
        pretty_print(node.child, indent + 1)
    elif isinstance(node, UnionNode):
        print(f"{prefix}Union()")
        pretty_print(node.left, indent + 1)
        pretty_print(node.right, indent + 1)
    elif isinstance(node, ConcatNode):
        print(f"{prefix}Concat()")
        pretty_print(node.left, indent + 1)
        pretty_print(node.right, indent + 1)


def run_tests():
    test_cases = [
        'a*b',
        '(a|b)*c',
        'a+b?c',
        '(ab|cd)*'
    ]
    
    for tc in test_cases:
        print(f"\n--- Parsing Regex: '{tc}' ---")
        try:
            ast = parse(tc)
            pretty_print(ast)
        except Exception as e:
            print(f"Error parsing '{tc}': {e}")
            
    print("\n--- Testing Error Handling ---")
    error_cases = ['(a|b', 'a|*b', '[abc', 'a)', '|a', 'a**']
    for ec in error_cases:
        try:
            parse(ec)
            print(f"Failed to catch error in '{ec}'")
        except ValueError as e:
            print(f"Correctly caught error in '{ec}': {e}")


if __name__ == '__main__':
    run_tests()
