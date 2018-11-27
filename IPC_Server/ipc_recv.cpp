#include "ipc_recv.h"

void *xmalloc(unsigned int sz) {
    unsigned int s = 0;

    if(sz > PAGE_SIZE) {
        s = ((sz+PAGE_SIZE+1) & ~(PAGE_SIZE-1));
    } else {
        s = sz;
    }

    void *v = (void *) malloc(s);

	if(v == NULL) {
		return v;
	}

    memset(v, 0x0, s);

    return v;
}

bool is_valid_ipc_function(uint32_t f) {
	bool ret = false;

	if(f >= IPCFunctions::ARCHIVE_WRITE && f <= IPCFunctions::AUTH_SESSION)
		ret = true;

	return ret;
}

bool is_valid_ipc_type(uint32_t type) {
	bool ret = false;

	if(type >= IPCTypes::IPC_ARCHIVE && type <= IPCTypes::IPC_AUTH)
		ret = true;

	return ret;
}

int32_t write_ipc_handle(SerializedIPC *s) {

	int retval = 0;

#ifdef READ_FILE
	ofstream fd;
    fd.open("ipc.out", ios::in | ios::binary);

	if(fd.is_open()) {
		fd.write((char *) s, sizeof(SerializedIPC));
	} else {
		return ERR;
	}
#endif

#ifdef LOCAL_SOCKET

#ifdef __linux__
	retval = send(c_sock, s, sizeof(SerializedIPC), MSG_DONTWAIT);

	if(retval < 0) {
		return ERR;
	}

	close(c_sock);
#endif

#if WIN32 || WIN64
	DWORD wrote;

	BOOL ret = WriteFile(pipe, s, sizeof(SerializedIPC), &wrote, NULL);

	if(ret == FALSE) {
		return ERR;
	}
#endif

#endif

#ifdef SHARED_MEMORY

#ifdef __linux__
	memcpy(shmPtr, s, sizeof(SerializedIPC));
#endif

#if WIN32 || WIN64
	memcpy((void *) shmPtr, s, sizeof(SerializedIPC));
#endif

#endif
	return retval;
}

void destroy_ipc_data(uint8_t **h) {
	free(*h);
	*h = NULL;
}

char *isValidPath(char *s) {
    char tmpBuf[512];
    memcpy(tmpBuf, s, 512);
    tmpBuf[sizeof(tmpBuf)-1] = '\0';

    char *p = tmpBuf;

    while(*p != '\0') {
        if((strncmp(p, "..", 2) == 0) || *p == '\\') {
            return p;
        }

        p++;
    }

    return s;
}

class IPC_Archive : public IPC {
    public:
		IPC_Archive() : updated_archive(false) {
			archive = (uint8_t *) xmalloc(ARCHIVE_SZ*2);
		}

		~IPC_Archive() {
			free(archive);
		}

		int32_t init(SerializedIPC *d) {
			copyToTrustedIPC(d);

			ifstream fd;
            fd.open("archive.log", ios::in | ios::binary);

			if(fd.is_open()) {
        	    fd.read((char *) archive, ARCHIVE_SZ*2);
				fd.close();
			}

			parseArchiveRecords();

			return OK;
		}

		void parseArchiveRecords() {
			if(recordListHead != NULL) {
				return;
			}

			Record *rPtr = (Record *) archive;
			recordListHead = (RecordList *) xmalloc(sizeof(RecordList));
			RecordList *cur = recordListHead;
			RecordList *prev = recordListHead;

			memcpy(&cur->rec, rPtr, sizeof(Record));
			rPtr++;

			for(uint32_t i = 0; i < ((ARCHIVE_SZ*2) / sizeof(Record) - (sizeof(Record))); i++) {
				cur = (RecordList *) xmalloc(sizeof(RecordList));
				prev->next = cur;
				memcpy(&cur->rec, rPtr, sizeof(Record));
				prev = cur;
				rPtr++;
			}

			updated_archive = false;
		}

		void purgeStoredRecords() {
			RecordList *p = recordListHead;
			RecordList *next;

			while(p->next != NULL) {
				next = p->next;
				free(p);
				p = next;
			}

			recordListHead = NULL;
		}

		int32_t exec_function() {
			// ARCHIVE_READ(index)
			// Returns an archive record at 'index'
 			if(ipc.function == IPCFunctions::ARCHIVE_READ) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_UINT) {
					if(ipc.args[0].u.uint < ((ARCHIVE_SZ*2) / sizeof(Record))) {
						RecordList *r = recordListHead;

						if(r == NULL) {
							SerializedIPCHelper *si = createIPCResponseERR();
							write_ipc_handle(si->ipc);
							delete si;
							return ERR;
						}

						if(updated_archive == true) {
							purgeStoredRecords();
							parseArchiveRecords();
						}

						while(true) {
							if(r->rec.index == ipc.args[0].u.uint) {
								break;
							}
							r = r->next;
						}

						if(r != NULL) {
							char tmp[8192];
							snprintf(tmp, sizeof(tmp)-1, "[+] ARCHIVE_READ() - record # %u", ipc.args[0].u.uint);
							logStr(tmp);

							SerializedIPCHelper *si = createIPCResponseOKArgs();
							si->setIPCArgBuf(0, (uint8_t *) r, sizeof(Record));
							write_ipc_handle(si->ipc);
						} else {
							SerializedIPCHelper *si = createIPCResponseERR();
							write_ipc_handle(si->ipc);
							delete si;
							return ERR;
						}
					}
				}
			// ARCHIVE_WRITE(record)
			// Appends a new Record to archive.log
			} else if(ipc.function == IPCFunctions::ARCHIVE_WRITE) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_BUF) {
					Record *r = (Record *) ipc.args[0].u.buf;

					ofstream fd;
	        	    fd.open("archive.log", ios::in | ios::binary);

					if(fd.is_open()) {
						fd.seekp(0, ios_base::end);
    		        	fd.write((char *) r, sizeof(Record));
						fd.close();
					} else {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}

					char tmp[8192];
					snprintf(tmp, sizeof(tmp)-1, "[+] ARCHIVE_WRITE() - record->index=%x record->info=%x record->err_code=%s", r->index, r->info, r->err_code);
					logStr(tmp);

					SerializedIPCHelper *si = createIPCResponseOK();
					write_ipc_handle(si->ipc);
					delete si;
					updated_archive = true;
				}
			// ARCHIVE_QUERY_SZ
			// Returns the size of the archive file
			} else if(ipc.function == IPCFunctions::ARCHIVE_QUERY_SZ) {
				struct stat fs;
				stat("archive.log", &fs);

				logStr("[+] ARCHIVE_QUERY_SZ()");

				SerializedIPCHelper *si = createIPCResponseOKArgs();
				si->setIPCArgUInt(0, fs.st_size);
				write_ipc_handle(si->ipc);
				delete si;
			}

			return OK;
		}

	private:
		RecordList *recordListHead;
		uint8_t *archive;
		bool updated_archive;
};

// Desktop IPC handler object
// This type of object is instantiated anytime we receive
// an IPC message with an IPC_TYPE of IPC_DESKTOP
// This is copy/paste to clipboard support but is only
// available for Win32/Win64
class IPC_Desktop : public IPC {
    public:
		IPC_Desktop() { }

		int32_t init(SerializedIPC *d) {
			copyToTrustedIPC(d);
			return OK;
		}

		int32_t exec_function() {
			// DESKTOP_CLIPBOARD_SET(cpb, size)
			// Sets the clipboard object
			if(ipc.function == IPCFunctions::DESKTOP_CLIPBOARD_SET) {
#if WIN32 || WIN64
				if(ipc.args[0].tag == IPCArgTypes::IPC_BUF && ipc.args[1].tag == IPCArgTypes::IPC_UINT) {
					if(!OpenClipboard(NULL)) {
						return ERR;
					}

					BitMap *bm;
					EmptyClipboard();

					HGLOBAL hglbl = GlobalAlloc(GMEM_MOVEABLE|GMEM_ZEROINIT, ipc.args[1].u.uint);

					if(hglbl == NULL) {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						CloseClipboard();
						return ERR;
					}

					LPVOID p = GlobalLock(hglbl);
					memcpy(p, ipc.args[0].u.buf, ipc.args[1].u.uint);

					BitMap *bmm = (BitMap *) p;
#ifndef SHARED_MEMORY
					// Ensure the validateBitMap function pointer is used
					bmm->f = reinterpret_cast<BitMapCb>(&validateBitMap);
#endif
					if((bmm->f(bmm)) == ERR) {
						SerializedIPCHelper *si = createIPCResponseERR();
                        write_ipc_handle(si->ipc);
                        delete si;
                        CloseClipboard();
						GlobalUnlock(hglbl);
						GlobalFree(hglbl);
                        return ERR;
					}

					SetClipboardData(CF_RIFF, hglbl);

                    char tmp[8192];
                    snprintf(tmp, sizeof(tmp)-1, "[+] DESKTOP_CLIPBOARD_SET() - data=%s BitMap=%x", p, bm);
                    logStr(tmp);

					SerializedIPCHelper *si = createIPCResponseOK();
					write_ipc_handle(si->ipc);
					delete si;
					CloseClipboard();
					GlobalUnlock(hglbl);
					GlobalFree(hglbl);
				}
#else
				SerializedIPCHelper *si = createIPCResponseERR();
				write_ipc_handle(si->ipc);
				delete si;
				return ERR;
#endif
			// DESKTOP_CLIPBOARD_GET(cpb)
			// Gets a clipboard object
			} else if(ipc.function == IPCFunctions::DESKTOP_CLIPBOARD_GET) {
#if WIN32 || WIN64
				if(!OpenClipboard(NULL)) {
					return ERR;
				}

				HANDLE h = GetClipboardData(CF_RIFF);

				if(h == NULL) {
					SerializedIPCHelper *si = createIPCResponseERR();
					write_ipc_handle(si->ipc);
					delete [] si;
					return ERR;
				}

				char *b = (char *) GlobalLock(h);

                logStr("[+] DESKTOP_CLIPBOARD_GET()");

				SerializedIPCHelper *si = createIPCResponseOKRaw();
				si->setIPCRaw((uint8_t *) b, strlen(b));
				write_ipc_handle(si->ipc);
				delete si;
#else
				SerializedIPCHelper *si = createIPCResponseERR();
				write_ipc_handle(si->ipc);
				delete si;
				return ERR;
#endif
			}

			return OK;
		}
};

// FileIO IPC handler object
// This type of object is instantiated anytime we receive
// an IPC message with an IPC_TYPE of IPC_FILEIO
// It is responsible for core functionality such
// as reading and writing files that are owned by
// privileged users
class IPC_FileIO : public IPC {
    public:
		IPC_FileIO() : file(NULL), ipcBH(NULL) { }
		~IPC_FileIO() {	}

		int32_t init(SerializedIPC *d) {
			copyToTrustedIPC(d);
			return OK;
		}

		int32_t exec_function() {
			// FILEIO_READ(file, offset, size)
			if(ipc.function == IPCFunctions::FILEIO_READ) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_BUF && ipc.args[1].tag == IPCArgTypes::IPC_UINT &&
					ipc.args[2].tag == IPCArgTypes::IPC_UINT) {
					ipc.args[0].u.buf[sizeof(ipc.args[0].u.buf)] = '\0';

					char *f = (char *) ipc.args[0].u.buf;
					uint32_t offset = ipc.args[1].u.uint;
					uint32_t size = ipc.args[2].u.uint;

					char *p = isValidPath(f);

					if(p != f) {
	                    char tmp[8192];
    	                snprintf(tmp, sizeof(tmp)-1, "[+] FILEIO_READ() (DIRECTORY TRAVERSAL ATTACK) %s", p);
        	            logStr(tmp);
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}

					if(offset + 1 == 0 || size + 1 == 0) {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}

					file = (uint8_t *) xmalloc(size);

					// Apply a special terminator value
					file[size-1] = 0x01;

					ifstream fd;
    	    	    fd.open(f, ios::in | ios::binary);

					if(fd.is_open()) {
    		    	    fd.read((char *) file, size);
						fd.close();
					} else {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						free(file);
						return ERR;
					}

					ipcBH = new BufferHelper(file, size);
					ipcBH->setOffset(offset);

					SerializedIPCHelper *si = createIPCResponseOKRaw();
					si->setIPCRaw(ipcBH->retrievePtrToOffset(), size);

					delete ipcBH;

					write_ipc_handle(si->ipc);
					delete si;

					char tmp[8192];
					snprintf(tmp, sizeof(tmp)-1, "[+] FILEIO_READ() - offset=%x size=%x filename=%s file=%s", offset, size, f, (char *) ipcBH->getRawPtr());
					logStr(tmp);
					free(file);
				}
			// FILEIO_WRITE(file, buf, offset, size)
			} else if(ipc.function == IPCFunctions::FILEIO_WRITE) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_BUF && ipc.args[1].tag == IPCArgTypes::IPC_BUF &&
					ipc.args[2].tag == IPCArgTypes::IPC_UINT && ipc.args[3].tag == IPCArgTypes::IPC_UINT) {

					ipc.args[0].u.buf[sizeof(ipc.args[0].u.buf)-1] = '\0';
					char *f = (char *) ipc.args[0].u.buf;
					char *b = (char *) ipc.args[1].u.buf;
					int offset = ipc.args[2].u.uint;
					int size = ipc.args[3].u.uint;

					char *p = isValidPath(f);

					if(p != f) {
	                    char tmp[8192];
    	                snprintf(tmp, sizeof(tmp)-1, "[+] FILEIO_READ() (DIRECTORY TRAVERSAL ATTACK) %s", p);
        	            logStr(tmp);
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}

					if(offset + 1 == 0 || size + 1 == 0) {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}

					if(size > IPC_ARGS_BUF_SZ) {
						size = IPC_ARGS_BUF_SZ;
					}

					ipcBH = new BufferHelper((uint8_t *) b, size);

					if(offset > IPC_ARGS_BUF_SZ) {
						ipcBH->setOffset(0);
					} else {
						ipcBH->setOffset(offset);
					}

					ofstream of;
    	    	    of.open(f, ios::in | ios::binary);

					if(of.is_open()) {
					    of.seekp(ipcBH->getOffset(), ios_base::beg);
    			        of.write((char *) ipcBH->retrievePtrToOffset(), ipcBH->getSize());
						of.close();
					} else {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						delete ipcBH;
						return ERR;
					}

					delete ipcBH;

					char tmp[8192];
					snprintf(tmp, sizeof(tmp)-1, "[+] FILEIO_WRITE() - offset=%x size=%x filename=%s", offset, size, f);
					logStr(tmp);

					SerializedIPCHelper *si = createIPCResponseOK();
					write_ipc_handle(si->ipc);
					delete si;
				}
			} else if(ipc.function == IPCFunctions::FILEIO_QUERY_SZ) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_BUF) {
					ipc.args[0].u.buf[sizeof(ipc.args[0].u.buf)-1] = '\0';

					char *f = (char *) ipc.args[0].u.buf;
	                struct stat fs;
    	            stat(f, &fs);

        	        SerializedIPCHelper *si = createIPCResponseOKArgs();
            	    si->setIPCArgUInt(0, fs.st_size);
                	write_ipc_handle(si->ipc);
	                delete si;
				}
			}

			return OK;
		}
	private:
		uint8_t *file;
		BufferHelper *ipcBH;
};

// CryptoHandler IPC object
// This class implements methods for setting/getting
// key bits and setting/getting a key name
class IPC_CryptoHandler : public IPC {
    public:
		IPC_CryptoHandler() : key_is_set(false), key_name_is_set(false), iv_is_set(false), key(NULL), key_size(512), iv(0) { }

		~IPC_CryptoHandler() {
			if(key) {
				delete [] key;
			}
		}

		int32_t init(SerializedIPC *d) {
			copyToTrustedIPC(d);
			return OK;
		}

		int32_t exec_function() {
			uint8_t key_buf[512];
			key = key_buf;

			// CRYPTO_SET_IV(iv)
			if(ipc.function == IPCFunctions::CRYPTO_SET_IV) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_ULONG) {
					iv = ipc.args[0].u.ulong;

					logStr("[+] CRYPTO_SET_IV()");

					iv_is_set = true;

        	        SerializedIPCHelper *si = createIPCResponseOK();
                	write_ipc_handle(si->ipc);
	                delete si;
				}
			// CRYPTO_GET_IV
			} else if(ipc.function == IPCFunctions::CRYPTO_GET_IV) {
				SerializedIPCHelper *si = createIPCResponseOKArgs();
				si->setIPCArgULong(0, iv);
				write_ipc_handle(si->ipc);
				delete si;
			// CRYPTO_SET_KEY(key, key_size)
			} else if(ipc.function == IPCFunctions::CRYPTO_SET_KEY) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_RAW && ipc.args[1].tag == IPCArgTypes::IPC_UINT) {
					uint8_t *k = ipc.raw;
					key_size = ipc.args[1].u.uint;

					if(key_size > sizeof(ipc.raw)) {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;

						if(key != NULL)
							delete [] key;

						return ERR;
					}

					char tmp[8192];
					snprintf(tmp, sizeof(tmp)-1, "[+] CRYPTO_SET_KEY() - key=%s", k);
					logStr(tmp);

					memcpy(key, k, key_size);
					key_is_set = true;

        	        SerializedIPCHelper *si = createIPCResponseOK();
                	write_ipc_handle(si->ipc);
	                delete si;
				}
			// CRYPTO_GET_KEY()
			} else if(ipc.function == IPCFunctions::CRYPTO_GET_KEY) {
				if(key_is_set = false) {
					SerializedIPCHelper *si = createIPCResponseOKRaw();
					si->setIPCRaw(key, key_size);
					write_ipc_handle(si->ipc);
					delete si;
				} else {
					SerializedIPCHelper *si = createIPCResponseERR();
					write_ipc_handle(si->ipc);
					delete si;
					return ERR;
				}
			// CRYPTO_GET_KEY_NAME()
			} else if(ipc.function == IPCFunctions::CRYPTO_GET_KEY_NAME) {
				if(key_name_is_set == false) {
					SerializedIPCHelper *si = createIPCResponseERR();
					write_ipc_handle(si->ipc);
					delete si;
					return ERR;
				} else {
					SerializedIPCHelper *si = createIPCResponseOKArgs();
					si->setIPCArgBuf(0, key_name, sizeof(key_name));
					write_ipc_handle(si->ipc);
					delete si;
				}
			// CRYPTO_SET_KEY_NAME(name, size)
			} else if(ipc.function == IPCFunctions::CRYPTO_SET_KEY_NAME) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_BUF && ipc.args[1].tag == IPCArgTypes::IPC_USHORT) {
					uint8_t *kn = ipc.args[0].u.buf;
					uint16_t ksz = ipc.args[1].u.ushort;

					if((checkKeyName(kn, ksz)) == OK) {
						if(ksz > sizeof(key_name)) {
							ksz = sizeof(key_name);
						}

						memcpy(key_name, kn, ksz);
						SerializedIPCHelper *si = createIPCResponseOK();
						write_ipc_handle(si->ipc);
						delete si;
					} else {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}
				}

				key_name_is_set = true;
			}

			return OK;
		}

		uint32_t checkKeyName(uint8_t *kn, uint16_t ksz) {
			int i;
			for(i=0;i<ksz;i++) {
				// Turn non ascii chars into spaces
				if(!isascii(kn[i])) {
					kn[i] = 0x20;
				}
			}

			return OK;
		}

	private:
		bool key_is_set;
		bool key_name_is_set;
		bool iv_is_set;
		uint8_t *key;
		uint8_t key_name[256];
		uint32_t key_size;
		unsigned long iv;
};

// ValidateBlob IPC Object
// This class implements validation functions
// that can be called internally or by a remote
// client. These functions return TRUE/FALSE
// values indicating whether the blob pointers
// should be considered safe or not. This class
// is a C++ wrapper around a legacy C API
class IPC_ValidateBlob : public IPC {
	public:
		IPC_ValidateBlob() {
			v_array[0] = &validateBlobFuncPtr;
			v_array[1] = &validateBlobOffset;
			v_array[2] = &validateBlobSize;
		}

		~IPC_ValidateBlob() { }

		int32_t init(SerializedIPC *d) {
			copyToTrustedIPC(d);
			return OK;
		}

		int32_t exec_function() {
			// VALIDATE_BLOB(validate_function, blob)
			if(ipc.function == IPCFunctions::VALIDATE_BLOB) {
				if(ipc.args[0].tag == IPCArgTypes::IPC_ULONG && ipc.args[1].tag == IPCArgTypes::IPC_BUF) {
					index = ipc.args[0].u.ulong;
					b = (Blob *) ipc.args[1].u.buf;

					if(index < 0) {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					}

					ValidateCb vcb = reinterpret_cast<ValidateCb>(&v_array[index]);
					vcb(b);
				}
			}

			return OK;
		}

	private:
		ValidateCb v_array[3];
		Blob *b;
		uint16_t index;
};

class IPC_Ping : public IPC {
    public:
		void init() {
			SerializedIPCHelper *si = createNewIPC();
			si->ipc->type = IPCTypes::IPC_RESPONSE;
			si->ipc->function = IPCFunctions::IPC_RESPONSE_PING;
			write_ipc_handle(si->ipc);
			delete si;
		}
};

class IPC_Encode : public IPC {
	public:
		void init(SerializedIPC *d) {
			copyToTrustedIPC(d);

			if (!m_encoder || ipc.function == IPCFunctions::ENCODE_ADD_DATA)
				m_encoder = new Base64Encoder;
		}

		uint32_t exec_function() {
			if (ipc.function == IPCFunctions::ENCODE_ADD_DATA) {
				if (ipc.args[0].tag == IPCArgTypes::IPC_UINT &&
					ipc.args[1].tag == IPCArgTypes::IPC_BUF) {
					m_encoder->addData(ipc.args[1].u.buf, ipc.args[0].u.uint);
				} else {
					SerializedIPCHelper *si = createIPCResponseERR();
					write_ipc_handle(si->ipc);
					delete si;
					return ERR;
				}
			} else if (ipc.function == IPCFunctions::ENCODE_GET_RESULT) {
				SerializedIPCHelper *si = createIPCResponseOKArgs();
				si->setIPCArgBuf(0, (uint8_t*)m_encoder->getResult(), m_encoder->getLength());
				write_ipc_handle(si->ipc);
				delete si;
			} else if (ipc.function == IPCFunctions::ENCODE_CLEAR) {
				if (m_encoder)
					delete m_encoder;
			}

			return OK;
		}

	private:
		class DataEncoder {
			public:
				virtual void addData(const uint8_t *data, uint32_t length) = 0;
				virtual uint32_t getLength() = 0;
				virtual const uint8_t *getResult() = 0;
		};

		class Base64Encoder : public DataEncoder {
			public:
				Base64Encoder() {
					m_data = NULL;
					m_length = 0;
				}

				~Base64Encoder() {
					if (m_data)
						delete [] m_data;
				}

				virtual void addData(const uint8_t *data, uint32_t length) {
					uint32_t newlength = (length/3)*4;
					uint8_t *newdata = new uint8_t[m_length+newlength];

					memcpy(newdata, m_data, m_length);
					base64encode(data, length, newdata+m_length, newlength);

					delete [] m_data;
					m_data = newdata;
					m_length += newlength;
					
					return;
				}

				virtual uint32_t getLength() {
					return m_length;
				}

				virtual const uint8_t *getResult() {
					return m_data;
				}

			private:
				int base64encode(const void* data_buf, size_t dataLength, uint8_t* result, size_t resultSize)
				{
				   const char base64chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
				   const uint8_t *data = (const uint8_t *)data_buf;
				   size_t resultIndex = 0;
				   size_t x;
				   uint32_t n = 0;
				   int padCount = dataLength % 3;
				   uint8_t n0, n1, n2, n3;
				 
				   /* increment over the length of the string, three characters at a time */
				   for (x = 0; x < dataLength; x += 3) 
				   {
				      /* these three 8-bit (ASCII) characters become one 24-bit number */
				      n = data[x] << 16;
				 
				      if((x+1) < dataLength)
				         n += data[x+1] << 8;
				 
				      if((x+2) < dataLength)
				         n += data[x+2];
				 
				      /* this 24-bit number gets separated into four 6-bit numbers */
				      n0 = (uint8_t)(n >> 18) & 63;
				      n1 = (uint8_t)(n >> 12) & 63;
				      n2 = (uint8_t)(n >> 6) & 63;
				      n3 = (uint8_t)n & 63;
				 
				      /*
				       * if we have one byte available, then its encoding is spread
				       * out over two characters
				       */
				      if(resultIndex >= resultSize) return 0;   /* indicate failure: buffer too small */
				      result[resultIndex++] = base64chars[n0];
				      if(resultIndex >= resultSize) return 0;   /* indicate failure: buffer too small */
				      result[resultIndex++] = base64chars[n1];
				 
				      /*
				       * if we have only two bytes available, then their encoding is
				       * spread out over three chars
				       */
				      if((x+1) < dataLength)
				      {
				         if(resultIndex >= resultSize) return 0;   /* indicate failure: buffer too small */
				         result[resultIndex++] = base64chars[n2];
				      }
				 
				      /*
				       * if we have all three bytes available, then their encoding is spread
				       * out over four characters
				       */
				      if((x+2) < dataLength)
				      {
				         if(resultIndex >= resultSize) return 0;   /* indicate failure: buffer too small */
				         result[resultIndex++] = base64chars[n3];
				      }
				   }

				   /*
				    * create and add padding that is required if we did not have a multiple of 3
				    * number of characters available
				    */
				   if (padCount > 0) 
				   { 
				      for (; padCount < 3; padCount++) 
				      { 
				         if(resultIndex >= resultSize) return 0;   /* indicate failure: buffer too small */
				         result[resultIndex++] = '=';
				      } 
				   }
				   if(resultIndex >= resultSize) return 0;   /* indicate failure: buffer too small */
				   result[resultIndex] = 0;
				   return 1;   /* indicate success */
				}

				uint8_t *m_data;
				uint32_t m_length;
		};

		Base64Encoder *m_encoder;
};

// Authentication Module
// This object authenticates all callers of the API
class IPC_Auth : public IPC {
    public:
		IPC_Auth() : valid_session(false) { 
			m_password = "c5a514664b81f21235d2d1e7e6454334abc3cf4b";
		}

		~IPC_Auth() { }

		int32_t init(SerializedIPC *d) {
			copyToTrustedIPC(d);
			return OK;
		}

		int32_t exec_function() {
			// AUTH_SESSION
			if(ipc.function == IPCFunctions::AUTH_SESSION) {
				if (ipc.args[0].tag == IPCArgTypes::IPC_UINT &&
					ipc.args[1].tag == IPCArgTypes::IPC_BUF) {

					string p((char *) ipc.args[1].u.buf, ipc.args[0].u.uint);

					if(p != m_password) {
						SerializedIPCHelper *si = createIPCResponseERR();
						write_ipc_handle(si->ipc);
						delete si;
						return ERR;
					} else {
						valid_session = true;
					}

				}
			}
		}

		bool check_session() { return valid_session; }

	bool valid_session;
	std::string m_password;
};

int main(int argc, char *argv[]) {

	if(argv[1] == NULL) {
		cout << "please supply a filename\n" << endl;
		return ERR;
	}

	// Does not return
	if(!(read_ipc_handle(argv[1]))) {
		cout << "An error occured\n";
		return ERR;
	}

    return 0;
}

int32_t read_ipc_handle(char *filename) {
	IPC_Archive *archive = new IPC_Archive();
	IPC_Desktop *desktop = new IPC_Desktop();
	IPC_FileIO *fileio = new IPC_FileIO();
	IPC_CryptoHandler *crypto = new IPC_CryptoHandler();
	IPC_ValidateBlob *valblob = new IPC_ValidateBlob();
	IPC_Ping *ping = new IPC_Ping();
    IPC_Encode *encode = new IPC_Encode();
    IPC_Auth *auth = new IPC_Auth();

	uint8_t *ipc_in_mem;
	int32_t retval = 0;

	while(true) {
    	ipc_in_mem = (uint8_t *) xmalloc(sizeof(SerializedIPC));
		retval = 0;

		if(ipc_in_mem == NULL) {
			return OK;
		}

#ifdef READ_FILE
    	ifstream fd;
	    fd.open(filename, ios::in | ios::binary);

    	if(fd.is_open() && ipc_in_mem) {
        	memset(ipc_in_mem, 0x0, sizeof(SerializedIPC));
	        fd.seekg(0, ios::beg);
    	    fd.read((char *) ipc_in_mem, sizeof(SerializedIPC));
        	fd.close();
	    } else {
			destroy_ipc_data(&ipc_in_mem);
        	return ERR;
	    }
#endif // READ_FILE

#ifdef LOCAL_SOCKET

#ifdef __linux__
		memset(&s_name, 0x0, sizeof(struct sockaddr_un));
		l_sock = socket(PF_LOCAL, SOCK_STREAM, 0);

		if(l_sock < 0) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		s_name.sun_family = PF_LOCAL;

		strncpy(s_name.sun_path, filename, strlen(filename));

		if((bind(l_sock, (struct sockaddr *) &s_name, SUN_LEN(&s_name)) < 0)) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		if((listen(l_sock, 10) < 0)) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		c_sock = accept(l_sock, NULL, NULL);

		if(c_sock < 0) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		int optval = 0;

		retval = setsockopt(c_sock, SOL_SOCKET, SO_RCVLOWAT, &optval, sizeof(optval));

		if(retval < 0) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		retval = recv(c_sock, ipc_in_mem, sizeof(SerializedIPC), 0);

		if(retval == ERR) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}
#endif

#if WIN32 || WIN64
		pipe = CreateNamedPipe("\\\\.\\pipe\\ipc_socket", PIPE_ACCESS_OUTBOUND, PIPE_TYPE_BYTE, 1, 0, 0, 0, NULL);

		if(pipe == INVALID_HANDLE_VALUE) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		BOOL ret;

		ret = ConnectNamedPipe(pipe, NULL);

		if(!ret) {
			CloseHandle(pipe);
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		DWORD bytesread;

		if((ReadFile(pipe, ipc_in_mem, sizeof(SerializedIPC), &bytesread, NULL)) == false) {
			CloseHandle(pipe);
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		if(bytesread < 0) {
			CloseHandle(pipe);
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}
#endif

#endif // LOCAL_SOCKET

#ifdef SHARED_MEMORY

#ifdef __linux__
	    shmKey = ftok(filename, 1);

	    if(shmKey == ERR) {
    		destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

    	shmId = shmget(shmKey, sizeof(int), IPC_CREAT | IPC_EXCL);

		if(shmId == ERR) {
			destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

	    shmPtr = shmat(shmId, NULL, 0);

		memcpy(ipc_in_mem, shmPtr, sizeof(SerializedIPC));
#endif

#if WIN32 || WIN64
		if(shmHandle == NULL) {
			shmHandle = CreateFileMapping(INVALID_HANDLE_VALUE, NULL, PAGE_EXECUTE_READWRITE, 0, PAGE_SIZE, filename);
		}

    	if(shmHandle == NULL) {
    		destroy_ipc_data(&ipc_in_mem);
			return ERR;
    	}

		if(shmPtr == NULL) {
		    shmPtr = (LPTSTR) MapViewOfFile(shmHandle, FILE_MAP_ALL_ACCESS, 0, 0, PAGE_SIZE);
		}

		if(shmPtr == NULL) {
			CloseHandle(shmHandle);
    		destroy_ipc_data(&ipc_in_mem);
			return ERR;
    	}

		memcpy(ipc_in_mem, shmPtr, sizeof(SerializedIPC));
#endif

#endif // SHARED_MEMORY

		SerializedIPC *raw_ipc = (SerializedIPC *) ipc_in_mem;

		if(is_valid_ipc_type(raw_ipc->type) == false) {
			cout << "Unknown type! (0x" << hex << raw_ipc->type << ")\n" << endl;
	    	destroy_ipc_data(&ipc_in_mem);
			return ERR;
		}

		if (auth->check_session() == false) {
			IPC *i = new IPC();
			SerializedIPCHelper *si = i->createIPCResponseERR();
			write_ipc_handle(si->ipc);
			delete si;
			delete i;
			continue;
		}

		if(raw_ipc->type == IPCTypes::IPC_ARCHIVE) {
			archive->init(raw_ipc);
			archive->exec_function();
		} else if(raw_ipc->type == IPCTypes::IPC_DESKTOP) {
			desktop->init(raw_ipc);
			desktop->exec_function();
		} else if(raw_ipc->type == IPCTypes::IPC_FILE_IO) {
			fileio->init(raw_ipc);
			fileio->exec_function();
		} else if(raw_ipc->type == IPCTypes::IPC_CRYPTO) {
			crypto->init(raw_ipc);
			crypto->exec_function();
		} else if(raw_ipc->type == IPCTypes::IPC_VALIDATE_BLOB) {
			valblob->init(raw_ipc);
			valblob->exec_function();
		} else if(raw_ipc->type == IPCTypes::IPC_PING) {
			ping->init();
		} else if(raw_ipc->type == IPCTypes::IPC_ENCODE) {
			encode->init(raw_ipc);
			encode->exec_function();
		} else if(raw_ipc->type == IPCTypes::IPC_AUTH)	{
			auth->init(raw_ipc);
			auth->exec_function();
		}

    	destroy_ipc_data(&ipc_in_mem);

		sleep(0.5);
	}

	// Never reached
	return OK;
}
