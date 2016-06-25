# pydslice.py
#
# Base Slice functionality 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>

try:
    from pydslice_debugger_gdb import *
    from pydslice_debugger import *
    from pydslice_parser_x86 import *
    from pydslice_parser_x86_64 import *
    from pydslice_insn import *
    from pydslice_operand import *
except ImportError:
    from pydslice.pydslice_debugger_gdb import *
    from pydslice.pydslice_debugger import *
    from pydslice.pydslice_parser_x86 import *
    from pydslice.pydslice_parser_x86_64 import *
    from pydslice.pydslice_insn import *
    from pydslice.pydslice_operand import *

# callback signature: 
# void callback(insn, matching_operands, operands_to_add, slice)
callbacks = []

# init callback signature: void init_callback(slice)
init_callbacks = []

class Slice():
    keep_going = True
    stepping = True
    operand_list = [] 
    insn_list = []
    insn = None
    debugger = None  
    parser = None
    followed_operand = None
    signal = 0
    pc = 0

    # Initializes Slice
    def __init__(self, crashed=False):
        global init_callbacks
        self.debugger = GDBDebugger()
        self.pc = self.debugger.get_pc()
        if "64" in self.debugger.get_architecture():
            self.parser = Parser_x86_64(self.debugger)
        else:
            self.parser = Parser_x86(self.debugger)
        self.operand_list = []
        self.insn_list = []

        if crashed == True:
            self.debugger.setup_slice(self, init_callbacks)
    
    # Stops the slice computation
    def stop(self):
        self.keep_going = False

    # Saves slice instruction list to file
    def save(self, path):
        with open(path, 'w') as f:
            for insn in self.insn_list:
                f.write(insn.to_string(False)+ "\n");
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "Slice saved to " + path)

    # Sets operand to be followed
    def set_followed_operand(self, operand):
        if operand == None:
            self.followed_operand = None
        else:
            self.followed_operand = self.operand_list[operand]

    # Prints current list of slice operand
    def print_operand_list(self):
        index = 1
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "--- operand list ---")
        for t in self.operand_list:
            str = "%d\t%s" % (index, t.to_string())
            if t == self.followed_operand:
                str = str + " (following)"
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, str)
            index = index + 1
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "")
     
    # Prints all instruction currently in the slice
    def print_insn_list(self, index=1, count=-1, verbose=False):
        try:
            current_level = pydslice_debugger.debug_print_level
        except NameError:
            current_level = pydslice.pydslice_debugger.debug_print_level
        
        if current_level > DEBUG_PRINT_LEVEL_INFO:
            verbose = True
        
        index = index - 1
        
        if count == -1:
            max = len(self.insn_list)
        else:
            max = index + count

        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                "--- slice instructions ---")
        if len(self.insn_list) == 0:
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "no instructions")
            return

        for insn in self.insn_list[index:max]:
            if current_level < DEBUG_PRINT_LEVEL_INFO and \
                    (insn.opcode == "call" or insn.opcode == "ret" or \
                    insn.opcode == "leave"):
                index = index + 1
                continue
            str = "%d\t%s" % (index+1, insn.to_string(verbose))
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, str)
            index = index + 1
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "")
   
    # Prints a specific instruction in the operand list
    def print_insn_list_index(self, index):
        str = "%d - %s" % (index, self.insn_list[index-1].to_string(True))
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, str)

    # Adds an instruction to the list of instructions in the slice
    def add_insn(self, insn):
        self.insn_list.append(insn)

    # Adds a operandn to the slice operand list
    def add_operand(self, operand):
        self.operand_list.append(operand)

    # Adds current instruction to the slice
    def add_current_insn(self):
        self.pc = self.debugger.get_pc()
        self.insn = self.parser.parse_insn(self.pc)
        to_add = []

        line,file,sym = self.debugger.get_line_info()
        self.insn.set_line_info(line,file,sym)

        # Add instruction's src operand to the slice operand
        for s in self.insn.src_list:
            # ... unless it should be ignored
            if self.parser.ignore_operand(s) == False:
                # Get symbol info for operand
                if s.operand_type == OPERAND_TYPE_MEMORY:
                    s.symbol = self.debugger.get_addr_info(s.address)
                to_add.append(s)

        # Prune operandl list of duplicates
        self.operand_list[:] = [x for x in self.operand_list]
        for item in to_add:
            exists = False
            for t in self.operand_list:
                if t.operand_type == item.operand_type and \
                        t.address == item.address:
                    exists = True
            if exists == False:
                self.add_operand(item)
        self.insn_list.append(self.insn)
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                "Added insn: " + self.insn.text)

    # Removes specified instruction from slice
    def delete_insn(self, index):
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                "Removed insn (%d): %s" % (index+1, self.insn_list[index].text))
        self.insn_list.remove(self.insn_list[index])

    # Adds an expression to the list of slice operand
    def add_expr_to_operand_list(self, expr):
        self.parser.add_expr_to_operand_list(expr, self.operand_list)
   
    # Removes operand from slice operand list
    def remove_operand_list_index(self, index):
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                "Removed operand (%d): %s" % \
                (index+1, self.operand_list[index].to_string()))
        self.operand_list.remove(self.operand_list[index]) 

    # Determines if parsed instruction is relevant to the slice
    def compute_insn(self, insn):
        global callbacks
        found_insn = False
        found_followed = False
        to_add = []
        matches = []

        matches[:] = [x for x in self.operand_list if x in insn.dest_list]
        
        # do we have a match?
        if not matches:
            return False,False

        if self.followed_operand in matches:
            self.followed_operand = None
            found_followed = True

        found_insn = True
        to_add = [x for x in insn.src_list if \
                self.parser.ignore_operand(x) == False]

        # Get some symbols
        for x in to_add:
            if x.operand_type == OPERAND_TYPE_MEMORY:
                x.symbol = self.debugger.get_addr_info(x.address)

        line,file,sym = self.debugger.get_line_info()
        self.insn.set_line_info(line,file,sym)

        # Do callbacks
        for callback in callbacks:
            callback(insn, matches, to_add, self)

        for operand in matches:
            if operand.match_function:
                operand.match_function(insn, matches, to_add, self)

        # remove matched operands
        self.operand_list[:] = [x for x in self.operand_list if \
                x not in matches and x not in insn.src_list]

        # add insn src operands
        self.operand_list = self.operand_list + to_add
        
        return found_insn, found_followed

    # Reverses step
    def reverse_step(self):
        self.parser.step_cleanup()
        self.last_pc = self.pc
        self.debugger.reverse_step()
        self.pc = self.debugger.get_pc()

        if self.insn:
            opcode = self.insn.opcode
        else:
            insn_text = self.debugger.disassemble(self.pc)
            opcode = insn_text.split()[0]
        
        if self.pc == self.last_pc and "rep" not in opcode:
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "Reached end of recording")
            return False 

        return True
    
    # Computes the rest of the slice or steps to the next slice instruction
    def compute_slice(self, stepping):

        if not self.operand_list:
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "No operands to track. " \
                    "Add new operands with 'slice operand add' or " \
                    "'slice new crashed'")

        self.keep_going = True
        self.pc = self.debugger.get_pc()

        while self.keep_going:
            self.insn = self.parser.parse_insn(self.pc)
            found_insn,found_operand = self.compute_insn(self.insn)
            
            # If we found an instruction in the slice, add to list and get line
            if found_insn:
                self.add_insn(self.insn)

            if self.operand_list.__len__() == 0:
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "Slice complete")
                break

            if not self.reverse_step():
                break

            if found_operand:
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        "At Instruction:")
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        self.insn.to_string(False))
                break

            if stepping and found_insn:
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        "Next slice instruction found:")
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        self.insn.to_string(False))
                break

