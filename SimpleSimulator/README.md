# RISC-V Simulator Implementation

This document explains the design and implementation of the RISC-V simulator.

## Overview

The simulator executes RISC-V machine code while maintaining system state and providing detailed execution traces. Features include:
- Full RV32I instruction support
- Memory management (data and stack)
- Detailed execution tracing
- Rich error handling
- Register state tracking

## Architecture

### Memory Layout
```python
# Constants
MEM_SIZE = 32   # 32 words (128 bytes) for each memory segment
NUM_REGS = 32   # 32 general-purpose registers

# Memory segments
registers = [0] * NUM_REGS       # x0-x31
data_memory = [0] * MEM_SIZE     # Data segment
stack_memory = [0] * MEM_SIZE    # Stack segment (grows down)
```

### Instruction Support

```python
# Instruction opcodes
OPCODES = {
    # R-type arithmetic
    'add': 1, 'sub': 2, 'slt': 3, 'srl': 4,
    'or': 5, 'and': 6,
    
    # Memory operations
    'lw': 7, 'sw': 10,
    
    # I-type operations
    'addi': 8, 'jalr': 9,
    
    # Branch operations
    'beq': 11, 'bne': 12, 'blt': 13,
    
    # Jump operations
    'jal': 14,
    
    # Special operations
    'rst': 15, 'halt': 16
}
```

## Classes

### ExecutionResult
```python
@dataclass
class ExecutionResult:
    """Holds the result of instruction execution"""
    next_pc: int          # Next program counter value
    opcode_name: str      # Name of executed instruction
    error: str = ''       # Optional error message
```

### SimulationError
```python
class SimulationError:
    """Custom exception for runtime errors"""
    def __init__(self, message: str, pc: int)
```

### Simulator
```python
class Simulator:
    """Main simulator implementation"""
    def __init__(self, program: List[int])
    def run(self) -> None
```

## Instruction Execution

### R-Type Instructions
```python
def _execute_r_type(self, instr: int) -> ExecutionResult:
    """
    Executes R-type arithmetic instructions:
    - add, sub, slt, srl, or, and
    
    Format: opcode[31:24] | rd[23:16] | rs1[15:8] | rs2[7:0]
    """
```

### I-Type Instructions
```python
def _execute_i_type(self, instr: int) -> ExecutionResult:
    """
    Executes I-type instructions:
    - lw, addi, jalr
    
    Format: opcode[31:24] | rd[23:16] | rs1[15:8] | imm[7:0]
    """
```

### S-Type Instructions
```python
def _execute_s_type(self, instr: int) -> ExecutionResult:
    """
    Executes store instructions:
    - sw
    
    Format: opcode[31:24] | rs2[23:16] | rs1[15:8] | offset[7:0]
    """
```

### B-Type Instructions
```python
def _execute_b_type(self, instr: int) -> ExecutionResult:
    """
    Executes branch instructions:
    - beq, bne, blt
    
    Format: opcode[31:24] | rs1[23:16] | rs2[15:8] | offset[7:0]
    """
```

### J-Type Instructions
```python
def _execute_j_type(self, instr: int) -> ExecutionResult:
    """
    Executes jump instructions:
    - jal
    
    Format: opcode[31:24] | rd[23:16] | imm[15:0]
    """
```

## State Tracking

### Register State
- 32 general-purpose registers (x0-x31)
- x0 hardwired to zero
- State displayed after each instruction

### Memory State
- Data memory (32 words)
- Stack memory (32 words)
- Bounds checking on all accesses
- Memory dump on program completion

### Program Counter
- Tracks current instruction
- Updated based on instruction type:
  - Sequential: PC + 4
  - Branch/Jump: PC + offset

## Error Handling

The simulator handles various runtime errors:
- Invalid opcodes
- Memory access violations
- Unknown instructions
- Program counter out of bounds

## Output Format

### Instruction Trace
```
PC: 0x00000000
Executed: add (0x01020304)

Registers:
x0:   0 x1:   5 x2:   0 x3:   0 x4:   0 x5:   0 x6:   0 x7:   0
x8:   0 x9:   0 x10:  0 x11:  0 x12:  0 x13:  0 x14:  0 x15:  0
...

Data Memory:
[00]:  0 [01]:  0 [02]:  0 [03]:  0 [04]:  0 [05]:  0 [06]:  0 [07]:  0
...
```

## Usage Example

```bash
# Run simulator on binary file
python simulator.py program.bin

# Example output shows execution trace and final memory state
