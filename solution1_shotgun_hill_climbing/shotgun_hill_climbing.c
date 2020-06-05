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
void hillclimbing(char *C, char *key, int n, double (*fitnessFunc)(char *, short), short (*compareFunc)(double, double), double *bestScore, char *bestKey) {
	// initialize variables
	int Clen = strlen(C);
	int keylen = strlen(key);
	char *nkey = malloc((keylen + 1) * sizeof(char));
	char *P = malloc((Clen + 1) * sizeof(char));
	double delta, score;
	decipher(key, C, P, Clen);
	*bestScore = fitnessFunc(P, n);
	strncpy(bestKey, key, keylen);

	// do the main loop
	int maxIterations = 1000000;
	int stopIterations = 100000;
	int currentIteration = 0;
	int iterationWithoutImprovement = 0;

	while(iterationWithoutImprovement < stopIterations && currentIteration < maxIterations) {
		mutate(nkey, key, 0.05, 0.05, 0.1, 0.1, 0.01, 0.01, 0.6, 0.002, 8, 20, 5, 5);
		decipher(nkey, C, P, Clen);
		score = fitnessFunc(P, n);
		delta = score - *bestScore;
		if(compareFunc(score, *bestScore)) {
			strncpy(key, nkey, keylen);
			*bestScore = score;
			strncpy(bestKey, key, keylen);
			iterationWithoutImprovement = 0;
			printf("---------------------------\niteration: %d\nBest score: %f\nBest key: %s\n---------------------------\n", currentIteration, *bestScore, key);
		}
		else {
			iterationWithoutImprovement++;
		}
		currentIteration++;
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
shotgun wrapper for hill climbing
*/
void shotgun(char *C, char *alphabet, int n, int seed, double (*fitnessFunc)(char *, short), short (*compareFunc)(double, double), int restarts) {
	// setup variables
	int keylen = strlen(alphabet);
	double bestScore = 0.0;
	char *bestKey = malloc((keylen + 1) * sizeof(char));
	char *startkey = malloc((keylen + 1) * sizeof(char));

	// setup keys and bestkey
	strcpy(bestKey, alphabet);
	startkey[keylen] = '\0';
	bestKey[keylen] = '\0';
	srand(seed);
	strcpy(startkey, alphabet);
	printf("STARTING SHOTGUN HILLCLIMBING:\nStart key: %s(%d) \nSeed: %d\n", startkey, keylen, seed);
	for(int i=0; i<restarts; ++i) {
		double *maxScore = malloc(sizeof(double));
		char *maxKey = malloc((keylen + 1) * sizeof(char));
		strcpy(startkey, alphabet);
		// bestscore and bestkey are passed by reference
		hillclimbing(C, startkey, n, fitnessFunc, compareFunc, maxScore, maxKey);
		if(bestScore == 0.0 || compareFunc(*maxScore, bestScore)) {
			printf("score improved from %s(%f) to %s(%f)\n", bestKey, bestScore, maxKey, *maxScore);
			strcpy(bestKey, maxKey);
			bestScore = *maxScore;
		}
		free(maxScore);
		free(maxKey);
	}
	// decrypt using best found key
	char *P = malloc((strlen(C) + 1) * sizeof(char));
	decipher(bestKey, C, P, strlen(C));
	printf("RESULTS:\nBest key: %s\nBest score: %f\nDecrypted text: %s\n", bestKey, bestScore, P);
	free(P);
	free(bestKey);
	free(startkey);
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
	int restarts = 10;
	double (*fitnessFunc)(char *, short) = &freqScore;
	short (*compareFunc)(double, double) = &compare;

	// parse command line arguments
	switch(argc) {
		case 6:
			seed = atoi(argv[5]);
		case 5:
			restarts = atoi(argv[4]);
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
				printf("Usage: ./shotgun_hill_climbing [filename] [fitness function] [n] [restarts] [seed]\n");
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
			free(rawtext);
		    fclose(fp);
			break;
		default:
			// executes when the incorrect number of params is given
			printf("Usage: ./shotgun_hill_climbing [filename] [fitness function] [n] [restarts] [seed]\n");
			exit(0);
	}
	// initialize fitness function statistics
	initialize();
	shotgun(text, alphabet, n, seed, &freqScore, &compare, 2);
	free(text);
}