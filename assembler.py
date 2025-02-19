# Register mapping (ABI names to binary)
# Register map (ABI -> x0-x31) 
REG_MAP = {
    # Zero reg and call-related
    "x0": "00000", "zero": "00000",
    "ra": "00001",   # Return address (x1)
    
    # Stack & global pointers
    "sp": "00010",   # Stack pointer (x2)
    "gp": "00011",   # Global pointer (x3)
    
    # Thread/Temp regs
    "tp": "00100",   # Thread pointer (x4)
    "t0": "00101", "t1": "00110", "t2": "00111",  # x5-7
    
    # Saved regs
    "s0": "01000", "s1": "01001",  # x8-9
    
    # Function args
    "a0": "01010", "a1": "01011",   # x10-11
    "a2": "01100", "a3": "01101",   # x12-13
    "a4": "01110", "a5": "01111",   # x14-15
    "a6": "10000", "a7": "10001",   # x16-17
    
    # More saved
    "s2": "10010", "s3": "10011",   # x18-19
    "s4": "10100", "s5": "10101",   # x20-21
    "s6": "10110", "s7": "10111",   # x22-23
    "s8": "11000", "s9": "11001",   # x24-25
    "s10": "11010", "s11": "11011", # x26-27
    
    # Temp extras
    "t3": "11100", "t4": "11101",   # x28-29
    "t5": "11110", "t6": "11111"    # x30-31
}

# Opcodes and function codes
INSTRUCTIONS = {
    "add": {"type": "R", "funct7": "0000000", "funct3": "000", "opcode": "0110011"},
    "sub": {"type": "R", "funct7": "0100000", "funct3": "000", "opcode": "0110011"},
    "lw": {"type": "I", "funct3": "010", "opcode": "0000011"},
    "addi": {"type": "I", "funct3": "000", "opcode": "0010011"},
    "jalr": {"type": "I", "funct3": "000", "opcode": "1100111"},
    "sw": {"type": "S", "funct3": "010", "opcode": "0100011"},
    "beq": {"type": "B", "funct3": "000", "opcode": "1100011"},
    "bne": {"type": "B", "funct3": "001", "opcode": "1100011"},
    "jal": {"type": "J", "opcode": "1101111"},
}


def find_labels(code):
    """Scan code for labels and build address map"""
    labels = {}
    pc = 0  # Start at 0
    
    # First pass - find all labels
    for lin in code:
        if ':' in lin:
            lbl = lin.split(':')[0].strip()
            if lbl in labels:
                raise ValueError(f"Duplicate label {lbl}")
            labels[lbl] = pc
        else:
            pc += 4  # 4 bytes per instruction
            
    # Debug: show found labels
    print(f"Found {len(labels)} labels: {', '.join(labels.keys())}")
    
    return labels

def add_virtual_halt(assembly_code):
    """
    Add Virtual Halt instruction if missing.
    """
    if not assembly_code[-1].strip().startswith("beq zero, zero, 0x00000000"):
        assembly_code.append("beq zero, zero, 0x00000000")
    return assembly_code

def read_assembly_file(file_path):
    """
    Read assembly code from a file.
    """
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def write_binary_file(file_path, binary_code):
    """
    Write binary code to a file.
    """
    with open(file_path, "w") as file:
        for binary in binary_code:
            file.write(binary + "\n")

def assemble_instruction(asm_line, label_map, pc):
    """Convert assembly line to machine code"""
    # Skip comments/empty lines
    asm_line = asm_line.split('#')[0].strip()
    if not asm_line:
        return None
        
    # Split the instruction into parts
    parts = [part.strip() for part in asm_line.split()]
    if not parts:
        return None
        
    # Get opcode and instruction type
    opcode = parts[0].lower()
    if opcode not in INSTRUCTIONS:
        raise ValueError(f"Unknown instruction: {opcode}")
    
    instr_type = INSTRUCTIONS[opcode]["type"]
        
    # Validate minimum number of parts based on instruction type
    min_parts = {
        "R": 4,  # opcode, rd, rs1, rs2
        "I": 3,  # opcode, rd, offset(rs1) or opcode, rd, rs1, imm
        "S": 3,  # opcode, rs2, offset(rs1)
        "B": 4,  # opcode, rs1, rs2, imm/label
        "U": 3,  # opcode, rd, imm
        "J": 3   # opcode, rd, imm/label
    }
    
    if len(parts) < min_parts.get(instr_type, 3):
        raise ValueError(f"Insufficient operands for {opcode} instruction. Expected at least {min_parts.get(instr_type)} parts, got {len(parts)}")

    print(f"Processing: {asm_line}")  # Show current line

    # Continue with instruction type handling...
    if instr_type == "R":
        rd, rs1, rs2 = parts[1].strip(","), parts[2].strip(","), parts[3]
        # ...existing R-type handling...
        funct7 = INSTRUCTIONS[opcode]["funct7"]
        funct3 = INSTRUCTIONS[opcode]["funct3"]
        opcode = INSTRUCTIONS[opcode]["opcode"]

        # Convert registers to binary
        # Get register codes with fallback to zero
        rd_bin = REG_MAP.get(rd, "00000")  
        rs1_bin = REG_MAP.get(rs1, "00000")
        rs2_bin = REG_MAP.get(rs2, "00000")

        # Combine fields into 32-bit binary
        binary = f"{funct7}{rs2_bin}{rs1_bin}{funct3}{rd_bin}{opcode}"
        return binary

    elif instr_type == "I":
        # Load word uses a slightly different format
        if opcode == "lw":
            rd = parts[1].strip(",")
            offset_rs1 = parts[2]  # e.g. 12(sp)
            offset, rs1 = offset_rs1.split("(")
            rs1 = rs1.strip(")")
            imm = offset
        else:
            rd, rs1, imm = parts[1].strip(","), parts[2].strip(","), parts[3]

        funct3 = INSTRUCTIONS[opcode]["funct3"]
        opcode_bin = INSTRUCTIONS[opcode]["opcode"]

        # Registers to binary
        rd_bin = REG_MAP.get(rd, "00000")
        rs1_bin = REG_MAP.get(rs1, "00000")

        # Immediates (offset or direct value)
        if imm in label_map:
            offset = label_map[imm] - pc
            imm_int = offset
        else:
            # Handle hex/dec numbers
            if imm.startswith('0x'):
                imm_int = int(imm, 16)
            else:
                imm_int = int(imm)
        if imm_int < -2048 or imm_int > 2047:
            raise ValueError(f"Immediate {imm_int} out of bounds for I-type instruction")
        imm_bin = format(imm_int & 0xFFF, "012b")  # 12-bit signed

        # Final binary I-type
        binary = f"{imm_bin}{rs1_bin}{funct3}{rd_bin}{opcode_bin}"
        return binary

    elif instr_type == "S":
        rs2, offset_rs1 = parts[1].strip(","), parts[2]
        offset, rs1 = offset_rs1.split("(")
        rs1 = rs1.strip(")")

        # Convert registers to binary
        rs2_bin = REG_MAP.get(rs2, "00000")
        rs1_bin = REG_MAP.get(rs1, "00000")

        # Convert immediate to 12-bit binary
        # Handle hex numbers (0x...) and decimal numbers
        if offset.startswith('0x'):
            imm_int = int(offset, 16)
        else:
            imm_int = int(offset)
        if imm_int < -2048 or imm_int > 2047:
            raise ValueError(f"Immediate {imm_int} out of bounds for S-type instruction")
        imm_bin = format(imm_int & 0xFFF, "012b")  # 12-bit signed immediate

        # Split immediate into imm[11:5] and imm[4:0]
        imm_11_5 = imm_bin[:7]
        imm_4_0 = imm_bin[7:]

        # Combine fields into 32-bit binary
        funct3 = INSTRUCTIONS[opcode]["funct3"]
        opcode_bin = INSTRUCTIONS[opcode]["opcode"]
        binary = f"{imm_11_5}{rs2_bin}{rs1_bin}{funct3}{imm_4_0}{opcode_bin}"
        return binary

    elif instr_type == "B":
        rs1, rs2, imm = parts[1].strip(","), parts[2].strip(","), parts[3]

        # Convert registers to binary
        rs1_bin = REG_MAP.get(rs1, "00000")
        rs2_bin = REG_MAP.get(rs2, "00000")

        # Calculate offset for labels
        if imm in label_map:
            offset = label_map[imm] - pc
            imm_int = offset
        else:
            # Handle hex numbers (0x...) and decimal numbers
            if imm.startswith('0x'):
                imm_int = int(imm, 16)
            else:
                imm_int = int(imm)
        if imm_int < -4096 or imm_int > 4095:
            raise ValueError(f"Immediate {imm_int} out of bounds for B-type instruction")
        imm_bin = format((imm_int >> 1) & 0xFFF, "012b")  # 12-bit signed immediate (LSB=0)

        # Split immediate into imm[12], imm[10:5], imm[4:1], imm[11]
        imm_12 = imm_bin[0]
        imm_10_5 = imm_bin[2:8]
        imm_4_1 = imm_bin[8:12]
        imm_11 = imm_bin[1]

        # Combine fields into 32-bit binary
        funct3 = INSTRUCTIONS[opcode]["funct3"]
        opcode_bin = INSTRUCTIONS[opcode]["opcode"]
        binary = f"{imm_12}{imm_10_5}{rs2_bin}{rs1_bin}{funct3}{imm_4_1}{imm_11}{opcode_bin}"
        return binary
#J-Type Instruction Added By Naman Goyal 2024367
    elif instr_type == "J":
        rd, imm = parts[1].strip(","), parts[2]

        # Convert register to binary
        rd_bin = REG_MAP.get(rd, "00000")

        # Calculate offset for labels
        if imm in label_map:
            offset = label_map[imm] - pc
            imm_int = offset
        else:
            # Handle hex numbers (0x...) and decimal numbers
            if imm.startswith('0x'):
                imm_int = int(imm, 16)
            else:
                imm_int = int(imm)
        if imm_int < -1048576 or imm_int > 1048575:
            raise ValueError(f"Immediate {imm_int} out of bounds for J-type instruction")
        imm_bin = format((imm_int >> 1) & 0xFFFFF, "020b")  # 20-bit signed immediate (LSB=0)

        # Split immediate into imm[20], imm[10:1], imm[11], imm[19:12]
        imm_20 = imm_bin[0]        # bit 20
        imm_19_12 = imm_bin[1:9]   # bits 19:12
        imm_11 = imm_bin[9]        # bit 11
        imm_10_1 = imm_bin[10:20]  # bits 10:1

        # Combine fields into 32-bit binary in correct order:
        # imm[20] | imm[10:1] | imm[11] | imm[19:12] | rd | opcode
        opcode_bin = INSTRUCTIONS[opcode]["opcode"]
        binary = f"{imm_20}{imm_10_1}{imm_11}{imm_19_12}{rd_bin}{opcode_bin}"
        return binary

    else:
        raise ValueError(f"Unsupported instruction type: {instr_type}")

def assemble(assembly_code):
    """
    Assemble RISC-V assembly code into binary.
    """
    # Find and map labels
    labels = find_labels(assembly_code)

    # Add Virtual Halt if missing
    assembly_code = add_virtual_halt(assembly_code)

    binary_code = []
    address = 0  # Program counter (PC)
    for line in assembly_code:
        if ":" in line:
            # Skip label definition lines
            continue

        parts = line.split()
        if not parts:
            continue  # Skip empty lines

        opcode = parts[0]

        if opcode in INSTRUCTIONS:
            binary = assemble_instruction(line, labels, address)
            if binary:
                binary_code.append(binary)
            address += 4  # Increment PC
        else:
            raise ValueError(f"Unknown instruction: {opcode}")

    return binary_code

if __name__ == "__main__":
    """Main CLI for assembler"""
    import sys, os
    
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(__file__)} input.asm")
        print("Example: assembler.py demo.asm")
        sys.exit(1)

    input_file = sys.argv[1]
    assembly_code = read_assembly_file(input_file)
    binary_code = assemble(assembly_code)
    write_binary_file("output.bin", binary_code)
    print("Assembled binary written to output.bin")
