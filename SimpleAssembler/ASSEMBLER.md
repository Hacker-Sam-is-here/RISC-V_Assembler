# RISC-V Assembler Implementation

This document explains the line-by-line implementation of the RISC-V assembler.

## Class Overview

```python
class Assembler:
```
The main class that handles the conversion of RISC-V assembly code to machine code.

## Class Initialization

```python
def __init__(self):
```

### Register Aliases
```python
self.aliases = {
    "zero": 0, "x0": 0, "ra": 1, "x1": 1, "sp": 2, "x2": 2, ...
}
```
- Maps register names to their numeric values
- Supports both ABI names (e.g., "ra", "sp") and numeric names (e.g., "x0", "x1")
- Important registers:
  - x0/zero: Hardwired zero
  - ra: Return address
  - sp: Stack pointer
  - etc.

### Instruction Opcodes
```python
self.instructions = {
    'add': 0x33, 'sub': 0x33, 'slt': 0x33, ...
}
```
- Maps instruction names to their base opcodes
- Instructions are grouped by type:
  - R-type (register): add, sub, slt, etc.
  - I-type (immediate): lw, addi, etc.
  - S-type (store): sw
  - B-type (branch): beq, bne, etc.
  - U-type (upper immediate): lui, auipc
  - J-type (jump): jal, jalr

## Helper Methods

### Sign Extension
```python
def sign_extend(self, value, bits):
```
- Handles sign extension for immediate values
- Parameters:
  - value: The number to sign extend
  - bits: Number of bits in the original value
- Returns sign-extended value

```python
def sign_extend_64(self, value, bits):
```
- Special case for 64-bit values
- Handles Python's integer implementation
- Used for lui/auipc instructions

## Main Assembly Process

### The Assemble Method
```python
def assemble(self, input_path, output_path):
```
Performs two-pass assembly:

#### First Pass
- Collects all labels and their addresses
- Calculates the address of each instruction
- Handles both labeled and non-labeled lines
- Skips empty lines and comments

#### Second Pass
Generates machine code for each instruction:

1. **R-type Instructions**
   ```python
   if inst in ['add', 'sub', 'slt', 'sll', 'srl', 'or', 'and', 'xor']:
   ```
   - Format: `inst rd, rs1, rs2`
   - Fields: funct7|rs2|rs1|funct3|rd|opcode

2. **I-type Instructions**
   ```python
   elif inst in ['addi', 'slti', 'sltiu', 'ori', 'andi', 'xori']:
   ```
   - Format: `inst rd, rs1, imm`
   - Fields: imm[11:0]|rs1|funct3|rd|opcode

3. **Load Instructions**
   ```python
   elif inst in ['lw']:
   ```
   - Format: `lw rd, offset(rs1)`
   - Fields: imm[11:0]|rs1|funct3|rd|opcode

4. **Store Instructions**
   ```python
   elif inst == 'sw':
   ```
   - Format: `sw rs2, offset(rs1)`
   - Fields: imm[11:5]|rs2|rs1|funct3|imm[4:0]|opcode

5. **Branch Instructions**
   ```python
   elif inst in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
   ```
   - Format: `inst rs1, rs2, label/offset`
   - Fields: imm[12|10:5]|rs2|rs1|funct3|imm[4:1|11]|opcode

6. **Jump Instructions**
   ```python
   elif inst in ['jal', 'jalr']:
   ```
   - JAL Format: `jal rd, label/offset`
   - JALR Format: `jalr rd, rs1, imm`
   - Fields (JAL): imm[20|10:1|11|19:12]|rd|opcode
   - Fields (JALR): imm[11:0]|rs1|funct3|rd|opcode

7. **Upper Immediate Instructions**
   ```python
   elif inst in ['lui', 'auipc']:
   ```
   - Format: `inst rd, imm`
   - Fields: imm[31:12]|rd|opcode

### Output Generation
```python
with open(output_path, 'w') as f:
    for code in codes:
        binary = f"{code:032b}\n"
        f.write(binary)
```
- Converts each instruction to 32-bit binary
- Writes one instruction per line
- Uses zero padding to ensure 32-bit width

## Usage
```python
if __name__ == "__main__":
```
Command line usage:
```bash
python3 assembler.py <input_file> <output_file>
```
- input_file: RISC-V assembly source code
- output_file: Generated binary machine code
