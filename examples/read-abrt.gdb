# read-abrt.gdb
# Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>

maintenance set target-async off
set height 0
b main
run /dev/urandom 
record
continue
