#!/usr/bin/env python3
"""
Decode a register value by breaking it down into bit fields.
Shows what each bit field is set to, including enumerated value names.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def format_binary(value, width):
    """Format value as binary with underscores every 4 bits for readability."""
    binary = format(value, f'0{width}b')
    # Add underscores every 4 bits from right
    result = []
    for i, bit in enumerate(reversed(binary)):
        if i > 0 and i % 4 == 0:
            result.append('_')
        result.append(bit)
    return ''.join(reversed(result))


def extract_field_value(reg_value, bit_offset, bit_width):
    """Extract a bit field value from a register value."""
    mask = (1 << bit_width) - 1
    return (reg_value >> bit_offset) & mask


def decode_field(field, reg_value, reg_size):
    """Decode a single field from the register value."""
    field_value = extract_field_value(reg_value, field.bit_offset, field.bit_width)
    
    result = {
        'name': field.name,
        'bit_range': f"[{field.bit_offset + field.bit_width - 1}:{field.bit_offset}]" if field.bit_width > 1 else f"[{field.bit_offset}]",
        'value': field_value,
        'value_hex': hex(field_value),
        'value_binary': format_binary(field_value, field.bit_width),
        'description': field.description,
    }
    
    # Check for enumerated values
    if field.enum_values:
        value_str = str(field_value)
        if value_str in field.enum_values:
            result['enum_match'] = field.enum_values[value_str]
        else:
            # Try hex format
            value_hex = hex(field_value)
            if value_hex in field.enum_values:
                result['enum_match'] = field.enum_values[value_hex]
            else:
                result['enum_match'] = None
                result['warning'] = 'Value does not match any enumerated value'
    
    return result


def find_register_by_name_or_address(parser, identifier):
    """Find register by 'PERIPHERAL.REGISTER' name or by hex address."""
    # Try parsing as address first
    try:
        address = int(identifier, 0)
        # Search by address
        peripherals_elem = parser.root.find('peripherals')
        if peripherals_elem is not None:
            for periph_elem in peripherals_elem.findall('peripheral'):
                peripheral = parser._parse_peripheral(periph_elem)
                for register in peripheral.registers:
                    reg_address = peripheral.base_address + register.address_offset
                    if reg_address == address:
                        return peripheral, register, reg_address
        return None, None, None
    except ValueError:
        pass
    
    # Try parsing as PERIPHERAL.REGISTER
    if '.' in identifier:
        parts = identifier.split('.', 1)
        if len(parts) == 2:
            peripheral_name, register_name = parts
            result = parser.find_register(peripheral_name, register_name)
            if result:
                peripheral, register = result
                address = peripheral.base_address + register.address_offset
                return peripheral, register, address
    
    return None, None, None


def main():
    if len(sys.argv) < 4:
        print("Usage: decode_value.py <svd_file> <register> <value> [--json]")
        print("\nRegister can be specified as:")
        print("  - Peripheral.Register name (e.g., TIMER0.CTRL)")
        print("  - Memory address (e.g., 0x40000000)")
        print("\nValue can be in hex (0x...) or decimal format")
        print("\nExamples:")
        print("  decode_value.py device.svd TIMER0.CTRL 0x03")
        print("  decode_value.py device.svd 0x40000000 7")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    register_id = sys.argv[2]
    value_str = sys.argv[3]
    output_json = '--json' in sys.argv
    
    # Parse value
    try:
        value = int(value_str, 0)
    except ValueError:
        print(f"Error: Invalid value format: {value_str}")
        sys.exit(1)
    
    try:
        parser = SVDParser(svd_file)
        peripheral, register, address = find_register_by_name_or_address(parser, register_id)
        
        if not peripheral or not register:
            print(f"Error: Register '{register_id}' not found")
            sys.exit(1)
        
        # Decode the value
        decoded_fields = []
        for field in sorted(register.fields, key=lambda f: f.bit_offset, reverse=True):
            decoded_fields.append(decode_field(field, value, register.size))
        
        if output_json:
            output = {
                'register': {
                    'peripheral': peripheral.name,
                    'name': register.name,
                    'address': hex(address),
                    'size': register.size,
                },
                'value': {
                    'decimal': value,
                    'hex': hex(value),
                    'binary': format_binary(value, register.size),
                },
                'fields': decoded_fields
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Register: {peripheral.name}.{register.name}")
            print(f"Address:  {hex(address)}")
            print(f"{'='*80}")
            
            print(f"\nValue:    {value} (decimal)")
            print(f"          {hex(value)} (hex)")
            print(f"          0b{format_binary(value, register.size)} (binary)")
            print(f"\nBit Field Breakdown:")
            print(f"{'-'*80}")
            
            if not register.fields:
                print("  No bit field definitions available.")
            else:
                for field_info in decoded_fields:
                    bits = field_info['bit_range'].ljust(8)
                    name = field_info['name'].ljust(20)
                    val = f"= {field_info['value']}".ljust(10)
                    hex_val = f"({field_info['value_hex']})".ljust(10)
                    
                    print(f"\n  {bits} {name} {val} {hex_val}")
                    print(f"         Binary: {field_info['value_binary']}")
                    
                    if field_info['description']:
                        print(f"         {field_info['description']}")
                    
                    if 'enum_match' in field_info:
                        if field_info['enum_match']:
                            print(f"         → {field_info['enum_match']}")
                        elif 'warning' in field_info:
                            print(f"         ⚠ {field_info['warning']}")
            
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
