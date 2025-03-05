# Assembler Grader class

from colors import bcolors
from Grader import Grader
import os

class AsmGrader(Grader):
    # simple test 0.1 x 10
    SIMPLE_MARKS = 0.2
    # Hard test 0.2 x 5
    HARD_MARKS = 0.2

    ASM_ERROR_DIR = "errorGen"
    ASM_HARD_DIR = "hardBin"
    ASM_SIMPLE_DIR = "simpleBin"

    BIN_HARD_DIR = "bin_h"
    BIN_SIMPLE_DIR = "bin_s"

    def __init__(self, verb, enable, operating_system):
        super().__init__(verb, enable, operating_system)
        self.enable = enable
        self.operating_system = operating_system

        self.ASM_RUN_DIR = ""

        # Create necessary output directories
        if self.operating_system == 'linux':
            os.makedirs("automatedTesting/tests/assembly/user_bin_s", exist_ok=True)
            os.makedirs("automatedTesting/tests/assembly/user_bin_h", exist_ok=True)
        elif self.operating_system == 'windows':
            os.makedirs("automatedTesting\\tests\\assembly\\user_bin_s", exist_ok=True)
            os.makedirs("automatedTesting\\tests\\assembly\\user_bin_h", exist_ok=True)

    def handleErrorGen(self):
        curDir = os.getcwd()
        if self.operating_system == 'linux':
            tests = self.listFiles("tests/assembly/" + self.ASM_ERROR_DIR)
        elif self.operating_system == 'windows':
            tests = self.listFiles("tests\\assembly\\" + self.ASM_ERROR_DIR)
        os.chdir(self.ASM_RUN_DIR)

        for test in tests:
            self.printSev(self.HIGH, bcolors.OKCYAN + "Running " + test + bcolors.ENDC)
            if self.operating_system == 'linux':
                python_command = 'python3 Assembler.py'
            elif self.operating_system == 'windows':
                python_command = 'py -3 Assembler.py'
            if self.operating_system == 'linux':
                assembly_file = '../automatedTesting/tests/assembly/' + self.ASM_ERROR_DIR + '/' + test
            elif self.operating_system == 'windows':
                assembly_file = '..\\automatedTesting\\tests\\assembly\\' + self.ASM_ERROR_DIR + '\\' + test

            # create a temp file
            if self.operating_system == 'linux':
                os.system('touch temp_file.txt')
            elif self.operating_system == 'windows':
                os.system('cd . > temp_file.txt')

            machine_code_file = 'temp_file.txt'
            command = python_command + ' ' + assembly_file + ' ' + machine_code_file
            errors = os.popen(command).read()
            if self.operating_system == 'linux':
                os.system('rm temp_file.txt')
            elif self.operating_system == 'windows':
                os.system('del temp_file.txt')

            self.printSev(self.HIGH, errors, end="")
            self.printSev(self.HIGH, "============================================\n")

        os.chdir(curDir)

    def handleBin(self, genDir, expDir):
        passCount = 0
        totalCount = 0

        curDir = os.getcwd()
        if self.operating_system == 'linux':
            tests = self.listFiles("tests/assembly/" + genDir)
        elif self.operating_system == 'windows':
            tests = self.listFiles("tests\\assembly\\" + genDir)
        tests.sort()

        for test in tests:
            python_command = 'python'
            assembly_file = 'automatedTesting/tests/assembly/' + genDir + '/' + test
            machine_code_file = 'automatedTesting/tests/assembly/user_' + expDir + '/' + test
            
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(machine_code_file), exist_ok=True)
            
            os.system('cd . > ' + machine_code_file)
            command = python_command + ' SimpleAssembler/Assembler.py ' + assembly_file + ' ' + machine_code_file
            os.system(command)
            generatedBin = [line.strip() for line in open(machine_code_file, 'r').readlines()]

            if self.operating_system == 'linux':
                exact_machine_code_file = "automatedTesting/tests/assembly/" + expDir + "/" + test
            elif self.operating_system == 'windows':
                exact_machine_code_file = "automatedTesting\\tests\\assembly\\" + expDir + "\\" + test
            expectedBin = [line.strip() for line in open(exact_machine_code_file, 'r').readlines()]

            if self.diff(generatedBin, expectedBin):
                self.printSev(self.HIGH, bcolors.OKGREEN + "[PASSED]" + bcolors.ENDC + " " + test)
                passCount += 1
            else:
                self.printSev(self.HIGH, bcolors.FAIL + "[FAILED]" + bcolors.ENDC + " " + test)
            totalCount += 1

        os.chdir(curDir)
        return passCount, totalCount

    def grade(self):
        res = None
        if self.enable:
            self.printSev(self.HIGH, bcolors.WARNING + bcolors.BOLD + "==================================================" + bcolors.ENDC)
            self.printSev(self.HIGH, bcolors.WARNING + bcolors.BOLD + "================ TESTING ASSEMBLER ===============" + bcolors.ENDC)
            self.printSev(self.HIGH, bcolors.WARNING + bcolors.BOLD + "==================================================" + bcolors.ENDC)
            self.printSev(self.HIGH, "")

            self.printSev(self.HIGH, bcolors.OKBLUE + bcolors.BOLD + "Runing simple tests" + bcolors.ENDC)
            simplePass, simpleTotal = self.handleBin(self.ASM_SIMPLE_DIR, self.BIN_SIMPLE_DIR)

            self.printSev(self.HIGH, bcolors.OKBLUE + bcolors.BOLD + "\nRunning hard tests" + bcolors.ENDC)
            hardPass, hardTotal = self.handleBin(self.ASM_HARD_DIR, self.BIN_HARD_DIR)

            # uncomment to evaluate error tests
            # self.printSev(self.HIGH, bcolors.OKBLUE + bcolors.BOLD + "Running error tests" + bcolors.ENDC)
            # self.handleErrorGen()  

            res = [
                ["Simple", simplePass, simpleTotal, self.SIMPLE_MARKS],
                ["Hard", hardPass, hardTotal, self.HARD_MARKS],
            ]

        return res
