import numpy as np
import sys
import concurrent.futures
import copy
import mutations as mt

from ctypes import *
libplayfair = CDLL("../lib/libplayfairdecrypt.so")
libfitness = CDLL("../lib/libfitness.so")

def sa(C, key, prng, alphabet, n, fitness_function, comparing_function):
	P = libplayfair.decipher(str.encode(key), str.encode(C), len(C)).decode()
	max_score = fitness_function(str.encode(P), n)
	best_score = max_score
	best_key = key
	print("key %s with score: %f" % (key, max_score))
	max_iterations = 100
	for annaelStep in np.arange(4, 32, 0.5):
		for iteration in range(max_iterations):
			nkey = mutate(key, prng)
			P = libplayfair.decipher(str.encode(nkey), str.encode(C), len(C)).decode()
			#P = P.replace("x", "")
			score = fitness_function(str.encode(P), n)
			delta = score - max_score
			#print fitness_score
			if comparing_function(score, max_score):
				key = nkey
				max_score = score
			elif annaelStep > 0:
				# at first the annael is pretty flexible, 
				# base if order of magnitude in dec difference 
				prob = np.power(score/max_score, annaelStep)
				if prob > prng.random(): 
					#print("replacing %s with %s, scores: %f and %f" % (key, nkey, current_score, fitness_score))
					key = nkey
					max_score = score
			if comparing_function(max_score, best_score):
				best_key = key
				best_score = max_score
				print("best score: %f for key %s (iter: %d, astep: %f)" % (best_score, key, iteration, annaelStep))
	return [best_key, best_score]

'''
compare functions so no if statement is needed for decrement and increment scoring
'''
def compare(score_1, score_2):
	return score_1 > score_2

def compare_reverse(score_1, score_2):
	return score_1 < score_2

def saw(C, seed=None, alphabet="abcdefghiklmnopqrstuvwxyz", n=2, fitness_function=libfitness.countScore, compare_function=compare):
	startkey = alphabet
	if seed == None:
		seed = np.random.randint(1000000)
	prng = np.random.RandomState(seed)
	print("seed: %d\nn: %d" % (seed, n))
	result = sa(C, startkey, prng, alphabet, n, fitness_function, compare_function)
	print("found %s\n for key %s with score %f" % (libplayfair.decipher(str.encode(result[0]), str.encode(C), len(C)).decode(), result[0], result[1]))
	

def mutate(key, prng):
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

def sanitize(text, alphabet="abcdefghijklmnopqrstuvwxyz"):
	text = text.lower()
	return "".join([t if t in alphabet else "" for t in text])

def main():
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
		print("Usage: python3 simmulated_annaeling.py [ciphertext filename] [n] [seed] [scoring function]\nappend \"> [filename]\" if output needs to be written to file")
	with open(filename) as f:
		text = sanitize(f.read())
		libfitness.initialize()
		saw(text, n=n, seed=seed, fitness_function=scoring_function, compare_function=compare_function)

if __name__== "__main__":
	main()