#include <stdio.h>
#include <string.h>
#include <signal.h>

int main(int argc, char *argv[])
{
    char buf[256];
    if(!argv[1]) return 0;
    strcpy(buf, argv[1]);
    if(strlen(buf) >= sizeof(buf - 1)) //no obos :) 
        raise(SIGTERM);
    return 0;
}
