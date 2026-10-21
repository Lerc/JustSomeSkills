#!/usr/bin/env python3
"""
Find all registers within a specified address range.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def main():
    if len(sys.argv) < 4:
        print("Usage: find_in_range.py <svd_file> <start_address> <end_address> [--json]")
        print("\nExamples:")
        print("  find_in_range.py device.svd 0x40000000 0x40000100")
        print("  find_in_range.py device.svd 0x40000000 0x40000100 --json")
        print("\nAddresses can be in hex (0x...) or decimal format")
        print("The range is inclusive (includes both start and end addresses)")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    start_str = sys.argv[2]
    end_str = sys.argv[3]
    output_json = '--json' in sys.argv
    
    # Parse addresses (handle hex or decimal)
    try:
        start_address = int(start_str, 0)
        end_address = int(end_str, 0)
    except ValueError as e:
        print(f"Error: Invalid address format: {e}")
        sys.exit(1)
    
    if start_address > end_address:
        print("Error: Start address must be less than or equal to end address")
        sys.exit(1)
    
    try:
        parser = SVDParser(svd_file)
        
        # Search through all peripherals and registers
        matches = []
        peripherals_elem = parser.root.find('peripherals')
        
        if peripherals_elem is not None:
            for periph_elem in peripherals_elem.findall('peripheral'):
                peripheral = parser._parse_peripheral(periph_elem)
                
                for register in peripheral.registers:
                    reg_address = peripheral.base_address + register.address_offset
                    
                    # Check if address is within range (inclusive)
                    if start_address <= reg_address <= end_address:
                        matches.append({
                            'peripheral': peripheral,
                            'register': register,
                            'address': reg_address
                        })
        
        # Sort by address
        matches.sort(key=lambda m: m['address'])
        
        if not matches:
            if output_json:
                print(json.dumps({
                    'error': 'No registers found in this range',
                    'start': hex(start_address),
                    'end': hex(end_address)
                }, indent=2))
            else:
                print(f"\nNo registers found in range {hex(start_address)} - {hex(end_address)}")
            sys.exit(0)
        
        if output_json:
            output = {
                'range': {
                    'start': hex(start_address),
                    'end': hex(end_address),
                    'size': hex(end_address - start_address + 1)
                },
                'count': len(matches),
                'registers': []
            }
            
            for match in matches:
                peripheral = match['peripheral']
                register = match['register']
                output['registers'].append({
                    'address': hex(match['address']),
                    'peripheral': peripheral.name,
                    'peripheral_base': hex(peripheral.base_address),
                    'register': register.name,
                    'register_offset': hex(register.address_offset),
                    'description': register.description,
                    'size': register.size,
                    'access': register.access,
                })
            
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Registers in range {hex(start_address)} - {hex(end_address)}")
            print(f"Found {len(matches)} register(s)")
            print(f"{'='*80}\n")
            
            # Group by peripheral for better readability
            current_peripheral = None
            for match in matches:
                peripheral = match['peripheral']
                register = match['register']
                
                if current_peripheral != peripheral.name:
                    if current_peripheral is not None:
                        print()  # Blank line between peripherals
                    print(f"{peripheral.name} (Base: {hex(peripheral.base_address)})")
                    print(f"{'-'*80}")
                    current_peripheral = peripheral.name
                
                addr = hex(match['address']).ljust(12)
                offset = hex(register.address_offset).ljust(10)
                name = register.name.ljust(20)
                access = f"({register.access})" if register.access else ""
                access_str = access.ljust(15)
                desc = register.description[:30] + '...' if len(register.description) > 30 else register.description
                
                print(f"  {addr} {name} {access_str} {desc}")
            
            print()
    
    except FileNotFoundError:
        print(f"Error: SVD file not found: {svd_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
