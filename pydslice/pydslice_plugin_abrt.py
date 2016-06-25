# pydslice_plugin_abrt.py
#
# Plugin for handling SIGABRT signals 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

try:
    from pydslice import *
    from pydslice import init_callbacks
    from pydslice_debugger_gdb import *
    from pydslice_debugger import *
    from pydslice_operand import *
except ImportError:
    from pydslice.pydslice import *
    from pydslice.pydslice import init_callbacks
    from pydslice.pydslice_debugger_gdb import *
    from pydslice.pydslice_debugger import *
    from pydslice.pydslice_operand import *

found_instruction = False
abrt_match_memory_func = None

def abrt_match_register(insn, matches, to_add, slice):
    global abrt_match_memory_func
    for operand in insn.src_list:
        if operand.operand_type == OPERAND_TYPE_MEMORY:
            operand.match_function = abrt_match_memory_func

        if operand.operand_type == OPERAND_TYPE_REGISTER:
            operand.match_function = abrt_match_register

def abrt_match_memory_malloc_assert(insn, matches, to_add, slice):
    global found_instruction

    if slice.debugger.inside_file("malloc.c"):
        abrt_match_register(insn, matches, to_add, slice)
        return

    if found_instruction == False:
        slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                "This instruction caused the heap corruption:")
        slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, insn.to_string(False))
        insn.comment = insn.comment + " Cause of heap corruption"
        slice.stop()
        found_instruction = True

def abrt_match_memory_stack_chk_fail(insn, matches, to_add, slice):
    global found_instruction

    if found_instruction == False:
        slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                "This instruction caused the stack corruption:")
        insn.comment = insn.comment + " Cause of stack corruption"
        slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, insn.to_string(False))
        slice.stop()
        found_instruction = True

def abrt_init_callback(slice):
    global abrt_match_memory_func
    if gdb_signals[slice.signal] == "SIGABRT":
        opcode = ''
        
        # Based on static analysis of the usage of __malloc_assert, an ABRT
        # signal is raised based on the result of a cmp instruction. The goal, 
        # then is to calculate a slice based on the operands of the cmp 
        # instruction
        if slice.debugger.inside_function("__malloc_assert"):
            abrt_func = '__malloc_assert'
            opcode = 'cmp'
            abrt_match_memory_func = abrt_match_memory_malloc_assert 
            slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "Heap was corrupted somehow")
            slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "ABRT signal raised by __malloc_assert()")
            slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "Searching for cmp instruction that led to signal...")
        
        # Based on static analysis of the usage of __stack_chk_fail, an ABRT
        # signal is raised based on the result of an xor instruction. The goal,
        # then is to calculate a slice based on the operands of the xor 
        # instruction
        elif slice.debugger.inside_function("__stack_chk_fail"): 
            abrt_func = '__stack_chk_fail'
            opcode = 'xor'
            abrt_match_memory_func = abrt_match_memory_stack_chk_fail 
            slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "Stack was corrupted somehow")
            slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "ABRT signal raised by __stack_chk_fail()")
            slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "Searching for cmp instruction that led to signal...")
        else:
            print('Not inside a supported function')
            return

        # skip to the call to function that raised the SIGABRT
        while True:
            if not slice.reverse_step():
                slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        "Could not find call to %s()" % abrt_func)
                return
            insn_text = slice.debugger.disassemble(slice.pc)
           
            if insn_text.split()[0] != "call":
                continue
   
            if abrt_func in insn_text:
                break

        # Found the call to function, now to find the comparison instruction
        while True: 
            if not slice.reverse_step():
                slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        "Could not find %s instruction" % opcode)
                return
                    
            insn_text = slice.debugger.disassemble(slice.pc)

            if insn_text.split()[0] == opcode:
                break

        # Found the instruction which lead to function that caused sigabrt 
        # Add this to our slice
        slice.add_current_insn()
        slice.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
            "Ready to compute slice")
        for operand in slice.operand_list:
            if operand.operand_type == OPERAND_TYPE_MEMORY:
                operand.match_function = abrt_match_memory_func

            if operand.operand_type == OPERAND_TYPE_REGISTER:
                operand.match_function = abrt_match_register

init_callbacks.append(abrt_init_callback)
