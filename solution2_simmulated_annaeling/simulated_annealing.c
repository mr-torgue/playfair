/* 
Python implementation was very slow. This had a huge impact because of the number of iterations.
TODO:
1) parameterize settings
2) flexible arguments
3) mutation rates as a struct
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include <math.h>
#include <time.h>
#include <ctype.h>

#include "../helpers/fitness.h"
#include "../helpers/mutations.h"
#include "../helpers/playfair.h"

/*
Performs the simmulated annaeling part. 
*/
void sa(char *C, char *key, int n, double (*fitnessFunc)(char *, short), short (*compareFunc)(double, double), double *bestScore, char *bestKey) {
	// initialize variables
	int Clen = strlen(C);
	int keylen = strlen(key);
	char *nkey = malloc((keylen + 1) * sizeof(char));
	char *P = malloc((Clen + 1) * sizeof(char));
	double delta, score;
	decipher(key, C, P, Clen);
	double maxScore = fitnessFunc(P, n);
	*bestScore = maxScore;
	strncpy(bestKey, key, keylen);

	// do the main loop
	int maxIterations = 100000;
	for(float annaelStep=4; annaelStep<32; annaelStep+=0.5) {
		printf("Step: %f\n", annaelStep);
		for(int i=0; i<maxIterations; ++i) {
			mutate(nkey, key, 0.05, 0.05, 0.1, 0.1, 0.01, 0.01, 0.6, 0.002, 8, 20, 5, 5);
			decipher(nkey, C, P, Clen);
			score = fitnessFunc(P, n);
			delta = score - maxScore;
			if(compareFunc(score, maxScore)) {
				strncpy(key, nkey, keylen);
				maxScore = score;
			}
			else if(annaelStep > 0) {
				if(pow(score/maxScore, annaelStep) > randd()) {
					strncpy(key, nkey, keylen);
					maxScore = score;
				}
			}
			if(compareFunc(maxScore, *bestScore)) {
				strncpy(bestKey, key, keylen);
				*bestScore = maxScore;
				printf("---------------------------\niteration: %d\nAnnael step: %f\nBest score: %f\nBest key: %s\n---------------------------\n", i, annaelStep, *bestScore, bestKey);
			}
		}
	}
	free(nkey);
	free(P);
}

/*
compare functions to take care of direction
*/
short compare(double score1, double score2) {
	return score1 > score2;
}

short compareReverse(double score1, double score2) {
	return score1 < score2;
}

/*
simmulated annael wrapper
*/
void saw(char *C, char *alphabet, int n, int seed, double (*fitnessFunc)(char *, short), short (*compareFunc)(double, double)) {
	// setup variables
	int keylen = strlen(alphabet);
	double *bestScore = malloc(sizeof(double));
	char *bestKey = malloc((keylen + 1) * sizeof(char));
	char *startkey = malloc((keylen + 1) * sizeof(char));

	// setup keys and bestkey
	strcpy(startkey, alphabet);
	startkey[keylen] = '\0';
	bestKey[keylen] = '\0';
	srand(seed);
	printf("STARTING SIMMULATED ANNAELING:\nStart key: %s(%d) \nSeed: %d ", startkey, keylen, seed);
	
	// bestscore and bestkey are passed by reference
	sa(C, startkey, n, fitnessFunc, compareFunc, bestScore, bestKey);
	
	// decrypt using best found key
	char *P = malloc((strlen(C) + 1) * sizeof(char));
	decipher(bestKey, C, P, strlen(C));
	printf("RESULTS:\nBest key: %s\nBest score: %f\nDecrypted text: %s\n", bestKey, *bestScore, P);
	free(bestKey);
	free(startkey);
	free(P);
	free(bestScore);
}
/*
Sanitizes the text by only allowing characters also in alphabet
*/
char *sanitize(char *text, const char *alphabet) {
	char c;
	int textlen = strlen(text);
	int alphalen = strlen(alphabet);
	char *newtext = malloc((textlen + 1) * sizeof(char));
	int index = 0;
	for(int i=0; i<textlen; ++i) {
		c = tolower(text[i]);
		for(int j=0; j<alphalen; ++j) {
			if(c == alphabet[j]) {
				newtext[index] = c;
				index++;
				break;
			}
		}
	}
	newtext[index] = '\0';
	return newtext;
}

/*
main function
*/
int main(int argc, char **argv) {
	// setup variables
	FILE *fp;
	char *rawtext, *text;
	char *alphabet = "abcdefghiklmnopqrstuvwxyz\0";
	int n = 3;
	int seed = 123;
	double (*fitnessFunc)(char *, short) = &freqScore;
	short (*compareFunc)(double, double) = &compare;

	// parse command line arguments
	switch(argc) {
		case 5:
			seed = atoi(argv[4]);
		case 4:
			n = atoi(argv[3]);
		case 3:
			if(strcmp(argv[2], "simple") == 0) {
				fitnessFunc = &freqScore;
				compareFunc = &compare;
			}
			else if(strcmp(argv[2], "diff") == 0) {
				fitnessFunc = &diffScore;
				compareFunc = &compare;
			}
			else if(strcmp(argv[2], "count") == 0) {
				fitnessFunc = &countScore;
				compareFunc = &compare;
			}
			else if(strcmp(argv[2], "chi") == 0) {
				fitnessFunc = &chiSquared;
				compareFunc = &compareReverse;
			}
			else if(strcmp(argv[2], "G") == 0) {
				fitnessFunc = &GTest;
				compareFunc = &compareReverse;
			}
			else {
				printf("Usage: ./simmulated_annaeling [filename] [fitness function] [n] [seed]\n");
				exit(0);
			}
		case 2:
		    fp = fopen(argv[1], "r");
		    fseek(fp, 0, SEEK_END);
			long fsize = ftell(fp);
			fseek(fp, 0, SEEK_SET);
			rawtext = malloc(fsize + 1);
			fread(rawtext, 1, fsize, fp);
			rawtext[fsize] = 0;
			text = sanitize(rawtext, alphabet);
		    fclose(fp);
			break;
		default:
			// executes when the incorrect number of params is given
			printf("Usage: ./simmulated_annaeling [filename] [fitness function] [n] [seed]\n");
			exit(0);
	}
	// initialize fitness function statistics
	initialize();
	saw(text, alphabet, n, seed, &freqScore, &compare);
	free(text);
}