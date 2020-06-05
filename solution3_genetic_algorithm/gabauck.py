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

from helpers import mutations
from helpers import selection
from ctypes import *
libplayfair = CDLL("../lib/libplayfairdecrypt.so")
libfitness = CDLL("../lib/libfitness.so")

class GAPlayFair:

	'''
	tries to return data[key] if it does not exist return default_value
	'''
	def try_load(self, key, data, default_value):
		try:
			return data[key]
		except:
			return default_value

	'''
	initialize GA from json settings file.
	'''
	def __init__(self, settings):
		with open(settings) as json_file:
    		data = json.load(json_file)
    		# load seed and create random number generator
			self.seed = self.try_load("seed", settings, np.random.randint(1000000))
			self.prng = np.random.RandomState(seed)
			# load general GA settings
			self.nr_restarts = self.try_load("nr_restarts", settings, 1)
			self.pop_size = self.try_load("population_size", settings, 200)
			self.nr_it = self.try_load("nr_iterations", settings, 100)
			self.alphabet = self.try_load("alphabet", settings, "abcdefghiklmnopqrstuvwxyz")
			# logging, log_n specifies that once every log_n generations the results are logged
			self.output_file = self.try_load("output_file", settings["logging"], "out")
			self.log_n = self.try_load("n", settings["logging"], 10)
			self.verbose = self.try_load("verbose", settings["logging"], False)
			self.quiet = self.try_load("quiet", settings["logging"], False)
			# scoring
			self.score_function_name = self.try_load("function", settings["scoring"], "simple")
			if self.score_function_name == "simple":
				self.score_function = libfitness.simpleScore
				n = self.try_load("n", settings["scoring"], 3)
				self.score_params = [n]
			elif self.score_function_name == "ioc":
				raise Exception("Not yet implemented!")
			elif self.score_function_name == "chi":
				self.scoring_function = libfitness.chiSquared
				n = self.try_load("n", settings["scoring"], 3)
				self.score_params = [n]
			elif self.score_function_name == "G":
				self.scoring_function = libfitness.GTest
				n = self.try_load("n", settings["scoring"], 3)
				self.score_params = [n]
			else:
				raise Exception("Scoring function %s not available!" % (self.score_function_name))
			# selection
			self.select_function_name = self.try_load("function", settings["selection"], "elite")
			if self.select_function_name == "elite":
				self.select_function = selection.select_elitism
				rate = self.try_load("rate", settings["selection"], 0.5)
				self.select_params = [rate]
			elif self.select_function_name == "roulette":
				self.select_function = selection.select_roulette,
				rate = self.try_load("rate", settings["selection"], 0.5)
				self.select_params = [rate]
			else:
				raise Exception("Selection function %s not available!" % (self.select_function_name))
			# mutation
			self.swap_rate = self.try_load("swap_rate", settings["mutation"], 0.25)
			self.row_swap_rate = self.try_load("row_swap_rate", settings["mutation"], 0.05)
			self.col_swap_rate = self.try_load("col_swap_rate", settings["mutation"], 0.02)
			self.row_shift_rate = self.try_load("row_shift_rate", settings["mutation"], 0.05)
			self.col_shift_rate = self.try_load("col_shift_rate", settings["mutation"], 0.02)
			self.shuffle_rate = self.try_load("shuffle_rate", settings["mutation"], 0.005)
			self.min_shuffle = self.try_load("min_shuffle", settings["mutation"], 5)
			self.print_settings()
			print("Verify settings!")
			input()

	'''
	Return settings as a string
	'''
	def settings_str(self):
		return """General:\nSeed: %s\nNr populations: %d\nPopulation size: %d\nNr restarts: %d\nAlphabet: %s\n
		Output:\nFile: %s\nLogN: %d\nScoring:\nFunctionname: %s\nParameters: %s\nSelection:\nFunctionname: %s\n
		Parameters: %s\nMutation:\nSwap rate: %f\nRow swap rate: %f\nCol swap rate: %f\nRow shift rate: %f\n
		Col shift rate: %f\nShuffle rate: %f\nMin shuffle: %d""" % (self.seed, self.nr_iterations, 
			self.population_size, self.nr_restarts, self.alphabet, self.output_file, self.log_n, self.score_function_name,
			self.score_params, self.select_function_name, self.select_params, self.swap_rate, self.row_swap_rate,
			self.col_swap_rate, self.row_shift_rate, self.col_shift_rate, self.shuffle_rate, self.min_shuffle)	
	'''
	Runs the genetic algorithm. Each restart can be done parralel.
	Max 16 processes.
	'''
	def run(self):
		results = [self.gago() for _ in self.nr_restarts]
		self.write_out_put(results)

	'''
	Run the algorithm
	'''
	def goga(self):

'''
Get statistics from scores.
Length should be equal to len(sorted_scores).
sorted_scores should be sorted from high to low
Returns [mean, standard deviation, max, min, 25percentile, median, 75percentile]
'''
def get_statistics(sorted_scores, length):
	mean = np.mean(sorted_scores)
	std = np.std(sorted_scores)
	_max = sorted_scores[0]
	_min = sorted_scores[-1]
	_25p = sorted_scores[]
	median = sorted_scores[]
	_75p = sorted_scores[]
	return [mean, std, _max, _min, _25p, median, _75p]

def start(text, settings):
	with open(settings["logging"]["file"], "w") as f:
		if "seed" in settings:
			seed = settings["seed"]
		else:
			seed = np.random.randint(1000000)
		prng = np.random.RandomState(seed)
		f.write("#text: %s\n#population_size: %d\n#nr_iterations: %d\n#seed: %d" % (text, settings["population_size"], settings["nr_iterations"], seed))
		population = generate(settings["population_size"], prng, settings["alphabet"])
		max_key = ""
		max_score = 0
		for iteration in range(nr_iterations):
			[scores, _sum]  = score(text, population, settings["scoring"])
			sorted_indices = np.argsort(scores)[::-1] 
			sorted_scores = scores[sorted_indices]
			if iteration % settings["logging"]["n"] == 0:
				Write to file
			max_index = sorted_indices[0]
			if scores[max_index] > max_score:
				max_score = scores[max_index]
				max_key = population[max_index]
			norm_scores = [score / _sum for score in scores]
			selection_indices = select(norm_scores, prng)
			selection_indices = selection_function(norm_scores, prng)
			selection = population[selection_indices]
			new_population = cross_over(selection, prng, population_size)
			new_population = mutate(new_population, prng)
			population = new_population


def start(text, population_size=800, nr_iterations=2500, output_file="out", alphabet="abcdefghiklmnopqrstuvwxyz", scoring_function=libfitness.simpleScore, n=3, selection_function=selection.select_elitism):
	with open(output_file, "w") as f:
		seed = np.random.randint(1000000)
		prng = np.random.RandomState(seed)
		f.write("text: %s\npopulation_size: %d\nnr_iterations: %d\nseed: %d" % (text, population_size, nr_iterations, seed))
		population = generate(population_size, prng, alphabet)
		max_key = ""
		max_score = 0
		for iteration in range(nr_iterations):
			scores = [scoring_function(libplayfair.decipher(str.encode(p), str.encode(text), len(text)), n) for p in population]
			_sum = sum(scores)
			max_index = np.argmax(scores)
			if scores[max_index] > max_score:
				max_score = scores[max_index]
				max_key = population[max_index]
			norm_scores = [score / _sum for score in scores]
			print("Gen %d: Average score: %f" % (iteration, np.mean(scores)))
			selection_indices = selection_function(norm_scores, prng)
			selection = population[selection_indices]
			new_population = cross_over(selection, prng, population_size)
			new_population = mutate(new_population, prng)
			population = new_population
		print("Average score: %f" % (np.mean(scores)))
		print("max_score: %f" % (max_score))
		print("max_key: %s" % (max_key))
		print("plaintext:\n%s" % libplayfair.decipher(str.encode(max_key), str.encode(text), len(text)).decode())

def score():

def select():

def mutate(population, prng, swap_rate=0.25, swap_row_rate=0.05, swap_col_rate=0.02, shuffle_rate = 0.005):
	new_population = []
	for p in population:
		if prng.random() < swap_rate:
			new_population.append(mutations.swap(p, prng.randint(0, 25), prng.randint(0, 25)))
		elif prng.random() < swap_row_rate:
			i = prng.randint(0, 5)
			j = (i + prng.randint(1, 5)) % 5
			new_population.append(mutations.swap_row(p, i, j))
		elif prng.random() < swap_col_rate:
			i = prng.randint(0, 5)
			j = (i + prng.randint(1, 5)) % 5
			new_population.append(mutations.swap_col(p, i, j))
		elif prng.random() < shuffle_rate:
			new_population.append(mutations.shuffle(p, prng, prng.randint(1, 26)))
		else:
			new_population.append(p)
	return np.array(new_population)

def swap2(index, str1, str2):
	return [str1[:index] + str2[index] + str1[(index + 1):], str2[:index] + str1[index] + str2[(index + 1):]]

def find_dup_index(str1, index):
	for i in range(len(str1)):
		for j in range(i + 1, len(str1)):
			if str1[i] == str1[j]:
				if i == index:
					return j
				else:
					return i

def cross_over(selection, prng, population_size):
	new_population = []
	for i in range(int(population_size / 2)):
		parents = prng.choice(selection, 2, False)
		index = prng.randint(len(parents[0]))
		offspring = swap2(index, parents[0], parents[1])
		while len(set(offspring[0])) != len(offspring[0]):
			index = find_dup_index(offspring[0], index)
			offspring = swap2(index, offspring[0], offspring[1])
		new_population += offspring
	return np.array(new_population)
'''
generates a 
'''
def generate(population_size, prng, alphabet):
	return np.array(["".join(prng.permutation(list(alphabet))) for i in range(population_size)])

libplayfair.decipher.restype = c_char_p 
libplayfair.decipher.argtypes = [c_char_p, c_char_p, c_int]
libfitness.simpleScore.restype = c_double 
libfitness.simpleScore.argtypes = [c_char_p, c_int]
libfitness.GTest.restype = c_double 
libfitness.GTest.argtypes = [c_char_p, c_int]
libfitness.chiSquared.restype = c_double 
libfitness.chiSquared.argtypes = [c_char_p, c_int]


C = "umcudpwntwkcdyeazuphsptiwdlaheftdypsurmkynarnkslphfrledpwgrdruwebqapoweulsalftrslsdpwukcsedpaualftkdaepaftmwqwbttrskulrslsrcumcudpawygaplfuespbltrlaapuldlaprslsumcudpwneqluzhdwsurgdrkfdkspmupuotutdrmtgqapumrdapluhaalfttrlsdpauftumcuqwbfphmymuesalftlwtspaftkcdyeavgclrfebkqresmhbaplwheftqwtoygrcfdtrshwmahkpabkbctmswqpuftkdaephsedpsphoygkpkodgulclrfeioteuwmledpwultfbwtapsmleulrclbksuvdpauftqweurcbqhbezaptrfrdprohoeveuruyntoygowebmwlskpphiqsuwgxnrarfpgendpuwedkphufttnmtamotrtcopsbphkrfkwwgtsahmlwqslpdxrmfrkaptryneutwfufxdpkbeaqiurrfkqkpbnslpdxrmfrkaptrynskhzumkplttoabwlusseurgdwmynapusphygapflpuedmsluyntoygfshoxrdtpkbmurlshasmpuftapflpuedzdygwqkgusftdhlrgrqwkcxldxabkbbcufdpgdwmynapusbfumstdxphtbwawtnbpkbmhopuglesedotdpouufotknzhhldkapsrnwrforoeauftumcuqwctdpnddhusftdpcukbdpfbedfbdpruynsktbtoasfthwwqebrdaplfrkkrkuwoeuhdelqusuiercpryualftofdlpuwmulwddlygapsrrduoruxlocmtwnmuyntoygdpauftkcdyeaquzhoepwxrpuwdququsukrghclrfpnumapwtfsumbqruuvwaaksuwgvdaprfpdspdklsftkpgdlswmotfrlcetspdkfshdpkpubfumstdxumcudpaudwiucrfxkpbnsllwbkusqnpualftoroewubmwespygtleapwsklugyhakwmuyntoyglsrfdwkpqwfbmscevurobpeveldpantokplutilfpwevuvkpflpudwtoyglwtsftdmumcudpagrolxrfaprfsmltktdpawygkrdyahkpdllsrfdwkpkpapumrdapcrfrzrnieuapueopurqweakbahygmtmypkmutwygkpapsrulehrdrerpkturwdeprvrddpaufttbdritbpfrbpevelaplfhzpsotqwocygdkabkbfzphlsfttodfulepusdrkaskahpdfrwpigalpaftdypsurmkynarprygapreutdrmtdpdykwmyigumcudpwukanttospdkrcclrfnkevskdkkcniwmlulwheftkanttospdkrcaputpksuonkpngrktodfuevgdkflpudwsuawdrdyoudkarpuftlwtsftwtahygkcydwfhakwiukpaprxnwtoyglsftkdaebaulezapumrdaptrlsdpgurdilbpfrabkbftohgalxueakurwtprkwwmygtleapweoufkwiugdwmynapusbfumstdxaplmkpngrkrcumcudpaobpfbrhsuwmkgetruaootulflwturfskphdluzhdwsulwxlfrnbiuahsudkprqdftpuftohslrcdykwpitskplarmmrhlapusrfiedhfrurkpapusfrhavdgepkdkaptmfrqkdluqtrfefrlteskpbnpdkasksphoetpkdkbqapaplmkpngrkrclbaltoyglafotrsuaplmkpngrkrcfdtrshwmahkpkpfdtrshwmahkpowltpksuaopspaftmkynarkrbmfrtoygapdrdnphkdaprfohlagepkdklafskcxraputpksuonkpngrkrcfdtrshwmahkpdpwnfrtoygkpapsmwmtbmfreulahsuluflrurgdrpeftdypsurmkynarketrwnynlaapuehasuwfsmynfrpdxrauftdypsurmkynarkrghfrhafwpswppdygkdaeftdmmwuedpry"
#attack_simulated_annael(C, n=3)
start(C, selection_function=selection.select_elitism, n=3)

def main(settings):
	start(settings)