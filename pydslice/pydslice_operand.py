# pydslice_operand.py
#
# Class for reprenting operands of an instruction 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

OPERAND_TYPE_UNKNOWN   = 0
OPERAND_TYPE_REGISTER  = 1
OPERAND_TYPE_MEMORY    = 2
OPERAND_TYPE_IMMEDIATE = 3

OPERAND_DIRECTION_SRC  = 1
OPERAND_DIRECTION_DST  = 2
OPERAND_DIRECTION_BOTH = 3

class Operand():
    operand_type = OPERAND_TYPE_UNKNOWN
    value = 0
    address = 0
    is_memory = False
    symbol = ''
    base_register = ''
    match_function = None

    # Initializes the operand
    def __init__(self, operand_type, is_memory, address, value):
        self.operand_type = operand_type
        self.address = address
        self.value = value
        self.is_memory = is_memory
        self.symbol = ''

    def __eq__(self, other):
        if not other:
            return False

        if self.operand_type == other.operand_type:
            if self.operand_type == OPERAND_TYPE_REGISTER:
                return self.base_register == other.base_register
            return self.address == other.address
        return False 

    # dests a human-readable string
    def to_string(self):
        if type(self.address) == type(0):
            str = ("0x%x:0x%x" % (self.address, self.value))
        else:
            str = ("%s:0x%x" % (self.address, self.value))

        if self.symbol:
            str = str + " // " + self.symbol

        return str
