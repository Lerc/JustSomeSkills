#!/usr/bin/env python3
"""
Find and display detailed information about a specific register.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def format_bit_field(field, reg_size=32):
    """Format a bit field for display."""
    bits = f"[{field.bit_offset + field.bit_width - 1}:{field.bit_offset}]" if field.bit_width > 1 else f"[{field.bit_offset}]"
    bits = bits.ljust(8)
    name = field.name.ljust(20)
    access = f"({field.access})" if field.access else ""
    
    output = f"  {bits} {name} {access}\n"
    if field.description:
        output += f"         {field.description}\n"
    
    if field.enum_values:
        output += "         Possible values:\n"
        for value, desc in field.enum_values.items():
            output += f"           {value}: {desc}\n"
    
    return output


def main():
    if len(sys.argv) < 4:
        print("Usage: find_register.py <svd_file> <peripheral> <register> [--json]")
        print("\nExample: find_register.py device.svd TIMER0 CTRL")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    peripheral_name = sys.argv[2]
    register_name = sys.argv[3]
    output_json = '--json' in sys.argv
    
    try:
        parser = SVDParser(svd_file)
        result = parser.find_register(peripheral_name, register_name)
        
        if result is None:
            print(f"Error: Register {register_name} not found in peripheral {peripheral_name}")
            sys.exit(1)
        
        peripheral, register = result
        absolute_address = peripheral.base_address + register.address_offset
        
        if output_json:
            data = {
                'peripheral': peripheral.name,
                'peripheral_base': hex(peripheral.base_address),
                'register': register.name,
                'offset': hex(register.address_offset),
                'absolute_address': hex(absolute_address),
                'size': register.size,
                'access': register.access,
                'reset_value': hex(register.reset_value) if register.reset_value is not None else None,
                'description': register.description,
                'fields': [
                    {
                        'name': f.name,
                        'bits': f"{f.bit_offset + f.bit_width - 1}:{f.bit_offset}" if f.bit_width > 1 else str(f.bit_offset),
                        'width': f.bit_width,
                        'access': f.access,
                        'description': f.description,
                        'enum_values': f.enum_values,
                    }
                    for f in register.fields
                ]
            }
            print(json.dumps(data, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Register: {peripheral.name}.{register.name}")
            print(f"{'='*80}")
            print(f"Peripheral Base:  {hex(peripheral.base_address)}")
            print(f"Register Offset:  {hex(register.address_offset)}")
            print(f"Absolute Address: {hex(absolute_address)}")
            print(f"Size:             {register.size} bits")
            if register.access:
                print(f"Access:           {register.access}")
            if register.reset_value is not None:
                print(f"Reset Value:      {hex(register.reset_value)}")
            print(f"\nDescription:")
            print(f"  {register.description}\n")
            
            if register.fields:
                print(f"Bit Fields:")
                print(f"{'-'*80}")
                for field in sorted(register.fields, key=lambda f: f.bit_offset, reverse=True):
                    print(format_bit_field(field, register.size))
            else:
                print("No bit field definitions available.\n")
    
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
