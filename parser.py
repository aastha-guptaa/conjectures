import sys
import os

OPERATORS = {
    '<=': 2, '+': 2, '-': 2, '*': 2, '/': 2, '^': 2,
    'max-v': 2, 'max-v-u': 2, 'max-v-w': 2, 'dist': 2, 'weight': 2,
    'rank': 1, 'laplac': 1, 'degree': 1, 'temp': 1, 'IndRand': 1,
    'rad': 1, 'eigen': 1, 'large': 1, 'large-2': 1, 'dia': 1,
    'log': 1, 'sqrt': 1, 'sum': 1,
}

MATH_MAP = {
    'Adj': 'A', 'laplac': 'Laplacian', 'IndRand': 'Randic',
    'large': 'λ_max', 'large-2': 'λ_2', 'degree': 'degree',
    'temp': 'temp', 'rank': 'rank', 'eigen': 'eigenvalues',
}

class ASTNode:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        if not self.children:
            return str(self.value)
        return f"{self.value}({', '.join(repr(c) for c in self.children)})"

def tokenize(conjecture_str):
    if ':' in conjecture_str:
        conjecture_str = conjecture_str.split(':', 1)[1]
    return conjecture_str.strip().split()

def parse_tokens(tokens):
    if not tokens:
        return None, []
    
    token = tokens[0]
    remaining = tokens[1:]
    arity = OPERATORS.get(token, 0)
    
    if arity > 0:
        children = []
        for _ in range(arity):
            child_node, remaining = parse_tokens(remaining)
            if child_node is None:
                raise ValueError(f"Malformed prefix: operator '{token}' expected {arity} arguments.")
            children.append(child_node)
        return ASTNode(token, children), remaining
    else:
        return ASTNode(token), remaining

def to_infix(node):
    if not node.children:
        return MATH_MAP.get(node.value, node.value)
    
    if len(node.children) == 2:
        op = node.value
        left = to_infix(node.children[0])
        right = to_infix(node.children[1])
        if op == '<=': return f"{left} ≤ {right}"
        elif op in ['+', '-', '*', '/']: return f"({left} {op} {right})"
        elif op == '^': return f"{left}^{right}"
        elif op in ['max-v', 'max-v-u', 'max-v-w']: return f"max_v({left}, {right})"
        elif op in ['dist', 'weight']: return f"{op}({left}, {right})"
        
    if len(node.children) == 1:
        op_name = MATH_MAP.get(node.value, node.value)
        return f"{op_name}({to_infix(node.children[0])})"
    
    return f"{node.value}({', '.join(to_infix(c) for c in node.children)})"

def parse_line(line):
    tokens = tokenize(line)
    if not tokens:
        return None, None
    ast, remaining = parse_tokens(tokens)
    return ast, to_infix(ast)
