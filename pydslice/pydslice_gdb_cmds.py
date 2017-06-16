# pydslice_gdb_cmds.py
#
# Defines GDB slice commands
#
# INSTALLATION: Copy/Move this file GDB's 'data-directory'/python/gdb/command 
#
# To find the location of GDB's data-directory, execute the following in gdb:
#     
#     show data-directory
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

import gdb
import binascii
import struct
import os
import sys
import traceback
from array import *

from pydslice import Slice
from pydslice.pydslice_debugger import * 

# Import pydslice plug-ins here:
import pydslice.pydslice_plugin_abrt

slice = None

class CmdSlice(gdb.Command):
    """Computes a slice"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE, True)

    def invoke (self, arg, from_tty):
        global slice
        try:
            if slice == None:
                gdb.write("Slice not initialized. Execute 'slice new' or " \
                        "'slice new crashed'\n")
                return
            if arg:
                gdb.write("Usage: slice\n")
                return

            gdb.write("Computing slice...\n")
            slice.compute_slice(False)

        except Exception:
            traceback.print_exc()

CmdSlice()

class CmdSliceSave(gdb.Command):
    """Saves slice information to html file"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice save", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_FILENAME)

    def invoke (self, arg, from_tty):
        global slice
        
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return
        try:
            if not arg:
                gdb.write("Usage: slice save <file path>\n")
            else:
                slice.save(arg)
        except Exception:
            traceback.print_exc()
CmdSliceSave()

class CmdSliceNew(gdb.Command):
    """Initializes Slice Computation"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice new", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE, True)

    def invoke (self, arg, from_tty):
        global slice
        try:
            slice = Slice()
        except Exception:
            traceback.print_exc()
CmdSliceNew()

class CmdSliceNewCrashed(gdb.Command):
    """Inits Slice Computation based on crash"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice new crashed", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        try:
            slice = Slice(crashed=True)
        except Exception:
            traceback.print_exc()

CmdSliceNewCrashed()

class CmdSliceStep(gdb.Command):
    """Step to next instruction in slice"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice step", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        try:
            if slice == None:
                gdb.write("Slice not initialized. Execute 'slice new' or " \
                       "'slice new crashed'\n")
                return
            gdb.write("Finding next slice instruction...\n")
            slice.compute_slice(True)
        except Exception:
            traceback.print_exc()

CmdSliceStep()

class CmdSliceOperand(gdb.Command):
    """Show tracked operands"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice operand", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE, True)

    def invoke (self, arg, from_tty):
        global slice

        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return

        slice.print_operand_list()

CmdSliceOperand()

class CmdSliceOperandAdd(gdb.Command):
    """Add operand to be tracked"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice operand add", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return
        
        if arg == "":
            gdb.write("Usage: slice operand add <expr>\n")
            return

        slice.add_expr_to_operand_list(arg)
CmdSliceOperandAdd()

class CmdSliceOperandDel(gdb.Command):
    """Remove operand from tracked list"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice operand delete", \
                gdb.COMMAND_OBSCURE, gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return
        
        if arg == "":
            gdb.write("Usage: slice operand del #\n")
            return
        slice.remove_operand_list_index(int(arg)-1)

CmdSliceOperandDel()

class CmdSliceOperandList(gdb.Command):
    """Show tracked operands"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice operand list", \
                gdb.COMMAND_OBSCURE, gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return

        slice.print_operand_list();

CmdSliceOperandList()

class CmdSliceFollow(gdb.Command):
    """Follow operand in slice"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice operand follow", \
                gdb.COMMAND_OBSCURE, gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return
        
        if arg == "":
            slice.set_followed_operand(None)
        else:
            slice.set_followed_operand(int(arg)-1)

CmdSliceFollow()

class CmdSliceInsn(gdb.Command):
    """Slice instruction commands"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice insn", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE, True)

    def invoke (self, arg, from_tty):
        global slice
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return
        
        slice.print_insn_list()

CmdSliceInsn()

class CmdSliceInsnList(gdb.Command):
    """List instructions in slice"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice insn list", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_SYMBOL)

    def invoke (self, arg, from_tty):
        global slice
        try:
            if slice == None:
                gdb.write("Slice not initialized. Execute 'slice new' or " \
                        "'slice new crashed'\n")
                return

            if arg == "":
                slice.print_insn_list()
                return
        except:
            traceback.print_exc()

        args = arg.split()
        if len(args) == 1:
            slice.print_insn_list(index=int(args[0]), count=1)
        elif len(args) == 2:
            start = int(args[0])
            num = int(args[1])
            slice.print_insn_list(index=start, count=num)
        else:
            gdb.write("Usage: slice insn list [index] [count]\n")

CmdSliceInsnList()

class CmdSliceInsnAdd(gdb.Command):
    """Add instruction to slice"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice insn add", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return
        slice.add_current_insn()

CmdSliceInsnAdd()

class CmdSliceInsnDel(gdb.Command):
    """Deletes instruction in slice"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice insn delete", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE)

    def invoke (self, arg, from_tty):
        global slice
        if slice == None:
            gdb.write("Slice not initialized. Execute 'slice new' or " \
                    "'slice new crashed'\n")
            return

        if arg == "":
            gdb.write("Usage: slice insn delete #\n") 
        else:
            slice.delete_insn(int(arg) - 1)

CmdSliceInsnDel()

class CmdSliceDebug(gdb.Command):
    """Slice debug commands"""

    def __init__ (self):
        gdb.Command.__init__(self, "slice debug", gdb.COMMAND_OBSCURE, \
                gdb.COMPLETE_NONE, True)
    
    def invoke (self, arg, from_tty):
        pass

CmdSliceDebug()

class CmdSliceDebugPrintLevel(gdb.Command):
    """Sets slice debug print level"""
    
    def __init__ (self):
        gdb.Command.__init__(self, "slice debug print_level", \
                gdb.COMMAND_OBSCURE) 

    def invoke (self, arg, from_tty):
        if "none" in arg:
            pydslice.pydslice_debugger.debug_print_level = \
                    DEBUG_PRINT_LEVEL_ALWAYS 
        elif "error" in arg:
            pydslice.pydslice_debugger.debug_print_level = \
                    DEBUG_PRINT_LEVEL_ERROR 
        elif "warning" in arg:
            pydslice.pydslice_debugger.debug_print_level = \
                    DEBUG_PRINT_LEVEL_WARNING 
        elif "info" in arg:
            pydslice.pydslice_debugger.debug_print_level = \
                    DEBUG_PRINT_LEVEL_INFO 
        elif "verbose" in arg:
            pydslice.pydslice_debugger.debug_print_level = \
                    DEBUG_PRINT_LEVEL_VERBOSE 
        else:
            pydslice.pydslice_debugger.debug_print_level = int(arg)

    def complete(self, text, word):
        return [x for x in ["none", "error", "warning", "info", "verbose"] \
                if x.startswith(text)]

CmdSliceDebugPrintLevel()

class CmdSliceDebugSymbolLevel(gdb.Command):
    """Sets slice debug symbol level"""
    
    def __init__ (self):
        gdb.Command.__init__(self, "slice debug symbol_level", \
                gdb.COMMAND_OBSCURE)

    def invoke (self, arg, from_tty):
        if "none" in arg:
            pydslice.pydslice_debugger.debug_symbol_level = \
                    DEBUG_SYMBOL_LEVEL_NONE 
        elif "line" in arg:
            pydslice.pydslice_debugger.debug_symbol_level = \
                    DEBUG_SYMBOL_LEVEL_LINES 
        elif "variables" in arg:
            pydslice.pydslice_debugger.debug_symbol_level = \
                    DEBUG_SYMBOL_LEVEL_VARIABLES 
        else:
            pydslice.pydslice_debugger.debug_symbol_level = int(arg)
    
    def complete(self, text, word):
        return [x for x in ["none", "line", "variables"] if x.startswith(text)]

CmdSliceDebugSymbolLevel()
