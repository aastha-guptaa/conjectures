import os
import sys
import time
import math
import multiprocessing as mp
import networkx as nx
from parser import parse_line
from evaluator import PrecomputedGraph, evaluate_ast_precomputed

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_test_graphs():
    
    atlas = nx.graph_atlas_g()
    connected_graphs = []
    for g in atlas:
        n = g.number_of_nodes()
        if 2 <= n <= 7 and nx.is_connected(g):
            connected_graphs.append(g)
            
    connected_graphs.sort(key=lambda g: g.number_of_nodes())
    
    print(f"Precomputing invariants for {len(connected_graphs)} graphs...")
    t0 = time.time()
    precomputed = [PrecomputedGraph(g) for g in connected_graphs]
    print(f"Precomputation finished in {time.time() - t0:.2f} seconds!")
    return precomputed

TEST_SUITE = load_test_graphs()

def evaluate_conjecture_on_suite(line):
    """
    Tests a single conjecture on the precomputed test suite of graphs.
    Returns: (line, status, counterexample_info)
    Where status is: 'REFUTED' or 'SURVIVED'
    """
    try:
        ast, infix = parse_line(line)
        if not ast:
            return line, 'SURVIVED', None
            
        lhs_node = ast.children[0]
        rhs_node = ast.children[1]
        
        for G in TEST_SUITE:
            try:
                lhs_val = evaluate_ast_precomputed(lhs_node, G)
                rhs_val = evaluate_ast_precomputed(rhs_node, G)
                
                if math.isnan(lhs_val) or math.isnan(rhs_val):
                    continue
                    
                score = lhs_val - rhs_val
                if score > 0.001:
                    counterexample = {
                        'nodes': G.n,
                        'edges': G.edges,
                        'score': score,
                        'infix': infix
                    }
                    return line, 'REFUTED', counterexample
            except Exception:
                continue
                
        return line, 'SURVIVED', None
    except Exception:
        return line, 'SURVIVED', None

def process_chunk(chunk):
    return [evaluate_conjecture_on_suite(line) for line in chunk]

def main():
    input_file = '/home/aastha/Downloads/conjectures/open_filtered.txt'
    output_filtered = '/home/aastha/Downloads/conjectures/open_filtered_step2.txt'
    output_refuted = '/home/aastha/Downloads/conjectures/refuted_by_atlas.txt'
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
        
    print(f"Reading conjectures from {input_file}...")
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    total_conjectures = len(lines)
    print(f"Loaded {total_conjectures:,} conjectures.")
    
    num_cores = mp.cpu_count()
    print(f"Using {num_cores} parallel CPU cores...")
    
    chunk_size = max(1, total_conjectures // (num_cores * 4))
    chunks = [lines[i:i + chunk_size] for i in range(0, total_conjectures, chunk_size)]
    
    print(f"Split dataset into {len(chunks)} chunks.")
    start_time = time.time()
    
    refuted_count = 0
    survived_count = 0
    
    with mp.Pool(processes=num_cores) as pool:
        results_iterator = pool.imap_unordered(process_chunk, chunks)
        
        with open(output_filtered, 'w') as out_f, open(output_refuted, 'w') as refuted_f:
            for idx, batch_result in enumerate(results_iterator):
                for raw_line, status, ce_info in batch_result:
                    if status == 'REFUTED':
                        refuted_count += 1
                        refuted_f.write(f"{raw_line.strip()} | Counterexample: nodes={ce_info['nodes']}, edges={ce_info['edges']}, score={ce_info['score']:.4f} | Infix: {ce_info['infix']}\n")
                    else:
                        survived_count += 1
                        out_f.write(raw_line)
                
                processed = refuted_count + survived_count
                percent = (processed / total_conjectures) * 100
                elapsed = time.time() - start_time
                speed = processed / elapsed if elapsed > 0 else 0
                eta = (total_conjectures - processed) / speed if speed > 0 else 0
                
                print(f"Progress: {processed:,}/{total_conjectures:,} ({percent:.2f}%) | "
                      f"Refuted: {refuted_count:,} | Kept: {survived_count:,} | "
                      f"Speed: {speed:.0f} lines/sec | ETA: {eta/60:.1f} min", end='\r')
                      
    print("\n\n--- Graph Atlas Filtering Completed Successfully! ---")
    print(f"Total Conjectures Processed : {total_conjectures:,}")
    print(f"Refuted & Removed by Atlas  : {refuted_count:,} ({refuted_count/total_conjectures*100:.1f}%)")
    print(f"True Open Survivors Kept    : {survived_count:,} ({survived_count/total_conjectures*100:.1f}%)")
    print(f"Survivors saved to          : {output_filtered}")
    print(f"Refuted list saved to       : {output_refuted}")
    print(f"Total time elapsed          : {time.time() - start_time:.1f} seconds.")

if __name__ == '__main__':
    mp.freeze_support()
    main()
