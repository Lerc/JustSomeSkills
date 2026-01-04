#!/usr/bin/env python3
"""
Display basic device information from an SVD file.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def main():
    if len(sys.argv) < 2:
        print("Usage: device_info.py <svd_file> [--json]")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    output_json = '--json' in sys.argv
    
    try:
        parser = SVDParser(svd_file)
        info = parser.get_device_info()
        
        if output_json:
            print(json.dumps(info, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Device Information")
            print(f"{'='*80}")
            print(f"Name:              {info['name']}")
            print(f"Vendor:            {info['vendor']}")
            print(f"Version:           {info['version']}")
            print(f"Description:       {info['description']}")
            print(f"Address Unit Bits: {info['address_unit_bits']}")
            print(f"Default Width:     {info['width']} bits")
            
            if info['cpu']:
                print(f"\nCPU:")
                print(f"{'-'*80}")
                for key, value in info['cpu'].items():
                    if value:
                        key_formatted = key.replace('_', ' ').title()
                        print(f"  {key_formatted.ljust(20)}: {value}")
            
            print()
    
    except FileNotFoundError:
        print(f"Error: SVD file not found: {svd_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing SVD file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
