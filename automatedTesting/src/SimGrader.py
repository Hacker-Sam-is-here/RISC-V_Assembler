# Simulator Grader class

from colors import bcolors
from Grader import Grader
import os

class SimGrader(Grader):

    # 0.2 x 10
    SIMPLE_MARKS = 2    #4/6 #0.2
    # 0.8 x 5
    HARD_MARKS = 1

    BIN_HARD_DIR = "hard"
    BIN_SIMPLE_DIR = "simple"

    TRACE_HARD_DIR = "hard"
    TRACE_SIMPLE_DIR = "simple"

    def __init__(self, verb, enable, operating_system):
        super().__init__(verb, enable, operating_system)
        self.enable = enable
        self.operating_system = operating_system

        if self.operating_system == 'linux':
            self.SIM_RUN_DIR = "../../SimpleSimulator/"
        elif self.operating_system == 'windows':
            self.SIM_RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "SimpleSimulator"))

    def handleBin(self, genDir, expDir):

        passCount = 0
        totalCount = 0

        curDir = os.getcwd()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Use absolute paths for test files
        test_bin_dir = os.path.abspath(os.path.join(base_dir, "tests", "bin", genDir))
        tests = self.listFiles(test_bin_dir)
        tests.sort()

        # Change to simulator directory using absolute path
        os.chdir(self.SIM_RUN_DIR)

        for test in tests:
            python_command = 'python Simulator.py' if self.operating_system == 'windows' else 'python3 Simulator.py'

            # Create absolute paths for all files
            machine_code_file = os.path.abspath(os.path.join(test_bin_dir, test))
            output_trace_dir = os.path.abspath(os.path.join(base_dir, "tests", "user_traces", genDir))
            output_trace_file = os.path.abspath(os.path.join(output_trace_dir, test))
            output_read_trace_file = os.path.abspath(os.path.join(output_trace_dir, test.split(".")[0] + "_r.txt"))

            # Ensure output directory exists
            if not os.path.exists(output_trace_dir):
                os.makedirs(output_trace_dir)

            # Clean up existing files
            for file in [output_trace_file, output_read_trace_file]:
                if os.path.exists(file):
                    os.remove(file)

            # Build command with proper path separators
            # Create output directory structure
            if not os.path.exists(output_trace_dir):
                os.makedirs(output_trace_dir, exist_ok=True)

            # Build command with proper path separators
            command = f"{python_command} \"{machine_code_file}\" \"{output_trace_file}\""
            os.system(command)

            # Read generated trace
            generatedTrace = open(output_trace_file, 'r').readlines()

            # Get expected trace file path
            exact_trace_file = os.path.abspath(os.path.join(base_dir, "tests", "traces", expDir, test))

            try:
                expectedTrace = open(exact_trace_file, 'r').readlines()
            except FileNotFoundError:
                self.printSev(self.HIGH, bcolors.WARNING + "[Golden Binary Trace File Not Found]\n" + exact_trace_file)
                expectedTrace = " "

            totalCount += 1
            if self.diff(generatedTrace, expectedTrace):
                self.printSev(self.HIGH, bcolors.OKGREEN + "[PASSED]" + bcolors.ENDC + " " + test)
                passCount += 1
            else:
                self.printSev(self.HIGH, bcolors.FAIL + "[FAILED]" + bcolors.ENDC + " " + test)

        os.chdir(curDir)
        return passCount, totalCount

    def grade(self):
        res = None
        if self.enable:
            self.printSev(self.HIGH, bcolors.WARNING + bcolors.BOLD + "==================================================" + bcolors.ENDC)
            self.printSev(self.HIGH, bcolors.WARNING + bcolors.BOLD + "================ TESTING SIMULATOR ===============" + bcolors.ENDC)
            self.printSev(self.HIGH, bcolors.WARNING + bcolors.BOLD + "==================================================" + bcolors.ENDC)
            self.printSev(self.HIGH, "")

            self.printSev(self.HIGH, bcolors.OKBLUE + bcolors.BOLD + "Runing simple tests" + bcolors.ENDC)
            simplePass, simpleTotal = self.handleBin(self.BIN_SIMPLE_DIR, self.TRACE_SIMPLE_DIR)

            self.printSev(self.HIGH, bcolors.OKBLUE + bcolors.BOLD + "\nRunning hard tests" + bcolors.ENDC)
            hardPass, hardTotal = self.handleBin(self.BIN_HARD_DIR, self.TRACE_HARD_DIR)

            res = [
                ["Simple", simplePass, simpleTotal, self.SIMPLE_MARKS],
                ["Hard", hardPass, hardTotal, self.HARD_MARKS],
            ]

        return res
