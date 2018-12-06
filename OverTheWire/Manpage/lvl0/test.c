#include <stdio.h>
#include <unistd.h>
#include <sys/cdefs.h>
#include <sys/types.h>
int main(){
	setreuid(getegid(), getegid());
	execve("/bin/sh", 0, 0);	
}
