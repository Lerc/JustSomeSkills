#!/usr/bin/env python3
"""
Find which register corresponds to a specific memory address.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def main():
    if len(sys.argv) < 3:
        print("Usage: find_by_address.py <svd_file> <address> [--json]")
        print("\nExamples:")
        print("  find_by_address.py device.svd 0x40000004")
        print("  find_by_address.py device.svd 0x40000004 --json")
        print("\nAddress can be in hex (0x...) or decimal format")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    address_str = sys.argv[2]
    output_json = '--json' in sys.argv
    
    # Parse address (handle hex or decimal)
    try:
        target_address = int(address_str, 0)
    except ValueError:
        print(f"Error: Invalid address format: {address_str}")
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
                    
                    # Check if address matches
                    if reg_address == target_address:
                        matches.append({
                            'peripheral': peripheral,
                            'register': register,
                            'address': reg_address
                        })
        
        if not matches:
            if output_json:
                print(json.dumps({'error': 'No register found at this address', 'address': hex(target_address)}, indent=2))
            else:
                print(f"\nNo register found at address {hex(target_address)}")
            sys.exit(0)
        
        if output_json:
            output = []
            for match in matches:
                peripheral = match['peripheral']
                register = match['register']
                output.append({
                    'address': hex(match['address']),
                    'peripheral': peripheral.name,
                    'peripheral_base': hex(peripheral.base_address),
                    'register': register.name,
                    'register_offset': hex(register.address_offset),
                    'description': register.description,
                    'size': register.size,
                    'access': register.access,
                    'reset_value': hex(register.reset_value) if register.reset_value is not None else None,
                })
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Register(s) at address {hex(target_address)}")
            print(f"{'='*80}")
            
            for match in matches:
                peripheral = match['peripheral']
                register = match['register']
                
                print(f"\nPeripheral:       {peripheral.name}")
                print(f"  Base Address:   {hex(peripheral.base_address)}")
                print(f"\nRegister:         {register.name}")
                print(f"  Offset:         {hex(register.address_offset)}")
                print(f"  Absolute Addr:  {hex(match['address'])}")
                print(f"  Size:           {register.size} bits")
                if register.access:
                    print(f"  Access:         {register.access}")
                if register.reset_value is not None:
                    print(f"  Reset Value:    {hex(register.reset_value)}")
                print(f"\nDescription:")
                print(f"  {register.description}")
                
                if register.fields:
                    print(f"\nBit Fields:")
                    print(f"{'-'*80}")
                    for field in sorted(register.fields, key=lambda f: f.bit_offset, reverse=True):
                        bits = f"[{field.bit_offset + field.bit_width - 1}:{field.bit_offset}]" if field.bit_width > 1 else f"[{field.bit_offset}]"
                        print(f"  {bits.ljust(8)} {field.name}")
                
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
