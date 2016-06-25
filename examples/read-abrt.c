/**
 * read-abrt.c
 *
 * Sample program with a SIGABRT crash where a buffer is over ran by reading
 * a file
 *
 * Test with (x86):
 *      gcc -g -o read-abrt32 read-abrt.c
 *      gdb -x read-abrt.gdb ./read-abrt32
 *
 * Test with (x64):
 *      gcc -g -o fread-abrt64 read-abrt.c
 *      gdb -x read-abrt.gdb ./read-abrt64
 *
 * Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
*/

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

void DoOverflow(char* file) {
    int fd = open(file, O_RDONLY);
    char buf[4];

    // Overflow happens inside here. Should be a syscall/sysenter instruction.
    read(fd, buf, 20);
    
    close(fd);

    // SIGABRT should occur upon returning from this function
}

void main ( int argc, char* argv[]) {
    if (argc == 2) 
        DoOverflow(argv[1]);
}
