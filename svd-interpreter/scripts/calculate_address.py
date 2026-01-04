#!/usr/bin/env python3
"""
Calculate absolute memory addresses for registers.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def main():
    if len(sys.argv) < 3:
        print("Usage: calculate_address.py <svd_file> <peripheral> [register] [--json]")
        print("\nExamples:")
        print("  calculate_address.py device.svd TIMER0")
        print("    Shows base address of TIMER0 peripheral")
        print("  calculate_address.py device.svd TIMER0 CTRL")
        print("    Shows absolute address of TIMER0.CTRL register")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    peripheral_name = sys.argv[2]
    register_name = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
    output_json = '--json' in sys.argv
    
    try:
        parser = SVDParser(svd_file)
        peripheral = parser.get_peripheral(peripheral_name)
        
        if peripheral is None:
            print(f"Error: Peripheral {peripheral_name} not found")
            sys.exit(1)
        
        if register_name:
            # Find specific register
            register = None
            for reg in peripheral.registers:
                if reg.name == register_name:
                    register = reg
                    break
            
            if register is None:
                print(f"Error: Register {register_name} not found in peripheral {peripheral_name}")
                sys.exit(1)
            
            absolute_address = peripheral.base_address + register.address_offset
            
            if output_json:
                data = {
                    'peripheral': peripheral.name,
                    'peripheral_base': hex(peripheral.base_address),
                    'register': register.name,
                    'register_offset': hex(register.address_offset),
                    'absolute_address': hex(absolute_address),
                }
                print(json.dumps(data, indent=2))
            else:
                print(f"\n{peripheral.name}.{register.name}")
                print(f"{'='*80}")
                print(f"Peripheral Base:  {hex(peripheral.base_address)}")
                print(f"Register Offset:  {hex(register.address_offset)}")
                print(f"Absolute Address: {hex(absolute_address)}")
                print()
        else:
            # Just show peripheral base and all register addresses
            if output_json:
                data = {
                    'peripheral': peripheral.name,
                    'base_address': hex(peripheral.base_address),
                    'registers': [
                        {
                            'name': reg.name,
                            'offset': hex(reg.address_offset),
                            'absolute_address': hex(peripheral.base_address + reg.address_offset),
                        }
                        for reg in peripheral.registers
                    ]
                }
                print(json.dumps(data, indent=2))
            else:
                print(f"\n{peripheral.name}")
                print(f"{'='*80}")
                print(f"Base Address: {hex(peripheral.base_address)}")
                print(f"\nRegisters:")
                print(f"{'-'*80}")
                
                for reg in peripheral.registers:
                    absolute = peripheral.base_address + reg.address_offset
                    name = reg.name.ljust(25)
                    offset = hex(reg.address_offset).ljust(10)
                    print(f"  {name} {offset} -> {hex(absolute)}")
                
                print()
    
    except FileNotFoundError:
        print(f"Error: SVD file not found: {svd_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
