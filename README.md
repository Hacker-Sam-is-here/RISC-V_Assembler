# RISC-V Assembler and Simulator

A custom implementation of a RISC-V assembler and simulator. This project provides a complete toolchain for working with RISC-V assembly programs, from assembly to execution simulation.

The system consists of two main components:
1. **Assembler**: Converts RISC-V assembly code into executable machine code
2. **Simulator**: Executes the machine code and simulates program behavior

Together they form a complete development environment for learning and experimenting with RISC-V architecture.

## Project Structure

```
.
├── SimpleAssembler/            # Assembler component
│   ├── Assembler.py            # Main assembler implementation
│   ├── README.md               # Assembler documentation
│
├── SimpleSimulator/            # Simulator component
│   ├── Simulator.py            # Main simulator implementation
│   └── README.md               # Simulator documentation
│
└── automatedTesting/           # Testing framework
    ├── src/                    # Test suite source code
    │   ├── AsmGrader.py        # Assembler test grading
    │   ├── Grader.py           # Test grading logic
    │   ├── Results.py          # Test result handling
    │   ├── SimGrader.py        # Simulator test grading
    │   ├── colors.py           # Console color handling
    │   └── main.py             # Test runner
    │
    └── tests/                  # Test cases
        ├── assembly/           # Assembly test inputs
        ├── bin/                # Binary test files
        ├── traces/             # Execution traces
        └── user_traces/        # User-generated traces
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
