#!/usr/bin/env python3
"""
Core SVD parsing utilities for extracting information from CMSIS SVD files.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import lzma


@dataclass
class BitField:
    """Represents a bit field within a register."""
    name: str
    description: str
    bit_offset: int
    bit_width: int
    access: Optional[str] = None
    enum_values: Optional[Dict[str, str]] = None


@dataclass
class Register:
    """Represents a register within a peripheral."""
    name: str
    description: str
    address_offset: int
    size: int
    access: Optional[str] = None
    reset_value: Optional[int] = None
    fields: List[BitField] = None
    
    def __post_init__(self):
        if self.fields is None:
            self.fields = []


@dataclass
class Peripheral:
    """Represents a peripheral in the microcontroller."""
    name: str
    description: str
    base_address: int
    group_name: Optional[str] = None
    registers: List[Register] = None
    
    def __post_init__(self):
        if self.registers is None:
            self.registers = []


class SVDParser:
    """Parser for CMSIS SVD files."""
    
    def __init__(self, svd_path: str):
        """Initialize parser with SVD file path. Supports .lzma compressed files."""
        # Check if file is LZMA compressed
        if svd_path.endswith('.lzma'):
            with lzma.open(svd_path, 'rt', encoding='utf-8') as f:
                svd_content = f.read()
            # Parse from string
            self.root = ET.fromstring(svd_content)
            self.tree = ET.ElementTree(self.root)
        else:
            # Parse regular XML file
            self.tree = ET.parse(svd_path)
            self.root = self.tree.getroot()
        
        self.device_name = self._get_text(self.root, 'name', 'Unknown')
        
    def _get_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """Safely get text from an XML element."""
        child = element.find(tag)
        return child.text.strip() if child is not None and child.text else default
    
    def _get_int(self, element: ET.Element, tag: str, default: int = 0) -> int:
        """Safely get integer value from an XML element (handles hex)."""
        text = self._get_text(element, tag)
        if not text:
            return default
        try:
            # Handle hex (0x...) and decimal
            return int(text, 0)
        except ValueError:
            return default
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get basic device information."""
        return {
            'name': self.device_name,
            'vendor': self._get_text(self.root, 'vendor'),
            'version': self._get_text(self.root, 'version'),
            'description': self._get_text(self.root, 'description'),
            'cpu': self._get_cpu_info(),
            'address_unit_bits': self._get_int(self.root, 'addressUnitBits', 8),
            'width': self._get_int(self.root, 'width', 32),
        }
    
    def _get_cpu_info(self) -> Dict[str, str]:
        """Extract CPU information."""
        cpu = self.root.find('cpu')
        if cpu is None:
            return {}
        
        return {
            'name': self._get_text(cpu, 'name'),
            'revision': self._get_text(cpu, 'revision'),
            'endian': self._get_text(cpu, 'endian'),
            'mpu_present': self._get_text(cpu, 'mpuPresent'),
            'fpu_present': self._get_text(cpu, 'fpuPresent'),
            'nvic_prio_bits': self._get_text(cpu, 'nvicPrioBits'),
            'vendor_systick': self._get_text(cpu, 'vendorSystickConfig'),
        }
    
    def list_peripherals(self) -> List[Dict[str, Any]]:
        """Get a list of all peripherals with basic info."""
        peripherals = []
        peripherals_elem = self.root.find('peripherals')
        
        if peripherals_elem is None:
            return peripherals
        
        for periph in peripherals_elem.findall('peripheral'):
            peripherals.append({
                'name': self._get_text(periph, 'name'),
                'description': self._get_text(periph, 'description'),
                'base_address': hex(self._get_int(periph, 'baseAddress')),
                'group_name': self._get_text(periph, 'groupName'),
            })
        
        return peripherals
    
    def get_peripheral(self, peripheral_name: str) -> Optional[Peripheral]:
        """Get detailed information about a specific peripheral."""
        peripherals_elem = self.root.find('peripherals')
        if peripherals_elem is None:
            return None
        
        for periph in peripherals_elem.findall('peripheral'):
            if self._get_text(periph, 'name') == peripheral_name:
                return self._parse_peripheral(periph)
        
        return None
    
    def _parse_peripheral(self, periph_elem: ET.Element) -> Peripheral:
        """Parse a peripheral element into a Peripheral object."""
        peripheral = Peripheral(
            name=self._get_text(periph_elem, 'name'),
            description=self._get_text(periph_elem, 'description'),
            base_address=self._get_int(periph_elem, 'baseAddress'),
            group_name=self._get_text(periph_elem, 'groupName'),
        )
        
        # Parse registers
        registers_elem = periph_elem.find('registers')
        if registers_elem is not None:
            for reg_elem in registers_elem.findall('register'):
                register = self._parse_register(reg_elem)
                peripheral.registers.append(register)
        
        return peripheral
    
    def _parse_register(self, reg_elem: ET.Element) -> Register:
        """Parse a register element into a Register object."""
        register = Register(
            name=self._get_text(reg_elem, 'name'),
            description=self._get_text(reg_elem, 'description'),
            address_offset=self._get_int(reg_elem, 'addressOffset'),
            size=self._get_int(reg_elem, 'size', 32),
            access=self._get_text(reg_elem, 'access'),
            reset_value=self._get_int(reg_elem, 'resetValue'),
        )
        
        # Parse fields
        fields_elem = reg_elem.find('fields')
        if fields_elem is not None:
            for field_elem in fields_elem.findall('field'):
                field = self._parse_field(field_elem)
                register.fields.append(field)
        
        return register
    
    def _parse_field(self, field_elem: ET.Element) -> BitField:
        """Parse a field element into a BitField object."""
        # Handle bitRange (e.g., "[7:0]") or separate bitOffset/bitWidth
        bit_range = self._get_text(field_elem, 'bitRange')
        if bit_range:
            # Parse "[msb:lsb]" format
            bit_range = bit_range.strip('[]')
            msb, lsb = map(int, bit_range.split(':'))
            bit_offset = lsb
            bit_width = msb - lsb + 1
        else:
            bit_offset = self._get_int(field_elem, 'bitOffset')
            bit_width = self._get_int(field_elem, 'bitWidth', 1)
        
        # Parse enumerated values if present
        enum_values = None
        enum_elem = field_elem.find('enumeratedValues')
        if enum_elem is not None:
            enum_values = {}
            for enum_val in enum_elem.findall('enumeratedValue'):
                name = self._get_text(enum_val, 'name')
                value = self._get_text(enum_val, 'value')
                desc = self._get_text(enum_val, 'description')
                if name and value:
                    enum_values[value] = f"{name}: {desc}" if desc else name
        
        return BitField(
            name=self._get_text(field_elem, 'name'),
            description=self._get_text(field_elem, 'description'),
            bit_offset=bit_offset,
            bit_width=bit_width,
            access=self._get_text(field_elem, 'access'),
            enum_values=enum_values,
        )
    
    def find_register(self, peripheral_name: str, register_name: str) -> Optional[tuple]:
        """Find a specific register and return (peripheral, register)."""
        peripheral = self.get_peripheral(peripheral_name)
        if peripheral is None:
            return None
        
        for register in peripheral.registers:
            if register.name == register_name:
                return (peripheral, register)
        
        return None
    
    def search_registers(self, pattern: str) -> List[tuple]:
        """Search for registers matching a pattern (case-insensitive)."""
        results = []
        pattern = pattern.lower()
        
        peripherals_elem = self.root.find('peripherals')
        if peripherals_elem is None:
            return results
        
        for periph_elem in peripherals_elem.findall('peripheral'):
            periph_name = self._get_text(periph_elem, 'name')
            
            registers_elem = periph_elem.find('registers')
            if registers_elem is not None:
                for reg_elem in registers_elem.findall('register'):
                    reg_name = self._get_text(reg_elem, 'name')
                    if pattern in reg_name.lower():
                        results.append((periph_name, reg_name))
        
        return results
