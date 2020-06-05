/*
Compile as shared library:
gcc -c -fPIC playfair_mydecrypt.c -o playfair.o
gcc playfair.o -shared -o libplayfairdecrypt.so
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Coords {
   short  row;
   short  col;
};  

void decipher(char *key, char *ciphertext, char *plaintext, int len) {
	char c1, c2;
	// generate the keymap
	struct Coords *keymap = calloc(25, sizeof(struct Coords));
	for(int i=0; i<5; ++i) {
		for(int j=0; j<5; ++j) {
			struct Coords coords = {i, j}; 
			keymap[(int)key[i*5+j] - 'a'] = coords;
		}
	}
	for (int i=0; i<len; i+=2) {
		c1 = ciphertext[i];
		c2 = ciphertext[i+1];
		struct Coords coords1 = keymap[(int)c1 - 'a'];
		struct Coords coords2 = keymap[(int)c2 - 'a'];
		if (coords1.row == coords2.row) { 
			plaintext[i] = key[coords1.row * 5 + (coords1.col + 4) % 5];
			plaintext[i+1] = key[coords2.row * 5 + (coords2.col + 4) % 5];
		} 
		else if (coords1.col == coords2.col ) {
			plaintext[i] = key[((coords1.row + 4) % 5) * 5 + coords1.col];
			plaintext[i+1] = key[((coords2.row + 4) % 5) * 5 + coords2.col];
		} 
		else { 
			plaintext[i] = key[coords1.row * 5 + coords2.col];
			plaintext[i+1] = key[coords2.row * 5 + coords1.col];
		}
	}
	plaintext[len] = '\0';
	free(keymap);
}

void decipherNoWrap(char *key, char *ciphertext, char *plaintext, int len) {
	char c1, c2;
	// generate the keymap
	struct Coords *keymap = calloc(25, sizeof(struct Coords));
	for(int i=0; i<5; ++i) {
		for(int j=0; j<5; ++j) {
			struct Coords coords = {i, j}; 
			keymap[(int)key[i*5+j] - 'a'] = coords;
		}
	}
	for (int i=0; i<len; i+=2) {
		c1 = ciphertext[i];
		c2 = ciphertext[i+1];
		struct Coords coords1 = keymap[(int)c1 - 'a'];
		struct Coords coords2 = keymap[(int)c2 - 'a'];
		if (coords1.row == coords2.row) { 
			if(coords1.col == 0) {
				plaintext[i] = key[coords1.row * 5 + (coords1.col + 1)];
			}
			else {
				plaintext[i] = key[coords1.row * 5 + (coords1.col - 1)];
			}
			if(coords2.col == 0) {
				plaintext[i+1] = key[coords2.row * 5 + (coords2.col + 1)];
			}
			else {
				plaintext[i+1] = key[coords2.row * 5 + (coords2.col - 1)];	
			}
		} 
		else if (coords1.col == coords2.col ) {
			if(coords1.row == 0) {
				plaintext[i] = key[(coords1.row + 1) * 5 + coords1.col];
			}
			else {
				plaintext[i] = key[(coords1.row - 1) * 5 + coords1.col];
			}
			if(coords2.row == 0) {
				plaintext[i+1] = key[(coords2.row + 1) * 5 + coords2.col];
			}
			else {
				plaintext[i+1] = key[(coords2.row - 1) * 5 + coords2.col];
			}
		} 
		else { 
			plaintext[i] = key[coords1.row * 5 + coords2.col];
			plaintext[i+1] = key[coords2.row * 5 + coords1.col];
		}
	}
	plaintext[len] = '\0';
	free(keymap);
}