"""
int source[256];

void gensource() {
	int factor = 0xEDB88320;
	for (int i=0;i<256;++i) {
		int tmp = i;
		for (int j=0;j<8;++j) {
			if (tmp&1) {
				tmp >>= 1;
				tmp ^= factor;
			} else {
				tmp >>= 1;
			}
		}
		source[i] = tmp;
	}
}

int checksum(char* buffer, int size) {
	int sum = 0xAA478422;

	for (int i=0;i<size;++i) {
		char c = buffer[i];
		int tmp = sum>>8;
		c = (sum^c)&0xFF;
		sum = source[c]^tmp;
	}
	return sum;
}
"""
