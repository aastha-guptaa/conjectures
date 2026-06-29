import networkx as nx
from parser import parse_line
from evaluator import evaluate_ast

def test():
    G = nx.path_graph(4)
    
    conjectures = [
        "<= rank Adj ^ max-v Adj + 2 degree v 2",
        "<= rank Adj - + rank Adj rank laplac Adj 1",
        "<= rank Adj - + rank Adj sqrt IndRand Adj 1",
        "<= rank Adj sqrt + 1 ^ 2 rank laplac Adj"
    ]
    
    print("Graph: Path Graph on 4 vertices (P_4)")
    print(f"Nodes: {list(G.nodes())}")
    print(f"Edges: {list(G.edges())}")
    print(f"Degrees: {[G.degree(i) for i in G.nodes()]}")
    print()

    for conj in conjectures:
        ast, infix = parse_line(conj)
        # Evaluate LHS and RHS separately
        lhs_node = ast.children[0]
        rhs_node = ast.children[1]
        
        lhs_val = evaluate_ast(lhs_node, G)
        rhs_val = evaluate_ast(rhs_node, G)
        is_true = evaluate_ast(ast, G)
        
        print(f"Conjecture: {infix}")
        print(f"  LHS value: {lhs_val}")
        print(f"  RHS value: {rhs_val}")
        print(f"  LHS <= RHS? {is_true}")
        print()

if __name__ == '__main__':
    test()
