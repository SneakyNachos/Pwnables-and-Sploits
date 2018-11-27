// Archive Record format with linked list structure

// A raw Record structure
typedef struct _Record {
	uint32_t index; // The record index (1,2,n)
	uint8_t info; // The type of archive record
	uint8_t err_code[16]; // The error code, a 16 byte ascii string
} Record;

// We keep an internal linked list of records
typedef struct _RecordList {
	Record rec;
	_RecordList *next; // A pointer to the next RecordList structure
} RecordList;
