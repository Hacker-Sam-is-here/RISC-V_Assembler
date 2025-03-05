#!/usr/bin/env python3
import sys

class Assembler:
    def __init__(self):
        self.labels = {}
        self.aliases = {
            "zero": 0, "x0": 0, "ra": 1, "x1": 1, "sp": 2, "x2": 2, "gp": 3, "x3": 3, "tp": 4, "x4": 4,
            "t0": 5, "t1": 6, "t2": 7,
            "s0": 8, "fp": 8, "s1": 9,
            "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17,
            "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23, "s8": 24, "s9": 25,
            "s10": 26, "s11": 27, "t3": 28, "t4": 29, "t5": 30, "t6": 31
        }
        self.instructions = {
            'add': 0x33, 'sub': 0x33, 'slt': 0x33, 'sll': 0x33, 'srl': 0x33,
            'or': 0x33, 'and': 0x33, 'xor': 0x33,
            'lw': 0x03, 'sw': 0x23,
            'addi': 0x13, 'slti': 0x13, 'sltiu': 0x13,
            'slli': 0x13, 'srli': 0x13,
            'ori': 0x13, 'andi': 0x13, 'xori': 0x13,
            'jal': 0x6f, 'jalr': 0x67,
            'beq': 0x63, 'bne': 0x63, 'blt': 0x63, 'bge': 0x63, 'bltu': 0x63, 'bgeu': 0x63,
            'lui': 0x37, 'auipc': 0x17,
            'rst': 0, 'halt': 0
        }

    def sign_extend(self, value, bits):
        sign_bit = 1 << (bits - 1)
        value = value & ((1 << bits) - 1)  # Get only lower bits
        return (value & (sign_bit - 1)) - (value & sign_bit)

    def sign_extend_64(self, value, bits):
        # Special case for 64-bit values to handle Python's int
        if value & (1 << (bits - 1)):
            value |= -1 << bits
        return value

    def assemble(self, input_path, output_path):
        # First pass: collect labels
        addr = 0
        with open(input_path, 'r') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                if ':' in line:
                    label = line[:line.find(':')].strip()
                    self.labels[label] = addr
                    rest = line[line.find(':')+1:].strip()
                    if not rest:
                        continue
                    parts = rest.split()
                    if parts:
                        inst = parts[0].lower()
                        if inst in self.instructions:
                            addr += 4
                else:
                    parts = line.split()
                    if parts:
                        inst = parts[0].lower()
                        if inst in self.instructions:
                            addr += 4

        # Second pass: generate code
        codes = []
        addr = 0
        with open(input_path, 'r') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                if ':' in line:
                    rest = line[line.find(':')+1:].strip()
                    if not rest:
                        continue
                    parts = rest.split()
                    if not parts:
                        continue
                    inst = parts[0].lower()
                    operands = [op.strip() for op in " ".join(parts[1:]).split(",")] if len(parts) > 1 else []
                else:
                    parts = line.split()
                    inst = parts[0].lower()
                    operands = [op.strip() for op in " ".join(parts[1:]).split(",")] if len(parts) > 1 else []

                if not inst:
                    continue

                try:
                    if inst not in self.instructions:
                        raise ValueError(f"Unknown instruction: {inst}")

                    opcode = self.instructions[inst]

                    if inst in ['add', 'sub', 'slt', 'sll', 'srl', 'or', 'and', 'xor']:
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        rs1 = int(operands[1][1:]) if operands[1].startswith('x') else self.aliases[operands[1]]
                        rs2 = int(operands[2][1:]) if operands[2].startswith('x') else self.aliases[operands[2]]
                        funct3 = {'add':0x0, 'sub':0x0, 'slt':0x2, 'sll':0x1, 'srl':0x5, 'or':0x6, 'and':0x7, 'xor':0x4}[inst]
                        funct7 = 0x20 if inst == 'sub' else 0x00
                        code = ((funct7 & 0x7f) << 25) | ((rs2 & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1f) << 7) | (0x33)

                    elif inst in ['addi', 'slti', 'sltiu', 'ori', 'andi', 'xori']:
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        rs1 = int(operands[1][1:]) if operands[1].startswith('x') else self.aliases[operands[1]]
                        imm = int(operands[2])
                        if inst == 'sltiu':
                            # For SLTIU, treat immediate as unsigned
                            imm = imm & 0xFFF
                        else:
                            imm = self.sign_extend(imm, 12)
                        funct3 = {'addi':0x0, 'slti':0x2, 'sltiu':0x3, 'ori':0x6, 'andi':0x7, 'xori':0x4}[inst]
                        code = ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1f) << 7) | (0x13)

                    elif inst in ['slli', 'srli']:
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        rs1 = int(operands[1][1:]) if operands[1].startswith('x') else self.aliases[operands[1]]
                        imm = int(operands[2])
                        funct3 = {'slli':0x1, 'srli':0x5}[inst]
                        code = (0x00 << 25) | ((imm & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1f) << 7) | 0x13

                    elif inst in ['lw', 'sw']:
                        if inst == 'lw':
                            rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        else:
                            rs2 = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        offset_part = operands[1][:operands[1].find('(')].strip()
                        rs1_part = operands[1][operands[1].find('(')+1:operands[1].find(')')].strip()
                        try:
                            imm = self.labels[offset_part]
                        except KeyError:
                            imm = int(offset_part)
                        imm = self.sign_extend(imm, 12)
                        rs1 = int(rs1_part[1:]) if rs1_part.startswith('x') else self.aliases[rs1_part]
                        if inst == 'sw':
                            imm11_5 = (imm & 0xfe0) >> 5
                            imm4_0 = imm & 0x1f
                            code = (imm11_5 << 25) | ((rs2 & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | (0x2 << 12) | (imm4_0 << 7) | 0x23
                        else:
                            code = ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | (0x2 << 12) | ((rd & 0x1f) << 7) | 0x03

                    elif inst in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
                        rs1 = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        rs2 = int(operands[1][1:]) if operands[1].startswith('x') else self.aliases[operands[1]]
                        try:
                            imm = self.labels[operands[2]] - addr
                        except KeyError:
                            imm = int(operands[2])
                        imm = self.sign_extend(imm, 13)
                        
                        funct3 = {'beq':0x0, 'bne':0x1, 'blt':0x4, 'bge':0x5, 'bltu':0x6, 'bgeu':0x7}[inst]
                        
                        # Branch encoding: imm[12|10:5] rs2 rs1 funct3 imm[4:1|11] opcode
                        imm11 = (imm >> 11) & 0x1
                        imm4_1 = (imm >> 1) & 0xf
                        imm10_5 = (imm >> 5) & 0x3f
                        imm12 = (imm >> 12) & 0x1
                        code = (imm12 << 31) | (imm10_5 << 25) | ((rs2 & 0x1f) << 20) | ((rs1 & 0x1f) << 15) | ((funct3 & 0x7) << 12) | (imm4_1 << 8) | (imm11 << 7) | 0x63

                    elif inst == 'jal':
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        try:
                            imm = self.labels[operands[1]] - addr
                        except KeyError:
                            imm = int(operands[1])
                        imm = self.sign_extend(imm, 21)
                        
                        # JAL encoding: imm[20|10:1|11|19:12] rd opcode
                        imm20 = (imm >> 20) & 0x1
                        imm10_1 = (imm >> 1) & 0x3ff
                        imm11 = (imm >> 11) & 0x1
                        imm19_12 = (imm >> 12) & 0xff
                        code = (imm20 << 31) | (imm10_1 << 21) | (imm11 << 20) | (imm19_12 << 12) | ((rd & 0x1f) << 7) | 0x6f

                    elif inst == 'jalr':
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        rs1 = int(operands[1][1:]) if operands[1].startswith('x') else self.aliases[operands[1]]
                        imm = int(operands[2])
                        imm = self.sign_extend(imm, 12)
                        code = ((imm & 0xfff) << 20) | ((rs1 & 0x1f) << 15) | (0x0 << 12) | ((rd & 0x1f) << 7) | 0x67

                    elif inst == 'lui':
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        imm = self.sign_extend_64(int(operands[1]), 32) >> 12
                        code = ((imm & 0xfffff) << 12) | ((rd & 0x1f) << 7) | (0x37)

                    elif inst == 'auipc':
                        rd = int(operands[0][1:]) if operands[0].startswith('x') else self.aliases[operands[0]]
                        imm = self.sign_extend_64(int(operands[1]), 32) >> 12
                        code = ((imm & 0xfffff) << 12) | ((rd & 0x1f) << 7) | (0x17)

                    elif inst == 'rst':
                        code = 0x00000000

                    elif inst == 'halt':
                        code = 0x7fffffff

                    else:
                        raise ValueError(f"Unknown instruction: {inst}")

                    codes.append(code)
                    addr += 4

                except Exception as e:
                    raise ValueError(f"Error on line '{line}': {str(e)}")

        # Write output
        with open(output_path, 'w') as f:
            for code in codes:
                # Convert to binary string with leading zeros
                binary = f"{code:032b}\n"
                f.write(binary)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 assembler.py <input_file> <output_file>")
        sys.exit(1)
    
    asm = Assembler()
    asm.assemble(sys.argv[1], sys.argv[2])
