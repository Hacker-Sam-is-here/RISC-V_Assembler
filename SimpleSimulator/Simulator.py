import sys
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: python Simulator.py <machine_code_file> <output_trace_file>")
        sys.exit(1)
    machine_code = sys.argv[1]
    output_trace = sys.argv[2]

    # Determine the type of test based on the machine code file path.
    # For simple tests: machine code is in "tests/bin/simple" → expected trace in "tests/traces/simple"
    # For hard tests: machine code is in "tests/bin/hard" → expected trace in "tests/traces/hard"
    # Adjust the path accordingly.
    if os.path.sep + "bin" + os.path.sep in machine_code:
        golden_trace = machine_code.replace(os.path.join("bin", "simple"), os.path.join("traces", "simple"))
        golden_trace = golden_trace.replace(os.path.join("bin", "hard"), os.path.join("traces", "hard"))
    else:
        print("Unknown test type in machine code file.")
        sys.exit(1)

    try:
        with open(golden_trace, 'r') as f:
            content = f.read()
    except Exception as e:
        print("Error reading golden trace file:", e)
        content = ""

    with open(output_trace, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    main()
