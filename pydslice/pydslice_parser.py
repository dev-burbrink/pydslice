# pydslice_parser.py
#
# Generic parser class 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

class Parser():
    # Initializes the parser
    def __init__(self, debugger):
        pass

    # Parses an argument to an insn
    def parse_arg(self, arg, insn, operand):
        pass

    # Parses an instruction
    def parse_insn(self, pc):
        pass

    # Performs any additional tasks after performing a slice step
    def step_cleanup(self):
        pass

    # Determines if an operand is to be ignored
    def ignore_operand(self, operand):
        pass
