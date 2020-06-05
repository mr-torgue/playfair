#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void swap(char *s,  char *s2, int i, int j) {
	strcpy(s, s2);
	s[i] = s2[j];
	s[j] = s2[i];
	s[strlen(s)] = '\0';
}

void swapRow(char *s,  char *s2, int r1, int r2, int nrcols) {
	strcpy(s, s2);
	for(int i=0; i < nrcols; ++i) {
		s[r1 * nrcols + i] = s2[r2 * nrcols + i];
		s[r2 * nrcols + i] = s2[r1 * nrcols + i];
	}
	s[strlen(s)] = '\0';
}

void swapCol(char *s,  char *s2, int c1, int c2, int nrrows) {
	strcpy(s, s2);
	for(int i=0; i < nrrows; ++i) {
		s[i * nrrows + c1] = s2[i * nrrows + c2];
		s[i * nrrows + c2] = s2[i * nrrows + c1];
	}
	s[strlen(s)] = '\0';
}

void shift(char *s,  char *s2, int shift) {
	strcpy(s, s2);
	int len = strlen(s2);
	for(int i=0; i<len; ++i) {
		s[i] = s2[(i-shift)%len];
	}
	s[strlen(s)] = '\0';
}

void reverse(char *s,  char *s2) {
	strcpy(s, s2);
	int len = strlen(s2);
	for(int i=0; i<len; ++i) {
		s[i] = s2[len-i-1];
	}
	s[strlen(s)] = '\0';
}

void reverseRow(char *s,  char *s2, int r, int nrcols) {
	strcpy(s, s2);
	for(int i=0; i < nrcols; ++i) {
		s[r * nrcols + i] = s2[(r + 1) * nrcols - i - 1];
	}
	s[strlen(s)] = '\0';
}

void reverseCol(char *s,  char *s2, int c, int nrrows) {
	strcpy(s, s2);
	for(int i=0; i < nrrows; ++i) {
		s[i * nrrows + c] = s2[(nrrows - i - 1) * nrrows + c];
	}
	s[strlen(s)] = '\0';
}

void shiftRow(char *s,  char *s2, int r, int shift, int nrcols) {
	strcpy(s, s2);
	for(int i=0; i < nrcols; ++i) {
		s[r * nrcols + i] = s2[r * nrcols + (i - shift + nrcols) % nrcols ];
	}
	s[strlen(s)] = '\0';
}

void shiftCol(char *s,  char *s2, int c, int shift, int nrrows) {
	strcpy(s, s2);
	for(int i=0; i < nrrows; ++i) {
		s[i * nrrows + c] = s2[((i - shift + nrrows) % nrrows) * nrrows + c];
	}
	s[strlen(s)] = '\0';
}


double randd() {
    return (double)rand() / (double)RAND_MAX ;
}

void mutate(char *nkey, char *key, double swapRowRate, double swapColRate, double shiftRowRate, double shiftColRate, double revRowRate, double revColRate, double swapRate, double shuffleRate, double minShuffle, int maxShuffle, int nrrows, int nrcols) {
	int i, j;
	int nrcells = nrrows * nrcols;
	if(randd() < swapRowRate) {
		//printf("swaprow\n");
		i = rand() % nrrows;
		j = (i + (rand() % (nrrows - 1) + 1)) % nrrows;
		swapRow(nkey, key, i, j, nrcols);
	}
	if(randd() < swapColRate) {
		//printf("swapcol\n");
		i = rand() % nrcols;
		j = (i + (rand() % (nrcols - 1) + 1)) % nrcols;
		swapCol(nkey, key, i, j, nrrows);
	}
	if(randd() < shiftRowRate) {
		//printf("shiftrow\n");
		i = rand() % nrcols;
		j = (i + (rand() % (nrcols - 1) + 1)) % nrcols;
		shiftRow(nkey, key, i, j, nrcols);
	}
	if(randd() < shiftColRate) {
		//printf("shiftcol\n");
		i = rand() % nrrows;
		j = (i + (rand() % (nrrows - 1) + 1)) % nrrows;
		shiftCol(nkey, key, i, j, nrrows);
	}
	if(randd() < revRowRate) {
		//printf("revrow\n");
		i = rand() % nrrows;
		reverseRow(nkey, key, i, nrcols);
	}
	if(randd() < revColRate) {
		//printf("revcol\n");
		i = rand() % nrcols;
		reverseCol(nkey, key, i, nrrows);
	}
	if(randd() < shuffleRate) {
		//printf("shuffle\n");
		for(i=0; i < (rand() % maxShuffle) + minShuffle; ++i) {
			i = rand() % nrcells;
			j = (i + rand() % (nrcells - 1) + 1) % nrcells;
			swap(nkey, key, i, j);
		}
	}
	if(randd() < swapRate) {
		//printf("swap\n");
		i = rand() % nrcells;
		j = (i + rand() % (nrcells - 1) + 1) % nrcells;
		swap(nkey, key, i, j);
	}
}