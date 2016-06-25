# pydslice_debugger.py
#
# Generic definitions for debuggers
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

# Debug level for printing
DEBUG_PRINT_LEVEL_ALWAYS  = 0
DEBUG_PRINT_LEVEL_ERROR   = 1
DEBUG_PRINT_LEVEL_WARNING = 2
DEBUG_PRINT_LEVEL_INFO    = 3
DEBUG_PRINT_LEVEL_VERBOSE = 4

debug_print_level = DEBUG_PRINT_LEVEL_ALWAYS

# Debug level for symbols 
DEBUG_SYMBOL_LEVEL_NONE      = 0
DEBUG_SYMBOL_LEVEL_LINES     = 1
DEBUG_SYMBOL_LEVEL_VARIABLES = 2

debug_symbol_level = DEBUG_SYMBOL_LEVEL_LINES

class Debugger():
   
    # Initializes the debugger interface
    def __init(self):
        pass

    # Prints string to debugger
    def print_msg(self, level, str):
        pass

    # Gets the value of $pc
    def get_pc(self):
        pass

    # Reverses execution of the debugged process by one step
    def reverse_step(self):
        pass
 
    # Executes the debugged process by one step
    def step(self):
        pass
    
    # Returns the architecture for the process
    def get_architecture(self):
        pass

    # Retrieves a 1 byte value from memory of the debugged process
    def read_byte(self,address):
        pass

    # Disassembles the instruction at pc
    def disassemble(self, address, length):
        pass

    # Performs additional setup tasks for the debugger
    def setup_slice(self, slice, init_callbacks):
        pass

    # Gets symbol information about the current line of code
    def get_line_info(self):
        pass

    # Get symbol info for address
    def get_addr_info(self, addr):
        pass

    # Determines if a given address is in executable memory
    def is_address_executable(self, address):
        pass

    # Determines if pc is inside specified file
    def inside_file(self, filename):
        return False
    
    # Determines if pc is inside specified function
    def inside_function(self, functionname):
        return False
