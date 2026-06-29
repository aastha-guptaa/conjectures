import math
import numpy as np
import networkx as nx

def get_matrix(obj, matrix_type='adjacency'):
    """Converts a networkx Graph or numpy array to the desired numpy matrix."""
    if isinstance(obj, nx.Graph):
        if matrix_type == 'adjacency':
            return nx.adjacency_matrix(obj).toarray().astype(float)
        elif matrix_type == 'laplacian':
            return nx.laplacian_matrix(obj).toarray().astype(float)
    return obj

# 1. Standard Evaluator (For dynamically constructed graphs / GNRPA)

def evaluate_ast(node, G, context=None):
    """
    Recursively evaluates an ASTNode on a networkx Graph G.
    context: dict mapping variable names (like 'v', 'u') to vertex IDs.
    """
    if context is None:
        context = {}

    if not node.children:
        val = node.value
        if val in context:
            return context[val]
        try:
            return float(val)
        except ValueError:
            pass
        if val == 'Adj':
            return G
        return val

    op = node.value

  
    if op == 'max-v':
        vals = []
        for node_id in G.nodes():
            new_context = context.copy()
            new_context['v'] = node_id
            try:
                val = evaluate_ast(node.children[1], G, new_context)
                if not math.isnan(val):
                    vals.append(val)
            except Exception:
                pass
        return max(vals) if vals else float('nan')

    elif op == 'max-v-u':
        vals = []
        for u_id, v_id in G.edges():
            new_context = context.copy()
            new_context['u'] = u_id
            new_context['v'] = v_id
            try:
                val = evaluate_ast(node.children[1], G, new_context)
                if not math.isnan(val):
                    vals.append(val)
            except Exception:
                pass
        return max(vals) if vals else float('nan')

    elif op == 'max-v-w':
        vals = []
        nodes = list(G.nodes())
        for i in range(len(nodes)):
            for j in range(i, len(nodes)):
                new_context = context.copy()
                new_context['u'] = nodes[i]
                new_context['v'] = nodes[j]
                try:
                    val = evaluate_ast(node.children[1], G, new_context)
                    if not math.isnan(val):
                        vals.append(val)
                except Exception:
                    pass
        return max(vals) if vals else float('nan')

    eval_children = []
    for child in node.children:
        val = evaluate_ast(child, G, context)
        eval_children.append(val)

    
    if len(eval_children) == 1:
        child_val = eval_children[0]
        if op == 'rank':
            matrix = get_matrix(child_val, 'adjacency')
            return float(np.linalg.matrix_rank(matrix))
        elif op == 'laplac':
            return get_matrix(child_val, 'laplacian')
        elif op == 'degree':
            return float(G.degree(child_val))
        elif op == 'temp':
            deg = G.degree(child_val)
            n = G.number_of_nodes()
            return float(deg) / (n - deg) if n - deg != 0 else float('inf')
        elif op == 'IndRand':
            total = 0.0
            for u_id, v_id in G.edges():
                deg_u = G.degree(u_id)
                deg_v = G.degree(v_id)
                if deg_u * deg_v > 0:
                    total += 1.0 / math.sqrt(deg_u * deg_v)
            return total
        elif op == 'rad':
            return float(nx.radius(G))
        elif op == 'dia':
            return float(nx.diameter(G))
        elif op == 'eigen':
            matrix = get_matrix(child_val, 'adjacency')
            eigs = np.linalg.eigvalsh(matrix)
            return sorted(list(eigs), reverse=True)
        elif op == 'large':
            if isinstance(child_val, list) and len(child_val) > 0:
                return child_val[0]
            return float('nan')
        elif op == 'large-2':
            if isinstance(child_val, list) and len(child_val) > 1:
                return child_val[1]
            return float('nan')
        elif op == 'sum':
            if isinstance(child_val, list):
                return float(sum(child_val))
            return float(child_val)
        elif op == 'sqrt':
            return math.sqrt(child_val) if child_val >= 0 else float('nan')
        elif op == 'log':
            return math.log(child_val) if child_val > 0 else float('nan')

   
    elif len(eval_children) == 2:
        left, right = eval_children
        if op == '<=':
            return left <= right
        elif op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right if right != 0 else float('nan')
        elif op == '^':
            try:
                return float(left ** right)
            except Exception:
                return float('nan')
        elif op == 'dist':
            return float(nx.shortest_path_length(G, source=left, target=right))
        elif op == 'weight':
            deg_u = G.degree(left)
            deg_v = G.degree(right)
            return 1.0 / math.sqrt(deg_u * deg_v) if deg_u * deg_v > 0 else float('nan')

    raise ValueError(f"Unknown operator/arity: {op} with {len(eval_children)} arguments")


# 2. Optimized Precomputed Evaluator (For batch testing on static atlas)

class PrecomputedLaplacian:
    def __init__(self, pg):
        self.pg = pg

class PrecomputedGraph:
    def __init__(self, G):
        self.n = G.number_of_nodes()
        self.nodes = list(G.nodes())
        self.edges = list(G.edges())
        
        
        self.degrees = {u: float(G.degree(u)) for u in G.nodes()}
        
        
        self.temp = {}
        for u in G.nodes():
            deg = self.degrees[u]
            self.temp[u] = deg / (self.n - deg) if self.n - deg != 0 else float('inf')
            
        adj_matrix = nx.adjacency_matrix(G).toarray().astype(float)
        lap_matrix = nx.laplacian_matrix(G).toarray().astype(float)
        
        self.rank_A = float(np.linalg.matrix_rank(adj_matrix))
        self.rank_L = float(np.linalg.matrix_rank(lap_matrix))
        
        self.eigen_A = sorted([float(x) for x in np.linalg.eigvalsh(adj_matrix)], reverse=True)
        self.eigen_L = sorted([float(x) for x in np.linalg.eigvalsh(lap_matrix)], reverse=True)
        self.sum_eigen_L = float(sum(self.eigen_L))
        
        self.rad = float(nx.radius(G))
        self.dia = float(nx.diameter(G))
        
        self.dist = dict(nx.all_pairs_shortest_path_length(G))
        
        self.edge_weights = {}
        self.randic = 0.0
        for u, v in G.edges():
            deg_u = self.degrees[u]
            deg_v = self.degrees[v]
            w = 1.0 / math.sqrt(deg_u * deg_v) if deg_u * deg_v > 0 else 0.0
            self.edge_weights[(u, v)] = w
            self.edge_weights[(v, u)] = w
            self.randic += w

def evaluate_ast_precomputed(node, pg, context=None):
    """
    Recursively evaluates an ASTNode on a PrecomputedGraph pg.
    Uses algebraic lookups to run in nanoseconds.
    """
    if context is None:
        context = {}

    if not node.children:
        val = node.value
        if val in context:
            return context[val]
        try:
            return float(val)
        except ValueError:
            pass
        if val == 'Adj':
            return pg
        return val

    op = node.value

    if op == 'max-v':
        vals = []
        for node_id in pg.nodes:
            new_context = context.copy()
            new_context['v'] = node_id
            try:
                val = evaluate_ast_precomputed(node.children[1], pg, new_context)
                if not math.isnan(val):
                    vals.append(val)
            except Exception:
                pass
        return max(vals) if vals else float('nan')

    elif op == 'max-v-u':
        vals = []
        for u_id, v_id in pg.edges:
            new_context = context.copy()
            new_context['u'] = u_id
            new_context['v'] = v_id
            try:
                val = evaluate_ast_precomputed(node.children[1], pg, new_context)
                if not math.isnan(val):
                    vals.append(val)
            except Exception:
                pass
        return max(vals) if vals else float('nan')

    elif op == 'max-v-w':
        vals = []
        for i in range(len(pg.nodes)):
            for j in range(i, len(pg.nodes)):
                new_context = context.copy()
                new_context['u'] = pg.nodes[i]
                new_context['v'] = pg.nodes[j]
                try:
                    val = evaluate_ast_precomputed(node.children[1], pg, new_context)
                    if not math.isnan(val):
                        vals.append(val)
                except Exception:
                    pass
        return max(vals) if vals else float('nan')

    eval_children = []
    for child in node.children:
        val = evaluate_ast_precomputed(child, pg, context)
        eval_children.append(val)

    if len(eval_children) == 1:
        child_val = eval_children[0]
        
        if op == 'rank':
            if child_val is pg:
                return pg.rank_A
            elif isinstance(child_val, PrecomputedLaplacian):
                return pg.rank_L
            return float('nan')
            
        elif op == 'laplac':
            if child_val is pg:
                return PrecomputedLaplacian(pg)
            return float('nan')
            
        elif op == 'degree':
            return pg.degrees[child_val]
            
        elif op == 'temp':
            return pg.temp[child_val]
            
        elif op == 'IndRand':
            return pg.randic
            
        elif op == 'rad':
            return pg.rad
            
        elif op == 'dia':
            return pg.dia
            
        elif op == 'eigen':
            if child_val is pg:
                return pg.eigen_A
            elif isinstance(child_val, PrecomputedLaplacian):
                return pg.eigen_L
            return float('nan')
            
        elif op == 'large':
            if isinstance(child_val, list) and len(child_val) > 0:
                return child_val[0]
            return float('nan')
            
        elif op == 'large-2':
            if isinstance(child_val, list) and len(child_val) > 1:
                return child_val[1]
            return float('nan')
            
        elif op == 'sum':
            if isinstance(child_val, list):
                return float(sum(child_val))
            return float(child_val)
            
        elif op == 'sqrt':
            return math.sqrt(child_val) if child_val >= 0 else float('nan')
            
        elif op == 'log':
            return math.log(child_val) if child_val > 0 else float('nan')

    elif len(eval_children) == 2:
        left, right = eval_children
        if op == '<=':
            return left <= right
        elif op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right if right != 0 else float('nan')
        elif op == '^':
            try:
                # avoid float overflow or complex values
                res = left ** right
                if isinstance(res, complex):
                    return float('nan')
                return float(res)
            except Exception:
                return float('nan')
        elif op == 'dist':
            return float(pg.dist[left][right])
        elif op == 'weight':
            return pg.edge_weights.get((left, right), float('nan'))

    raise ValueError(f"Unknown operator/arity: {op} with {len(eval_children)} arguments")
