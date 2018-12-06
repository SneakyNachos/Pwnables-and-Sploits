#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#define PWFILE "/etc/manpage_pass/manpage3"

int main(int argc, char *argv[])
{
    FILE *f;
    char *p;
    char pass[32];
    char buf[2];

    f = fopen(PWFILE, "r");
    fgets(pass, sizeof pass, f);
    pass[strlen(pass)-1] = '\0';

    p = getpass("password: ");

    if(!strcmp(p, pass))
    {
        system("sh");
        exit(0);
    }

    setuid(getuid()); /* dont need privs anymore */

    if(!argv[1])
    {
        argv[1] = buf;        
        buf[0] = '\0';
    }

    if( argv[1][0]++ >= 2) exit(0);

    argv[1][1] = '\0';
    execl(argv[0], argv[0], argv[1], 0); /* restart */
    return 0;
}
