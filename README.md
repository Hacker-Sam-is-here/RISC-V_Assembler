# RISC-V Assembler Code Explanation

This document provides a detailed explanation of each line of code in the `assembler.py` file.

## Register Mapping

```python
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
```

This section defines a dictionary `REG_MAP` that maps RISC-V register names (both ABI names like "ra", "sp", "a0" and their numerical counterparts like "x0", "x1") to their 5-bit binary representations. This mapping is used during the assembly process to convert register names used in the assembly code into their binary equivalents for machine code.

## Instruction Opcodes

```python
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
```

This section defines a dictionary `INSTRUCTIONS` that maps RISC-V instruction names (like "add", "sub", "lw") to their corresponding instruction formats and binary codes. Each instruction entry includes:

- `"type"`: The instruction type (R, I, S, B, J), which determines the instruction format.

- `"funct7"`: The 7-bit function code (for R-type instructions).

- `"funct3"`: The 3-bit function code.

- `"opcode"`: The 7-bit opcode.

These binary codes are used during the assembly process to construct the final machine code for each instruction.

## `find_labels(code)` Function

```python
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
```

This function takes a list of assembly code lines as input and returns a dictionary mapping labels to their corresponding memory addresses.

- `labels = {}`: Initializes an empty dictionary to store the labels and their addresses.

- `pc = 0`: Initializes the program counter `pc` to 0, representing the starting address.

- The code iterates through each line `lin` in the input `code`.

    - `if ':' in lin`: Checks if the line contains a label (indicated by a colon).

        - `lbl = lin.split(':')[0].strip()`: Extracts the label from the line by splitting the line at the colon and taking the first part, then removes any leading/trailing whitespace.

        - `if lbl in labels`: Checks if the label already exists in the `labels` dictionary. If it does, it raises a ValueError to indicate a duplicate label.

        - `labels[lbl] = pc`: Adds the label to the `labels` dictionary with the current program counter `pc` as its address.

    - `else`: If the line does not contain a label, it's assumed to be an instruction.

        - `pc += 4`: Increments the program counter by 4 bytes (the size of a RISC-V instruction).

- `print(f"Found {len(labels)} labels: {', '.join(labels.keys())}")`: Prints the labels that were found.

- `return labels`: Returns the `labels` dictionary.

## `add_virtual_halt(assembly_code)` Function

```python
def add_virtual_halt(assembly_code):
    """
    Add Virtual Halt instruction if missing.
    """
    if not assembly_code[-1].strip().startswith("beq zero, zero, 0x00000000"):
        assembly_code.append("beq zero, zero, 0x00000000")
    return assembly_code
```

This function takes a list of assembly code lines as input and adds a virtual halt instruction (`beq zero, zero, 0x00000000`) to the end of the code if it's not already present. This ensures that the program execution terminates properly.

- `if not assembly_code[-1].strip().startswith("beq zero, zero, 0x00000000")`: Checks if the last line of the assembly code, after removing leading/trailing whitespace, starts with the virtual halt instruction.

- `assembly_code.append("beq zero, zero, 0x00000000")`: If the last line is not the halt instruction, it appends the halt instruction to the end of the assembly code.

- `return assembly_code`: Returns the modified assembly code.

## `read_assembly_file(file_path)` Function

```python
def read_assembly_file(file_path):
    """
    Read assembly code from a file.
    """
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]
```

This function reads the assembly code from a file specified by `file_path`.

- `with open(file_path, "r") as file`: Opens the file in read mode (`"r"`) using a `with` statement, which ensures that the file is properly closed after it's used.

- `return [line.strip() for line in file if line.strip()]`: Reads each line from the file, removes any leading/trailing whitespace using `line.strip()`, and returns a list of these cleaned-up lines. It also skips empty lines.

## `write_binary_file(file_path, binary_code)` Function

```python
def write_binary_file(file_path):
    """
    Write binary code to a file.
    """
    with open(file_path, "w") as file:
        for binary in binary_code:
            file.write(binary + "\n")
```

This function writes the assembled binary code to a file specified by `file_path`.

- `with open(file_path, "w") as file`: Opens the file in write mode (`"w"`) using a `with` statement, which ensures that the file is properly closed after it's used.

- The code iterates through each binary instruction `binary` in the input `binary_code`.

    - `file.write(binary + "\n")`: Writes the binary instruction to the file, followed by a newline character to separate each instruction.

## `assemble_instruction(asm_line, label_map, pc)` Function

```python
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
            imm_int = int(imm)
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
            # Handle hex/dec numbers
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

    elif instr_type == "J":
        rd, imm = parts[1].strip(","), parts[2]

        # Convert register to binary
        rd_bin = REG_MAP.get(rd, "00000")

        # Calculate offset for labels
        if imm in label_map:
            offset = label_map[imm] - pc
            imm_int = offset
        else:
            # Handle hex/dec numbers
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
```

This function is the core of the assembler. It takes a single line of assembly code (`asm_line`), the `label_map` (mapping labels to addresses), and the current program counter (`pc`) as input. It converts the assembly line into its corresponding 32-bit machine code representation.

- `asm_line = asm_line.split('#')[0].strip()`: Removes any comments from the line (indicated by `#`) and any leading/trailing whitespace.

- `if not asm_line`: Checks if the line is empty after removing comments and whitespace. If it is, it returns `None`.

- `parts = [part.strip() for part in asm_line.split()]`: Splits the line into individual parts (opcode and operands) and removes any leading/trailing whitespace from each part.

- `if not parts`: Checks if the line has any parts after splitting. If not, it returns `None`.

- `opcode = parts[0].lower()`: Extracts the opcode (instruction name) from the first part and converts it to lowercase.

- `if opcode not in INSTRUCTIONS`: Checks if the opcode is a valid instruction by looking it up in the `INSTRUCTIONS` dictionary. If it's not a valid instruction, it raises a `ValueError`.

- `instr_type = INSTRUCTIONS[opcode]["type"]`: Retrieves the instruction type (R, I, S, B, or J) from the `INSTRUCTIONS` dictionary.

The code then uses a series of `if/elif/else` statements to handle each instruction type differently. Each block extracts the necessary operands, converts them to their binary representations, and combines them according to the RISC-V instruction format.

- **R-type Instructions**:

    - Extracts the destination register (`rd`), source registers (`rs1`, `rs2`).

    - Retrieves the function codes (`funct7`, `funct3`) and opcode from the `INSTRUCTIONS` dictionary.

    - Converts the register names to their binary representations using the `REG_MAP` dictionary.

    - Combines the fields into a 32-bit binary string.

- **I-type Instructions**:

    - Handles `lw` (load word) instructions separately due to their different operand format.

    - Extracts the destination register (`rd`), source register (`rs1`), and immediate value (`imm`).

    - Retrieves the function code (`funct3`) and opcode from the `INSTRUCTIONS` dictionary.

    - Converts the register names to their binary representations using the `REG_MAP` dictionary.

    - Converts the immediate value to a 12-bit binary string, handling both decimal and hexadecimal numbers.

    - Combines the fields into a 32-bit binary string.

- **S-type Instructions**:

    - Extracts the source register (`rs2`), base register (`rs1`), and immediate offset (`offset`).

    - Retrieves the function code (`funct3`) and opcode from the `INSTRUCTIONS` dictionary.

    - Converts the register names to their binary representations using the `REG_MAP` dictionary.

    - Converts the immediate offset to a 12-bit binary string, handling both decimal and hexadecimal numbers.

    - Splits the immediate into two parts (`imm[11:5]` and `imm[4:0]`) as required by the S-type format.

    - Combines the fields into a 32-bit binary string.

- **B-type Instructions**:

    - Extracts the source registers (`rs1`, `rs2`), and immediate offset/label (`imm`).

    - Retrieves the function code (`funct3`) and opcode from the `INSTRUCTIONS` dictionary.

    - Converts the register names to their binary representations using the `REG_MAP` dictionary.

    - Calculates the branch offset based on the label (if `imm` is a label) or converts the immediate to an integer.

    - Converts the immediate to a 12-bit binary string.

    - Splits the immediate into parts (`imm[12]`, `imm[10:5]`, `imm[4:1]`, `imm[11]`) as required by the B-type format.

    - Combines the fields into a 32-bit binary string.

- **J-type Instructions**:

    - Extracts the destination register (`rd`) and immediate offset/label (`imm`).

    - Retrieves the opcode from the `INSTRUCTIONS` dictionary.

    - Converts the register name to its binary representation using the `REG_MAP` dictionary.

    - Calculates the jump offset based on the label (if `imm` is a label) or converts the immediate to an integer.

    - Converts the immediate to a 20-bit binary string.

    - Splits the immediate into parts (`imm[20]`, `imm[10:1]`, `imm[11]`, `imm[19:12]`) as required by the J-type format.

    - Combines the fields into a 32-bit binary string.

- `else`: If the instruction type is not supported, it raises a `ValueError`.

## `assemble(assembly_code)` Function

```python
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
```

This function takes a list of assembly code lines as input and converts it into a list of 32-bit binary instructions.

- `labels = find_labels(assembly_code)`: Calls the `find_labels` function to identify all labels in the assembly code and store their addresses in the `labels` dictionary.

- `assembly_code = add_virtual_halt(assembly_code)`: Calls the `add_virtual_halt` function to add a virtual halt instruction to the end of the assembly code if it's not already present.

- `binary_code = []`: Initializes an empty list to store the generated binary instructions.

- `address = 0`: Initializes the program counter `address` to 0.

- The code iterates through each line `line` in the input `assembly_code`.

    - `if ":" in line`: Checks if the line contains a label (indicated by a colon). If it does, it skips the line because labels are already processed.

    - `parts = line.split()`: Splits the line into parts.

    - `if not parts`: Skips empty lines.

    - `opcode = parts[0]`: Gets the opcode.

    - `if opcode in INSTRUCTIONS`: Checks if the opcode is a valid instruction by looking it up in the `INSTRUCTIONS` dictionary.

        - `binary = assemble_instruction(line, labels, address)`: Calls the `assemble_instruction` function to convert the assembly line into its binary representation.

        - `if binary`: Checks if the `assemble_instruction` function returned a binary instruction (it might return `None` for comments or empty lines).

            - `binary_code.append(binary)`: Appends the binary instruction to the `binary_code` list.

        - `address += 4`: Increments the program counter by 4 bytes.

    - `else`: If the opcode is not a valid instruction, it raises a `ValueError`.

- `return binary_code`: Returns the list of binary instructions.

## Main Execution Block

```python
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
```

This block of code is executed when the `assembler.py` file is run as a script.

- `if __name__ == "__main__":`: Checks if the script is being run directly (not imported as a module).

- `import sys, os`: Imports the `sys` and `os` modules, which provide access to system-specific parameters and functions.

- `if len(sys.argv) != 2`: Checks if the correct number of command-line arguments is provided. The script expects one argument: the path to the input assembly file.

    - `print(f"Usage: {os.path.basename(__file__)} input.asm")`: Prints the usage instructions to the console.

    - `print("Example: assembler.py demo.asm")`: Prints an example of how to use the script.

    - `sys.exit(1)`: Exits the script with an error code of 1.

- `input_file = sys.argv[1]`: Retrieves the path to the input assembly file from the command-line arguments.

- `assembly_code = read_assembly_file(input_file)`: Calls the `read_assembly_file` function to read the assembly code from the specified file.

- `binary_code = assemble(assembly_code)`: Calls the `assemble` function to convert the assembly code into binary code.

- `write_binary_file("output.bin", binary_code)`: Calls the `write_binary_file` function to write the binary code to a file named "output.bin".

- `print("Assembled binary written to output.bin")`: Prints a message to the console indicating that the assembly process is complete and the binary code has been written to the output file.
