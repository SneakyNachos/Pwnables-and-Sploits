/* libvalidateblob is a legacy library for receiving an abstract
blob that includes a function pointer, raw data, size and offset.
The API this provides will validate the blob and its members. It
is not intended to be used by remote clients */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdint.h>

#define PAGE_SIZE 4096

/* C API for libValidateBlob */
typedef void(*Fptr)(void *);

typedef struct _Blob {
	/* A function pointer */
	Fptr ptr;
	/* Size of the blob */
	size_t sz;
	/* Offset into the blob */
	int offset;
	/* Raw blob */
	uint8_t blob[1024];
} Blob;

#ifdef __cplusplus
extern "C" {  
#endif  
  
typedef uint32_t(*ValidateCb)(Blob *);

uint32_t validateBlobFuncPtr(Blob *b);

uint32_t validateBlobOffset(Blob *b);

uint32_t validateBlobSize(Blob *b);

#ifdef __cplusplus
}
#endif
