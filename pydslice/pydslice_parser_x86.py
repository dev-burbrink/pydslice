# pydslice_parser_x86.py
#
# Parser for x86 architecture 
#
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
#

import re

try:
    from pydslice_insn import Insn
    from pydslice_debugger import *
    from pydslice_insn import *
    from pydslice_parser import Parser
    from pydslice_operand import *
    from pydslice_x86_defs import *
except ImportError:
    from pydslice.pydslice_insn import Insn
    from pydslice.pydslice_debugger import *
    from pydslice.pydslice_insn import *
    from pydslice.pydslice_parser import Parser
    from pydslice.pydslice_operand import *
    from pydslice.pydslice_x86_defs import *

class Parser_x86(Parser):
    debugger = None
    monitor_stack = False
    registers = None
    syscall_table = None
    last_eax = 0
    x86_parse_opcode_fxn = None

    # Initializes the parser
    def __init__(self, debugger):
        self.debugger = debugger
        self.monitor_stack = False 
        self.registers = x86_registers
        self.syscall_table = x86_syscall_table
        self.last_eax = 0
        self.x86_parse_opcode_fxn = x86_parse_opcode_fxn

    # Gets a register and its value
    def get_reg(self, arg):
        if arg.startswith("eiz"):
            return "$eiz",0

        if arg.startswith("xmm"):
            try:
                base = self.registers[arg[:5]]
                value = self.debugger.evaluate("$" + arg[:5] + ".uint128")
                address = "$" + arg[:5]
                return address,value
            except:
                pass

            try:
                base = self.registers[arg[:4]]
                value = self.debugger.evaluate("$" + arg[:4] + ".uint128")
                address = "$" + arg[:4]
                return address,value
            except:
                return "","" 
        try:
            base = self.registers[arg[:3]]
            value = self.debugger.evaluate("$" + arg[:3])
            address = "$" + arg[:3] 
            return address,value
        except:
            pass

        try:
            base = self.registers[arg[:2]]
            value = self.debugger.evaluate("$" + arg[:2])
            address = "$" + arg[:2] 
            return address,value
        except:
            pass
        return "",""

    # Determines if the register is a 'pointer' register
    def is_register_pointer(self, reg):
        return reg in ["$ebp", "$esp", "$eip"] 

    # Attempt to infer pointer size from instruction opcode
    def get_ptr_size_from_insn(self, insn):
        return 4

    # Determine memory reference size by PTR argument
    def get_ptr_size(self, arg):
        if arg.startswith("BYTE"):
            return 1
        if arg.startswith("WORD"):
            return 2
        if arg.startswith("DWORD"):
            return 4
        if arg.startswith("QWORD"):
            return 8
        if arg.startswith("XMMWORD"):
            return 16
        if arg.startswith("OWORD"):
            return 16
        if arg.startswith("TWORD"):
            return 10
        if arg.startswith("FWORD"):
            return 6

        self.debugger.print_msg(DEBUG_PRINT_LEVEL_WARNING, "Unknown ptr %s" % arg)
        return 0

    # Parse x86 blend opcodes
    def parse_blend(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_DST)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("xmm0", insn, OPERAND_DIRECTION_SRC)
 
    # Parse x86 movs opcode
    def parse_movs(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_DST)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
        
    # Parse x86 movsb opcode
    def parse_movsb(self, insn, args):
        self.parse_arg("BYTE PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("BYTE PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 movsw opcode
    def parse_movsw(self, insn, args):
        self.parse_arg("WORD PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 movsd opcode
    def parse_movsd(self, insn, args):
        self.parse_arg("DWORD PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)

    # Parse x86 movsq opcode
    def parse_movsq(self, insn, args):
        self.parse_arg("QWORD PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("QWORD PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 stosb opcode
    def parse_stosb(self, insn, args):
        self.parse_arg("BYTE PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("al", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
 
    # Parse x86 stosw opcode
    def parse_stosw(self, insn, args):
        self.parse_arg("WORD PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("ax", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
 
    # Parse x86 stosd opcode
    def parse_stosd(self, insn, args):
        self.parse_arg("DWORD PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("eax", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)

    # Parse x86 stosq opcode
    def parse_stosq(self, insn, args):
        self.parse_arg("QWORD PTR [edi]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("eax", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 lodsb opcode
    def parse_lodsb(self, insn, args):
        self.parse_arg("BYTE PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("al", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
 
    # Parse x86 lodsw opcode
    def parse_lodsw(self, insn, args):
        self.parse_arg("WORD PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("ax", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
 
    # Parse x86 lodsd opcode
    def parse_lodsd(self, insn, args):
        self.parse_arg("DWORD PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("eax", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 lodsq opcode
    def parse_lodsq(self, insn, args):
        self.parse_arg("QWORD PTR [esi]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("eax", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 scasb opcode
    def parse_scasb(self, insn, args):
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
 
    # Parse x86 scasw opcode
    def parse_scasw(self, insn, args):
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
 
    # Parse x86 scasd opcode
    def parse_scasd(self, insn, args):
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 scasq opcode
    def parse_scasq(self, insn, args):
        self.parse_arg("esi", insn, OPERAND_DIRECTION_BOTH)
    
    # Parse x86 aad opcode
    def parse_aad(self, insn, args):
        self.parse_arg("ah", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("al", insn, OPERAND_DIRECTION_BOTH)

    # Parse x86 enter opcode
    def parse_enter(self, insn, args):
        self.parse_arg("ebp", insn)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [ebp]", insn, OPERAND_DIRECTION_SRC)
        
    # Parse x86 leave opcode
    def parse_leave(self, insn, args):
        self.parse_arg("ebp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        
    # Parse x86 ret opcode
    def parse_ret(self, insn, args):
        self.parse_arg("eip", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)

    # Parse x86 iret opcode
    def parse_iret(self, insn, args):
        self.parse_arg("eip", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp+4]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp+8]", insn, OPERAND_DIRECTION_SRC)
 
    # Parse x86 retf opcode
    def parse_retf(self, insn, args):
        self.parse_arg("eip", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp+4]", insn, OPERAND_DIRECTION_SRC)
 
    # Parse x86 pushf opcode
    def parse_pushf(self, insn, args):
        self.parse_arg("WORD PTR [esp-4]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
 
    # Parse x86 pushfd opcode
    def parse_pushfd(self, insn, args):
        self.parse_arg("DWORD PTR [esp-4]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
 
    # Parse x86 lahf opcode
    def parse_lahf(self, insn, args):
        self.parse_arg("ah", insn, OPERAND_DIRECTION_DST)
    
    # Parse x86 push opcode
    def parse_push(self, insn, args):
        self.parse_arg("DWORD PTR [esp-4]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_SRC)
    
    # Parse x86 pusha opcode
    def parse_pusha(self, insn, args):
        self.parse_arg("WORD PTR [esp-2]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("ax", insn, OPERAND_DIRECTION_SRC)
        
        self.parse_arg("WORD PTR [esp-4]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("cx", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [esp-6]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("dx", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [esp-8]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("bx", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [esp-10]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("sp", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [esp-12]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("bp", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [esp-14]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("si", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("WORD PTR [esp-16]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("di", insn, OPERAND_DIRECTION_SRC)
 
    # Parse x86 pushad opcode
    def parse_pushad(self, insn, args):
        self.parse_arg("DWORD PTR [esp-4]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("eax", insn, OPERAND_DIRECTION_SRC)
        
        self.parse_arg("DWORD PTR [esp-8]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("ecx", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp-12]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("edx", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp-16]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("ebx", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp-20]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp-24]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("ebp", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp-28]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("DWORD PTR [esp-32]", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_SRC)

    # Parse x86 popa opcode
    def parse_popa(self, insn, args):
        self.parse_arg("WORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("ax", insn, OPERAND_DIRECTION_DST)
        
        self.parse_arg("WORD PTR [esp-2]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("cx", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("WORD PTR [esp-4]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("dx", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("WORD PTR [esp-6]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("bx", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("WORD PTR [esp-8]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("sp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("WORD PTR [esp-10]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("bp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("WORD PTR [esp-12]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("si", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("WORD PTR [esp-14]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("di", insn, OPERAND_DIRECTION_DST)
 
    # Parse x86 popad opcode
    def parse_popad(self, insn, args):
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("eax", insn, OPERAND_DIRECTION_DST)
        
        self.parse_arg("DWORD PTR [esp-4]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("ecx", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-8]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("edx", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-12]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("ebx", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-16]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-20]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("ebp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-24]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esi", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-28]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("edi", insn, OPERAND_DIRECTION_DST)
        
    # Parse x86 pop opcode
    def parse_pop(self, insn, args):
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_DST)

    # Parse x86 popf opcode
    def parse_popf(self, insn, args):
        self.parse_arg("WORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)

    # Parse x86 popfd opcode
    def parse_popfd(self, insn, args):
        self.parse_arg("DWORD PTR [esp]", insn, OPERAND_DIRECTION_SRC)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)

    # Parse x86 call opcode
    def parse_call(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_SRC) # in
        self.parse_arg("eip", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("esp", insn, OPERAND_DIRECTION_DST)
        self.parse_arg("DWORD PTR [esp-4]", insn, OPERAND_DIRECTION_DST)

    # Parse convert opcodes: cdq cdqe cwde cbw cwd
    def parse_convert(self, insn, args):
        self.parse_arg("eax", insn, OPERAND_DIRECTION_BOTH)

    # Parse x86 opcode of format <opcode> dest,src
    def parse_ds(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_DST)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
        
    # Parse x86 opcode of format <opcode> dest/src
    def parse_b(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_BOTH)
        
    # Parse x86 opcode of format <opcode> dest/src,dest/src
    def parse_bb(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_BOTH)
        
    # Parse x86 opcode of format <opcode> dest/src,src
    def parse_bs(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
        
    # Parse x86 opcode of format <opcode> src
    def parse_s(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_SRC)
        
    # Parse x86 opcode of format <opcode> dest 
    def parse_d(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_DST)
        
    # Parse x86 opcode of format <opcode> src,src 
    def parse_ss(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_SRC)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
          
    # Parse x86 opcode of format <opcode> dest,src,src
    def parse_dss(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_DST)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
        self.parse_arg(args[2], insn, OPERAND_DIRECTION_SRC)
 
    # Parse x86 opcode of format <opcode> both,src,src
    def parse_bss(self, insn, args):
        self.parse_arg(args[0], insn, OPERAND_DIRECTION_BOTH)
        self.parse_arg(args[1], insn, OPERAND_DIRECTION_SRC)
        self.parse_arg(args[2], insn, OPERAND_DIRECTION_SRC)
    
    # Parse x86 opcode of format <opcode> (or just ignore instruction)
    def parse_none(self, insn, args):
        pass
  
    def parse_syscall_args(self, insn, args, eax):
        
        # Don't do anything if we don't understand the syscall
        if not eax in self.syscall_table.keys():
            return
        
        # Based on syscall, add appropriate src args
        self.parse_arg("eax", insn, OPERAND_DIRECTION_DST)
        num_args,name = self.syscall_table[eax]
        
        if num_args >= 1:
            self.parse_arg("ebx", insn, OPERAND_DIRECTION_SRC)
        if num_args >= 2:
            self.parse_arg("ecx", insn, OPERAND_DIRECTION_SRC)
        if num_args >= 3:
            self.parse_arg("edx", insn, OPERAND_DIRECTION_SRC)
        if num_args >= 4:
            self.parse_arg("esi", insn, OPERAND_DIRECTION_SRC)
        if num_args >= 5:
            self.parse_arg("edi", insn, OPERAND_DIRECTION_SRC)
        if num_args >= 6:
            self.parse_arg("ebp", insn, OPERAND_DIRECTION_SRC)
        insn.comment = insn.comment + "<" + name + ">"

    # Parse syscall opcode
    def parse_syscall(self, insn, args):
        
        # Get EAX
        eax = self.debugger.evaluate('$eax')
        
        # Determine if syscall requires us to do anything special
        # For now, only read() is special
        if eax == 3: # read
            # last_eax shows how many bytes were read or if the read failed
            if self.last_eax > 0:
                # Add address pointed to by $ecx
                self.parse_mem_addr_value("[ecx]", self.last_eax, insn, \
                        OPERAND_DIRECTION_DST)
       
        self.parse_syscall_args(insn, args, eax)
            
    # Error parsing instruction 
    def parse_error(self, insn, args):
        self.debugger.print_msg(DEBUG_PRINT_LEVEL_ERROR, \
                "Got an Error - insn %s" % insn.text)
    
    # Parses opcode argument as memory type
    def parse_mem_addr_value(self, arg, size, insn, operand_direction):
        i = 0
        expr = ""
        if arg[i] == '[':
            i = i + 1
        
        length = len(arg)

        while i < length and arg[i] != ']':
            # Do we have an operator?
            if arg[i] == '+' or arg[i] == '-' or arg[i] == '*':
                expr = expr + arg[i]
                i = i + 1
       
            # Do we have an immediate?
            if (arg[i] == '0' and arg[i+1] == 'x') or \
                    (arg[i] >= '0' and arg[i] <= '9'):
                m = re.match('([0x]*[0-9a-f]+).*', arg[i:], re.M | re.I)
                expr = expr + m.group(1)
                i = i + len(m.group(1))
                continue
            
            # Do we have a segment reference
            if arg[i:i+3] == "ds:" and arg[i+3] >= '0' and arg[i+3] <= '9':
                i = i + 3 
                m = re.match('([0x]*[0-9a-f]+).*', arg[i:], re.M | re.I)
                expr = expr + m.group(1)
                i = i + len(m.group(1))
                continue

            # Do we have a register?
            reg,reg_value = self.get_reg(arg[i:])

            if reg != "":
                if reg == "$eiz":
                    expr = expr + "0"
                    i = i + len(reg) - 1
                    continue
                 
                if self.is_register_pointer(reg):
                    reg_value = self.debugger.evaluate_as_address(reg)
                    expr = expr + ("0x%x"%reg_value)
                    i = i + len(reg) - 1
                else:    
                    expr = expr + reg
                    i = i + len(reg) - 1
                
                operand = Operand(OPERAND_TYPE_REGISTER, True, reg, reg_value)
                operand.base_register = self.registers[reg[1:]]
                insn.add_operand(operand, OPERAND_DIRECTION_SRC)
                continue
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_VERBOSE, \
                    "Unknown Operand: " + arg[i:] + " - Insn: " + insn.text)
            return

        address = self.debugger.evaluate_as_address(expr)
        for i in range(0, size):
            addr = "0x%x" % (address + i) 
            value = self.debugger.read_byte(addr)
            operand = Operand(OPERAND_TYPE_MEMORY, False, address+i, value)
            insn.add_operand(operand, operand_direction)

    # Parses the argument to an opcode
    def parse_arg(self, arg, insn, operand_direction):
        if "gs:" in arg:
            return
            
        # is it a memory reference 
        if arg.find(":0x") == 2:
            size = self.get_ptr_size_from_insn(insn)
            self.parse_mem_addr_value(arg, size, insn, operand_direction)
            
        elif arg.startswith("["):
            size = self.get_ptr_size_from_insn(insn)
            self.parse_mem_addr_value(arg, size, insn, operand_direction)
            
        elif "PTR" in arg:
            tok = arg.split()
            size = self.get_ptr_size(tok[0])
            
            if size == 0:
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_VERBOSE, \
                        "Unknown size: %s - Insn: %s" % (tok[0], insn.text))
            
            if tok[2] == "gs:":
                return
            
            if tok[2][2] == ":":
                self.parse_mem_addr_value(tok[2][3:], size, insn, \
                        operand_direction)
            else:
                self.parse_mem_addr_value(tok[2], size, insn, \
                        operand_direction)
               
        elif ord(arg[0]) >= ord('0') and ord(arg[0]) <= ord('9'):
            if arg[1] == 'x':
                base = 16
            else:
                base = 10
            m = re.match("^(0x)*([0-9a-f]+)", arg, re.M | re.I)
            num = m.group(1) + m.group(2)
            operand = Operand(OPERAND_TYPE_IMMEDIATE, False, 0, int(num, base))
            insn.add_operand(operand, operand_direction)
        
        # Is it a register ?
        elif arg in self.registers.keys():
            if arg == "eiz":
                operand = Operand(OPERAND_TYPE_IMMEDIATE, False, 0, 0)
                operand.base_register = self.registers[arg]
                insn.add_operand(operand, operand_direction)
            else:
                reg_addr,reg_value = self.get_reg(arg)

                operand = Operand(OPERAND_TYPE_REGISTER, False, 
                                reg_addr, reg_value)
                operand.base_register = self.registers[arg]
                insn.add_operand(operand, operand_direction)
        else:
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_VERBOSE, \
                    "Unknown Operand: " + arg + " - Insn: " + insn.text)
   
    # Adds an expression to a list of operand
    def add_expr_to_operand_list(self, expr, operand_list):
        # is it a register?
        if expr[0] == '$' and expr[1:] in self.registers.keys():
            address,value = self.get_reg(expr[1:])
            operand_type = OPERAND_TYPE_REGISTER
            operand = Operand(operand_type, False, address, value)
            operand.base_register = self.registers[expr[1:]]
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "added register %s" % address)
        else:
            # assume expression that is memory address - may want size
            address = self.debugger.evaluate_as_address(expr)
            value = self.debugger.read_byte(address)
            operand_type = OPERAND_TYPE_MEMORY
            operand = Operand(operand_type, False, address, value)
            self.debugger.print_msg(DEBUG_PRINT_LEVEL_ALWAYS, \
                    "added address %s" % address)

        operand_list.append(operand)

    # Detremines if a operand should be considered for a slice
    def ignore_operand(self, operand):
        if operand.operand_type == OPERAND_TYPE_IMMEDIATE:
            return True 
        if self.monitor_stack == False:
            if operand.operand_type == OPERAND_TYPE_REGISTER and \
                    (operand.address == "$eip" or operand.address == "$ebp" \
                    or operand.address == "$esp"):
                return True
        return False

    # Parses an x86 instruction
    def parse_insn(self, pc):
        line,file,sym = self.debugger.get_line_info() 
        insn = Insn(pc)
        insn.text = self.debugger.disassemble(pc)
        tok = insn.text.split(' ', 1)
        insn.opcode = tok[0]
        if insn.opcode in ["rep", "repz", "repnz"]:
            tok = insn.text.split(' ', 2)
            insn.opcode2 = tok[1]
            if len(tok) > 2:
                args = tok[2].strip().split(",")
            else:
                args = ""
            if insn.opcode2 in self.x86_parse_opcode_fxn.keys():
                self.x86_parse_opcode_fxn[insn.opcode2](self, insn, args)
            else:
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_VERBOSE, \
                        "Unknown Opcode: %s - Insn: %s" % \
                        (insn.opcode2, insn.text))
        else:
            if len(tok) > 1:
                args = tok[1].strip().split(",")
            else:
                args = ""
            
            if insn.opcode in self.x86_parse_opcode_fxn.keys():
                self.x86_parse_opcode_fxn[insn.opcode](self, insn, args)
            else:
                self.debugger.print_msg(DEBUG_PRINT_LEVEL_VERBOSE, \
                        "Unknown Opcode: %s - Insn: %s" % \
                        (insn.opcode, insn.text))
        
        return insn 
    
    # Performs any additional tasks after performing a slice step
    def step_cleanup(self):
        self.last_eax = self.debugger.evaluate('$eax')

x86_parse_opcode_fxn = {
    'aaa'  : Parser_x86.parse_none,
    'aad'  : Parser_x86.parse_aad,
    'aam'  : Parser_x86.parse_none,
    'aas'  : Parser_x86.parse_none,
    'adc' : Parser_x86.parse_bs,
    'add' : Parser_x86.parse_bs,
    'addsubpd' : Parser_x86.parse_bs,
    'addsubps' : Parser_x86.parse_bs,
    'and' : Parser_x86.parse_bs,
    'arpl'  : Parser_x86.parse_none,
    'blendpd' : Parser_x86.parse_blend,
    'blendps' : Parser_x86.parse_blend,
    'blendvpd' : Parser_x86.parse_blend,
    'blendvps' : Parser_x86.parse_blend,
    'bound'  : Parser_x86.parse_none,
    'bsf' : Parser_x86.parse_ds,
    'bsr' : Parser_x86.parse_ds,
    'bswap' : Parser_x86.parse_b,
    'bt' : Parser_x86.parse_none,
    'callf'  : Parser_x86.parse_call,
    'calln'  : Parser_x86.parse_call,
    'call' : Parser_x86.parse_call,
    'cbw' : Parser_x86.parse_convert,
    'cdqe' : Parser_x86.parse_convert,
    'cdq' : Parser_x86.parse_convert,
    'clc' : Parser_x86.parse_none,
    'cld' : Parser_x86.parse_none,
    'cli' : Parser_x86.parse_none,
    'clts' : Parser_x86.parse_none,
    'cmc' : Parser_x86.parse_none,
    'cmovae' : Parser_x86.parse_ds,
    'cmova' : Parser_x86.parse_ds,
    'cmovbe' : Parser_x86.parse_ds,
    'cmovb' : Parser_x86.parse_ds,
    'cmove' : Parser_x86.parse_ds,
    'cmovne' : Parser_x86.parse_ds,
    'cmovns' : Parser_x86.parse_ds,
    'cmovs' : Parser_x86.parse_ds,
    'cmp' : Parser_x86.parse_ss,
    'cmppd' : Parser_x86.parse_bs,
    'cmpps' : Parser_x86.parse_bs,
    'cmpsb' : Parser_x86.parse_none,
    'cmpsd' : Parser_x86.parse_bs,
    'cmpsd' : Parser_x86.parse_none,
    'cmps' : Parser_x86.parse_none,
    'cmpsq' : Parser_x86.parse_none,
    'cmpss' : Parser_x86.parse_bs,
    'cmpsw' : Parser_x86.parse_none,
    'cmpxchg' : Parser_x86.parse_ss,
    'comisd' : Parser_x86.parse_ss,
    'comiss' : Parser_x86.parse_ss,
    'cvtdq2pd' : Parser_x86.parse_ds,
    'cvtdq2ps' : Parser_x86.parse_ds,
    'cvtpd2dq' : Parser_x86.parse_ds,
    'cvtpd2pi' : Parser_x86.parse_ds,
    'cvtpd2ps' : Parser_x86.parse_ds,
    'cvtpi2pd' : Parser_x86.parse_ds,
    'cvtpi2ps' : Parser_x86.parse_ds,
    'cvtpi2sd' : Parser_x86.parse_ds,
    'cvtpi2ss' : Parser_x86.parse_ds,
    'cvtps2dq' : Parser_x86.parse_ds,
    'cvtps2pd' : Parser_x86.parse_ds,
    'cvtps2pi' : Parser_x86.parse_ds,
    'cvtsd2pi' : Parser_x86.parse_ds,
    'cvtsd2ss' : Parser_x86.parse_ds,
    'cvtss2pi' : Parser_x86.parse_ds,
    'cvtss2sd' : Parser_x86.parse_ds,
    'cvttpd2dq' : Parser_x86.parse_ds,
    'cvttpd2pi' : Parser_x86.parse_ds,
    'cvttps2dq' : Parser_x86.parse_ds,
    'cvttps2pi' : Parser_x86.parse_ds,
    'cvttsd2pi' : Parser_x86.parse_ds,
    'cvttss2pi' : Parser_x86.parse_ds,
    'cwde' : Parser_x86.parse_convert,
    'cwd' : Parser_x86.parse_convert,
    'daa'  : Parser_x86.parse_none,
    'das'  : Parser_x86.parse_none,
    'dec' : Parser_x86.parse_b,
    'div' : Parser_x86.parse_s,
    'dppd' : Parser_x86.parse_bss,
    'dpps' : Parser_x86.parse_bss,
    'enter' : Parser_x86.parse_enter,
    'extractps' : Parser_x86.parse_dss,
    'fimul' : Parser_x86.parse_s,
    'fwait'  : Parser_x86.parse_none,
    'haddpd' : Parser_x86.parse_bs,
    'haddps' : Parser_x86.parse_bs,
    'hlt' : Parser_x86.parse_none,
    'hsubpd' : Parser_x86.parse_bs,
    'hsubps' : Parser_x86.parse_bs,
    'idiv' : Parser_x86.parse_s,
    'imul' : Parser_x86.parse_none,
    'inc' : Parser_x86.parse_b,
    'in' : Parser_x86.parse_none,
    'insb' : Parser_x86.parse_none,
    'insd' : Parser_x86.parse_none,
    'insertps' : Parser_x86.parse_dss,
    'insw' : Parser_x86.parse_none,
    'int1' : Parser_x86.parse_none,
    'into'  : Parser_x86.parse_none,
    'int' : Parser_x86.parse_none,
    'iret' : Parser_x86.parse_iret,
    'jae' : Parser_x86.parse_s,
    'ja' : Parser_x86.parse_s,
    'jbe' : Parser_x86.parse_s,
    'jb' : Parser_x86.parse_s,
    'jcxz' : Parser_x86.parse_s,
    'jecxz' : Parser_x86.parse_s,
    'je' : Parser_x86.parse_s,
    'jeq' : Parser_x86.parse_s,
    'jge' : Parser_x86.parse_s,
    'jg' : Parser_x86.parse_s,
    'jle' : Parser_x86.parse_s,
    'jl' : Parser_x86.parse_s,
    'jmpf' : Parser_x86.parse_s,
    'jmpn' : Parser_x86.parse_s,
    'jmp' : Parser_x86.parse_s,
    'jne' : Parser_x86.parse_s,
    'jno' : Parser_x86.parse_s,
    'jns' : Parser_x86.parse_s,
    'jo' : Parser_x86.parse_s,
    'jpe' : Parser_x86.parse_s,
    'jpo' : Parser_x86.parse_s,
    'jp' : Parser_x86.parse_s,
    'jrcxz' : Parser_x86.parse_s,
    'js' : Parser_x86.parse_s,
    'lahf'  : Parser_x86.parse_lahf,
    'lar' : Parser_x86.parse_none,
    'lddqu' : Parser_x86.parse_ds,
    'lds' : Parser_x86.parse_ds,
    'lea' : Parser_x86.parse_ds,
    'leave' : Parser_x86.parse_leave,
    'les' : Parser_x86.parse_ds,
    'lgs' : Parser_x86.parse_ds,
    'lldt' : Parser_x86.parse_s,
    'lodsb' : Parser_x86.parse_lodsb,
    'lodsd' : Parser_x86.parse_lodsd,
    'lodsq' : Parser_x86.parse_lodsq,
    'lodsw' : Parser_x86.parse_lodsw,
    'loope' : Parser_x86.parse_none,
    'loopne' : Parser_x86.parse_none,
    'loop' : Parser_x86.parse_none,
    'lsl' : Parser_x86.parse_none,
    'lss' : Parser_x86.parse_ds,
    'ltr' : Parser_x86.parse_s,
    'maskmovdqu' : Parser_x86.parse_ss,
    'maskmovq' : Parser_x86.parse_ss,
    'movabs' : Parser_x86.parse_ds,
    'movapd' : Parser_x86.parse_ds,
    'movaps' : Parser_x86.parse_ds,
    'movddup' : Parser_x86.parse_ds,
    'movd' : Parser_x86.parse_ds,
    'movdq2q' : Parser_x86.parse_ds,
    'movdqa' : Parser_x86.parse_ds,
    'movdqu' : Parser_x86.parse_ds,
    'movhlps' : Parser_x86.parse_ds,
    'movhpd' : Parser_x86.parse_ds,
    'movhps' : Parser_x86.parse_ds,
    'movlhps' : Parser_x86.parse_ds,
    'movlpd' : Parser_x86.parse_ds,
    'movlps' : Parser_x86.parse_ds,
    'movmskpd' : Parser_x86.parse_bs,
    'movmskps' : Parser_x86.parse_bs,
    'movntdqa' : Parser_x86.parse_ds,
    'movntdq' : Parser_x86.parse_ds,
    'movnti' : Parser_x86.parse_ds,
    'movntpd' : Parser_x86.parse_ds,
    'movntps' : Parser_x86.parse_ds,
    'movntq' : Parser_x86.parse_ds,
    'movntsd' : Parser_x86.parse_ds,
    'movntss' : Parser_x86.parse_ds,
    'mov' : Parser_x86.parse_ds,
    'movq2dq' : Parser_x86.parse_ds,
    'movq' : Parser_x86.parse_ds,
    'movsb' : Parser_x86.parse_movsb,
    'movsd' : Parser_x86.parse_movsd,
    'movshdup' : Parser_x86.parse_ds,
    'movsldup' : Parser_x86.parse_ds,
    'movs' : Parser_x86.parse_movs,
    'movsq' : Parser_x86.parse_movsq,
    'movss' : Parser_x86.parse_ds,
    'movsw' : Parser_x86.parse_movsw,
    'movsxd' : Parser_x86.parse_ds,
    'movsx' : Parser_x86.parse_ds,
    'movupd' : Parser_x86.parse_ds,
    'movups' : Parser_x86.parse_ds,
    'movzx' : Parser_x86.parse_ds,
    'mpsadbw' : Parser_x86.parse_bss,
    'mul' : Parser_x86.parse_s,
    'neg' : Parser_x86.parse_b,
    'nop' : Parser_x86.parse_none,
    'not' : Parser_x86.parse_b,
    'or' : Parser_x86.parse_bs,
    'out' : Parser_x86.parse_none,
    'outsb' : Parser_x86.parse_none,
    'outsd' : Parser_x86.parse_none,
    'outsw' : Parser_x86.parse_none,
    'pabsb' : Parser_x86.parse_ss,
    'pabsd' : Parser_x86.parse_ss,
    'pabsw' : Parser_x86.parse_ss,
    'packusdw' : Parser_x86.parse_bs,
    'paddb' : Parser_x86.parse_bs,
    'paddd' : Parser_x86.parse_bs,
    'paddq' : Parser_x86.parse_bs,
    'paddsb' : Parser_x86.parse_bs,
    'paddsw' : Parser_x86.parse_bs,
    'paddusb' : Parser_x86.parse_bs,
    'paddusw' : Parser_x86.parse_bs,
    'paddw' : Parser_x86.parse_bs,
    'palignr' : Parser_x86.parse_bs,
    'pandn' : Parser_x86.parse_bs,
    'pand' : Parser_x86.parse_bs,
    'pavgb' : Parser_x86.parse_bs,
    'pavgw' : Parser_x86.parse_bs,
    'pblendvb' : Parser_x86.parse_blend,
    'pblendw' : Parser_x86.parse_blend,
    'pcmpeqb' : Parser_x86.parse_bs,
    'pcmpeqd' : Parser_x86.parse_bs,
    'pcmpeqq' : Parser_x86.parse_bs,
    'pcmpeqw' : Parser_x86.parse_bs,
    'pcmpestri' : Parser_x86.parse_ss,
    'pcmpestrm' : Parser_x86.parse_ss,
    'pcmpgtq' : Parser_x86.parse_bs,
    'pcmpistri' : Parser_x86.parse_ss,
    'pcmpistrm' : Parser_x86.parse_ss,
    'pextrb' : Parser_x86.parse_dss,
    'pextrd' : Parser_x86.parse_dss,
    'pextrw' : Parser_x86.parse_dss,
    'phaddd' : Parser_x86.parse_bs,
    'phaddsw' : Parser_x86.parse_bs,
    'phaddw' : Parser_x86.parse_bs,
    'phminposuw' : Parser_x86.parse_bs,
    'phsubd' : Parser_x86.parse_bs,
    'phsubsw' : Parser_x86.parse_bs,
    'phsubw' : Parser_x86.parse_bs,
    'pinsrb' : Parser_x86.parse_dss,
    'pinsrd' : Parser_x86.parse_dss,
    'pinsrw' : Parser_x86.parse_dss,
    'pmaddubsw' : Parser_x86.parse_bs,
    'pmaddwd' : Parser_x86.parse_bs,
    'pmaxsb' : Parser_x86.parse_bs,
    'pmaxsd' : Parser_x86.parse_bs,
    'pmaxsw' : Parser_x86.parse_bs,
    'pmaxub' : Parser_x86.parse_bs,
    'pmaxud' : Parser_x86.parse_bs,
    'pmaxuw' : Parser_x86.parse_bs,
    'pminsb' : Parser_x86.parse_bs,
    'pminsd' : Parser_x86.parse_bs,
    'pminsw' : Parser_x86.parse_bs,
    'pminub' : Parser_x86.parse_bs,
    'pminud' : Parser_x86.parse_bs,
    'pminuw' : Parser_x86.parse_bs,
    'pmovmskb' : Parser_x86.parse_ds,
    'pmovsxbd' : Parser_x86.parse_ds,
    'pmovsxbq' : Parser_x86.parse_ds,
    'pmovsxbw' : Parser_x86.parse_ds,
    'pmovsxdq' : Parser_x86.parse_ds,
    'pmovsxwd' : Parser_x86.parse_ds,
    'pmovsxwq' : Parser_x86.parse_ds,
    'pmovzxbd' : Parser_x86.parse_ds,
    'pmovzxbq' : Parser_x86.parse_ds,
    'pmovzxbw' : Parser_x86.parse_ds,
    'pmovzxdq' : Parser_x86.parse_ds,
    'pmovzxwd' : Parser_x86.parse_ds,
    'pmovzxwq' : Parser_x86.parse_ds,
    'pmuldq' : Parser_x86.parse_bs,
    'pmulhrsw' : Parser_x86.parse_bs,
    'pmulhuw' : Parser_x86.parse_bs,
    'pmulhw' : Parser_x86.parse_bs,
    'pmulld' : Parser_x86.parse_bs,
    'pmullw' : Parser_x86.parse_bs,
    'pmuludq' : Parser_x86.parse_bs,
    'popcnt' : Parser_x86.parse_ds, 
    'popfd' : Parser_x86.parse_popfd,
    'popf' : Parser_x86.parse_popf,
    'pop' : Parser_x86.parse_pop,
    'por' : Parser_x86.parse_bs,
    'psadbw' : Parser_x86.parse_bs,
    'pshufd' : Parser_x86.parse_dss,
    'pshufhw' : Parser_x86.parse_dss,
    'pshuflw' : Parser_x86.parse_dss,
    'pshufw' : Parser_x86.parse_dss,
    'psignb' : Parser_x86.parse_bs,
    'psignd' : Parser_x86.parse_bs,
    'psignw' : Parser_x86.parse_bs,
    'pslld' : Parser_x86.parse_bs,
    'pslldq' : Parser_x86.parse_bs,
    'psllq' : Parser_x86.parse_bs,
    'psllw' : Parser_x86.parse_bs,
    'psrad' : Parser_x86.parse_bs,
    'psraw' : Parser_x86.parse_bs,
    'psrld' : Parser_x86.parse_bs,
    'psrldq' : Parser_x86.parse_bs,
    'psrlq' : Parser_x86.parse_bs,
    'psrlw' : Parser_x86.parse_bs,
    'psubb' : Parser_x86.parse_bs,
    'psubd' : Parser_x86.parse_bs,
    'psubq' : Parser_x86.parse_bs,
    'psubsb' : Parser_x86.parse_bs,
    'psubsw' : Parser_x86.parse_bs,
    'psubusb' : Parser_x86.parse_bs,
    'psubusw' : Parser_x86.parse_bs,
    'psubw' : Parser_x86.parse_bs,
    'ptest' : Parser_x86.parse_ss,
    'punpcklbw' : Parser_x86.parse_bs,
    'punpckldq' : Parser_x86.parse_bs,
    'punpcklqdq' : Parser_x86.parse_bs,
    'punpcklwd' : Parser_x86.parse_bs,
    'pushfd' : Parser_x86.parse_pushfd,
    'pushf' : Parser_x86.parse_pushf,
    'push' : Parser_x86.parse_push,
    'pusha' : Parser_x86.parse_pusha,
    'pushad' : Parser_x86.parse_pushad,
    'pxor' : Parser_x86.parse_bs,
    'rcl' : Parser_x86.parse_b,
    'rcr' : Parser_x86.parse_b,
    'repnz' : Parser_x86.parse_error,
    'rep' : Parser_x86.parse_error,
    'repz' : Parser_x86.parse_error,
    'retf' : Parser_x86.parse_retf,
    'ret' : Parser_x86.parse_ret,
    'rol' : Parser_x86.parse_b,
    'ror' : Parser_x86.parse_b,
    'roundpd' : Parser_x86.parse_dss,
    'roundps' : Parser_x86.parse_dss,
    'roundsd' : Parser_x86.parse_dss,
    'roundss' : Parser_x86.parse_dss,
    'sahf'  : Parser_x86.parse_none,
    'sal' : Parser_x86.parse_b,    
    'sar' : Parser_x86.parse_b,
    'sbb' : Parser_x86.parse_bs,
    'scasb'  : Parser_x86.parse_scasb,
    'scasd'  : Parser_x86.parse_scasd,
    'scas' : Parser_x86.parse_ss,
    'scasq'  : Parser_x86.parse_scasq,
    'scasw'  : Parser_x86.parse_scasw,
    'setae' : Parser_x86.parse_d,
    'seta' : Parser_x86.parse_d,
    'setbe' : Parser_x86.parse_d,
    'setb' : Parser_x86.parse_d,
    'sete' : Parser_x86.parse_d,
    'setge' : Parser_x86.parse_d,
    'setg' : Parser_x86.parse_d,
    'setle' : Parser_x86.parse_d,
    'setl' : Parser_x86.parse_d,
    'setne' : Parser_x86.parse_d,
    'setno' : Parser_x86.parse_d,
    'setns' : Parser_x86.parse_d,
    'seto' : Parser_x86.parse_d,
    'setpe' : Parser_x86.parse_d,
    'setpo' : Parser_x86.parse_d,
    'sets' : Parser_x86.parse_d,
    'shl' : Parser_x86.parse_b,
    'shr' : Parser_x86.parse_b,
    'shufpd' : Parser_x86.parse_bss,
    'shufps' : Parser_x86.parse_bss,
    'sldt' : Parser_x86.parse_d,
    'stc' : Parser_x86.parse_none,
    'std' : Parser_x86.parse_none,
    'sti' : Parser_x86.parse_none,
    'stos' : Parser_x86.parse_ds,
    'stosb' : Parser_x86.parse_stosb,
    'stosd' : Parser_x86.parse_stosd,
    'stosd' : Parser_x86.parse_stosq,
    'stosw' : Parser_x86.parse_stosw,
    'str' : Parser_x86.parse_d,
    'sub' : Parser_x86.parse_bs,
    'syscall' : Parser_x86.parse_syscall,
    'sysenter' : Parser_x86.parse_syscall,
    'test' : Parser_x86.parse_ss,
    'ucomisd' : Parser_x86.parse_ss,
    'ucomiss' : Parser_x86.parse_ss,
    'unpckhpd' : Parser_x86.parse_bs,
    'unpckhps' : Parser_x86.parse_bs,
    'unpcklpd' : Parser_x86.parse_bs,
    'unpcklps' : Parser_x86.parse_bs,
    'verr' : Parser_x86.parse_none,
    'verw' : Parser_x86.parse_none,
    'vpunpcklbw' : Parser_x86.parse_bs,
    'vpunpckldq' : Parser_x86.parse_bs,
    'vpunpcklqdq' : Parser_x86.parse_bs,
    'vpunpcklwd' : Parser_x86.parse_bs,
    'xadd' : Parser_x86.parse_bs,
    'xchg' : Parser_x86.parse_bb,
    'xor' : Parser_x86.parse_bs
    }
