#!/usr/bin/env python3
"""
List all peripherals in an SVD file with their base addresses.
"""

import sys
import json
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def main():
    if len(sys.argv) < 2:
        print("Usage: list_peripherals.py <svd_file> [--json]")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    output_json = '--json' in sys.argv
    
    try:
        parser = SVDParser(svd_file)
        peripherals = parser.list_peripherals()
        
        if output_json:
            print(json.dumps(peripherals, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Device: {parser.device_name}")
            print(f"Peripherals: {len(peripherals)}")
            print(f"{'='*80}\n")
            
            # Group by group_name if available
            grouped = {}
            for p in peripherals:
                group = p.get('group_name', 'Other')
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(p)
            
            for group in sorted(grouped.keys()):
                if group != 'Other':
                    print(f"\n{group}:")
                    print("-" * 80)
                
                for p in grouped[group]:
                    name = p['name'].ljust(20)
                    addr = p['base_address'].ljust(12)
                    desc = p['description'][:45] + '...' if len(p['description']) > 45 else p['description']
                    print(f"  {name} {addr} {desc}")
            
            print()
    
    except FileNotFoundError:
        print(f"Error: SVD file not found: {svd_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing SVD file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
