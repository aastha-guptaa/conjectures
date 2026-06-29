import random
import math
import numpy as np
import networkx as nx
from parser import parse_line
from evaluator import evaluate_ast

def get_possible_edges(n):
    """Returns a list of all possible undirected edges for n vertices."""
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            edges.append((u, v))
    return edges

def get_edge_idx(u, v, n):
    """Maps an edge (u, v) to its index in the possible edges list."""
    if u > v:
        u, v = v, u
    return u * n - u * (u + 1) // 2 + v - u - 1

def playout(policy, ast, n):
    """
    Performs a single playout.
    Starts with a random spanning tree, then decides whether to add remaining edges.
    Returns: (score, G, chosen_decisions)
    """
    G = nx.random_labeled_tree(n)
    
    possible = get_possible_edges(n)
    tree_edges = set(G.edges())
    
    chosen_decisions = {} 
    
    for u, v in possible:
        if (u, v) in tree_edges or (v, u) in tree_edges:
            continue
            
        idx = get_edge_idx(u, v, n)
        w = policy[idx]
        if w > 50:
            p_add = 1.0
        elif w < -50:
            p_add = 0.0
        else:
            p_add = math.exp(w) / (math.exp(w) + 1.0)
            
        added = random.random() < p_add
        chosen_decisions[idx] = (added, p_add)
        
        if added:
            G.add_edge(u, v)
            
    lhs_node = ast.children[0]
    rhs_node = ast.children[1]
    
    try:
        lhs_val = evaluate_ast(lhs_node, G)
        rhs_val = evaluate_ast(rhs_node, G)
        if math.isnan(lhs_val) or math.isnan(rhs_val):
            score = float('-inf')
        else:
            score = lhs_val - rhs_val
    except Exception:
        score = float('-inf')
        
    return score, G, chosen_decisions

def adapt(policy, chosen_decisions, alpha):
    """Updates the policy weights based on the best playout decisions."""
    for idx, (added, p_add) in chosen_decisions.items():
        if added:
            policy[idx] += alpha * (1.0 - p_add)
        else:
            policy[idx] -= alpha * p_add

def gnrpa(level, policy, ast, n, iterations=10, alpha=0.1):
    """
    Recursive GNRPA Search.
    Returns: (best_score, best_graph, best_decisions)
    """
    if level == 0:
        return playout(policy, ast, n)
        
    best_score = float('-inf')
    best_graph = None
    best_decisions = None
    
    for i in range(iterations):
        score, G, decisions = gnrpa(level - 1, policy, ast, n, iterations, alpha)
        
        if score > 0.001:
            return score, G, decisions
            
        if score > best_score:
            best_score = score
            best_graph = G
            best_decisions = decisions
            
        if best_decisions:
            adapt(policy, best_decisions, alpha)
            
    return best_score, best_graph, best_decisions

def refute_conjecture(conjecture_str, n_start=5, n_max=12, level=2, iterations=10):
    """
    Runs Progressive GNRPA to refute a conjecture.
    Increases the graph size n gradually.
    """
    ast, infix = parse_line(conjecture_str)
    if not ast or ast.value != '<=' or len(ast.children) != 2:
        return False, None, "Invalid conjecture format: Must be an inequality starting with '<='"
        
    print(f"Refuting: {infix}")
    
    for n in range(n_start, n_max + 1):
        num_possible = n * (n - 1) // 2
        policy = [0.0] * num_possible
        
        print(f"  Testing GNRPA level {level} on graphs of size n={n}...")
        
        score, G, decisions = gnrpa(level, policy, ast, n, iterations=iterations)
        
        if score > 0.001:
            print(f"  SUCCESS! Refuted at n={n} with score={score:.4f}")
            print(f"  Counterexample Edges: {list(G.edges())}")
            return True, G, f"Refuted at n={n}"
            
    return False, None, "Could not find a counterexample within limits"
