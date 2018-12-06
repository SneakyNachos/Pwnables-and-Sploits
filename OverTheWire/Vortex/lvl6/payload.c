#include <stdio.h>
#include <stdlib.h>


int main(){
    FILE *fptr;
    
    char filename[] = "/etc/vortex_pass/vortex7", c;
    fptr = fopen(filename,"rb");

    if(fptr == 0x0){
        printf("Cannot open file\n");
        exit(0);
    }
    c = fgetc(fptr);
    while(c != EOF){
        printf("%c",c);
        c = fgetc(fptr);
    }
    fclose(fptr);
    return 0;
    
}
