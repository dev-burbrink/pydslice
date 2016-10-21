# pydslice_debugger_gdb.py
#
# Debugger definitions for GDB 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

import gdb
import re

try:
    import pydslice_debugger
    from pydslice_debugger import *
    from pydslice_parser_x86 import Parser
    from pydslice_operand import *
except ImportError:
    import pydslice.pydslice_debugger
    from pydslice.pydslice_debugger import *
    from pydslice.pydslice_parser_x86 import Parser
    from pydslice.pydslice_operand import *

gdb_signals = [
    "",
    "SIGHUP",
    "SIGINT",
    "SIGQUIT",
    "SIGILL",
    "SIGTRAP",
    "SIGABRT",
    "SIGEMT",
    "SIGFPE",
    "SIGKILL",
    "SIGBUS",
    "SIGSEGV",
    "SIGSYS",
    "SIGPIPE",
    "SIGALRM",
    "SIGTERM",
    "SIGURG",
    "SIGSTOP",
    "SIGTSTP",
    "SIGCONT",
    "SIGCHLD",
    "SIGTTIN",
    "SIGTTOU",
    "SIGIO",
    "SIGXCPU",
    "SIGXFSZ",
    "SIGVTALRM",
    "SIGPROF",
    "SIGWINCH",
    "SIGLOST",
    "SIGUSR1",
    "SIGUSR2",
    "SIGPWR",
    "SIGPOLL",
    "SIGWIND",
    "SIGPHONE",
    "SIGWAITING",
    "SIGLWP",
    "SIGDANGER",
    "SIGGRANT",
    "SIGRETRACT",
    "SIGMSG",
    "SIGSOUND",
    "SIGSAK",
    "SIGPRIO",
    "SIG33",
    "SIG34",
    "SIG35",
    "SIG36",
    "SIG37",
    "SIG38",
    "SIG39",
    "SIG40",
    "SIG41",
    "SIG42",
    "SIG43",
    "SIG44",
    "SIG45",
    "SIG46",
    "SIG47",
    "SIG48",
    "SIG49",
    "SIG50",
    "SIG51",
    "SIG52",
    "SIG53",
    "SIG54",
    "SIG55",
    "SIG56",
    "SIG57",
    "SIG58",
    "SIG59",
    "SIG60",
    "SIG61",
    "SIG62",
    "SIG63",
    "SIGCANCEL",
    "SIG32",
    "SIG64",
    "SIG65",
    "SIG66",
    "SIG67",
    "SIG68",
    "SIG69",
    "SIG70",
    "SIG71",
    "SIG72",
    "SIG73",
    "SIG74",
    "SIG75",
    "SIG76",
    "SIG77",
    "SIG78",
    "SIG79",
    "SIG80",
    "SIG81",
    "SIG82",
    "SIG83",
    "SIG84",
    "SIG85",
    "SIG86",
    "SIG87",
    "SIG88",
    "SIG89",
    "SIG90",
    "SIG91",
    "SIG92",
    "SIG93",
    "SIG94",
    "SIG95",
    "SIG96",
    "SIG97",
    "SIG98",
    "SIG99",
    "SIG100",
    "SIG101",
    "SIG102",
    "SIG103",
    "SIG104",
    "SIG105",
    "SIG106",
    "SIG107",
    "SIG108",
    "SIG109",
    "SIG110",
    "SIG111",
    "SIG112",
    "SIG113",
    "SIG114",
    "SIG115",
    "SIG116",
    "SIG117",
    "SIG118",
    "SIG119",
    "SIG120",
    "SIG121",
    "SIG122",
    "SIG123",
    "SIG124",
    "SIG125",
    "SIG126",
    "SIG127",
    "SIGINFO",
    "NULL1",
    "NULL2",
    "EXC_BAD_ACCESS",
    "EXC_BAD_INSTRUCTION",
    "EXC_ARITHMETIC",
    "EXC_EMULATION",
    "EXC_SOFTWARE",
    "EXC_BREAKPOINT",
    "NULL3"
    ]

class GDBDebugger(Debugger):
    architecture = None

    # Initializes the gdb debugger interface
    def __init__(self):
        self.architecture = gdb.selected_frame().architecture()
        
        # our parser expects certain settings from gdb
        gdb.execute("set radix 0x10", False, to_string=True)
        gdb.execute("set disassembly-flavor intel", False, to_string=True)
    
    # Prints string to gdb based on current debug level
    def print_msg(self, level, str):
        try:
            current_level = pydslice_debugger.debug_print_level
        except NameError:
            current_level = pydslice.pydslice_debugger.debug_print_level

        if level <= current_level:
            gdb.write(str + '\n')
            gdb.flush()

    # Gets the value of $pc
    def get_pc(self):
        return gdb.selected_frame().pc()

    # Reverses execution of the debugged process by one step
    def reverse_step(self):
        gdb.execute("reverse-stepi", False, to_string=True)

    # Executes the debugged process by one step
    def step(self):
        gdb.execute("stepi", False, to_string=True)

    # Returns the architecture for the process
    def get_architecture(self):
        return self.architecture.name()

    # Disassembles the instruction at pc
    def disassemble(self, pc):
        return self.architecture.disassemble(pc)[0]['asm'].split('#')[0]
   
    # Gets symbol information about the current line of code
    def get_line_info(self):
        try:
            current_level = pydslice_debugger.debug_symbol_level
        except NameError:
            current_level = pydslice.pydslice_debugger.debug_symbol_level

        if  current_level< DEBUG_SYMBOL_LEVEL_LINES:
            return "","",""

        try:
            infoline = gdb.execute("info line", False, True)
            m = re.match("Line ([0-9]+) of \"(.*)\" .* (<.*>)", infoline, \
                    re.I | re.M)
            line = "%d" % (int(m.group(1)) - 1)
            filename = m.group(2)
            sym = m.group(3)
        except:
            line = ""
            filename = ""
            sym = ""

        return line,filename,sym

    # Get symbol info for address
    def get_addr_info(self, address):
        try:
            current_level = pydslice_debugger.debug_symbol_level
        except:
            current_level = pydslice.pydslice_debugger.debug_symbol_level

        if current_level < DEBUG_SYMBOL_LEVEL_VARIABLES:
            return ''

        addr = '0x%x' % address
        
        # Is it a local?
        all_locals = gdb.execute("info locals", False, True)

        for var in all_locals.split("\n"):
            tok = var.split()
            if len(tok) < 3:
                continue

            name = tok[0]
            val = tok[2]
            if addr == val:
                return '<' + name + '>'
            try:
                ref = gdb.parse_and_eval('&' + name).__str__()
                if addr == ref:
                    return '<&' + name + '>'
            except:
                pass
        
        # Is it an arg?
        all_args = gdb.execute("info args", False, True)

        for var in all_args.split("\n"):
            tok = var.split()
            if len(tok) < 3:
                continue
            name = tok[0]
            val = tok[2]
            if addr == val:
                return '<' + name + '>'
            
            try:
                ref = gdb.parse_and_eval('&' + name).__str__()
                if addr == ref:
                    return '<&' + name + '>'
            except:
                pass

        # Is it a global?
        all_globals = gdb.execute("info variables", False, True)

        for var in all_globals.split("\n")[3:]:
            tok = var.split()
            if len(tok) < 2:
                continue
            name = tok[1]
            val = tok[0]
            if addr == val:
                return '<' + name + '>'
            try:
                ref = gdb.parse_and_eval('&' + name).__str__()
                if addr == ref:
                    return '<&' + name + '>'
            except:
                pass

        return ''
 
    # Evaluates an expression
    def evaluate(self, expr):
        try:
            val = int(gdb.parse_and_eval(expr).__str__().split()[0], 16)
            return val
        except:
            self.print_msg(DEBUG_PRINT_WARNING, "GDB failed to parse arg %s" %expr)
            return 0

    # Evaluates an expression as an address
    def evaluate_as_address(self, expr):
        value = gdb.parse_and_eval(expr).__str__()
        m = re.match(".*(0x[0-9a-f]+).*", value, re.M | re.I)
        ret = 0
        try:
            ret = int(m.group(1),16)
        except:
            pass
        return ret
   
    # Retrieves a 1 byte value from memory of the debugged process
    def read_byte(self, address):
        try:
            mem = gdb.selected_inferior().read_memory(int(address,16), 1)
            return int(mem.tobytes()[0])
        except Exception:
            return 0

    # Gets the signal value for the debugged process
    def get_signal(self):
        sig = int(gdb.parse_and_eval("$_siginfo.si_signo").__str__(), 16)
        return sig

    # Determines if a given address is in executable memory
    def is_address_executable(self, address):
        all_sections = gdb.execute("maintenance info sections", False, True)
        sections = all_sections.split("\n")
        for section in sections:
            if "CODE" in section:
                s = section.split()
                if "->" in s[0]:
                    mem_range = s[0].split("->")
                else:
                    mem_range = s[1].split("->")
                        
                # is the address in the memory range of the section?
                if address >= int(mem_range[0],16) and \
                        address <= int(mem_range[1],16):
                    return True 
        return False 

    # Performs initial callbacks
    def do_init_callbacks(self, init_callbacks, slice):
        for callback in init_callbacks:
            callback(slice)

    # Performs additional setup tasks for the debugger
    def setup_slice(self, slice, init_callbacks):
        
        slice.signal = self.get_signal()
        pc = self.get_pc()
        
        if gdb_signals[slice.signal] == "SIGABRT":
            # Nothing to do with current instruction. Just call callbacks
            self.reverse_step()
            self.do_init_callbacks(init_callbacks, slice)

        elif gdb_signals[slice.signal] == "SIGBUS":
            crash_insn = slice.parser.parse_insn(pc)
            line,file,sym = self.get_line_info()
            crash_insn.set_line_info(line,file,sym)
            slice.parser.monitor_stack = False
            slice.add_insn(crash_insn) 
            
            for operand in crash_insn.src_list:
                if crash_insn.opcode in ["ret", "leave", "pop", "push"] or \
                        (operand.operand_type == OPERAND_TYPE_REGISTER and \
                        operand.is_memory):
                    # With a SIGBUS, we tried to access misaligned memory or a 
                    # non-existant physical address. 
                    # These operands were used in the invalid dereference
                    slice.add_operand(operand)
            self.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "Signal: SIGBUS\n");
            slice.print_operand_list()
            slice.print_insn_list(verbose=False)
            self.reverse_step()
            self.do_init_callbacks(init_callbacks, slice)

        elif gdb_signals[slice.signal] == "SIGSEGV":
            crash_insn = slice.parser.parse_insn(pc)
            line,file,sym = self.get_line_info()
            crash_insn.set_line_info(line,file,sym)
            slice.parser.monitor_stack = False
            slice.add_insn(crash_insn)
            self.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, crash_insn.to_string(False)) 
            for operand in crash_insn.src_list:
                if crash_insn.opcode in ["ret", "leave", "pop", "push"] or \
                        (operand.operand_type == OPERAND_TYPE_REGISTER and \
                        operand.is_memory):
                    # With a SIGSEGV, we tried to access misaligned memory or a
                    # non-existant physical address. 
                    # These operands were used in the invalid dereference
                    slice.add_operand(operand)
                    if slice.parser.is_register_pointer(operand.address):
                        slice.parser.monitor_stack = True
                        print("Monitoring stack")

            self.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, "Signal: SIGSEGV\n");
            slice.print_operand_list()
            slice.print_insn_list(verbose=False)
            self.reverse_step()
            self.do_init_callbacks(init_callbacks, slice)
             
        elif gdb_signals[slice.signal] == "SIGFPE":
            crash_insn = slice.parser.parse_insn(pc)
            line,file,sym = self.get_line_info()
            crash_insn.set_line_info(line,file,sym)
            slice.parser.monitor_stack = False
            slice.add_insn(crash_insn)
            for operand in crash_insn.src_list:
                if operand.operand_type == OPERAND_TYPE_REGISTER and \
                        operand.is_memory:
                    # With a SIGSEGV, we tried to access misaligned memory or a
                    # non-existant physical address. 
                    # These operands were used in the invalid dereference
                    slice.add_operand(operand)

            self.reverse_step()
            self.do_init_callbacks(init_callbacks, slice)
        else:

            # is $pc is in a bad spot
            if self.is_address_executable(pc) == False:
                if "64" in self.get_architecture():
                    operand = Operand(OPERAND_TYPE_REGISTER, False, "$rip", pc)
                    operand.base_register = ['rip']
                else:
                    operand = Operand(OPERAND_TYPE_REGISTER, False, "$eip", pc)
                    operand.base_register = ['eip']
                slice.add_operand(operand)
                slice.parser.monitor_stack = True
                self.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        "$pc (0x%x) is invalid" % pc)
                slice.print_operand_list()
                slice.print_insn_list(verbose=False)
                self.do_init_callbacks(init_callbacks, slice)
            else:
                self.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                        "Unhandled signal %d : %s" % (slice.signal, \
                        gdb_signals[slice.signal]))
        
        self.reverse_step()

    # Determines if pc is inside specified file
    def inside_file(self, filename):
        frame = gdb.selected_frame()
        while frame:
            sal = frame.find_sal()
            if sal and sal.symtab and sal.symtab.filename == filename:
                return True
            frame = frame.older()
        return False
    
    # Determines if pc is inside specified function
    def inside_function(self, function_name):
        frame = gdb.selected_frame()
        while frame:
            frame_function = frame.name()
            if frame_function:
                if function_name == frame_function.__str__():
                    return True
            frame = frame.older()
        return False
