import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import parse_line
from z3_prover import prove_conjecture
from batch_prover import main as run_batch_prover
from filter_by_graphs import main as run_graph_atlas_sieve
from batch_refuter_gnrpa import main as run_gnrpa_batch_sieve
from gnrpa import refute_conjecture

def print_header(title):
    print("\n" + "=" * 50)
    print(f" {title:^48}")
    print("=" * 50)

def show_statistics():
    print_header("PIPELINE STATISTICS & FILES")
    base_dir = '/home/aastha/Downloads/conjectures'
    
    files = {
        'open.txt': 'Surviving Open Conjectures (Target)',
        'max.txt': 'Conjectures with Max Observed Slack',
        'nan.txt': 'Ill-defined / NaN Conjectures',
        'part1.txt': 'Raw Generated Candidates (Batch 1)',
        'part2.txt': 'Raw Generated Candidates (Batch 2)',
        'open_filtered.txt': 'Phase 1 Sieve Survivors (Filtered Targets)',
        'open_filtered_step2.txt': 'Phase 2 Sieve Survivors (Atlas Filtered)',
        'refuted_by_atlas.txt': 'Atlas Refuted Conjectures Log',
        'open_filtered_step3.txt': 'Phase 3 Sieve Survivors (GNRPA Filtered)',
        'refuted_by_gnrpa.txt': 'GNRPA Refuted Conjectures Log'
    }
    
    for filename, desc in files.items():
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            line_count = 0
            with open(path, 'r') as f:
                for _ in f: line_count += 1
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f" {filename:<23} | {line_count:>9,} lines | {size_mb:>6.1f} MB | {desc}")
        else:
            print(f" {filename:<23} | Not generated yet                       | {desc}")

def run_single_interactive():
    print_header("SINGLE CONJECTURE VERIFIER")
    print("Paste a Polish notation conjecture below (e.g. from open.txt):")
    print("Example: <= rank Adj - + rank Adj rank laplac Adj 1\n")
    
    try:
        line = input("Conjecture: ").strip()
        if not line:
            return
            
        print("\n1. Parsing and translating...")
        ast, infix = parse_line(line)
        print(f"  AST   : {ast}")
        print(f"  Infix : {infix}")
        
        print("\n2. Invoking Z3 SMT Solver under spectral graph axioms...")
        status, _ = prove_conjecture(line)
        
        if status == 'PROVEN':
            print("   SMT RESULT: PROVEN (Algebraically true for all connected graphs n>=2)")
        elif status == 'POSSIBLE_FAIL':
            print("   SMT RESULT: POSSIBLE_FAIL (SMT solver found numeric violations under bounds)")
        else:
            print("   SMT RESULT: UNKNOWN / Non-linear limits")
            
        print("\n3. Do you want to run Progressive GNRPA search to find a counterexample graph? (y/n)")
        run_mc = input("Choice: ").strip().lower()
        if run_mc == 'y':
            n_start = int(input("Start graph size (e.g., 4): ").strip() or "4")
            n_max = int(input("Max graph size (e.g., 10): ").strip() or "10")
            level = int(input("GNRPA search level (1 or 2): ").strip() or "2")
            iterations = int(input("Playout iterations per step (e.g., 10): ").strip() or "10")
            
            print("\nRunning Progressive GNRPA Search...")
            success, G, msg = refute_conjecture(line, n_start=n_start, n_max=n_max, level=level, iterations=iterations)
            if success:
                print(f"\n   REFUTED! Counterexample found at size n={G.number_of_nodes()}")
                print(f"  Edges: {list(G.edges())}")
            else:
                print(f"\n   SURVIVED! {msg}")
            
    except Exception as e:
        print(f"Error: {e}")

def run_parser_preview():
    print_header("PARSER & PREVIEW (FIRST 10 OPEN CONJECTURES)")
    input_file = '/home/aastha/Downloads/conjectures/open.txt'
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
        
    with open(input_file, 'r') as f:
        for idx, line in enumerate(f):
            if idx >= 10:
                break
            try:
                _, infix = parse_line(line)
                print(f"[{idx+1:02d}] {infix}")
            except Exception as e:
                print(f"[{idx+1:02d}] Error parsing line: {line.strip()} ({e})")

def run_gnrpa_interactive():
    print_header("RUN PROGRESSIVE GNRPA SEARCH")
    line = input("Paste Polish notation conjecture: ").strip()
    if not line:
        return
    try:
        success, G, msg = refute_conjecture(line, n_start=4, n_max=10, level=2, iterations=15)
        if success:
            print(f"\n   REFUTED! Counterexample found at size n={G.number_of_nodes()}")
            print(f"  Edges: {list(G.edges())}")
        else:
            print(f"\n   SURVIVED! {msg}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        print_header("SPECTRAL GRAPH CONJECTURE PROVER PIPELINE")
        print("1. Show Workspace Files & Statistics")
        print("2. Parse & Preview first 10 Open Conjectures")
        print("3. Verify a Single Conjecture (Interactive - SMT + Monte Carlo)")
        print("4. Phase 1: Run Parallel Batch ATP Sieve (SMT Prove: open.txt -> open_filtered.txt)")
        print("5. Phase 2: Run Parallel Batch Atlas Sieve (Atlas Refute: open_filtered.txt -> open_filtered_step2.txt)")
        print("6. Phase 3: Run Parallel Batch GNRPA Sieve (GNRPA Refute: open_filtered_step2.txt -> open_filtered_step3.txt)")
        print("7. Run Progressive GNRPA Search on a Single Conjecture")
        print("8. Exit")
        
        try:
            choice = input("\nSelect an option (1-8): ").strip()
            if choice == '1':
                show_statistics()
            elif choice == '2':
                run_parser_preview()
            elif choice == '3':
                run_single_interactive()
            elif choice == '4':
                print_header("RUNNING PARALLEL BATCH ATP Sieve (Phase 1)")
                print("Warning: This will process all 305k conjectures in open.txt using Z3 boundary logic.")
                confirm = input("Do you want to proceed? (y/n): ").strip().lower()
                if confirm == 'y':
                    run_batch_prover()
            elif choice == '5':
                print_header("RUNNING PARALLEL BATCH ATLAS SIEVE (Phase 2)")
                print("Warning: This will evaluate all survivors against the 995 non-isomorphic connected atlas graphs (sizes 2-7).")
                confirm = input("Do you want to proceed? (y/n): ").strip().lower()
                if confirm == 'y':
                    run_graph_atlas_sieve()
            elif choice == '6':
                print_header("RUNNING PARALLEL BATCH GNRPA Monte Carlo Sieve (Phase 3)")
                print("Warning: This will run level 1 GNRPA on all survivors for graph sizes 8, 9, 10.")
                confirm = input("Do you want to proceed? (y/n): ").strip().lower()
                if confirm == 'y':
                    run_gnrpa_batch_sieve()
            elif choice == '7':
                run_gnrpa_interactive()
            elif choice == '8':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please enter 1-8.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        
        input("\nPress Enter to return to menu...")

if __name__ == '__main__':
    main()
