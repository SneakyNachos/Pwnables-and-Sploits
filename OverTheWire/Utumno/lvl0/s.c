#include <stdio.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/syscall.h>

int main(){
    pid_t pid;

    pid = fork();
    if(pid == 0){
        ptrace(PTRACE_TRACEME,0,NULL,NULL);
        execl("/utumno/utumno0","/utumno/utumno0",NULL);
    }
    else {
        int status;
        struct user_regs_struct regs;
        
        FILE *fp;
        fp = fopen("o.txt","wb");

        while(1){
            wait(&status);
            if(WIFEXITED(status)){
                break;
            }
            ptrace(PTRACE_GETREGS,pid,NULL,&regs);
            
            if(regs.eip == 0xf7fdbb23 && regs.eax == 0x4){
                long check = ptrace(PTRACE_PEEKTEXT,pid,regs.ecx,0);
                printf("eip:%lx\n",regs.eip);
                printf("eax:%lx\n",regs.eax);
                printf("ebx:%lx\n",regs.ebx);
                printf("ecx:%lx\n",regs.ecx);
                printf("pecx:%lx\n",check);
                printf("edx:%lx\n",regs.edx);
                printf("---------------\n");

                int count = 0;
                while(count <= 4194304){
                   long data = ptrace(PTRACE_PEEKTEXT,pid,0xf7000000+(count*4));
                   if(data != 0xffffffff){
                        //printf("%x:%lx\n",(0xf7000000+(count*4)),data);
                        unsigned char byteArray[4];
                        byteArray[3] = (int)((data >> 24) & 0xFF);
                        byteArray[2] = (int)((data >> 16) & 0xFF);
                        byteArray[1] = (int)((data >> 8) & 0xFF);
                        byteArray[0] = (int)((data & 0xFF));
                        fwrite(byteArray,1,sizeof(byteArray),fp);
                   }
                    ++count;
                
                }
            }
            
            ptrace(PTRACE_SINGLESTEP,pid,NULL,NULL);
        }
    }
    return 0;
}
