void *xmalloc(unsigned int sz);

class RefCountedObj {
	public:
		RefCountedObj(void *p)
			: ptr(p) {
				refcount = 1;
		}

		~RefCountedObj () { }

		int32_t refcount;
		void *ptr;
};

class BufferHelper {
	public:
		BufferHelper(size_t sz) : size(sz), offset(0) {
			uint8_t *o = (uint8_t *) xmalloc(sz);
			rco = createRefCountedObj((void *) o);
		}

		BufferHelper(uint8_t *p, size_t sz) : size(sz) {
			rco = createRefCountedObj((void *) p);
		}

		BufferHelper(BufferHelper *r) {
			size = r->size;
			offset = r->offset;
			rco = r->rco;
			rco->refcount++;
		}

		BufferHelper * operator=(BufferHelper *r) {
			rco->refcount--;
			size = r->size;
			offset = r->offset;
			rco = r->rco;
			return r;
		}

		virtual ~BufferHelper() {
			maybeDeleteRefObj();
		}

		RefCountedObj *createRefCountedObj(void *t) {
			RefCountedObj *o = new RefCountedObj(t);
			return o;
		}

		virtual void maybeDeleteRefObj() {
			rco->refcount--;
			if(rco->refcount <= 0) {
				free(rco->ptr);
				delete rco;
			}
		}

       	virtual uint8_t *retrievePtrToOffset() {
            return (uint8_t *) rco->ptr+offset;
        }

        virtual uint32_t getOffset() {
            return offset;
        }

        virtual void setOffset(uint32_t o) {
            offset = o;
        }

        virtual uint32_t getSize() {
            return size;
        }

        virtual void setSize(uint32_t s) {
            size = s;
        }

        virtual uint32_t sizeFromOffset() {
            return (size - offset);
        }

        virtual void *getRawPtr() {
            return rco->ptr;
        }

	private:
		RefCountedObj *rco;
        size_t size;
        uint32_t offset;
};