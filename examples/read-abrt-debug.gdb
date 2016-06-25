# read-abrt.gdb
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>

maintenance set target-async off
set height 0
set disassembly-flavor intel
b main
run /dev/urandom 
b read
record
continue
disp /i $pc
disp /x $eax
