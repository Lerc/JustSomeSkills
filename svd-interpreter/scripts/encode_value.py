#!/usr/bin/env python3
"""
Encode a register value by specifying bit field values.
Validates field values against enumerated values and checks for conflicts.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svd_parser import SVDParser


def format_binary(value, width):
    """Format value as binary with underscores every 4 bits for readability."""
    binary = format(value, f'0{width}b')
    result = []
    for i, bit in enumerate(reversed(binary)):
        if i > 0 and i % 4 == 0:
            result.append('_')
        result.append(bit)
    return ''.join(reversed(result))


def find_register_by_name_or_address(parser, identifier):
    """Find register by 'PERIPHERAL.REGISTER' name or by hex address."""
    try:
        address = int(identifier, 0)
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


def parse_field_value(field, value_str):
    """
    Parse a field value string. Can be:
    - Numeric (decimal or hex): "1", "0x3"
    - Enumerated name: "ONESHOT", "PERIODIC"
    Returns (value, enum_name_used) or (None, error_message)
    """
    # Try as enumerated value first
    if field.enum_values:
        for enum_key, enum_desc in field.enum_values.items():
            # Check if value_str matches the enum name (first part before colon)
            enum_name = enum_desc.split(':')[0].strip()
            if value_str.upper() == enum_name.upper():
                try:
                    return int(enum_key, 0), enum_name
                except ValueError:
                    pass
            # Also check if it matches the key directly
            if value_str == enum_key:
                return int(enum_key, 0), enum_name
    
    # Try as numeric value
    try:
        value = int(value_str, 0)
        # Check if value fits in field width
        max_value = (1 << field.bit_width) - 1
        if value < 0 or value > max_value:
            return None, f"Value {value} out of range for {field.bit_width}-bit field (max: {max_value})"
        
        # Check if it's a valid enumerated value
        if field.enum_values:
            value_key = str(value)
            hex_key = hex(value)
            if value_key not in field.enum_values and hex_key not in field.enum_values:
                valid_values = [f"{k} ({field.enum_values[k].split(':')[0]})" for k in field.enum_values.keys()]
                return None, f"Value {value} not in enumerated values. Valid: {', '.join(valid_values)}"
        
        return value, None
    except ValueError:
        return None, f"Invalid value format: '{value_str}'"


def main():
    if len(sys.argv) < 3:
        print("Usage: encode_value.py <svd_file> <register> [field=value ...] [--base=value] [--json]")
        print("\nRegister can be specified as:")
        print("  - Peripheral.Register name (e.g., TIMER0.CTRL)")
        print("  - Memory address (e.g., 0x40000000)")
        print("\nField assignments:")
        print("  - FIELD_NAME=numeric_value (e.g., ENABLE=1)")
        print("  - FIELD_NAME=enum_name (e.g., MODE=PERIODIC)")
        print("\nOptions:")
        print("  --base=value    Start from base value (default: 0, use 'reset' for reset value)")
        print("  --json          Output in JSON format")
        print("\nExamples:")
        print("  encode_value.py device.svd TIMER0.CTRL ENABLE=1 MODE=PERIODIC")
        print("  encode_value.py device.svd 0x40000000 ENABLE=1 MODE=0x1")
        print("  encode_value.py device.svd TIMER0.CTRL ENABLE=1 --base=reset")
        sys.exit(1)
    
    svd_file = sys.argv[1]
    register_id = sys.argv[2]
    
    # Parse arguments
    field_assignments = {}
    base_value = 0
    output_json = False
    
    for arg in sys.argv[3:]:
        if arg == '--json':
            output_json = True
        elif arg.startswith('--base='):
            base_str = arg.split('=', 1)[1]
            if base_str.lower() == 'reset':
                base_value = 'reset'  # Will be resolved later
            else:
                try:
                    base_value = int(base_str, 0)
                except ValueError:
                    print(f"Error: Invalid base value: {base_str}")
                    sys.exit(1)
        elif '=' in arg:
            parts = arg.split('=', 1)
            if len(parts) == 2:
                field_assignments[parts[0].strip()] = parts[1].strip()
    
    try:
        parser = SVDParser(svd_file)
        peripheral, register, address = find_register_by_name_or_address(parser, register_id)
        
        if not peripheral or not register:
            print(f"Error: Register '{register_id}' not found")
            sys.exit(1)
        
        # Resolve base value
        if base_value == 'reset':
            base_value = register.reset_value if register.reset_value is not None else 0
        
        # Start with base value
        result_value = base_value
        applied_fields = []
        errors = []
        warnings = []
        
        # Build field lookup
        field_map = {field.name.upper(): field for field in register.fields}
        
        # Process each field assignment
        for field_name, value_str in field_assignments.items():
            field_name_upper = field_name.upper()
            
            if field_name_upper not in field_map:
                errors.append(f"Field '{field_name}' not found in register")
                continue
            
            field = field_map[field_name_upper]
            parsed_value, error_or_enum = parse_field_value(field, value_str)
            
            if parsed_value is None:
                errors.append(f"{field.name}: {error_or_enum}")
                continue
            
            # Clear the bits for this field
            mask = ((1 << field.bit_width) - 1) << field.bit_offset
            result_value = (result_value & ~mask) | (parsed_value << field.bit_offset)
            
            applied_fields.append({
                'name': field.name,
                'value': parsed_value,
                'value_hex': hex(parsed_value),
                'bit_range': f"[{field.bit_offset + field.bit_width - 1}:{field.bit_offset}]" if field.bit_width > 1 else f"[{field.bit_offset}]",
                'enum_used': error_or_enum,
            })
        
        # Check for unset fields (that aren't zero from base)
        for field in register.fields:
            if field.name.upper() not in [f['name'].upper() for f in applied_fields]:
                field_mask = ((1 << field.bit_width) - 1) << field.bit_offset
                field_value = (result_value & field_mask) >> field.bit_offset
                if field_value != 0:
                    warnings.append(f"{field.name} not specified, using value from base: {field_value} ({hex(field_value)})")
        
        if output_json:
            output = {
                'register': {
                    'peripheral': peripheral.name,
                    'name': register.name,
                    'address': hex(address),
                },
                'base_value': {
                    'decimal': base_value,
                    'hex': hex(base_value),
                },
                'result_value': {
                    'decimal': result_value,
                    'hex': hex(result_value),
                    'binary': format_binary(result_value, register.size),
                },
                'applied_fields': applied_fields,
                'errors': errors,
                'warnings': warnings,
                'valid': len(errors) == 0,
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Register: {peripheral.name}.{register.name}")
            print(f"Address:  {hex(address)}")
            print(f"{'='*80}")
            
            if errors:
                print(f"\n❌ ERRORS:")
                for error in errors:
                    print(f"  • {error}")
                print(f"\nConfiguration is INVALID. Please fix errors above.")
                sys.exit(1)
            
            print(f"\nBase Value:   {base_value} ({hex(base_value)})")
            print(f"Result Value: {result_value} ({hex(result_value)})")
            print(f"Binary:       0b{format_binary(result_value, register.size)}")
            
            if applied_fields:
                print(f"\nApplied Fields:")
                print(f"{'-'*80}")
                for field_info in applied_fields:
                    bits = field_info['bit_range'].ljust(8)
                    name = field_info['name'].ljust(20)
                    val = f"= {field_info['value']}".ljust(10)
                    hex_val = f"({field_info['value_hex']})".ljust(10)
                    
                    print(f"  {bits} {name} {val} {hex_val}", end='')
                    if field_info['enum_used']:
                        print(f"  [{field_info['enum_used']}]")
                    else:
                        print()
            
            if warnings:
                print(f"\n⚠ WARNINGS:")
                for warning in warnings:
                    print(f"  • {warning}")
            
            print(f"\n✅ Configuration is VALID")
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
