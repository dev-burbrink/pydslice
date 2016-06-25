# pydslice_ins.py
#
# Class for representing instructions 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

try:
    from pydslice_operand import *
except ImportError:
    from pydslice.pydslice_operand import *

class Insn():
    comment = ""
    opcode = ""
    opcode2 = ""
    text = ""
    pc = 0
    line = ""
    file = ""
    sym = ""

    dest_list = []
    src_list = []

    # Initializes the instruction
    def __init__(self, pc):
        self.pc = pc
        self.dest_list = []
        self.src_list = []

    # Sets symbol information about the instruction
    def set_line_info(self, line, file, sym):
        self.line = line
        self.file = file
        self.sym = sym

    # Adds operand to specified list of instruction
    def add_operand(self, operand, operand_direction):
        if operand.address == '':
            import traceback
            traceback.print_exc()

        if operand_direction == OPERAND_DIRECTION_SRC or \
                operand_direction == OPERAND_DIRECTION_BOTH:
            self.src_list.append(operand)
        if operand_direction == OPERAND_DIRECTION_DST or \
                operand_direction == OPERAND_DIRECTION_BOTH:
            self.dest_list.append(operand)

    # Outputs a human readable string for the instruction
    def to_string(self, verbose):
        symbols = ''
        operands = ''

        if self.file == "":
            str = "0x%x: %s" % (self.pc, self.text)
        else:
            str = "%s:%s %s 0x%x: %s" % (self.file, self.line, self.sym, \
                    self.pc, self.text)

        operands = operands + "\n\t["
        
        for s in self.src_list:
            operands = operands + s.to_string() + ", "
            if s.symbol:
                symbols = symbols + s.symbol + ' '

        operands = operands[:-2] + "] -> ["
        
        for d in self.dest_list:
            operands = operands + d.to_string() + ", "
            if d.symbol:
                symbols = symbols + d.symbol + ' '

        operands = operands[:-2] + "]"

        if verbose == True:
            str = str + operands

        if symbols:
            str = str + " // " + symbols

        if self.comment:
            str = str + " # " + self.comment

        return str 
