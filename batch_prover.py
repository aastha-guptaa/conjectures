import os
import sys
import time
import multiprocessing as mp


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from z3_prover import prove_conjecture

def evaluate_line(line):
    try:
        status, infix = prove_conjecture(line)
        return line, status, infix
    except Exception:
        return line, 'SURVIVED', None

def process_batch(chunk):
    return [evaluate_line(line) for line in chunk]

def main():
    input_file = '/home/aastha/Downloads/conjectures/open.txt'
    output_file = '/home/aastha/Downloads/conjectures/open_filtered.txt'
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
        
    print("Reading conjectures from open.txt...")
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
    
    proven_count = 0
    survived_count = 0
    
    with mp.Pool(processes=num_cores) as pool:
        results_iterator = pool.imap_unordered(process_batch, chunks)
        
        with open(output_file, 'w') as out_f:
            for idx, batch_result in enumerate(results_iterator):
                for raw_line, status, infix in batch_result:
                    if status == 'PROVEN':
                        proven_count += 1
                    else:
                        survived_count += 1
                        out_f.write(raw_line)
                
                processed = proven_count + survived_count
                percent = (processed / total_conjectures) * 100
                elapsed = time.time() - start_time
                speed = processed / elapsed if elapsed > 0 else 0
                eta = (total_conjectures - processed) / speed if speed > 0 else 0
                
                print(f"Progress: {processed:,}/{total_conjectures:,} ({percent:.2f}%) | "
                      f"Proven: {proven_count:,} | Kept: {survived_count:,} | "
                      f"Speed: {speed:.0f} lines/sec | ETA: {eta/60:.1f} min", end='\r')
                      
    print("\n\n--- Batch Processing Completed Successfully! ---")
    print(f"Total Conjectures Processed : {total_conjectures:,}")
    print(f"Trivially Proven & Removed  : {proven_count:,} ({proven_count/total_conjectures*100:.1f}%)")
    print(f"True Open Survivors Kept    : {survived_count:,} ({survived_count/total_conjectures*100:.1f}%)")
    print(f"Survivors saved to          : {output_file}")
    print(f"Total time elapsed          : {time.time() - start_time:.1f} seconds.")

if __name__ == '__main__':
    mp.freeze_support()
    main()
