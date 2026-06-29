from gnrpa import refute_conjecture

def run_test():
    # This conjecture was in open.txt but is actually false!
    # rank(A) <= sqrt(1 + 2^rank(Laplacian(A)))
    conjecture = "49167 : <= rank Adj sqrt + 1 ^ 2 rank laplac Adj"
    
    # Run the GNRPA refuter starting at size n=4
    success, G, message = refute_conjecture(conjecture, n_start=4, n_max=6, level=1, iterations=15)
    
    print("\n--- Test GNRPA Result ---")
    print(f"Success: {success}")
    print(f"Message: {message}")
    if success and G:
        print(f"Nodes: {list(G.nodes())}")
        print(f"Edges: {list(G.edges())}")

if __name__ == '__main__':
    run_test()
