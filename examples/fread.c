/**
 * fread.c
 *
 * Sample program with a crash where $pc jumps to an address in a file 
 *
 * Test with (x86):
 *      gcc -g -o fread32 -m32 fread.c
 *      gdb -x fread.gdb ./fread32
 *
 * Test with (x64):
 *      gcc -g -o fread64 fread.c
 *      gdb -x fread.gdb ./fread64
 *
 * Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
*/

#include <stdio.h>
#include <stdlib.h>

typedef void (*fx)(void);

void MyFunc() {
    printf("\nDid it");
}

void CallFile(char* file) {
    unsigned int func;
    fx myFx;
    FILE* f = fopen(file, "r");

    // myFx value is set inside fread()
    fread(&myFx, sizeof(fx), 1 , f);
    
    // myFx() will presumably crash because it will be an invalid address
    myFx();
}

void main ( int argc, char* argv[]) {
    if (argc == 2) 
        CallFile(argv[1]);
}
