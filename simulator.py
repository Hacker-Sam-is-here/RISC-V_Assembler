# Memory Layout:
# 0x000-0x0FF (0-255):    Program memory
# 0x100-0x17F (256-383):  Stack memory
# 0x180-0x1FF (384-511):  Data memory

# Initialize registers (x0 to x31)
registers = [0] * 32  # All registers initialized to 0
registers[2] = 320    # Initialize stack pointer (sp) to 320 (middle of stack memory)

# Initialize memory
program_memory = [0] * 64    # 64 words (0-255 bytes)
stack_memory = [0] * 32      # 32 words (256-383 bytes)
data_memory = [0] * 32       # 32 words (384-511 bytes)

# Program Counter (PC)
pc = 0  # Start execution at address 0

def load_program_memory(file_path):
    """
    Load binary instructions into program memory.
    """
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            program_memory[i] = int(line.strip(), 2)  # Convert binary string to integer

def decode_instruction(instruction):
    """
    Decode an instruction for debug printing
    """
    opcode = instruction & 0x7F
    funct3 = (instruction >> 12) & 0x7
    funct7 = (instruction >> 25) & 0x7F
    
    if opcode == 0b0110011:  # R-type
        rd = (instruction >> 7) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        if funct3 == 0b000:
            if funct7 == 0b0000000:  # add
                return f"add x{rd}, x{rs1}, x{rs2}"
            elif funct7 == 0b0100000:  # sub
                return f"sub x{rd}, x{rs1}, x{rs2}"
    elif opcode == 0b0010011 and funct3 == 0b000:  # addi
        rd = (instruction >> 7) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        imm = (instruction >> 20) & 0xFFF
        if imm & 0x800:  # Sign extend
            imm |= ~0xFFF
        return f"addi x{rd}, x{rs1}, {imm}"
    elif opcode == 0b0000011 and funct3 == 0b010:  # lw
        rd = (instruction >> 7) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        imm = (instruction >> 20) & 0xFFF
        if imm & 0x800:  # Sign extend
            imm |= ~0xFFF
        return f"lw x{rd}, {imm}(x{rs1})"
    elif opcode == 0b0100011 and funct3 == 0b010:  # sw
        rs2 = (instruction >> 20) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        imm_11_5 = (instruction >> 25) & 0x7F
        imm_4_0 = (instruction >> 7) & 0x1F
        imm = (imm_11_5 << 5) | imm_4_0
        return f"sw x{rs2}, {imm}(x{rs1})"
    elif opcode == 0b1100011:  # B-type
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        if funct3 == 0b000:
            return f"beq x{rs1}, x{rs2}"
        elif funct3 == 0b001:
            return f"bne x{rs1}, x{rs2}"
    elif opcode == 0b1101111:  # jal
        rd = (instruction >> 7) & 0x1F
        imm_20 = (instruction >> 31) & 0x1
        imm_10_1 = (instruction >> 21) & 0x3FF
        imm_11 = (instruction >> 20) & 0x1
        imm_19_12 = (instruction >> 12) & 0xFF
        imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
        if imm_20:  # Sign extend
            imm |= 0xFFE00000
        return f"jal x{rd}, {imm}"
    elif opcode == 0b1100111:  # jalr
        rd = (instruction >> 7) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        imm = (instruction >> 20) & 0xFFF
        if imm & 0x800:  # Sign extend
            imm |= 0xFFFFF000
        return f"jalr x{rd}, {imm}(x{rs1})"
    
    return f"Unknown instruction: {bin(instruction)}"

def execute_instruction(instruction):
    """
    Execute a single RISC-V instruction.
    """
    global pc, registers, stack_memory, data_memory

    # Print decoded instruction
    print(f"Executing: {decode_instruction(instruction)}")

    # Extract opcode (bits 6:0)
    opcode = instruction & 0x7F

    if opcode == 0b0110011:  # R-type
        rd = (instruction >> 7) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        funct7 = (instruction >> 25) & 0x7F

        if funct3 == 0b000:
            if funct7 == 0b0000000:  # add
                registers[rd] = registers[rs1] + registers[rs2]
            elif funct7 == 0b0100000:  # sub
                registers[rd] = registers[rs1] - registers[rs2]

    elif opcode == 0b1100111:  # jalr
        rd = (instruction >> 7) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        imm = (instruction >> 20) & 0xFFF
        if imm & 0x800:  # Sign extend
            imm |= 0xFFFFF000

        next_pc = (registers[rs1] + imm) & ~1  # Clear least significant bit
        if 0 <= (next_pc // 4) < len(program_memory):
            registers[rd] = pc + 4  # Save return address
            pc = next_pc - 4  # -4 because we add 4 at the end

    elif opcode == 0b1110011:  # Custom opcode for rst and halt
        if instruction == 0b0000000_00000_00000_000_00000_1110011:  # rst halt
            # Reset all registers (except PC)
            registers = [0] * 32
            registers[2] = 384  # Reset stack pointer to end of stack memory
            print("Processor halted and registers reset.")
            return  # Halt execution
        else:
            raise ValueError("Unknown custom instruction")

    elif opcode == 0b0010011 or opcode == 0b0000011:  # I-type (addi, lw)
        imm = (instruction >> 20) & 0xFFF
        # Sign extend 12-bit immediate
        if imm & 0x800:  # If sign bit (bit 11) is set
            imm = imm | ~0xFFF  # Sign extend by inverting bits 12-31
        rs1 = (instruction >> 15) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        rd = (instruction >> 7) & 0x1F

        if opcode == 0b0010011 and funct3 == 0b000:  # addi
            if rd == 0 and rs1 == 0 and imm == 0:  # nop (addi x0, x0, 0)
                pass  # Do nothing
            else:
                registers[rd] = registers[rs1] + imm
        elif opcode == 0b0000011 and funct3 == 0b010:  # lw
            address = registers[rs1] + imm
            # Convert address to stack_memory index, handling negative offsets
            stack_index = (address - 256) // 4  # 256 is the base of stack memory
            if stack_index < 0 or stack_index >= len(stack_memory):
                raise ValueError(f"Stack access out of bounds: {address} (index {stack_index})")
            registers[rd] = stack_memory[stack_index]

    # (Rest of the code remains the same)

    elif opcode == 0b0100011:  # S-type (e.g., sw)
        imm_11_5 = (instruction >> 25) & 0x7F
        rs2 = (instruction >> 20) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        imm_4_0 = (instruction >> 7) & 0x1F

        imm = (imm_11_5 << 5) | imm_4_0  # Combine immediate bits
        # Sign extend 12-bit immediate
        if imm & 0x800:  # If sign bit (bit 11) is set
            imm = imm | ~0xFFF  # Sign extend by inverting bits 12-31
        address = registers[rs1] + imm

        if funct3 == 0b010:  # sw
            # Convert address to stack_memory index, handling negative offsets
            stack_index = (address - 256) // 4  # 256 is the base of stack memory
            if stack_index < 0 or stack_index >= len(stack_memory):
                raise ValueError(f"Stack access out of bounds: {address} (index {stack_index})")
            stack_memory[stack_index] = registers[rs2]

    elif opcode == 0b1100011:  # B-type (e.g., beq)
        imm_12 = (instruction >> 31) & 0x1
        imm_10_5 = (instruction >> 25) & 0x3F
        rs2 = (instruction >> 20) & 0x1F
        rs1 = (instruction >> 15) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        imm_4_1 = (instruction >> 8) & 0xF
        imm_11 = (instruction >> 7) & 0x1

        # Combine and sign extend immediate for branches
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
        # Sign extend for negative immediates (13-bit immediate)
        if imm_12:
            imm |= 0xFFFFE000  # Sign extend to 32 bits

        if funct3 == 0b000:  # beq
            if registers[rs1] == registers[rs2]:
                next_pc = pc + imm
                if 0 <= (next_pc // 4) < len(program_memory):
                    pc = next_pc - 4  # -4 because we add 4 at the end
        elif funct3 == 0b001:  # bne
            if registers[rs1] != registers[rs2]:
                next_pc = pc + imm
                if 0 <= (next_pc // 4) < len(program_memory):
                    pc = next_pc - 4  # -4 because we add 4 at the end

    elif opcode == 0b1101111:  # J-type (e.g., jal)
        imm_20 = (instruction >> 31) & 0x1
        imm_10_1 = (instruction >> 21) & 0x3FF
        imm_11 = (instruction >> 20) & 0x1
        imm_19_12 = (instruction >> 12) & 0xFF
        rd = (instruction >> 7) & 0x1F

        imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
        # Sign extend for negative immediates (21-bit immediate)
        if imm_20:  # If sign bit is set
            imm |= 0xFFE00000  # Sign extend to 32 bits

        next_pc = pc + imm
        if 0 <= (next_pc // 4) < len(program_memory):
            registers[rd] = pc + 4  # Save return address
            pc = next_pc - 4  # -4 because we add 4 at the end

    # Increment PC
    pc += 4

def print_trace():
    """
    Print the state of registers and memory.
    """
    print(f"PC: {pc}")
    print("Registers:")
    for i, value in enumerate(registers):
        print(f"x{i}: {value}")
    print("Stack Memory:")
    for i, value in enumerate(stack_memory):
        print(f"Address {i * 4}: {value}")
    print("Data Memory:")
    for i, value in enumerate(data_memory):
        print(f"Address {i * 4}: {value}")
    print("-" * 40)

def simulate(file_path):
    """
    Simulate the execution of a RISC-V program.
    """
    global pc

    # Load program memory
    load_program_memory(file_path)

    # Simulate execution
    while True:
        instruction = program_memory[pc // 4]
        if instruction == 0b0000000_00000_00000_000_00000_1100011:  # Virtual Halt (beq zero, zero, 0)
            break

        execute_instruction(instruction)
        print_trace()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python simulator.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    simulate(input_file)
