#include "libvalidateblob.h"

/* Legacy C API for libValidateBlob */
uint32_t validateBlobFuncPtr(Blob *b) {
	if( b->ptr >= 0 && (uint32_t) b->ptr <= (0 + PAGE_SIZE))
		return -1;

    return 0;
}

uint32_t validateBlobOffset(Blob *b) {
    if(b->offset > b->sz)
        return -1;

    return 0;
}

uint32_t validateBlobSize(Blob *b) {
    if(b->sz == 0)
        return -1;

	if(b->sz > sizeof(b->blob))
		return -1;

	if(b->offset > sizeof(b->blob))
		return -1;

    return 0;
}
