import os
import sys
from z3 import *


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parser import parse_line

def setup_solver():
    n = Real('n')
    rank_A = Real('rank_A')
    rank_L = Real('rank_L')
    randic = Real('randic')
    lambda_max = Real('lambda_max')
    lambda_2 = Real('lambda_2')
    max_degree = Real('max_degree')
    rad = Real('rad')
    dia = Real('dia')
    sum_eigen_L = Real('sum_eigen_L')
    v = Real('v')
    u = Real('u')
    degree_v = Real('degree_v')
    temp_v = Real('temp_v')
    
    s = Solver()
    
    # Axioms
    s.add(n >= 2)
    s.add(rank_A >= 0, rank_A <= n)
    s.add(rank_L >= 1, rank_L <= n - 1)
    s.add(rank_A <= rank_L)
    s.add(randic >= 0)
    s.add(max_degree >= 1, max_degree <= n - 1)
    s.add(degree_v >= 1, degree_v <= max_degree)
    s.add(lambda_max >= 0)
    s.add(lambda_2 <= lambda_max)
    s.add(sum_eigen_L >= rank_L)
    
    var_map = {
        'n': n, 'rank_A': rank_A, 'rank_L': rank_L, 'randic': randic,
        'lambda_max': lambda_max, 'lambda_2': lambda_2, 'max_degree': max_degree,
        'rad': rad, 'dia': dia, 'sum_eigen_L': sum_eigen_L,
        'v': v, 'u': u, 'degree_v': degree_v, 'temp_v': temp_v
    }
    return s, var_map

def node_to_z3(node, var_map):
    if not node.children:
        val = node.value
        try: return RealVal(float(val))
        except ValueError: pass
        if val == 'Adj': return var_map['rank_A']
        if val == 'v': return var_map['v']
        if val == 'u': return var_map['u']
        return Real(val)
        
    if len(node.children) == 2:
        op = node.value
        left = node_to_z3(node.children[0], var_map)
        right = node_to_z3(node.children[1], var_map)
        if op == '+': return left + right
        elif op == '-': return left - right
        elif op == '*': return left * right
        elif op == '/': return left / right
        elif op == '^': return left ** right
        elif op in ['max-v', 'max-v-u', 'max-v-w']:
            formula_str = str(node.children[1])
            if 'degree' in formula_str:
                return 2 + var_map['max_degree'] if '+' in formula_str else var_map['max_degree']
            return Real(f"max_v_{node.children[1].value}")
            
    if len(node.children) == 1:
        op = node.value
        child = node.children[0]
        if op == 'rank':
            if child.value == 'Adj': return var_map['rank_A']
            if child.value == 'laplac': return var_map['rank_L']
        elif op == 'IndRand': return var_map['randic']
        elif op == 'large': return var_map['lambda_max']
        elif op == 'large-2': return var_map['lambda_2']
        elif op == 'degree' and child.value == 'v': return var_map['degree_v']
        elif op == 'temp' and child.value == 'v': return var_map['temp_v']
        elif op == 'sum' and child.value == 'eigen': return var_map['sum_eigen_L']
        elif op == 'sqrt': return node_to_z3(child, var_map) ** 0.5
        elif op == 'log': return Real(f"log_{child.value if not child.children else 'expr'}")
        
    return Real(node.value)

def prove_conjecture(line):
    ast, infix = parse_line(line)
    if not ast or ast.value != '<=' or len(ast.children) != 2:
        return "INVALID", None
    lhs_node = ast.children[0]
    rhs_node = ast.children[1]
    
    # Quick identity check
    if str(lhs_node) == str(rhs_node):
        return "PROVEN", infix
        
    s, var_map = setup_solver()
    z3_lhs = node_to_z3(lhs_node, var_map)
    z3_rhs = node_to_z3(rhs_node, var_map)
    
    s.add(z3_lhs > z3_rhs)
    result = s.check()
    
    if result == unsat:
        return "PROVEN", infix
    elif result == sat:
        return "POSSIBLE_FAIL", infix
    return "UNKNOWN", infix
