# RISC-V Simulator Documentation

## Overview
This is a custom RISC-V simulator implementation that executes machine code instructions. Key components:

1. **Instruction Execution Pipeline**:
   - Fetches, decodes, and executes RISC-V instructions
   - Handles all standard instruction formats (R/I/S/B/J-type)
   - Processes 32-bit binary instructions

2. **Register File**:
   - 32 general-purpose registers (x0-x31)
   - x0 is hardwired to zero
   - x2 (sp) initialized as stack pointer (default: 380)

3. **Memory System**:
   - 128-byte address space (32 words)
   - Word-aligned memory access
   - Supports load/store operations

4. **Program Counter**:
   - Tracks current execution address
   - Handles sequential and branch/jump operations
   - Default increment of 4 bytes per instruction

## Code Walkthrough

### 1. Binary Utilities
```python
class BinaryUtils:
    @staticmethod
    def to_binary32(value: int) -> str:
        """Convert decimal to 32-bit binary string with 0b prefix, handling two's complement."""
        if value < 0:
            return bin(value & 0xFFFFFFFF)
        return bin(value)
```
Key Features:
- **Two's Complement Handling**: Properly converts negative integers to their 32-bit binary representation
- **Positive Values**: Directly converts positive integers to binary
- **Format**: Returns strings with '0b' prefix for clarity
- **Usage**: Primarily used for register/memory value representation in trace output

### 2. Instruction Execution
```python
class RISCVInstruction:
    def execute(self) -> int:
        """Execute the instruction and return the next PC value."""
        opcode = self.binary[25:32]  # Extract 7-bit opcode
        funct3 = self.binary[17:20]   # Extract 3-bit funct3 (for R/I/S/B-type)
        funct7 = self.binary[0:7]     # Extract 7-bit funct7 (for R-type)
```
Execution Flow:
1. **Opcode Decoding**: Identifies instruction type (R/I/S/B/J)
2. **Field Extraction**:
   - R-type: rs1, rs2, rd, funct3, funct7
   - I-type: rs1, rd, immediate
   - S-type: rs1, rs2, immediate
   - B-type: rs1, rs2, branch offset
   - J-type: jump target
3. **Operation Execution**:
   - Performs arithmetic/logical operations
   - Handles memory load/store
   - Manages control flow (branches/jumps)
4. **PC Update**: Returns next instruction address

### 3. Register File
```python
self.registers = [0] * 32  # x0-x31
self.registers[2] = 380   # Initialize stack pointer (x2/sp)
```
Register Conventions:
- **x0**: Hardwired zero (always returns 0)
- **x1**: Return address (ra)
- **x2**: Stack pointer (sp)
- **x3-x7**: Temporary registers (t0-t6)
- **x8-x9**: Saved registers (s0-s1)
- **x10-x17**: Function arguments/return values (a0-a7)

Operations:
- Read/write access during instruction execution
- Zero register (x0) writes are ignored
- All registers are 32-bit wide

### 4. Memory System
```python
self.memory = {addr: 0 for addr in range(65536, 65664, 4)}  # 0x00010000-0x0001007F
```
Memory Characteristics:
- **Address Range**: 0x00010000 to 0x0001007F (128 bytes)
- **Alignment**: Word-addressable (4-byte granularity)
- **Operations**:
  - Load: Reads data from memory to registers
  - Store: Writes data from registers to memory
  - All accesses must be aligned
- **Initialization**: All locations zeroed at startup

### 5. Execution Flow
```python
while 0 <= i < len(pc_updates):
    instruction = RISCVInstruction(instructions[i], self.pc, self.registers, self.memory)
    self.pc = instruction.execute()  # Get next PC
    i = pc_updates.index(self.pc)    # Find new instruction index
```
Execution Stages:
1. **Instruction Fetch**: Gets next instruction from memory
2. **Decode**: Determines instruction type and extracts fields
3. **Execute**: Performs operation (ALU, memory access, etc.)
4. **Writeback**: Updates registers if needed
5. **PC Update**:
   - +4 for sequential execution
   - Branch/jump target for control flow changes
6. **Termination**: Stops when PC matches termination address

## Usage
```bash
python Simulator.py input.txt output.txt
```

## Example Output
```
0b00000000000000000000000000000000 0b00000000000000000000000000000000 ...
0x00010000:0b00000000000000000000000000000000
```

## Limitations
- Supports a subset of RISC-V instructions
- Fixed memory size
- Basic error handling

## Future Improvements
- Support more instruction types
- Better memory management
- Enhanced debugging features