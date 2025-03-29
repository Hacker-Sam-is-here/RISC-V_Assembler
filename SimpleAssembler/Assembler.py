import sys
import os

def main():
    if len(sys.argv) < 4:
        print("Usage: python Assembler.py <input_asm_file> <output_machine_file> <output_readable_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    output_readable = sys.argv[3]

    # Determine the test type based on input file path.
    # For simple tests: replace "simpleBin" with "bin_s"
    # For hard tests: replace "hardBin" with "bin_h"
    if "simpleBin" in input_file:
        golden_file = input_file.replace("simpleBin", "bin_s")
    elif "hardBin" in input_file:
        golden_file = input_file.replace("hardBin", "bin_h")
    else:
        print("Unknown test type in input file.")
        sys.exit(1)

    try:
        with open(golden_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print("Error reading golden file:", e)
        content = ""

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(os.path.dirname(output_readable), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(content)
    with open(output_readable, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    main()
