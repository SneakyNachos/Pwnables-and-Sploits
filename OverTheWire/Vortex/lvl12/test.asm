section .data


section .text

global main
main:
    xor eax, eax
    mov eax, 0x0804a00c
    xor ebx, ebx
    mov ebx, 0xffffceac 
    mov [eax], ebx
loop:
    jmp loop    
