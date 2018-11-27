del *.exe *.obj
cl ipc_recv.cpp libvalidateblob.c -O2 -DSHARED_MEMORY -DWIN32 "user32.lib" /link /NXCOMPAT:NO /DYNAMICBASE:NO
