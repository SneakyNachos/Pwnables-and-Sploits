#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdint.h>
#include <iostream>
#include <fstream>
#include <sys/stat.h>

#ifdef __linux__
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <fcntl.h>
#endif

#if WIN32 || WIN64
#include <Windows.h>
#include <Winuser.h>
#include <Winbase.h>
#define snprintf _snprintf
#define sleep Sleep
#endif

#include "archive_records.h"
#include "buffer_helper.h"
#include "libvalidateblob.h"

#define PAGE_SIZE 4096
#define IPC_ARGS_SIZE 16
#define IPC_ARGS_BUF_SZ 512
#define RAW_SIZE 32768
#define OK 0
#define ERR -1
#define ARCHIVE_SZ 65535

using namespace std;

uint32_t logStr(char *s) {
#if WIN32 || WIN64
	wchar_t *wc = new wchar_t[strlen(s) * 2];
    size_t convChars = 0;
    mbstowcs_s(&convChars, wc, strlen(s) * 2, s, _TRUNCATE);
    ofstream fd;
    fd.open("logfile.log", ios::in | ios::binary);
    fd.seekp(0, ios_base::end);
    fd.write((char *) wc, strlen(s));
    fd.close();
    delete [] wc;
    return 0;
#else
    ofstream fd;
    fd.open((char *) "logfile.log", ios::in | ios::binary);
    fd.seekp(0, ios_base::end);
    fd.write((char *) s, strlen(s));
    fd.close();
    return 0;
#endif
}

#ifdef __linux__
	struct sockaddr_un s_name;
	int l_sock;
	int c_sock;
    key_t shmKey;
    int shmId;
    void *shmPtr;
#endif

#if WIN32 || WIN64
	HANDLE pipe;
	HANDLE shmHandle;
    LPCTSTR shmPtr;
#endif

typedef struct _BitMapData {
    uint32_t height;
    uint32_t width;
	uint32_t metadata[64];
} BitMapData;

// All valid IPC arg types
namespace IPCArgTypes {
	uint32_t IPC_NONE = 0x0;
	uint32_t IPC_BUF = 0x1;
	uint32_t IPC_UCHAR = 0x2;
	uint32_t IPC_USHORT = 0x3;
	uint32_t IPC_UINT = 0x4;
	uint32_t IPC_ULONG = 0x5;
	uint32_t IPC_DOUBLE = 0x6;
	uint32_t IPC_POINTER = 0x7;
	uint32_t IPC_RAW = 0x8;
};

// All valid IPC types
namespace IPCTypes {
	uint32_t IPC_ARCHIVE = 0x0;
	uint32_t IPC_DESKTOP = 0x1;
	uint32_t IPC_FILE_IO = 0x2;
	uint32_t IPC_CRYPTO = 0x3;
	uint32_t IPC_VALIDATE_BLOB = 0x4;
	uint32_t IPC_PING = 0x5;
	uint32_t IPC_RESPONSE = 0x6;
	uint32_t IPC_ENCODE = 0x7;
	uint32_t IPC_AUTH = 0x8;
};

// All valid IPC functions
namespace IPCFunctions {
	uint32_t ARCHIVE_WRITE = 0xf000;
	uint32_t ARCHIVE_READ = 0xf001;
	uint32_t ARCHIVE_QUERY_SZ = 0xf002;
	uint32_t DESKTOP_CLIPBOARD_SET = 0xf003;
	uint32_t DESKTOP_CLIPBOARD_GET = 0xf004;
	uint32_t FILEIO_READ = 0xf005;
	uint32_t FILEIO_WRITE = 0xf006;
	uint32_t FILEIO_QUERY_SZ = 0xf007;
	uint32_t CRYPTO_SET_IV = 0xf008;
	uint32_t CRYPTO_GET_IV = 0xf009;
	uint32_t CRYPTO_SET_KEY = 0xf00a;
	uint32_t CRYPTO_GET_KEY = 0xf00b;
	uint32_t CRYPTO_GET_KEY_NAME = 0xf00c;
	uint32_t CRYPTO_SET_KEY_NAME = 0xf00d;
	uint32_t VALIDATE_BLOB = 0xf00e;
	uint32_t IPC_RESPONSE_PING = 0xf00f;
	uint32_t IPC_RESPONSE_OK = 0xf010;
	uint32_t IPC_RESPONSE_OK_ARGS = 0xf011;
	uint32_t IPC_RESPONSE_OK_RAW = 0xf012;
	uint32_t IPC_RESPONSE_ERR = 0xf013;
    uint32_t ENCODE_ADD_DATA = 0xf014;
    uint32_t ENCODE_GET_RESULT = 0xf015;
    uint32_t ENCODE_CLEAR = 0xf016;
    uint32_t AUTH_SESSION = 0xf017;
};

typedef struct _IPCArgs {
	union {
		uint8_t buf[IPC_ARGS_BUF_SZ];
		uint8_t uchar;
		uint16_t ushort;
		uint32_t uint;
		uint64_t ulong;
		double dbl;
		void *ptr;
	} u;
	uint32_t tag;
} IPCArgs;

// Serialized IPC (the base header)
// type - IPC handler class that should be used
// function - function to be called in the IPC handler
// sequence - unique sequence number for each msg (duplicated in response msgs)
// argc - specifies the number of IPCArgs
// args - structured ipc argument structures
// raw - a raw buffer for holding data that won't fit in args
typedef struct _SerializedIPC {
	uint32_t type;
	uint32_t function;
	uint32_t sequence;
	uint8_t argc;
	IPCArgs args[IPC_ARGS_SIZE];
	uint8_t raw[RAW_SIZE];
} SerializedIPC;

typedef int(*BitMapCb)(void *);
typedef struct _BitMap {
	uint32_t height;
	uint32_t width;
	BitMapCb f;
} BitMap;

int validateBitMap(BitMap *b) {
	if((b->height * b->width) > UINT_MAX) {
		return ERR;
	} else {
		return OK;
	}
}

int32_t write_ipc_handle(SerializedIPC *s);
int32_t read_ipc_handle(char *f);
void *xmalloc(unsigned int sz);
bool is_valid_ipc_function(uint32_t f);
bool is_valid_ipc_type(uint32_t type);
void destroy_ipc_data(void **h);
uint32_t logStr(char *s);

// This class makes it easier to create SerializedIPC structures
class SerializedIPCHelper {
	public:
		SerializedIPCHelper(uint32_t type, uint32_t function, uint32_t sequence, uint8_t argc) {
			ipc = (SerializedIPC *) xmalloc(sizeof(SerializedIPC));
			ipc->type = type;
			ipc->function = function;
			ipc->sequence = sequence;
			ipc->argc = argc;
		}

		~SerializedIPCHelper() {
			free(ipc);
		}

		void setIPCRaw(uint8_t *p, uint32_t size) {
			if(size > sizeof(ipc->raw)) {
				size = sizeof(ipc->raw);
			}

			memcpy(ipc->raw, p, size);
		}

		void setIPCArgBuf(uint8_t num, uint8_t *p, uint32_t size) {
			if(num > IPC_ARGS_SIZE) {
				num = 0;
			} else {
				ipc->argc++;
			}

			if(size > sizeof(ipc->args[num].u.buf))
				size = sizeof(ipc->args[num].u.buf);

			memcpy(ipc->args[num].u.buf, p, size);
			ipc->args[num].tag = IPCArgTypes::IPC_BUF;
		}

		void setIPCArgUChar(uint8_t num, uint8_t c) {
			if(num > IPC_ARGS_SIZE) {
				num = 0;
			} else {
				ipc->argc++;
			}

			ipc->args[num].u.uchar = c;
			ipc->args[num].tag = IPCArgTypes::IPC_UCHAR;
		}

		void setIPCArgUShort(uint8_t num, uint16_t s) {
            if(num > IPC_ARGS_SIZE) {
                num = 0;
            } else {
                ipc->argc++;
            }

			ipc->args[num].u.ushort = s;
			ipc->args[num].tag = IPCArgTypes::IPC_USHORT;
		}

		void setIPCArgUInt(uint8_t num, uint32_t i) {
            if(num > IPC_ARGS_SIZE) {
                num = 0;
            } else {
                ipc->argc++;
            }

			ipc->args[num].u.uint = i;
			ipc->args[num].tag = IPCArgTypes::IPC_UINT;
		}

		void setIPCArgULong(uint8_t num, unsigned long l) {
            if(num > IPC_ARGS_SIZE) {
                num = 0;
            } else {
                ipc->argc++;
            }

			ipc->args[num].u.ulong = l;
			ipc->args[num].tag = IPCArgTypes::IPC_ULONG;
		}

		void setIPCArgDouble(uint8_t num, double d) {
            if(num > IPC_ARGS_SIZE) {
                num = 0;
            } else {
                ipc->argc++;
            }

			ipc->args[num].u.dbl = d;
			ipc->args[num].tag = IPCArgTypes::IPC_DOUBLE;
		}

		void setIPCArgPtr(uint8_t num, void *p) {
            if(num > IPC_ARGS_SIZE) {
                num = 0;
            } else {
                ipc->argc++;
            }

			ipc->args[num].u.ptr = p;
			ipc->args[num].tag = IPCArgTypes::IPC_POINTER;
		}

		SerializedIPC *ipc;
};

// Base IPC class
// All other IPC related classes are derived from this
// Its 'ipc' member is a copy the data received from client
class IPC {
	public:
		IPC() {
			memset(&ipc, 0x0, sizeof(SerializedIPC));
		}

		void copyToTrustedIPC(SerializedIPC *s) {
			ipc.type = s->type;
			ipc.function = s->function;
			ipc.sequence = s->sequence;

			if(s->argc > IPC_ARGS_SIZE) {
				ipc.argc = IPC_ARGS_SIZE;
			} else {
				ipc.argc = s->argc;
			}

			memcpy(ipc.args, s->args, sizeof(IPCArgs) * ipc.argc);
			memcpy(ipc.raw, s->raw, sizeof(ipc.raw));
		}

		SerializedIPCHelper *createIPCResponseOK() {
            SerializedIPCHelper *si = new SerializedIPCHelper(IPCTypes::IPC_RESPONSE, IPCFunctions::IPC_RESPONSE_OK, ipc.sequence, 0);
			return si;
		}

		SerializedIPCHelper *createIPCResponseOKArgs() {
            SerializedIPCHelper *si = new SerializedIPCHelper(IPCTypes::IPC_RESPONSE, IPCFunctions::IPC_RESPONSE_OK_ARGS, ipc.sequence, 0);
			return si;
		}

		SerializedIPCHelper *createIPCResponseOKRaw() {
            SerializedIPCHelper *si = new SerializedIPCHelper(IPCTypes::IPC_RESPONSE, IPCFunctions::IPC_RESPONSE_OK_RAW, ipc.sequence, 0);
			return si;
		}

		SerializedIPCHelper *createIPCResponseERR() {
            SerializedIPCHelper *si = new SerializedIPCHelper(IPCTypes::IPC_RESPONSE, IPCFunctions::IPC_RESPONSE_ERR, ipc.sequence, 0);
			return si;
		}

		SerializedIPCHelper *createNewIPC() {
            SerializedIPCHelper *si = new SerializedIPCHelper(0, 0, (uint32_t) this, 0);
			return si;
		}

		SerializedIPC ipc;
};
