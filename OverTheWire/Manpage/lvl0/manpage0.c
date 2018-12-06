//quick warmup
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char *argv[]){
    char buf[256];
    setuid( getuid() );     
    strcpy(buf, argv[1]);
    return 0;
}

