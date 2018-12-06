#include <sys/types.h>
#include <openssl/md5.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc, char * argv[]){
	unsigned char digest[16];
	const char * target = "a75e40766d56841fd5710d93a6416e8d";
	MD5_CTX ctx;
	MD5_Init(&ctx);
	int index = 0;
	unsigned int end = atoi(argv[2]);
	while(index <= end){
		MD5_Update(&ctx,argv[1],strlen(argv[1]));
       		MD5_Final(digest,&ctx);

		char md5string[33];
        	int i;
        	for(i=0;i<16;++i){
                	sprintf(&md5string[i*2],"%02x",(unsigned int)digest[i]);
        	}

        	printf("md5 digest: %s\n",md5string);
		if(!strcmp(md5string,target)){
			printf("Found Match: %s %d\n",argv[1],index);
		}
		index++;
	}
	
	return 0;

}
