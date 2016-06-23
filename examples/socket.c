/**
 * socket.c 
 *
 * Sample program with SIGsocket signal due to a buffer overflow
 *
 * Test with (x86):
 *      gcc -g -o socket32 -m32 socket.c
 *      gdb -x socket.gdb ./socket32
 *
 * Test with (x64):
 *      gcc -g -o socket64 socket.c
 *      gdb -x socket.gdb ./socket64
 *
 * Copyright (C) 2016 Josh Burbrink <dev.burbrink@gmail.com>
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

void testSocket(char* argv[], char* buff)
{
    int listenfd = 0, connfd=0;
    int so_reuseaddr = 1;
    struct sockaddr_in serv_addr;
    char sendBuff[1024];

    int bytesRead = 0;
    listenfd = socket(AF_INET, SOCK_STREAM, 0);

    setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &so_reuseaddr, sizeof(int));
    memset(&serv_addr, '0', sizeof(serv_addr));
    memset(sendBuff, '0', sizeof(sendBuff));

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if ( bind(listenfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) != 0 ) {
        printf("\nCould not bind to port %d\n", atoi(argv[1]));
        return;
    }

    listen(listenfd, 10);

    connfd = accept(listenfd, (struct sockaddr*)NULL, NULL);
    snprintf(sendBuff, sizeof(sendBuff), "Wecome to my server\n");

    write(connfd, sendBuff, strlen(sendBuff));
    bytesRead = read(connfd, buff, 100);
    printf("\nclient sent %c %d", buff[0], bytesRead);
    close(connfd);
    close(listenfd);
}

void main ( int argc, char* argv[]) {
    // buf gets overflowed by socket read in testSocket()
    char buff[3];

    testSocket(argv, buff);
}
