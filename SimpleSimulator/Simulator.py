
import sys
from typing import Dict, List, Optional, Tuple

class BinaryUtils:
    @staticmethod
    def to_binary32(value: int) -> str:
        """Convert decimal to 32-bit binary string with 0b prefix, handling two's complement."""
        if value < 0:
            value = (1 << 32) + value
        binary = bin(value)[2:].zfill(32)[-32:]
        return f"0b{binary}"
    
    @staticmethod
    def binary_to_decimal(binary: str) -> int:
        """Convert binary string to decimal."""
        return int(binary, 2)
    
    @staticmethod
    def twos_complement_to_decimal(binary: str) -> int:
        """Convert binary string to decimal using two's complement."""
        bit_length = len(binary)
        result = 0
        msb_power = bit_length - 1
        
        # Handle MSB (sign bit)
        if binary[0] == '1':
            result -= int(binary[0]) * (2 ** msb_power)
        else:
            result += int(binary[0]) * (2 ** msb_power)
            
        # Process remaining bits
        for i in range(1, bit_length):
            power = bit_length - 1 - i
            result += int(binary[i]) * (2 ** power)
        return result

class RISCVInstruction:
    def __init__(self, binary: str, pc: int, registers: List[int], memory: Dict[int, int]):
        self.binary = binary
        self.pc = pc
        self.registers = registers
        self.memory = memory
        
    def execute(self) -> int:
        """Execute the instruction and return the next PC value."""
        opcode = self.binary[25:32]
        instruction_map = {
            "0110011": self._execute_r_type,
            "0000011": self._execute_i_type,
            "0010011": self._execute_i_type,
            "1100111": self._execute_i_type,
            "0100011": self._execute_s_type,
            "1100011": self._execute_b_type,
            "1101111": self._execute_j_type
        }
        
        if opcode not in instruction_map:
            print(f"Error: Invalid opcode {opcode} in instruction {self.binary}")
            return self.pc + 4
            
        return instruction_map[opcode]()
    
    def _execute_r_type(self) -> int:
        func7 = self.binary[0:7]
        func3 = self.binary[17:20]
        rs1 = BinaryUtils.binary_to_decimal(self.binary[12:17])
        rs2 = BinaryUtils.binary_to_decimal(self.binary[7:12])
        rd = BinaryUtils.binary_to_decimal(self.binary[20:25])
        
        if rd == 0:  # x0 is hardwired to 0
            return self.pc + 4
            
        if func3 == "000":
            if func7 == "0100000":  # SUB
                self.registers[rd] = self.registers[rs1] - self.registers[rs2]
            elif func7 == "0000000":  # ADD
                self.registers[rd] = self.registers[rs1] + self.registers[rs2]
        elif func3 == "110":  # OR
            self.registers[rd] = self.registers[rs1] | self.registers[rs2]
        elif func3 == "111":  # AND
            self.registers[rd] = self.registers[rs1] & self.registers[rs2]
        elif func3 == "010":  # SLT
            self.registers[rd] = 1 if self.registers[rs1] < self.registers[rs2] else 0
        elif func3 == "101":  # SRL
            shift = self.registers[rs2] & 0b11111
            self.registers[rd] = (self.registers[rs1] & 0xFFFFFFFF) >> shift
            
        return self.pc + 4
    
    def _execute_i_type(self) -> int:
        opcode = self.binary[25:32]
        func3 = self.binary[17:20]
        rs1 = BinaryUtils.binary_to_decimal(self.binary[12:17])
        rd = BinaryUtils.binary_to_decimal(self.binary[20:25])
        imm = BinaryUtils.twos_complement_to_decimal(self.binary[0:12])
        
        if opcode == "0010011" and func3 == "000":  # ADDI
            if rd != 0:
                self.registers[rd] = self.registers[rs1] + imm
        elif opcode == "1100111" and func3 == "000":  # JALR
            next_pc = (self.registers[rs1] + imm) & ~1
            if rd != 0:
                self.registers[rd] = self.pc + 4
            return next_pc
        elif opcode == "0000011" and func3 == "010":  # LW
            if rd != 0:
                address = self.registers[rs1] + imm
                self.registers[rd] = self.memory.get(address, 0)
                
        return self.pc + 4
    
    def _execute_s_type(self) -> int:
        imm = BinaryUtils.twos_complement_to_decimal(self.binary[0:7] + self.binary[20:25])
        rs1 = BinaryUtils.binary_to_decimal(self.binary[12:17])
        rs2 = BinaryUtils.binary_to_decimal(self.binary[7:12])
        func3 = self.binary[17:20]
        
        if func3 == "010":  # SW
            address = self.registers[rs1] + imm
            self.memory[address] = self.registers[rs2]
            
        return self.pc + 4
    
    def _execute_b_type(self) -> int:
        func3 = self.binary[17:20]
        rs1 = BinaryUtils.binary_to_decimal(self.binary[12:17])
        rs2 = BinaryUtils.binary_to_decimal(self.binary[7:12])
        imm = BinaryUtils.twos_complement_to_decimal(
            self.binary[0] + self.binary[24] + self.binary[1:7] + self.binary[20:24] + '0'
        ) & ~1
        
        if func3 == "000":  # BEQ
            return self.pc + imm if self.registers[rs1] == self.registers[rs2] else self.pc + 4
        elif func3 == "001":  # BNE
            return self.pc + imm if self.registers[rs1] != self.registers[rs2] else self.pc + 4
            
        return self.pc + 4
    
    def _execute_j_type(self) -> int:
        rd = BinaryUtils.binary_to_decimal(self.binary[20:25])
        imm = BinaryUtils.twos_complement_to_decimal(
            self.binary[0] + self.binary[12:20] + self.binary[11] + self.binary[1:11] + '0'
        ) & ~1
        
        if rd != 0:
            self.registers[rd] = self.pc + 4
        return self.pc + imm

class RISCVSimulator:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.pc = 0
        self.registers = [0] * 32
        self.registers[2] = 380  # Initialize stack pointer
        self.memory = {addr: 0 for addr in range(65536, 65664, 4)}
        
    def run(self):
        """Execute the RISC-V program and generate output trace."""
        instructions = self._load_instructions()
        pc_updates = [4 * i for i in range(len(instructions) + 1)]
        
        with open(self.output_file, 'w') as outfile:
            i = 0
            while 0 <= i < len(pc_updates):
                instruction = RISCVInstruction(instructions[i], self.pc, self.registers, self.memory)
                terminate_pc = pc_updates[i]
                
                self.pc = instruction.execute()
                i = pc_updates.index(self.pc)
                
                self._write_trace(outfile)
                
                if self.pc == terminate_pc:
                    break
                    
            self._write_memory_dump(outfile)
    
    def _load_instructions(self) -> List[str]:
        """Load and return instructions from input file."""
        with open(self.input_file, 'r') as infile:
            return [line.strip() for line in infile]
    
    def _write_trace(self, outfile):
        """Write the current execution trace to output file."""
        trace = [BinaryUtils.to_binary32(self.pc)]
        trace.extend(BinaryUtils.to_binary32(r) for r in self.registers)
        outfile.write(' '.join(trace) + '\n')
    
    def _write_memory_dump(self, outfile):
        """Write memory dump to output file."""
        hex_memory = {f"0x{addr:08X}": value for addr, value in self.memory.items()}
        for i, (addr, value) in enumerate(hex_memory.items()):
            if i >= 32:
                break
            outfile.write(f"{addr}:{BinaryUtils.to_binary32(value)}\n")

def main():
        
    simulator = RISCVSimulator(sys.argv[1], sys.argv[2])
    simulator.run()

if __name__ == "__main__":
    main()
