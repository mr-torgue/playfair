'''
Genetic algorith approach for cracking playfair cipher. 
GENETIC REPRESENTATION:
A string of 25 charcters, each character occurs only once.
Alphabet by default is abcdefghiklmnopqrstuvwxyz.
FITNESS FUNCTION:
Sum of ngram frequencies after decrypting a text with the solutions.
G-test or chi-squared test also possible.
AGORITHM:
Specify number of iterations and population size
Generate a set with random individuals. 
Score inviduals.
Select individuals for cross-over to create offspring(until population size is reached)
Mutate new inviduals.
Repeat...
'''

import numpy as np
import json
import pickle

from time import localtime, strftime
from helpers import mutations as mut
from helpers import selection as sel
from ctypes import *

libplayfair = CDLL("../lib/libplayfairdecrypt.so")
libfitness = CDLL("../lib/libfitness.so")

class GAPlayFair:

	'''
	initialize GA from json settings file.
	'''
	def __init__(self, settings):
		with open(settings) as json_file:
			data = json.load(json_file)
			# load seed and create random number generator
			self.seed = self.try_load("seed", settings, np.random.randint(1000000))
			self.prng = np.random.RandomState(self.seed)
			# load general GA settings
			self.nr_restarts = self.try_load("nr_restarts", data, 1)
			self.population_size = self.try_load("population_size", data, 200)
			self.nr_iterations = self.try_load("nr_iterations", data, 100)
			self.alphabet = self.try_load("alphabet", data, "abcdefghiklmnopqrstuvwxyz")
			# logging, log_n specifies that once every log_n generations the results are logged
			self.output_file = self.try_load("output_file", data["logging"], "out")
			self.log_n = self.try_load("n", data["logging"], 10)
			self.verbose = self.try_load("verbose", data["logging"], False)
			self.quiet = self.try_load("quiet", data["logging"], False)
			# scoring
			self.score_function_name = self.try_load("function", data["scoring"], "simple")
			if self.score_function_name == "simple":
				self.score_function = libfitness.simpleScore
				n = self.try_load("n", data["scoring"], 3)
				self.score_params = [n]
			elif self.score_function_name == "ioc":
				raise Exception("Not yet implemented!")
			elif self.score_function_name == "chi":
				self.score_function = libfitness.chiSquared
				n = self.try_load("n", data["scoring"], 3)
				self.score_params = [n]
			elif self.score_function_name == "G":
				self.score_function = libfitness.GTest
				n = self.try_load("n", data["scoring"], 3)
				self.score_params = [n]
			elif self.score_function_name == "weight":
				self.score_function = libfitness.weightedSimpleScore
				n = self.try_load("n", data["scoring"], 3)
				self.score_params = [n]
			else:
				raise Exception("Scoring function %s not available!" % (self.score_function_name))
			# selection
			self.select_function_name = self.try_load("function", data["selection"], "elite")
			if self.select_function_name == "elite":
				self.select_function = sel.select_elitism
				rate = self.try_load("rate", data["selection"], 0.5)
				self.select_params = [rate]
			elif self.select_function_name == "roulette":
				self.select_function = sel.select_roulette
				rate = self.try_load("rate", data["selection"], 0.5)
				self.select_params = [rate]
			else:
				raise Exception("Selection function %s not available!" % (self.select_function_name))
			# mutation
			self.swap_rate = self.try_load("swap_rate", data["mutation"], 0.25)
			self.row_swap_rate = self.try_load("row_swap_rate", data["mutation"], 0.05)
			self.col_swap_rate = self.try_load("col_swap_rate", data["mutation"], 0.02)
			self.row_shift_rate = self.try_load("row_shift_rate", data["mutation"], 0.05)
			self.col_shift_rate = self.try_load("col_shift_rate", data["mutation"], 0.02)
			self.shuffle_rate = self.try_load("shuffle_rate", data["mutation"], 0.005)
			self.min_shuffle = self.try_load("min_shuffle", data["mutation"], 5)
			print("%s" % (self.settings_str()))
			print("Verify settings!")
			input()

	'''
	tries to return data[key] if it does not exist return default_value
	'''
	def try_load(self, key, data, default_value):
		try:
			return data[key]
		except:
			return default_value

	'''
	Return settings as a string
	'''
	def settings_str(self):
		return """GENERAL:\nSeed: %s\nNr populations: %d\nPopulation size: %d\nNr restarts: %d\nAlphabet: %s
OUTPUT:\nFile: %s\nLogN: %d\nSCORING:\nFunctionname: %s\nParameters: %s\nSELECTION:\nFunctionname: %s
Parameters: %s\nMUTATION:\nSwap rate: %f\nRow swap rate: %f\nCol swap rate: %f\nRow shift rate: %f
Col shift rate: %f\nShuffle rate: %f\nMin shuffle: %d""" % (self.seed, self.nr_iterations, 
			self.population_size, self.nr_restarts, self.alphabet, self.output_file, self.log_n, self.score_function_name,
			self.score_params, self.select_function_name, self.select_params, self.swap_rate, self.row_swap_rate,
			self.col_swap_rate, self.row_shift_rate, self.col_shift_rate, self.shuffle_rate, self.min_shuffle)	
	
	'''
	Runs the genetic algorithm. Each restart can be done parralel.
	Max 16 processes.
	'''
	def run(self, text):
		results = [self.gago(text) for _ in range(self.nr_restarts)]
		timestamp = strftime("%Y-%m-%d_%H:%M:%S", localtime())
		for i in range(len(results)):
			result = results[i]
			fname = "dataout/" + self.output_file + "_" + timestamp + "_" + str(i)
			with open(fname + ".pickle", "wb") as f:
				pickle.dump(result, f)
			with open(fname + ".out", "w") as f:
				f.write("%s\n" % (self.settings_str()))
				f.write("key %s: score %f" % (result[1], result[2]))
				f.write("plaintext:\n%s" % libplayfair.decipher(str.encode(result[1]), str.encode(text), len(text)).decode())


		'''
		with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
			futures = [executor.submit(self.gago, text) for i in range(self.nr_restarts)]
			for future in futures:
				data = future.result()
		'''


	'''
	Get statistics from scores.
	Length should be equal to len(sorted_scores).
	sorted_scores should be sorted from high to low
	Returns [mean, standard deviation, max, min, 25percentile, median, 75percentile]
	'''
	def get_statistics(self, sorted_scores, _sum):
		length = len(sorted_scores)
		mean = _sum / length
		_max = sorted_scores[0]
		_min = sorted_scores[-1]
		_25p = sorted_scores[int(length * 0.75)]
		median = sorted_scores[int(length * 0.5)]
		_75p = sorted_scores[int(length * 0.25)]
		return [mean, _max, _min, _25p, median, _75p]

	'''
	Run the algorithm
	'''
	def gago(self, text):
		if not self.quiet:
			print("Starting GA with seed %d\nNr populations: %s, Population size: %d\nLogging every %d generation." % (self.seed, self.nr_iterations, self.population_size, self.log_n))
		population = self.generate()
		max_key = ""
		max_score = 0
		results = []
		for iteration in range(self.nr_iterations):
			# score and sort
			[scores, _sum]  = self.score(text, population)
			sorted_indices = np.argsort(scores)[::-1] 
			sorted_scores = scores[sorted_indices]
			# store results
			result = self.get_statistics(sorted_scores, _sum)
			if not self.quiet:
				print("%d: %f" % (iteration, result[0]))
			results.append(result)
			max_index = sorted_indices[0]
			if scores[max_index] > max_score:
				max_score = scores[max_index]
				max_key = population[max_index]
			# normalize scores and select indices
			norm_scores = [score / _sum for score in scores]
			selection_indices = self.select_function(norm_scores, self.prng, *self.select_params)
			selection = population[selection_indices]
			new_population = self.cross_over(selection)
			new_population = self.mutate(new_population)
			population = new_population
		return [results, max_key, max_score]

	'''
	Scores population based on provided function and params.
	Also returns the sum of the scores.
	'''
	def score(self, text, population):
		scores = [0] * len(population)
		_sum = 0.0
		for i in range(len(population)):
			p = population[i]
			scores[i] = self.score_function(libplayfair.decipher(str.encode(p), str.encode(text), len(text)), *self.score_params)
			_sum += scores[i]
		return [np.array(scores), _sum]

	'''
	Mutates all individuals in the population.
	Mutations are not exclusive.
	'''
	def mutate(self, population):
		new_population = []
		for p in population:
			if self.prng.random() < self.swap_rate:
				i = self.prng.randint(0, 25)
				j = (i + self.prng.randint(1, 25)) % 25
				p = mut.swap(p, i, j)
			if self.prng.random() < self.row_swap_rate:
				i = self.prng.randint(0, 5)
				j = (i + self.prng.randint(1, 5)) % 5
				p = mut.swap_row(p, i, j)
			if self.prng.random() < self.col_swap_rate:
				i = self.prng.randint(0, 5)
				j = (i + self.prng.randint(1, 5)) % 5
				p = mut.swap_col(p, i, j)
			if self.prng.random() < self.row_shift_rate:
				i = self.prng.randint(0, 5)
				j = (i + self.prng.randint(1, 5)) % 5
				p = mut.shift_row(p, i, j)
			if self.prng.random() < self.col_shift_rate:
				i = self.prng.randint(0, 5)
				j = (i + self.prng.randint(1, 5)) % 5
				p = mut.shift_col(p, i, j)
			if self.prng.random() < self.shuffle_rate:
				for _ in range(self.prng.randint(self.min_shuffle, 20)):
					i = self.prng.randint(0, 25)
					j = (i + self.prng.randint(1, 25)) % 25
					p = mut.swap(p, i, j)
			new_population.append(p)
		return np.array(new_population)

	'''
	Swaps str1[index] and str2[index]
	'''
	def swap2(self, index, str1, str2):
		return [str1[:index] + str2[index] + str1[(index + 1):], str2[:index] + str1[index] + str2[(index + 1):]]

	'''
	Crossover helper function
	'''
	def find_dup_index(self, str1, index):
		for i in range(len(str1)):
			for j in range(i + 1, len(str1)):
				if str1[i] == str1[j]:
					if i == index:
						return j
					else:
						return i
	'''
	Does a fancy cross-over
	'''
	def cross_over(self, selection):
		new_population = []
		for i in range(int(self.population_size / 2)):
			parents = self.prng.choice(selection, 2, False)
			index = self.prng.randint(len(parents[0]))
			offspring = self.swap2(index, parents[0], parents[1])
			while len(set(offspring[0])) != len(offspring[0]):
				index = self.find_dup_index(offspring[0], index)
				offspring = self.swap2(index, offspring[0], offspring[1])
			new_population += offspring
		return np.array(new_population)

	'''
	generates a random population
	'''
	def generate(self):
		return np.array(["".join(self.prng.permutation(list(self.alphabet))) for i in range(self.population_size)])

libplayfair.decipher.restype = c_char_p 
libplayfair.decipher.argtypes = [c_char_p, c_char_p, c_int]
libfitness.simpleScore.restype = c_double 
libfitness.simpleScore.argtypes = [c_char_p, c_int]
libfitness.weightedSimpleScore.restype = c_double 
libfitness.weightedSimpleScore.argtypes = [c_char_p, c_int]
libfitness.GTest.restype = c_double 
libfitness.GTest.argtypes = [c_char_p, c_int]
libfitness.chiSquared.restype = c_double 
libfitness.chiSquared.argtypes = [c_char_p, c_int]

'''
C = "umcudpwntwkcdyeazuphsptiwdlaheftdypsurmkynarnkslphfrledpwgrdruwebqapoweulsalftrslsdpwukcsedpaualftkdaepaftmwqwbttrskulrslsrcumcudpawygaplfuespbltrlaapuldlaprslsumcudpwneqluzhdwsurgdrkfdkspmupuotutdrmtgqapumrdapluhaalfttrlsdpauftumcuqwbfphmymuesalftlwtspaftkcdyeavgclrfebkqresmhbaplwheftqwtoygrcfdtrshwmahkpabkbctmswqpuftkdaephsedpsphoygkpkodgulclrfeioteuwmledpwultfbwtapsmleulrclbksuvdpauftqweurcbqhbezaptrfrdprohoeveuruyntoygowebmwlskpphiqsuwgxnrarfpgendpuwedkphufttnmtamotrtcopsbphkrfkwwgtsahmlwqslpdxrmfrkaptryneutwfufxdpkbeaqiurrfkqkpbnslpdxrmfrkaptrynskhzumkplttoabwlusseurgdwmynapusphygapflpuedmsluyntoygfshoxrdtpkbmurlshasmpuftapflpuedzdygwqkgusftdhlrgrqwkcxldxabkbbcufdpgdwmynapusbfumstdxphtbwawtnbpkbmhopuglesedotdpouufotknzhhldkapsrnwrforoeauftumcuqwctdpnddhusftdpcukbdpfbedfbdpruynsktbtoasfthwwqebrdaplfrkkrkuwoeuhdelqusuiercpryualftofdlpuwmulwddlygapsrrduoruxlocmtwnmuyntoygdpauftkcdyeaquzhoepwxrpuwdququsukrghclrfpnumapwtfsumbqruuvwaaksuwgvdaprfpdspdklsftkpgdlswmotfrlcetspdkfshdpkpubfumstdxumcudpaudwiucrfxkpbnsllwbkusqnpualftoroewubmwespygtleapwsklugyhakwmuyntoyglsrfdwkpqwfbmscevurobpeveldpantokplutilfpwevuvkpflpudwtoyglwtsftdmumcudpagrolxrfaprfsmltktdpawygkrdyahkpdllsrfdwkpkpapumrdapcrfrzrnieuapueopurqweakbahygmtmypkmutwygkpapsrulehrdrerpkturwdeprvrddpaufttbdritbpfrbpevelaplfhzpsotqwocygdkabkbfzphlsfttodfulepusdrkaskahpdfrwpigalpaftdypsurmkynarprygapreutdrmtdpdykwmyigumcudpwukanttospdkrcclrfnkevskdkkcniwmlulwheftkanttospdkrcaputpksuonkpngrktodfuevgdkflpudwsuawdrdyoudkarpuftlwtsftwtahygkcydwfhakwiukpaprxnwtoyglsftkdaebaulezapumrdaptrlsdpgurdilbpfrabkbftohgalxueakurwtprkwwmygtleapweoufkwiugdwmynapusbfumstdxaplmkpngrkrcumcudpaobpfbrhsuwmkgetruaootulflwturfskphdluzhdwsulwxlfrnbiuahsudkprqdftpuftohslrcdykwpitskplarmmrhlapusrfiedhfrurkpapusfrhavdgepkdkaptmfrqkdluqtrfefrlteskpbnpdkasksphoetpkdkbqapaplmkpngrkrclbaltoyglafotrsuaplmkpngrkrcfdtrshwmahkpkpfdtrshwmahkpowltpksuaopspaftmkynarkrbmfrtoygapdrdnphkdaprfohlagepkdklafskcxraputpksuonkpngrkrcfdtrshwmahkpdpwnfrtoygkpapsmwmtbmfreulahsuluflrurgdrpeftdypsurmkynarketrwnynlaapuehasuwfsmynfrpdxrauftdypsurmkynarkrghfrhafwpswppdygkdaeftdmmwuedpry"
#attack_simulated_annael(C, n=3)
start(C, selection_function=selection.select_elitism, n=3)

def main(settings):
	start(settings)
'''
#C = "umcudpwntwkcdyeazuphsptiwdlaheftdypsurmkynarnkslphfrledpwgrdruwebqapoweulsalftrslsdpwukcsedpaualftkdaepaftmwqwbttrskulrslsrcumcudpawygaplfuespbltrlaapuldlaprslsumcudpwneqluzhdwsurgdrkfdkspmupuotutdrmtgqapumrdapluhaalfttrlsdpauftumcuqwbfphmymuesalftlwtspaftkcdyeavgclrfebkqresmhbaplwheftqwtoygrcfdtrshwmahkpabkbctmswqpuftkdaephsedpsphoygkpkodgulclrfeioteuwmledpwultfbwtapsmleulrclbksuvdpauftqweurcbqhbezaptrfrdprohoeveuruyntoygowebmwlskpphiqsuwgxnrarfpgendpuwedkphufttnmtamotrtcopsbphkrfkwwgtsahmlwqslpdxrmfrkaptryneutwfufxdpkbeaqiurrfkqkpbnslpdxrmfrkaptrynskhzumkplttoabwlusseurgdwmynapusphygapflpuedmsluyntoygfshoxrdtpkbmurlshasmpuftapflpuedzdygwqkgusftdhlrgrqwkcxldxabkbbcufdpgdwmynapusbfumstdxphtbwawtnbpkbmhopuglesedotdpouufotknzhhldkapsrnwrforoeauftumcuqwctdpnddhusftdpcukbdpfbedfbdpruynsktbtoasfthwwqebrdaplfrkkrkuwoeuhdelqusuiercpryualftofdlpuwmulwddlygapsrrduoruxlocmtwnmuyntoygdpauftkcdyeaquzhoepwxrpuwdququsukrghclrfpnumapwtfsumbqruuvwaaksuwgvdaprfpdspdklsftkpgdlswmotfrlcetspdkfshdpkpubfumstdxumcudpaudwiucrfxkpbnsllwbkusqnpualftoroewubmwespygtleapwsklugyhakwmuyntoyglsrfdwkpqwfbmscevurobpeveldpantokplutilfpwevuvkpflpudwtoyglwtsftdmumcudpagrolxrfaprfsmltktdpawygkrdyahkpdllsrfdwkpkpapumrdapcrfrzrnieuapueopurqweakbahygmtmypkmutwygkpapsrulehrdrerpkturwdeprvrddpaufttbdritbpfrbpevelaplfhzpsotqwocygdkabkbfzphlsfttodfulepusdrkaskahpdfrwpigalpaftdypsurmkynarprygapreutdrmtdpdykwmyigumcudpwukanttospdkrcclrfnkevskdkkcniwmlulwheftkanttospdkrcaputpksuonkpngrktodfuevgdkflpudwsuawdrdyoudkarpuftlwtsftwtahygkcydwfhakwiukpaprxnwtoyglsftkdaebaulezapumrdaptrlsdpgurdilbpfrabkbftohgalxueakurwtprkwwmygtleapweoufkwiugdwmynapusbfumstdxaplmkpngrkrcumcudpaobpfbrhsuwmkgetruaootulflwturfskphdluzhdwsulwxlfrnbiuahsudkprqdftpuftohslrcdykwpitskplarmmrhlapusrfiedhfrurkpapusfrhavdgepkdkaptmfrqkdluqtrfefrlteskpbnpdkasksphoetpkdkbqapaplmkpngrkrclbaltoyglafotrsuaplmkpngrkrcfdtrshwmahkpkpfdtrshwmahkpowltpksuaopspaftmkynarkrbmfrtoygapdrdnphkdaprfohlagepkdklafskcxraputpksuonkpngrkrcfdtrshwmahkpdpwnfrtoygkpapsmwmtbmfreulahsuluflrurgdrpeftdypsurmkynarketrwnynlaapuehasuwfsmynfrpdxrauftdypsurmkynarkrghfrhafwpswppdygkdaeftdmmwuedpry"
C = "ocoyfolbvnpiasakopvygeskovmufguwmlnooedrncforsocvmtuutyerpfolbvnpiasakopvivkyeocnkoccaricvvltsocoytrfdvcvoouegkpvooyvkthzscvmbtwtrhpnklrcuegmslnvlzscansckopormzckizuslccvfdlvorthzscleguxmifolbimvivkiuayvuufvwvccbovovpfrhcacsfgeolckmocgeumohuebrlxrhemhpbmpltvoedrncforsgisthogilcvaioamvzirrlniiwusgewsrhcaugimforskvzmgclbcgdrnkcvcpyuxlokfyfolbvcckdokuuhavococlciusycrgufhbevkroicsvpftuqumkigpecemgcgpggmoqusyefvgfhralauqolevkroeokmuqirxccbcvmaodclanoynkbmvsmvcnvroedrncgeskysysluuxnkgegmzgrsonlcvagebglbimordprockinankvcnfolbceumnkptvktcgefhokpdulxsueopclanoynkvkbuoyodorsnxlckmglvcvgrmnopoyofocvkocvkvwofclanyefvuavnrpncwmipordgloshimocnmlccvgrmnopoyhxaifoouepgchk"
#x = GAPlayFair("../experiments/exp1/mut7.json")
x = GAPlayFair("settings.json")
x.run(C)


# lijst met frequenties
# Veel voorkomende frequenties belonen
# 