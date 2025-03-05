#!/usr/bin/env python3
"""
RISC-V Assembler

A straightforward RISC-V assembler that converts assembly code into machine code.
Supports a subset of RV32I instructions with focus on readability and error handling.

Example assembly code:
    main:
        addi x1, x0, 5    # Load immediate value 5 into x1
        addi x2, x0, 3    # Load immediate value 3 into x2
        add x3, x1, x2    # Add x1 and x2, store in x3
        sw x3, 0(x0)      # Store result in memory
        halt              # Stop execution

Usage:
    python assembler.py input.asm output.bin
"""

import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Register name mappings
REGISTER_ALIASES = {
    # Zero register
    "zero": 0, "x0": 0,
    # Return address
    "ra": 1, "x1": 1,
    # Stack and global pointers
    "sp": 2, "x2": 2, "gp": 3, "x3": 3,
    # Thread pointer
    "tp": 4, "x4": 4,
    # Temporaries
    "t0": 5, "t1": 6, "t2": 7,
    # Saved registers and frame pointer
    "s0": 8, "fp": 8, "s1": 9,
    # Function arguments
    "a0": 10, "a1": 11, "a2": 12, "a3": 13,
    "a4": 14, "a5": 15, "a6": 16, "a7": 17,
    # More saved registers
    "s2": 18, "s3": 19, "s4": 20, "s5": 21,
    "s6": 22, "s7": 23, "s8": 24, "s9": 25,
    "s10": 26, "s11": 27,
    # More temporaries
    "t3": 28, "t4": 29, "t5": 30, "t6": 31
}

# Instruction opcodes and types
INSTRUCTION_DETAILS = {
    # R-type arithmetic
    'add':  (0x33, 'R'), 'sub':  (0x33, 'R'),
    'slt':  (0x33, 'R'), 'sll':  (0x33, 'R'),
    'srl':  (0x33, 'R'), 'or':   (0x33, 'R'),
    'and':  (0x33, 'R'), 'xor':  (0x33, 'R'),
    
    # I-type loads and immediates
    'lw':   (0x03, 'I'), 'addi': (0x13, 'I'),
    'slti': (0x13, 'I'), 'sltiu':(0x13, 'I'),
    'slli': (0x13, 'I'), 'srli': (0x13, 'I'),
    'ori':  (0x13, 'I'), 'andi': (0x13, 'I'),
    'xori': (0x13, 'I'), 'jalr': (0x67, 'I'),
    
    # S-type stores
    'sw':   (0x23, 'S'),
    
    # B-type branches
    'beq':  (0x63, 'B'), 'bne':  (0x63, 'B'),
    'blt':  (0x63, 'B'), 'bge':  (0x63, 'B'),
    'bltu': (0x63, 'B'), 'bgeu': (0x63, 'B'),
    
    # U-type and J-type
    'lui':  (0x37, 'U'), 'auipc':(0x17, 'U'),
    'jal':  (0x6f, 'J'),
    
    # Special instructions
    'rst':  (0x00, 'X'), 'halt': (0x00, 'X')
}

@dataclass
class Instruction:
    """Represents a parsed assembly instruction."""
    name: str
    operands: List[str]
    line_num: int
    label: str = ''

class AssemblyError(Exception):
    """Custom exception for assembly errors with line information."""
    def __init__(self, message: str, line_num: int):
        self.message = message
        self.line_num = line_num
        super().__init__(f"Line {line_num}: {message}")

class Assembler:
    def __init__(self):
        self.labels: Dict[str, int] = {}

    def _sign_extend(self, value: int, bits: int) -> int:
        """
        Sign-extends a value to the specified number of bits.
        
        Args:
            value: Integer value to sign extend
            bits: Number of bits in the original value
            
        Returns:
            Sign-extended integer value
        """
        sign_bit = 1 << (bits - 1)
        value &= (1 << bits) - 1  # Mask to specified bits
        return (value & (sign_bit - 1)) - (value & sign_bit)

    def _parse_instruction(self, line: str, line_num: int) -> Instruction:
        """
        Parses a line of assembly code into an Instruction object.
        
        Args:
            line: Assembly code line
            line_num: Line number for error reporting
            
        Returns:
            Parsed Instruction object
        
        Raises:
            AssemblyError: If the instruction format is invalid
        """
        # Remove comments and whitespace
        line = line.split('#')[0].strip()
        if not line:
            return None
            
        # Extract label if present
        label = ''
        if ':' in line:
            parts = line.split(':')
            if len(parts) != 2:
                raise AssemblyError("Invalid label format", line_num)
            label = parts[0].strip()
            line = parts[1].strip()
            
        if not line:
            return Instruction(name='', operands=[], line_num=line_num, label=label)
            
        # Parse instruction and operands
        parts = line.split()
        name = parts[0].lower()
        if name not in INSTRUCTION_DETAILS:
            raise AssemblyError(f"Unknown instruction: {name}", line_num)
            
        operands = []
        if len(parts) > 1:
            operands = [op.strip() for op in ' '.join(parts[1:]).split(',')]
            
        return Instruction(name=name, operands=operands, line_num=line_num, label=label)

    def _encode_r_type(self, inst: Instruction) -> int:
        """Encodes R-type instructions (add, sub, etc.)."""
        if len(inst.operands) != 3:
            raise AssemblyError(f"{inst.name} requires 3 registers", inst.line_num)
            
        try:
            rd = int(inst.operands[0][1:]) if inst.operands[0].startswith('x') else REGISTER_ALIASES[inst.operands[0]]
            rs1 = int(inst.operands[1][1:]) if inst.operands[1].startswith('x') else REGISTER_ALIASES[inst.operands[1]]
            rs2 = int(inst.operands[2][1:]) if inst.operands[2].startswith('x') else REGISTER_ALIASES[inst.operands[2]]
        except (KeyError, ValueError):
            raise AssemblyError("Invalid register name", inst.line_num)
            
        funct3 = {
            'add': 0x0, 'sub': 0x0, 'slt': 0x2,
            'sll': 0x1, 'srl': 0x5, 'or': 0x6,
            'and': 0x7, 'xor': 0x4
        }[inst.name]
        
        funct7 = 0x20 if inst.name == 'sub' else 0x00
        return ((funct7 & 0x7f) << 25) | ((rs2 & 0x1f) << 20) | \
               ((rs1 & 0x1f) << 15) | ((funct3 & 0x7) << 12) | \
               ((rd & 0x1f) << 7) | 0x33

    def assemble(self, input_path: str, output_path: str) -> None:
        try:
            # First pass: collect labels and validate syntax
            instructions = []
            current_addr = 0
            
            with open(input_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    inst = self._parse_instruction(line, line_num)
                    if not inst:
                        continue
                        
                    if inst.label:
                        if inst.label in self.labels:
                            raise AssemblyError(f"Duplicate label: {inst.label}", line_num)
                        self.labels[inst.label] = current_addr
                        
                    if inst.name:  # Valid instruction
                        instructions.append(inst)
                        current_addr += 4

            # Second pass: generate machine code
            machine_code = []
            current_addr = 0
            
            for inst in instructions:
                try:
                    opcode, inst_type = INSTRUCTION_DETAILS[inst.name]
                    
                    if inst_type == 'R':
                        code = self._encode_r_type(inst)
                    elif inst_type == 'I':
                        code = self._encode_i_type(inst, current_addr)
                    elif inst_type == 'S':
                        code = self._encode_s_type(inst)
                    elif inst_type == 'B':
                        code = self._encode_b_type(inst, current_addr)
                    elif inst_type == 'U':
                        code = self._encode_u_type(inst)
                    elif inst_type == 'J':
                        code = self._encode_j_type(inst, current_addr)
                    elif inst_type == 'X':
                        code = 0x7fffffff if inst.name == 'halt' else 0
                    
                    machine_code.append(code)
                    current_addr += 4
                    
                except (KeyError, ValueError) as e:
                    raise AssemblyError(str(e), inst.line_num)
            # Write binary output
            with open(output_path, 'w') as f:
                for code in machine_code:
                    f.write(f"{code:032b}\n")
                    
        except FileNotFoundError:
            print(f"Error: Could not open file {input_path}")
            sys.exit(1)
        except AssemblyError as e:
            print(f"Assembly error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    def _encode_i_type(self, inst: Instruction, current_addr: int) -> int:
        """
        Encodes I-type instructions (loads, immediates).
        Format: imm[11:0] | rs1[4:0] | funct3[2:0] | rd[4:0] | opcode[6:0]
        """
        if len(inst.operands) != 3:
            raise AssemblyError(f"{inst.name} requires 3 operands", inst.line_num)
            
        try:
            rd = int(inst.operands[0][1:]) if inst.operands[0].startswith('x') else REGISTER_ALIASES[inst.operands[0]]
            rs1 = int(inst.operands[1][1:]) if inst.operands[1].startswith('x') else REGISTER_ALIASES[inst.operands[1]]
            
            if inst.name == 'lw':
                # Parse memory offset format: offset(rs1)
                offset_str = inst.operands[1][:inst.operands[1].find('(')].strip()
                rs1_str = inst.operands[1][inst.operands[1].find('(')+1:inst.operands[1].find(')')].strip()
                imm = int(offset_str)
                rs1 = int(rs1_str[1:]) if rs1_str.startswith('x') else REGISTER_ALIASES[rs1_str]
            else:
                imm = int(inst.operands[2])
                
            # Handle special cases
            if inst.name == 'sltiu':
                imm &= 0xFFF  # Treat as unsigned
            else:
                imm = self._sign_extend(imm, 12)
                
            funct3 = {
                'addi': 0x0, 'slti': 0x2, 'sltiu': 0x3,
                'ori': 0x6, 'andi': 0x7, 'xori': 0x4,
                'lw': 0x2, 'jalr': 0x0
            }[inst.name]
            
            return ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | \
                   ((funct3 & 0x7) << 12) | ((rd & 0x1f) << 7) | \
                   INSTRUCTION_DETAILS[inst.name][0]
                   
        except (KeyError, ValueError):
            raise AssemblyError("Invalid register or immediate value", inst.line_num)

    def _encode_s_type(self, inst: Instruction) -> int:
        """
        Encodes S-type instructions (stores).
        Format: imm[11:5] | rs2[4:0] | rs1[4:0] | funct3[2:0] | imm[4:0] | opcode[6:0]
        """
        if len(inst.operands) != 2:
            raise AssemblyError(f"{inst.name} requires 2 operands", inst.line_num)
            
        try:
            rs2 = int(inst.operands[0][1:]) if inst.operands[0].startswith('x') else REGISTER_ALIASES[inst.operands[0]]
            
            # Parse memory offset format: offset(rs1)
            offset_str = inst.operands[1][:inst.operands[1].find('(')].strip()
            rs1_str = inst.operands[1][inst.operands[1].find('(')+1:inst.operands[1].find(')')].strip()
            
            try:
                imm = self.labels.get(offset_str, int(offset_str))
            except ValueError:
                raise AssemblyError(f"Invalid immediate value: {offset_str}", inst.line_num)
                
            imm = self._sign_extend(imm, 12)
            rs1 = int(rs1_str[1:]) if rs1_str.startswith('x') else REGISTER_ALIASES[rs1_str]
            
            # Split immediate into two parts for encoding
            imm11_5 = (imm & 0xfe0) >> 5
            imm4_0 = imm & 0x1f
            
            return (imm11_5 << 25) | ((rs2 & 0x1f) << 20) | \
                   ((rs1 & 0x1f) << 15) | (0x2 << 12) | \
                   (imm4_0 << 7) | 0x23
                   
        except (KeyError, ValueError):
            raise AssemblyError("Invalid register or offset format", inst.line_num)

    def _encode_b_type(self, inst: Instruction, current_addr: int) -> int:
        """
        Encodes B-type instructions (branches).
        Format: imm[12] | imm[10:5] | rs2[4:0] | rs1[4:0] | funct3[2:0] | imm[4:1] | imm[11] | opcode[6:0]
        """
        if len(inst.operands) != 3:
            raise AssemblyError(f"{inst.name} requires 3 operands", inst.line_num)
            
        try:
            rs1 = int(inst.operands[0][1:]) if inst.operands[0].startswith('x') else REGISTER_ALIASES[inst.operands[0]]
            rs2 = int(inst.operands[1][1:]) if inst.operands[1].startswith('x') else REGISTER_ALIASES[inst.operands[1]]
            
            # Calculate branch offset
            try:
                target = self.labels.get(inst.operands[2], int(inst.operands[2]))
                if inst.operands[2] in self.labels:
                    imm = target - current_addr
                else:
                    imm = target
            except ValueError:
                raise AssemblyError(f"Invalid branch target: {inst.operands[2]}", inst.line_num)
                
            imm = self._sign_extend(imm, 13)
            
            funct3 = {
                'beq': 0x0, 'bne': 0x1, 'blt': 0x4,
                'bge': 0x5, 'bltu': 0x6, 'bgeu': 0x7
            }[inst.name]
            
            # Complex immediate encoding for B-type
            imm12 = (imm >> 12) & 0x1
            imm11 = (imm >> 11) & 0x1
            imm10_5 = (imm >> 5) & 0x3f
            imm4_1 = (imm >> 1) & 0xf
            
            return (imm12 << 31) | (imm10_5 << 25) | \
                   ((rs2 & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | \
                   (funct3 << 12) | (imm4_1 << 8) | \
                   (imm11 << 7) | 0x63
                   
        except (KeyError, ValueError):
            raise AssemblyError("Invalid register or branch target", inst.line_num)

    def _encode_u_type(self, inst: Instruction) -> int:
        """
        Encodes U-type instructions (lui, auipc).
        Format: imm[31:12] | rd[4:0] | opcode[6:0]
        """
        if len(inst.operands) != 2:
            raise AssemblyError(f"{inst.name} requires 2 operands", inst.line_num)
            
        try:
            rd = int(inst.operands[0][1:]) if inst.operands[0].startswith('x') else REGISTER_ALIASES[inst.operands[0]]
            imm = int(inst.operands[1])
            
            # Handle upper immediate
            if imm & (1 << 31):  # Sign bit is set
                imm |= -1 << 32  # Sign extend to 64 bits
            imm = (imm >> 12) & 0xfffff  # Keep only upper 20 bits
            
            return (imm << 12) | ((rd & 0x1f) << 7) | INSTRUCTION_DETAILS[inst.name][0]
            
        except (KeyError, ValueError):
            raise AssemblyError("Invalid register or immediate value", inst.line_num)

    def _encode_j_type(self, inst: Instruction, current_addr: int) -> int:
        """
        Encodes J-type instructions (jal).
        Format: imm[20] | imm[10:1] | imm[11] | imm[19:12] | rd[4:0] | opcode[6:0]
        """
        if len(inst.operands) != 2:
            raise AssemblyError(f"{inst.name} requires 2 operands", inst.line_num)
            
        try:
            rd = int(inst.operands[0][1:]) if inst.operands[0].startswith('x') else REGISTER_ALIASES[inst.operands[0]]
            
            # Calculate jump offset
            try:
                target = self.labels.get(inst.operands[1], int(inst.operands[1]))
                if inst.operands[1] in self.labels:
                    imm = target - current_addr
                else:
                    imm = target
            except ValueError:
                raise AssemblyError(f"Invalid jump target: {inst.operands[1]}", inst.line_num)
                
            imm = self._sign_extend(imm, 21)
            
            # Complex immediate encoding for J-type
            imm20 = (imm >> 20) & 0x1
            imm10_1 = (imm >> 1) & 0x3ff
            imm11 = (imm >> 11) & 0x1
            imm19_12 = (imm >> 12) & 0xff
            
            return (imm20 << 31) | (imm10_1 << 21) | \
                   (imm11 << 20) | (imm19_12 << 12) | \
                   ((rd & 0x1f) << 7) | 0x6f
                   
        except (KeyError, ValueError):
            raise AssemblyError("Invalid register or jump target", inst.line_num)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 assembler.py <input_file> <output_file>")
        sys.exit(1)
        
    assembler = Assembler()
    try:
        assembler.assemble(sys.argv[1], sys.argv[2])
        print(f"Successfully assembled {sys.argv[1]} to {sys.argv[2]}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
