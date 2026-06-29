import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(nodes, edges, filename, title):
    G = nx.Graph()
    G.add_nodes_from(range(nodes))
    G.add_edges_from(edges)
    
    plt.figure(figsize=(4, 4), dpi=300)
    pos = nx.circular_layout(G)
    
    nx.draw_networkx_edges(G, pos, edge_color='#cbd5e1', width=1.2)
    
    nx.draw_networkx_nodes(G, pos, node_color='#4f46e5', node_size=350, edgecolors='#312e81', linewidths=1.0)
    
    nx.draw_networkx_labels(G, pos, font_color='white', font_size=8, font_family='sans-serif', font_weight='bold')
    
    plt.title(title, fontsize=10, fontweight='bold', pad=10)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', transparent=True)
    plt.close()

if __name__ == '__main__':
    # Graph 1 (Conjecture 767491)
    edges1 = [(0, 6), (0, 3), (0, 1), (0, 2), (0, 8), (1, 2), (1, 9), (1, 4), (1, 8), (2, 5), (2, 4), (2, 3), (2, 7), (3, 4), (3, 8), (4, 9), (5, 6), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9), (7, 9)]
    draw_graph(10, edges1, 'counterexample1.png', 'Counterexample for Conj 767491')
    
    # Graph 2 (Conjecture 804453)
    edges2 = [(0, 6), (0, 5), (0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (0, 9), (1, 8), (1, 2), (1, 3), (1, 4), (1, 7), (1, 9), (2, 4), (2, 5), (2, 8), (2, 9), (2, 3), (2, 7), (3, 8), (3, 4), (3, 5), (4, 7), (4, 9), (5, 8), (6, 8), (6, 9), (7, 8), (8, 9)]
    draw_graph(10, edges2, 'counterexample2.png', 'Counterexample for Conj 804453')
    
    # Graph 3 (Conjecture 812918)
    edges3 = [(0, 6), (0, 5), (0, 9), (0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (1, 2), (1, 4), (1, 5), (1, 6), (1, 8), (2, 7), (2, 3), (2, 4), (2, 5), (2, 6), (2, 8), (2, 9), (3, 5), (3, 6), (3, 7), (4, 9), (4, 5), (4, 8), (5, 7), (5, 8), (6, 8), (6, 9), (7, 8), (7, 9), (8, 9)]
    draw_graph(10, edges3, 'counterexample3.png', 'Counterexample for Conj 812918')
    
