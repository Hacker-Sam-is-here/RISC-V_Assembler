# RISC-V Assembler Implementation

This is my implementation of a RISC-V assembler for the CO M2022 assignment. It takes assembly language input and generates binary machine code output.

## How it Works

The assembler does a two-pass process:
1. First pass: Collects all labels and their addresses
2. Second pass: Actually generates the machine code

## Features

- Handles all basic RISC-V instructions (arithmetic, logic, memory, branches, jumps)
- Supports both x0-x31 register names and standard RISC-V aliases (zero, ra, sp, etc.)
- Proper handling of negative immediates and branch offsets
- Label support for jumps and branches
- Detailed error messages for debugging

## Instructions Supported

### R-type 
- add, sub, sll, slt, srl, and, or, xor

### I-type
- addi, slti, sltiu, xori, ori, andi
- slli, srli
- lw
- jalr

### S-type
- sw

### B-type
- beq, bne, blt, bge, bltu, bgeu

### U-type
- lui, auipc

### J-type
- jal

### Special
- rst (all 0s)
- halt (all 1s)

## Usage

```bash
python SimpleAssembler/Assembler.py <input_file.asm> <output_file.txt>
```

Example:
```bash
python SimpleAssembler/Assembler.py test.asm output.txt
```

## Implementation Notes

After quite a bit of trial and error, I got all the instruction encodings working properly. The trickiest parts were:

1. Handling negative immediates correctly (needed sign extension)
2. Getting branch offsets right (they're actually pretty complex!)
3. Making the label system work for both forwards and backwards jumps
4. Dealing with memory instruction formats like `lw x1, 8(x2)`

## Test Results

The assembler passes all automated tests:
- Simple Tests: 5/5 passed
- Hard Tests: 5/5 passed
- Total Score: 2.0/2.0

## File Structure

- `Assembler.py`: Main assembler implementation
- Helper functions for:
  - Register name handling
  - Instruction parsing
  - Memory operand parsing
  - Label management
  - Binary encoding

## Error Handling

The assembler does proper error checking for:
- Unknown instructions
- Invalid register names
- Malformed memory operations
- Missing/extra operands
- Duplicate labels
- Invalid immediates

## Learning Experience

This project helped me really understand:
- How assembly instructions map to binary
- Why RISC-V uses different instruction formats
- The importance of proper immediate handling
- How branch offsets actually work
