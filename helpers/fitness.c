/*
Author: Folmer Heikamp
Date: 05-08-2019
This C file contains several fitness functions based on character frequency.
Frequencies for mono, bi, tri and quad-grams are provided in the frequencies header.


Compile as shared library:
gcc -c -fPIC fitness.c -o fitness.o
gcc fitness.o -shared -o libfitness.so

*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include <math.h>
#include <time.h>

#include "helpers.h"
#include "counts.h"

extern long countMonogram[];
extern long countBigram[];
extern long countTrigram[];
extern long countQuadgram[];

long *counts[4];
double *frequencies[4];
int *ranks[4];

/*
Initializes
*/
void initialize() {
	int lenMono =  sizeof(countMonogram)/sizeof(countMonogram[0]);
	int lenBi =  sizeof(countBigram)/sizeof(countBigram[0]);
	int lenTri =  sizeof(countTrigram)/sizeof(countTrigram[0]);
	int lenQuad =  sizeof(countQuadgram)/sizeof(countQuadgram[0]);
	counts[0] = countMonogram;
	counts[1] = countBigram;
	counts[2] = countTrigram;
	counts[3] = countQuadgram;
	//ranks[0] = rank(countMonogram, lenMono);
	//ranks[1] = rank(countBigram, lenBi);
	//ranks[2] = rank(countTrigram, lenTri);
	//ranks[3] = rank(countQuadgram, lenQuad);
	frequencies[0] = getFrequencies(countMonogram, lenMono);
	frequencies[1] = getFrequencies(countBigram, lenBi); 
	frequencies[2] = getFrequencies(countTrigram, lenTri); 
	frequencies[3] = getFrequencies(countQuadgram, lenQuad);
}

/*
ngram returns the ngrams found in the text. 
text is the input. n is the size of the ngram, so n=2 are bigrams, n=3 are trigrams, etc.
counts and keys are passed by reference, it is assumed they have enough to store in.
counts has to be of size(text) and keys has to be of size(number of ngrams)
returns a int specigying how many different ngrams have been found.
counts is an array with counts per ngram, keys specifies which ngrams have been hit.
*/
int *ngram(char *text, short n) {
	int len = strlen(text);
	int *counts = calloc((int)pow(26, n), sizeof(int));
	for(int i=0; i<(len - (n - 1)); ++i) {
		int key = 0;
		for(int j=0; j<n; ++j) {
			key += (*(text + i + (n-j-1)) - 'a') * (int)pow(26, j);
		}
		counts[key]++;
	}
	return counts;
}

/*
Calculates the chi squared statistic based on text and n.
The observed ngram frequency is compared with the expected frequency (based on statistics)
*/
double chiSquared(char *text, short n) {
	int *counts;
	int len = strlen(text);
	double fitness = 0.0;
	double total = len - (n - 1);
	counts = ngram(text, n);
	for(int i=0; i<(int)pow(26, n); ++i) {
		fitness += pow((counts[i] / total) - frequencies[n-1][i], 2) / frequencies[n-1][i];
	}
	free(counts);
	return fitness * total;
}

/*
Works the same as the chiSquared function. It only uses other values.
*/
double GTest(char *text, short n) {
	int *counts;
	int len = strlen(text);
	counts = ngram(text, n);
	double fitness = 0.0;
	int total = len - (n - 1); 
	for(int i=0; i<(int)pow(26, n); ++i) {
		fitness += counts[i] * log(counts[i] / (frequencies[n-1][i] * total));
	}
	free(counts);
	return fitness * 2;
}

/*
*/
double countScore(char *text, short n) {
	double fitness = 0.0;
	int total = strlen(text) - (n - 1);
	for (int i = 0; i < total; i++) {
		int key = 0;
		for(int j=0; j<n; ++j) {
			key += (*(text + i + (n-j-1)) - 'a') * (int)pow(26, j);
		}
		fitness += log2(counts[n-1][key]);
	}
	return fitness;
}

double freqScore(char *text, short n) {
	double fitness = 0.0;
	int total = strlen(text) - (n - 1);
	for (int i = 0; i < total; i++) {
		int key = 0;
		for(int j=0; j<n; ++j) {
			key += (*(text + i + (n-j-1)) - 'a') * (int)pow(26, j);
		}
		fitness += frequencies[n-1][key];
	}
	return fitness;
}

double diffScore(char *text, short n) {
	int *ngramcounts = ngram(text, n);
	int total = strlen(text) - (n - 1);
	double fitness = 0.0;
	for(int i=0; i<(int)pow(26, n); ++i) {
		fitness += fabs(frequencies[n-1][i] - (double)(ngramcounts[i]) / total);
	}
	if(fitness == 0.0)
		return 0.001;
	free(ngramcounts);
	return 1 - log2(fitness);
}

/*
A simple scoring mechanism
*/
double weightedSimpleScore(char *text, short n) {
	double fitness = 0.0;
	int total = strlen(text) - (n - 1);
	for (int i = 0; i < total; i++) {
		int key = 0;
		for(int j=0; j<n; ++j) {
			key += (*(text + i + (n-j-1)) - 'a') * (int)pow(26, j);
		}
		fitness += frequencies[n-1][key];
	}
	return fitness;
}