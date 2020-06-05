'''
A set of selection methods which can be used by the genetic algorithm.
Make sure that the definition for each function is the same.
'''
import numpy as np

'''
roulette wheel selection. 
The best scoring individuals have more chance of being selected.
'''
def select_roulette(scores, rand, rate=0.5):
	n = int(rate * len(scores))
	sorted_indices = np.argsort(scores)[::-1]
	scores = np.array(scores)
	sorted_scores = scores[sorted_indices]
	acc_scores = np.cumsum(sorted_scores)
	selection = []
	for i in range(n):
		r = rand.random()
		for j in range(len(acc_scores)):
			if acc_scores[j] > r:
				selection.append(sorted_indices[j])
				break
	return np.array(selection)

'''
elitism, just select the best individuals.
Has the benefit of being fast and never decreases fitness.
'''
def select_elitism(scores, rand, rate=0.5):
	n = int(rate * len(scores))
	sorted_indices = np.argsort(scores)[::-1]
	return sorted_indices[:n]
