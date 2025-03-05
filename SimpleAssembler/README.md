# RISC-V Assembler Implementation

This document explains the design and implementation details of the RISC-V assembler.

## Overview

The assembler converts RISC-V assembly code into machine code through a two-pass process. It features:
- Support for all basic RV32I instructions
- Label resolution for jumps and branches
- Robust error handling with line numbers
- Register alias support (x0-x31 and ABI names)

## Code Structure

### Constants and Types

```python
# Register mappings
REGISTER_ALIASES = {
    "zero": 0, "x0": 0,    # Zero register
    "ra": 1, "x1": 1,      # Return address
    "sp": 2, "x2": 2,      # Stack pointer
    ...
}

# Instruction definitions
INSTRUCTION_DETAILS = {
    # R-type arithmetic
    'add':  (0x33, 'R'), 'sub':  (0x33, 'R'),
    # I-type loads and immediates
    'lw':   (0x03, 'I'), 'addi': (0x13, 'I'),
    # S-type stores
    'sw':   (0x23, 'S'),
    ...
}
```

### Classes

#### Instruction Class
```python
@dataclass
class Instruction:
    name: str          # Instruction name (e.g., "add")
    operands: List[str]# List of operands
    line_num: int      # Source line number
    label: str = ''    # Optional label
```

#### AssemblyError Class
```python
class AssemblyError:
    """Custom exception with line number tracking"""
    def __init__(self, message: str, line_num: int)
```

#### Assembler Class
```python
class Assembler:
    """Main assembler implementation"""
    def __init__(self)
    def assemble(self, input_path: str, output_path: str) -> None
```

## Assembly Process

### First Pass
1. Reads source file line by line
2. Collects and validates labels
3. Builds symbol table with label addresses
4. Validates basic instruction syntax

### Second Pass
1. Processes each instruction
2. Resolves labels to addresses
3. Encodes instructions based on type
4. Generates binary output

## Instruction Encoding

### R-Type Instructions
- Format: `op rd, rs1, rs2`
- Examples: add, sub, slt, and, or, xor
- Encoding: `funct7[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]`

### I-Type Instructions
- Format: `op rd, rs1, imm`
- Examples: lw, addi, jalr
- Encoding: `imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]`

### S-Type Instructions
- Format: `op rs2, offset(rs1)`
- Example: sw
- Encoding: `imm[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:7] | opcode[6:0]`

### B-Type Instructions
- Format: `op rs1, rs2, label`
- Examples: beq, bne, blt
- Encoding: `imm[31] | imm[30:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:8] | imm[7] | opcode[6:0]`

### J-Type Instructions
- Format: `op rd, label`
- Example: jal
- Encoding: `imm[31] | imm[30:21] | imm[20] | imm[19:12] | rd[11:7] | opcode[6:0]`

## Error Handling

The assembler provides detailed error messages including:
- Invalid instruction formats
- Unknown instructions
- Invalid register names
- Invalid immediate values
- Duplicate labels
- Memory access violations

## Usage Example

```asm
# Example assembly program
main:
    addi x1, x0, 5    # Load immediate value 5
    addi x2, x0, 3    # Load immediate value 3
    add  x3, x1, x2   # Add values
    sw   x3, 0(x0)    # Store result
    halt              # Stop execution
```

```bash
# Command line usage
python assembler.py input.asm output.bin
