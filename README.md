# PyDSlice
GDB Python extension for creating [dynamic slices](https://en.wikipedia.org/wiki/Program_slicing#Dynamic_slicing)

Leverages GDB's [record](https://sourceware.org/gdb/onlinedocs/gdb/Process-Record-and-Replay.html) and [reverse stepping](https://sourceware.org/gdb/onlinedocs/gdb/Reverse-Execution.html#Reverse-Execution) capabilities for computing dynamic slices. The goal is to identify a list of instructions which were responsible for maniuplating data (memory addresses or registers) that lead to the crash. Useful for debugging hard-to-follow bugs or reverse-engineering.

## Features
* Plugin architecture allows for easy extension of slices. One extension for debugging SIGABRT signals is provided.
* Allows users to manually change operands in slice
* Provides command to save slice to file for view in other text editors
* Optionally uses debug symbol information to determine source code lines and variable names of addresses

## Prerequisites
* GDB and Python must be installed on the system
* GDB's record and reverse stepping capbilities must also be supported

## Installation
```
# Install PyDSlice library. Be sure to use the same version of Python that GDB uses
sudo python setup.py install

# copy/move pydslice_gdb_cmds.py to GDB's data-directory/python/gdb/command/. 
# GDB's data-directory can be found using the gdb command "show data-directory"
cp pydslice_gdb_cmds.py /usr/share/gdb/python/gdb/command/
```

## Usage
* Record execution of the program using GDB's 'record' command
* Resume execution of the program
* When program execution pauses or crashes, initialize the slice with "slice new" for manual slice computation or "slice new crashed" for computing a slice based on a crash
* Compute the slice with "slice" or "slice step" (for incremental computation of the slice)
* <CTRL+C> will halt the slice computation
* Inspect the slice using "slice insn list" for all instructions which impacted data relevant to the slice

## GDB Commands
* "slice new" initializes a new blank slice
* "slice new crashed" initializes a new slice based on the current instruction and crash signal
* "slice" computes the slice until no more operands are left or the last recorded instruction is reached 
* "slice step" finds the next instruction in the slice 
* "slice insn list" lists all instructions in the slice
* "slice insn add" adds the current instruction to the slice
* "slice insn delete" deletes the current instruction from the slice
* "slice operand list" lists all operands being tracked by the slice 
* "slice operand add" adds the specified operand to the slice's operand list
* "slice operand delete" removes the specified operand from the slice's operand list
* "slice operand follow" resumes computation of the slice until the specified operand has been found 
* "slice save" saves the slice instruction list to the specified path
* "slice debug print_level" adjusts the printing level for slice output (verbose, error, info, warning, or none)
* "slice debug symbol_level" specifies what level of symbols are used in slice output (line information, variable names, or none)

## Examples
Example (abrt.c) of a slice for a crash from a SIBABRT signal:

```
master@linux:~/examples$ gdb -x abrt.gdb ./abrt32
GNU gdb (Ubuntu 7.10-1ubuntu2) 7.10
Copyright (C) 2015 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
<http://www.gnu.org/software/gdb/documentation/>.
For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from ./abrt32...done.
Breakpoint 1 at 0x400652: file abrt.c, line 47.

Breakpoint 1, main (argc=2, argv=0x7fffffffe2b8) at abrt.c:47
47          test();
abrt32: malloc.c:2373: sysmalloc: Assertion `(old_top == (((mbinptr) (((char *) &((av)->bins[((1) - 1) * 2])) - __builtin_offsetof (struct malloc_chunk, fd)))) && old_size == 0) || ((unsigned long) (old_size) >= (unsigned long)((((__builtin_offsetof (struct malloc_chunk, fd_nextsize))+((2 *(sizeof(size_t))) - 1)) & ~((2 *(sizeof(size_t))) - 1))) && ((old_top)->size & 0x1) && ((unsigned long) old_end & pagemask) == 0)' failed.

Program received signal SIGABRT, Aborted.
0x00007ffff7a441c7 in __GI_raise (sig=sig@entry=6) at ../sysdeps/unix/sysv/linux/raise.c:55
55      ../sysdeps/unix/sysv/linux/raise.c: No such file or directory.
(gdb) slice new crashed
Heap was corrupted somehow
ABRT signal raised by __malloc_assert()
Searching for cmp instruction that led to signal...
Added insn: cmp    QWORD PTR [rsp],0x1f
Ready to compute slice
(gdb) slice
Computing slice...
This instruction caused the heap corruption:
../sysdeps/x86_64/multiarch/../memset.S:81 <__memset_sse2+113> 0x7ffff7a9e1b4: movdqu XMMWORD PTR [rdi+0x10],xmm8
(gdb) slice insn list
--- slice instructions ---
1       0x7ffff7a91630: cmp    QWORD PTR [rsp],0x1f
2       malloc.c:3760 <_int_malloc+1633> 0x7ffff7a91580: mov    QWORD PTR [rsp],rax
3       malloc.c:3760 <_int_malloc+1633> 0x7ffff7a90e8d: and    rax,0xfffffffffffffff8
4       malloc.c:3760 <_int_malloc+1633> 0x7ffff7a90e8a: mov    rax,rdx
5       malloc.c:3760 <_int_malloc+1633> 0x7ffff7a90e86: mov    rdx,QWORD PTR [r11+0x8]
6       malloc.c:3759 <_int_malloc+1649> 0x7ffff7a90e7d: mov    r11,QWORD PTR [rbp+0x58]
7       ../sysdeps/x86_64/multiarch/../memset.S:81 <__memset_sse2+113> 0x7ffff7a9e1b4: movdqu XMMWORD PTR [rdi+0x10],xmm8 #  Cause of heap corruption

(gdb) bt
#0  __memset_sse2 () at ../sysdeps/x86_64/multiarch/../memset.S:80
#1  0x0000000000400602 in test () at abrt.c:34
#2  0x000000000040065c in main (argc=0x2, argv=0x7fffffffe2b8) at abrt.c:47
(gdb)
```

## Limitations
* Depends on GDB's 'record' functionality, which signicantly slows the execution of the program.
* Does not completely support multi-threaded programs - only supports computing a slice on a single thread's execution
* Not all x86/x64 opcodes are supported
* Known to periodically cause GDB to crash
* GDB has a bug in which reverse-stepping over a sysenter/syscall instruction for a read() does not correctly update the value of $eax/$rax. Therefore, the slice cannot correctly determine that the syscall was, in fact, a read()
* GDB option "maintenance set target-async off" is required for reverse-debugging
* Flag and Floating point registers are not supported

## Notes
* Only tested on Ubuntu 14.04 with GDB version 7.10 and Python version 3.4 and 2.7
* Note that GDB, based on configuration, will record a maximum number of instructions
* Performance of recording/slice computation is better with statically linked executables (avoids recording of loading shared objects from the file system, etc..)
* This slice software, by default, ignores the stack and frame registers for operands during slice computation as it would flood the slice with additional instructions that are purely just for making function calls. However, if $pc is corrupt, the frame and stack registers will be included as part of the slice.
* The dynamic slice computed by this software only pertains to instructions that
impact the data that lead to the crash. Because flag registers are not
supported, conditional statements would not be included in the slice. For
example, in the code below, instructions for the if statement would not show up
in the crash. However, lines 2 and 5 would show up in the crash as they relate
to the data flow which lead to the crash.

```
1: a = 3
2: b = 0
3: if (a < 5)
4: {
5:    d = *b
6: }
```
