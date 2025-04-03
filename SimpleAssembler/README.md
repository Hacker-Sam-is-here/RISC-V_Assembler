# RISC-V Assembler Documentation

## Overview
This is a custom RISC-V assembler implementation that converts assembly code into machine code. It handles:
- Basic RISC-V instructions (R-type, I-type, branches, jumps, etc.)
- Label resolution
- Negative immediate handling
- Error checking

## Code Walkthrough

### 1. Register Mapping System
The assembler maintains a register map that converts both standard RISC-V register names (like 'zero', 'ra') and numeric names (like 'x0', 'x1') to register numbers.

### 2. Instruction Parsing
The `parse_instruction()` method handles:
- Stripping comments and whitespace
- Label detection (lines ending with ':')
- Instruction and operand separation

### 3. Memory Operand Parsing
The `parse_mem_operand()` method handles memory access formats like `8(t0)` by:
- Extracting offset and register parts
- Handling both numeric offsets and label references
- Validating register names

### 4. Instruction Encoding Methods
The assembler includes specialized methods for each instruction type:
- `make_r_type()` for arithmetic/logic instructions
- `make_i_type()` for immediate instructions
- Special handling for branches and jumps

### 5. Two-Pass Assembly Process
1. **First Pass**: Collects all label addresses by scanning through the code
2. **Second Pass**: Generates actual machine code using the collected label information

## Usage
```bash
python Assembler.py input.asm output.txt
```

## Example
```asm
# Sample RISC-V assembly
addi x1, x0, 42
loop:
    addi x1, x1, -1
    bne x1, x0, loop
```

## Limitations
- Currently supports a subset of RISC-V instructions
- Limited error handling for malformed instructions

## Future Improvements
- Support for more instruction types
- Better error messages
- Macro support