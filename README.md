# RISC-V Assembler and Simulator

A custom implementation of a RISC-V assembler and simulator. This project consists of two main components that work together to convert assembly code to machine code and simulate its execution.

## Project Structure

```
.
├── SimpleAssembler/
│   ├── Assembler.py     # Main assembler implementation
│   └── test.asm         # Sample assembly file
├── SimpleSimulator/
│   └── Simulator.py     # Main simulator implementation
└── automatedTesting/    # Testing framework
    ├── src/             # Source code for test suite
    └── tests/           # Test cases and expected outputs
        ├── assembly/    # Assembly test inputs
        ├── bin/         # Binary test files
        └── traces/      # Execution traces
```

## Components

### Simple Assembler

Located in `SimpleAssembler/`, this component converts RISC-V assembly code into machine code. It handles:
- Basic assembly instructions
- Label resolution
- Error checking

### Simple Simulator 

Located in `SimpleSimulator/`, this component simulates the execution of machine code. Features include:
- Instruction execution
- Memory management
- Program counter tracking

### Automated Testing

The `automatedTesting/` directory contains a comprehensive test suite with:
- Simple test cases for basic functionality
- Hard test cases for edge cases
- Verification of assembler output
- Validation of simulator execution traces

## Usage

1. **Assembly**: Convert assembly code to machine code:
```bash
python SimpleAssembler/Assembler.py
```

2. **Simulation**: Simulate machine code execution:
```bash
python SimpleSimulator/Simulator.py
```

3. **Testing**: Run automated tests:
```bash
python automatedTesting/src/main.py
```

## Test Cases

The test suite includes:
- Simple cases (`tests/assembly/bin_s/`)
- Hard cases (`tests/assembly/bin_h/`)
- User test cases (`tests/assembly/user_bin_s/` and `tests/assembly/user_bin_h/`)

Execution traces are stored in `tests/traces/` for verification.
