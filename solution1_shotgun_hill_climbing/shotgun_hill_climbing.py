'''
Basic shotgun hill climbing algorithm.
The interface is through sysargs and is not very advanced.
The algorithm should be able to crack a message encrypted with the playfair cipher.
Approach is random but reproducable because of the seed. If no solution is found you can try another seed.

TODO:
1) Implent in C with concurrency. Ctypes does make multiprocessing difficult and multithreading does not give better results.
2) Parameterize the input
'''

import numpy as np
import sys
import concurrent.futures
import copy
import mutations as mt

# implementation uses ctypes because it is significantly faster than native python
from ctypes import *
libplayfair = CDLL("../lib/libplayfairdecrypt.so")
libfitness = CDLL("../lib/libfitness.so")

'''
Performs the hillclimbing part. Compare function is added because some scoring techniques value lower scores
whilst other value higher scores. Returns the best key with the coresponding score.
'''
def hillclimbing(C, key, prng, alphabet, n, fitness_function, compare_function):
	P = libplayfair.decipher(str.encode(key), str.encode(C), len(C)).decode()
	max_score = fitness_function(str.encode(P), n)
	print("key %s with score: %f" % (key, max_score))
	max_iterations = 1000000
	stop_iterations = 100000
	current_iteration = 0
	iteration_without_improvement = 0
	while iteration_without_improvement < stop_iterations and current_iteration < max_iterations:
		nkey = mutate(key, prng)
		P = libplayfair.decipher(str.encode(nkey), str.encode(C), len(C)).decode()
		fitness_score = fitness_function(str.encode(P), n)
		if compare_function(fitness_score, max_score):
			key = nkey
			max_score = fitness_score
			iteration_without_improvement = 0
			print("best score: %f for key %s (iter: %d)" % (max_score, key, current_iteration))
		else:
			iteration_without_improvement += 1
		current_iteration += 1
	return [key, max_score]

'''
compare functions so no if statement is needed for decrement and increment scoring
'''
def compare(score_1, score_2):
	return score_1 > score_2

def compare_reverse(score_1, score_2):
	return score_1 < score_2

'''
Mutate function. Mutation rates are not mutually exclusive.
Rates are a bit of trial and error.
'''
def mutate(key, prng):
	# is this copy needed?
	nkey = copy.deepcopy(key)
	if prng.random() < 0.05:
		i = prng.randint(0, 5)
		j = (i + prng.randint(1, 5)) % 5
		nkey = mt.swap_row(nkey, i, j)
	if prng.random() < 0.05:
		i = prng.randint(0, 5)
		j = (i + prng.randint(1, 5)) % 5
		nkey = mt.swap_col(nkey, i, j)
	if prng.random() < 0.1:
		i = prng.randint(0, 5)
		j = (i + prng.randint(1, 5)) % 5
		nkey = mt.shift_row(nkey, i, j)
	if prng.random() < 0.1:
		i = prng.randint(0, 5)
		j = (i + prng.randint(1, 5)) % 5
		nkey = mt.shift_col(nkey, i, j)
	if prng.random() < 0.01:
		i = prng.randint(0, 5)
		nkey = mt.reverse_row(nkey, i)
	if prng.random() < 0.01:
		i = prng.randint(0, 5)
		nkey = mt.reverse_col(nkey, i)
	if prng.random() < 0.002:
		for _ in range(prng.randint(8, 20)):
			i = prng.randint(0, 25)
			j = (i + prng.randint(1, 25)) % 25
			nkey = mt.swap(nkey, i, j)
	if prng.random() < 0.6:
		i = prng.randint(0, 25)
		j = (i + prng.randint(1, 25)) % 25
		nkey = mt.swap(nkey, i, j)
	return nkey

'''
Performs the shotgun part.
'''
def shotgun(C, seed=None, alphabet="abcdefghiklmnopqrstuvwxyz", random_restarts=32, n=3, fitness_function=libfitness.freqScore, compare_function=compare):
	max_results_key = ""
	max_results_score = None
	if seed == None:
		seed = np.random.randint(1000000)
	prng = np.random.RandomState(seed)
	print("seed: %d\nrestarts: %d\nn: %d" % (seed, random_restarts, n))
	for _ in range(random_restarts):
		startkey = "".join(prng.permutation(list(alphabet)))
		print("new restart with key %s" % startkey)
		result = hillclimbing(C, startkey, prng, alphabet, n, fitness_function, compare_function)
		if max_results_score == None or compare_function(result[1], max_results_score):
			max_results_key = result[0]
			max_results_score = result[1]
	print("found %s\nfor key %s with score %f" % (libplayfair.decipher(str.encode(max_results_key), str.encode(C), len(C)).decode(), max_results_key, max_results_score))
	
'''
sanitizes input.
'''
def sanitize(text, alphabet="abcdefghiklmnopqrstuvwxyz"):
	text = text.lower()
	return "".join([t if t in alphabet else "" for t in text])

def main():
	# initialize ctypes functions
	libplayfair.decipher.restype = c_char_p 
	libplayfair.decipher.argtypes = [c_char_p, c_char_p, c_int]
	libplayfair.decipherNoWrap.restype = c_char_p 
	libplayfair.decipherNoWrap.argtypes = [c_char_p, c_char_p, c_int]
	libfitness.countScore.restype = c_double 
	libfitness.countScore.argtypes = [c_char_p, c_int]
	libfitness.freqScore.restype = c_double 
	libfitness.freqScore.argtypes = [c_char_p, c_int]
	libfitness.diffScore.restype = c_double 
	libfitness.diffScore.argtypes = [c_char_p, c_int]
	libfitness.weightedSimpleScore.restype = c_double 
	libfitness.weightedSimpleScore.argtypes = [c_char_p, c_int]
	libfitness.GTest.restype = c_double 
	libfitness.GTest.argtypes = [c_char_p, c_int]
	libfitness.chiSquared.restype = c_double 
	libfitness.chiSquared.argtypes = [c_char_p, c_int]
	# load sys params
	try:
		filename = sys.argv[1]
		try:
			n = int(sys.argv[2])
		except:
			n = 4
		try:
			seed = int(sys.argv[3])
		except:
			seed = None
		try:
			score = sys.argv[4]
			if score == "simple":
				scoring_function = libfitness.freqScore
				compare_function = compare
			if score == "count":
				scoring_function = libfitness.countScore
				compare_function = compare
			if score == "diff":
				scoring_function = libfitness.diffScore
				compare_function = compare
			elif score == "chi":
				scoring_function = libfitness.chiSquared
				compare_function = compare_reverse
			elif score == "G":
				scoring_function = libfitness.GTest
				compare_function = compare_reverse
			elif score == "weight":
				scoring_function = libfitness.weightedSimpleScore
				compare_function = compare
			else:
				raise Exception("Unknown scoring function")
		except:
			scoring_function = libfitness.freqScore
			compare_function = compare	
	except:
		print("Usage: python3 attack_hill_climbing.py [ciphertext filename] [n] [seed] [scoring function]\nappend \"> [filename]\" if output needs to be written to file")
	with open(filename) as f:
		text = sanitize(f.read())
		libfitness.initialize()
		shotgun(text, n=n, seed=seed, fitness_function=scoring_function, compare_function=compare_function)

if __name__== "__main__":
	main() 