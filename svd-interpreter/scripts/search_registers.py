#!/usr/bin/env python3
"""
Search for registers matching a pattern across all peripherals.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def main():
    if len(sys.argv) < 3:
        print("Usage: search_registers.py <svd_file> <pattern> [--json]")
        print("\nExample: search_registers.py device.svd ctrl")
        print("         Searches for all registers containing 'ctrl' (case-insensitive)")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    pattern = sys.argv[2]
    output_json = '--json' in sys.argv
    
    try:
        parser = SVDParser(svd_file)
        results = parser.search_registers(pattern)
        
        if not results:
            print(f"No registers found matching pattern: {pattern}")
            sys.exit(0)
        
        if output_json:
            output = [
                {'peripheral': periph, 'register': reg}
                for periph, reg in results
            ]
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Found {len(results)} register(s) matching '{pattern}'")
            print(f"{'='*80}\n")
            
            for peripheral, register in results:
                print(f"  {peripheral}.{register}")
            
            print()
    
    except FileNotFoundError:
        print(f"Error: SVD file not found: {svd_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
