#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define B(r,i)	((r >> (i*8)) & 0xFF)
#define C(i,j)	(B(crc32_table[i],j))

int crc32_table[256] = { 0, 0x77073096, [...] 0x2d02ef8d };

unsigned int crc32(unsigned int seed, const char* str, int len) {
	unsigned int i,k;
	for(i=0; i>= 8;
		seed ^= crc32_table[k];
	}
	return seed;
}

void print_str(const char *s, int len) {
	int i;
	for(i=0; i
		if(isalpha(s[i]))
			printf("%c",s[i]);
		else
			printf("\\x%02x", (unsigned char)s[i]);
	}
}

int find_entry(unsigned char top) {
	int i;
	for(i=0; i<256; i++)
		if(C(i,3) == top)
			return i;
	return -1;
}

int main(int argc, char **argv) {
	const char *S = argv[1];
	const unsigned int result = 0xe1ca95ee;
	unsigned int seed = crc32(0,S,strlen(S));

	int x1 = find_entry(B(result,3));
	int x2 = find_entry(B(result,2)^C(x1,2));
	int x3 = find_entry(B(result,1)^C(x1,1)^C(x2,2));
	int x4 = find_entry(B(result,0)^C(x1,0)^C(x2,1)^C(x3,2));

	unsigned int padding =
		((x4 ^ B(seed,0)) << 24) +
		((x3 ^ B(seed,1) ^ C(x4,0)) << 16) +
		((x2 ^ B(seed,2) ^ C(x4,1) ^ C(x3,0)) << 8 ) +
		((x1 ^ B(seed,3) ^ C(x4,2) ^ C(x3,1) ^ C(x2,0)));

	int len = strlen(S);
	char *ptr = malloc(len+4+1);
	strncpy(ptr, S, len);
	ptr[len++] = B(padding,3);
	ptr[len++] = B(padding,2);
	ptr[len++] = B(padding,1);
	ptr[len++] = B(padding,0);
	ptr[len] = '\0';

	print_str(ptr,len);

	free(ptr);

}
