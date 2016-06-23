/**
 * abrt.c
 *
 * Sample program with SIGABRT signal
 *
 * Test with (x86):
 *      gcc -g -o abrt32 -m32 abrt.c
 *      gdb -x abrt.gdb ./abrt32
 *
 * Test with (x64):
 *      gcc -g -o abrt64 abrt.c
 *      gdb -x abrt.gdb ./abrt64
 * 
 * Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char buffer[200];
    int* j;
    char buffer2[50];
} A;

void test(){
    char* k;
    int l;
    A* a;
    k = (char*)malloc(4);

    // memset() causes heap corruption
    memset(k, 0, 200);

    // SEGABRT in malloc()
    k = (char*)malloc(4);
    k = (char*)a->j;
    
    // SEGFAULT here
    l = *k;

    printf("\nl is %d \n", l);
}

void main( int argc, char* argv[] ) {
    test();
}
