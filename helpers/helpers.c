/*
Contains helper functions. Used for generating frequencies out of counts.
*/

#include <stdio.h>
#include <stdlib.h>

void sortIndices(long counts[], int indices[], int l, int r);
void merge(long counts[], int indices[], int l, int m, int r);

double *getFrequencies(long counts[], int len) {
	double *frequencies = malloc(len * sizeof(double));
	long total = 0;
	for(int i=0; i<len; ++i) {
		total += counts[i];
	}
	for(int i=0; i<len; ++i) {
		frequencies[i] = (double)counts[i] / total;
	}
	return frequencies;
}

/*
Ranks all the ngrams from 0 to total ngrams.
Returns a list with ranks.
*/
int *rank(long counts[], int len) {
    // initialize int array
    int *indices = malloc(len * sizeof(int));
    int *rankings = malloc(len * sizeof(int));
    for(int i=0; i < len; ++i) {
        indices[i] = i;
    }
	sortIndices(counts, indices, 0, len);
	for(int i=0; i < len; ++i) {
		rankings[indices[i]] = i;
	}
    free(indices);
	return rankings;
}

void sortIndices(long counts[], int indices[], int l, int r) {
	if(l < r) {
		int m = (l+r)/2;
		sortIndices(counts, indices, l, m);
		sortIndices(counts, indices, m+1, r);
		merge(counts, indices, l, m, r);
	}
}

void merge(long counts[], int indices[], int l, int m, int r) {
	int i, j, k; 
    int n1 = m - l + 1; 
    int n2 =  r - m; 
    /* create temp arrays */
    int L[n1], LI[n1], R[n2], RI[n2]; 
    /* Copy data to temp arrays L[] and R[] */
    for (i = 0; i < n1; i++) {
        L[i] = counts[l + i]; 
        LI[i] = indices[l + i];
    }
    for (j = 0; j < n2; j++) {
        R[j] = counts[m + 1+ j]; 
        RI[j] = indices[m + 1+ j];
    }
    /* Merge the temp arrays back into arr[l..r]*/
    i = 0; // Initial index of first subarray 
    j = 0; // Initial index of second subarray 
    k = l; // Initial index of merged subarray 
    while (i < n1 && j < n2) { 
        if (L[i] <= R[j]) { 
            counts[k] = L[i];
            indices[k] = LI[i];
            i++; 
        } 
        else { 
            counts[k] = R[j]; 
            indices[k] = RI[j];
            j++; 
        } 
        k++; 
    } 
    /* Copy the remaining elements of L[], if there 
       are any */
    while (i < n1) { 
        counts[k] = L[i]; 
        indices[k] = LI[i];
        i++; 
        k++; 
    }
    /* Copy the remaining elements of R[], if there 
       are any */
    while (j < n2) { 
        counts[k] = R[j]; 
        indices[k] = RI[j];
        j++; 
        k++; 
    } 
}