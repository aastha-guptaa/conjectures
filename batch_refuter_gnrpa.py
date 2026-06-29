import os
import sys
import time
import multiprocessing as mp
from parser import parse_line
from gnrpa import gnrpa


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def evaluate_conjecture_gnrpa(line):
    """
    Quietly refutes a conjecture using Progressive GNRPA on sizes n = 8 to 10.
    Returns: (line, status, counterexample_info)
    """
    try:
        ast, infix = parse_line(line)
        if not ast or ast.value != '<=' or len(ast.children) != 2:
            return line, 'INVALID', None
            
        # Run GNRPA at level 1 (fast batch settings)
        for n in [8, 9, 10]:
            num_possible = n * (n - 1) // 2
            policy = [0.0] * num_possible
            
            # 10 iterations per size
            score, G, decisions = gnrpa(level=1, policy=policy, ast=ast, n=n, iterations=10)
            
            if score > 0.001:
                counterexample = {
                    'nodes': n,
                    'edges': list(G.edges()),
                    'score': score,
                    'infix': infix
                }
                return line, 'REFUTED', counterexample
                
        return line, 'SURVIVED', None
    except Exception:
        return line, 'SURVIVED', None

def process_chunk(chunk):
    return [evaluate_conjecture_gnrpa(line) for line in chunk]

def main():
    input_file = '/home/aastha/Downloads/conjectures/open_filtered_step2.txt'
    output_filtered = '/home/aastha/Downloads/conjectures/open_filtered_step3.txt'
    output_refuted = '/home/aastha/Downloads/conjectures/refuted_by_gnrpa.txt'
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found. Run Phase 2 first.")
        sys.exit(1)
        
    print(f"Reading conjectures from {input_file}...")
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    total_conjectures = len(lines)
    print(f"Loaded {total_conjectures:,} conjectures.")
    
    num_cores = mp.cpu_count()
    print(f"Using {num_cores} parallel CPU cores...")
    
    # Split into chunks
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
                    elif status == 'SURVIVED':
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
                      
    print("\n\n--- GNRPA Monte Carlo Filtering Completed Successfully! ---")
    print(f"Total Conjectures Processed : {total_conjectures:,}")
    print(f"Refuted & Removed by GNRPA  : {refuted_count:,} ({refuted_count/total_conjectures*100:.1f}%)")
    print(f"True Open Survivors Kept    : {survived_count:,} ({survived_count/total_conjectures*100:.1f}%)")
    print(f"Survivors saved to          : {output_filtered}")
    print(f"Refuted list saved to       : {output_refuted}")
    print(f"Total time elapsed          : {time.time() - start_time:.1f} seconds.")

if __name__ == '__main__':
    mp.freeze_support()
    main()
