#!/usr/bin/env python3
"""
Custom RISC-V Assembler

This is my implementation of a RISC-V assembler for the Computer Organization course.
Had some trouble with negative immediates initially but fixed it. The hardest part
was getting the branch offsets right!

Usage: Just run with input and output files as arguments:
python assembler.py input.asm output.txt
"""
import sys

class Assembler:
    def __init__(self):
        # Maps both x0-x31 and standard RISC-V names to numbers
        # Was super helpful for debugging when I mixed up register names!
        self.reg_map = {
            # Zero reg - always good to have at the top
            "zero": 0, "x0": 0,
            
            # Return address - took me a while to realize I needed this
            "ra": 1, "x1": 1,
            
            # Stack and globals
            "sp": 2, "x2": 2,
            "gp": 3, "x3": 3,
            "tp": 4, "x4": 4,
            
            # Temporary registers - use these a lot
            "t0": 5, "t1": 6, "t2": 7,
            
            # Saved registers (super useful for functions)
            "s0": 8, "fp": 8, "s1": 9,
            
            # These made testing way easier
            "a0": 10, "a1": 11, "a2": 12, "a3": 13,
            "a4": 14, "a5": 15, "a6": 16, "a7": 17,
            
            # More saved regs - needed all of these!
            "s2": 18, "s3": 19, "s4": 20, "s5": 21,
            "s6": 22, "s7": 23, "s8": 24, "s9": 25,
            "s10": 26, "s11": 27,
            
            # Extra temporaries
            "t3": 28, "t4": 29, "t5": 30, "t6": 31
        }
        
        # Keep track of where labels point to
        self.label_addresses = {}

    def fix_negative(self, num, bits):
        """
        Handles negative numbers in binary. This was tricky to get right!
        Spent way too long debugging why -5 wasn't working...
        """
        if num < 0:
            num = (1 << bits) + num
        return num & ((1 << bits) - 1)

    def get_reg_num(self, reg_name):
        """
        Gets the register number - handles both x0 style and regular names.
        Added this helper because I kept repeating the logic everywhere.
        """
        if reg_name.startswith('x'):
            return int(reg_name[1:])
        return self.reg_map.get(reg_name)

    def parse_instruction(self, line):
        # First strip out comments and whitespace
        line = line.split('#')[0].strip()
        if not line:
            return None, None
            
        # Check if this line has a label
        label = None
        if ':' in line:
            label, line = line.split(':')
            label = label.strip()
            line = line.strip()
            
        # Empty line after label
        if not line:
            return label, None
            
        # Get instruction and operands    
        parts = line.split()
        instr = parts[0].lower()  # convert to lowercase to handle stuff like ADD vs add
        
        # Parse out the operands, handling cases like "add x1, x2, x3"
        operands = []
        if len(parts) > 1:
            operands = [op.strip() for op in ' '.join(parts[1:]).split(',')]
            
        return label, (instr, operands)

    def parse_mem_operand(self, mem_str):
        """
        Parses memory operands like: 8(t0) or label(s1)
        The format gave me headaches until I drew it out on paper
        """
        if '(' not in mem_str or ')' not in mem_str:
            raise ValueError("Memory operand format should be: offset(reg)")
            
        # Split into offset and register parts
        offset = mem_str[:mem_str.find('(')].strip()
        reg = mem_str[mem_str.find('(')+1:mem_str.find(')')].strip()
        
        # Convert offset - could be a label or number
        try:
            if offset in self.label_addresses:
                offset_val = self.label_addresses[offset]
            else:
                offset_val = int(offset)
        except ValueError:
            raise ValueError(f"Bad offset value: {offset}")
            
        # Get the register number
        reg_num = self.get_reg_num(reg)
        if reg_num is None:
            raise ValueError(f"Unknown register: {reg}")
                
        return offset_val, reg_num

    def make_r_type(self, op, rd, rs1, rs2):
        """Helper for R-type instructions (the regular ones)"""
        f3_map = {
            'add': 0, 'sub': 0,  # Shared funct3, different funct7
            'sll': 1, 'slt': 2,
            'srl': 5, 'or': 6,
            'and': 7, 'xor': 4
        }
        
        # sub is special - needs different funct7
        funct7 = 0x20 if op == 'sub' else 0
        funct3 = f3_map[op]
        
        return f"{funct7:07b}{rs2:05b}{rs1:05b}{funct3:03b}{rd:05b}0110011"

    def make_i_type(self, op, rd, rs1, imm):
        """
        I-type instructions were annoying because of all the different immediate formats.
        Finally wrapped them all in one helper.
        """
        f3_map = {
            'addi': 0, 'slti': 2,
            'sltiu': 3, 'xori': 4,
            'ori': 6, 'andi': 7,
            'slli': 1, 'srli': 5
        }
        
        # Shifts are special - only use bottom 5 bits
        if op in ['slli', 'srli']:
            imm &= 0x1F
        else:
            imm = self.fix_negative(imm, 12)
        
        return f"{imm:012b}{rs1:05b}{f3_map[op]:03b}{rd:05b}0010011"

    def assemble(self, input_file, output_file):
        # First pass - collect all the label addresses
        cur_addr = 0
        with open(input_file) as f:
            for line in f:
                label, instr = self.parse_instruction(line)
                if label:
                    if label in self.label_addresses:
                        print(f"Error: Duplicate label '{label}'")
                        return False
                    self.label_addresses[label] = cur_addr
                if instr:
                    cur_addr += 4  # Instructions are 4 bytes each

        # Second pass - generate machine code
        machine_code = []
        cur_addr = 0
        
        with open(input_file) as f:
            for line in f:
                _, instr = self.parse_instruction(line)
                if not instr:
                    continue
                    
                op, args = instr
                try:
                    # Regular R-type arithmetic 
                    if op in ['add', 'sub', 'sll', 'slt', 'srl', 'and', 'or', 'xor']:
                        if len(args) != 3:
                            raise ValueError(f"{op} needs 3 registers")
                        rd = self.get_reg_num(args[0])
                        rs1 = self.get_reg_num(args[1])
                        rs2 = self.get_reg_num(args[2])
                        code = self.make_r_type(op, rd, rs1, rs2)

                    # I-type arithmetic and logic
                    elif op in ['addi', 'slti', 'sltiu', 'xori', 'ori', 'andi', 'slli', 'srli']:
                        if len(args) != 3:
                            raise ValueError(f"{op} needs reg, reg, imm")
                        rd = self.get_reg_num(args[0])
                        rs1 = self.get_reg_num(args[1])
                        imm = int(args[2])
                        code = self.make_i_type(op, rd, rs1, imm)

                    # Load instructions 
                    elif op == 'lw':
                        if len(args) != 2:
                            raise ValueError("lw needs dest and mem location")
                        rd = self.get_reg_num(args[0])
                        offset, rs1 = self.parse_mem_operand(args[1])
                        offset = self.fix_negative(offset, 12)
                        code = f"{offset:012b}{rs1:05b}010{rd:05b}0000011"

                    # Store instructions
                    elif op == 'sw':
                        if len(args) != 2:
                            raise ValueError("sw needs source and mem location")
                        rs2 = self.get_reg_num(args[0])
                        offset, rs1 = self.parse_mem_operand(args[1])
                        offset = self.fix_negative(offset, 12)
                        imm11_5 = (offset >> 5) & 0x7F
                        imm4_0 = offset & 0x1F
                        code = f"{imm11_5:07b}{rs2:05b}{rs1:05b}010{imm4_0:05b}0100011"

                    # Branches - the worst ones to encode!
                    elif op in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
                        if len(args) != 3:
                            raise ValueError(f"{op} needs two regs and target")
                        rs1 = self.get_reg_num(args[0])
                        rs2 = self.get_reg_num(args[1])
                        
                        # Calculate branch offset
                        if args[2] in self.label_addresses:
                            offset = self.label_addresses[args[2]] - cur_addr
                        else:
                            offset = int(args[2])
                            
                        offset = self.fix_negative(offset, 13)
                        
                        f3_map = {
                            'beq': 0, 'bne': 1,
                            'blt': 4, 'bge': 5,
                            'bltu': 6, 'bgeu': 7
                        }
                        
                        # This bit ordering is crazy but it works!
                        imm12 = (offset >> 12) & 1
                        imm11 = (offset >> 11) & 1
                        imm10_5 = (offset >> 5) & 0x3F
                        imm4_1 = (offset >> 1) & 0xF
                        
                        code = f"{imm12}{imm10_5:06b}{rs2:05b}{rs1:05b}{f3_map[op]:03b}{imm4_1:04b}{imm11}1100011"

                    # Jump instructions
                    elif op == 'jal':
                        if len(args) != 2:
                            raise ValueError("jal needs dest reg and target")
                        rd = self.get_reg_num(args[0])
                        
                        if args[1] in self.label_addresses:
                            offset = self.label_addresses[args[1]] - cur_addr
                        else:
                            offset = int(args[1])
                            
                        offset = self.fix_negative(offset, 21)
                        
                        # More crazy bit ordering
                        imm20 = (offset >> 20) & 1
                        imm10_1 = (offset >> 1) & 0x3FF
                        imm11 = (offset >> 11) & 1
                        imm19_12 = (offset >> 12) & 0xFF
                        
                        code = f"{imm20}{imm10_1:010b}{imm11}{imm19_12:08b}{rd:05b}1101111"

                    elif op == 'jalr':
                        if len(args) != 3:
                            raise ValueError("jalr needs rd, rs1, offset")
                        rd = self.get_reg_num(args[0])
                        rs1 = self.get_reg_num(args[1])
                        offset = int(args[2])
                        offset = self.fix_negative(offset, 12)
                        code = f"{offset:012b}{rs1:05b}000{rd:05b}1100111"

                    # Upper immediates
                    elif op in ['lui', 'auipc']:
                        if len(args) != 2:
                            raise ValueError(f"{op} needs dest reg and imm")
                        rd = self.get_reg_num(args[0])
                        imm = int(args[1])
                        
                        # Handle negative immediates properly
                        if imm < 0:
                            imm = ((abs(imm) >> 12) ^ 0xFFFFF) + 1
                        else:
                            imm = (imm >> 12) & 0xFFFFF
                        
                        opcode = '0110111' if op == 'lui' else '0010111'
                        code = f"{imm:020b}{rd:05b}{opcode}"

                    # Special instructions
                    elif op == 'rst':
                        code = "0" * 32  # All zeros
                    elif op == 'halt':
                        code = "1" * 32  # All ones
                    else:
                        raise ValueError(f"Unknown instruction: {op}")

                    machine_code.append(code)
                    cur_addr += 4

                except Exception as e:
                    print(f"Error on line '{line.strip()}': {str(e)}")
                    return False

        # Write the binary to output file
        with open(output_file, 'w') as f:
            for code in machine_code:
                f.write(code + '\n')
                
        return True

def main():
    asm = Assembler()
    print(f"Assembling {sys.argv[1]}...")
    if asm.assemble(sys.argv[1], sys.argv[2]):
        print(f"Successfully assembled to {sys.argv[2]}")
    else:
        print("Assembly failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
