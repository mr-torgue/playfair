import numpy as np
import copy
import sys
import playfairbigramfrequencies

'''
This python script is a user guided program which helps finding the plaintext message for a given
message which was encrypted with the playfair cipher. Algorithm is simple. It contains a bigram frequency
table(duplicates and bigrams with 'j' are taken care of). The bigram counts in the ciphertext are calculated.
Starting with the most common bigram(working down), each bigram is compared with known frequencies. The n
best scoring possible plaintext bigrams are given as options for decryption. The user selects one, the values 
are filled in and the user continues with the second bigram.
TODO:
1) Key reconstruction: it is possible to reconstruct a key from the mapping, but couldn't find a 
siple algorithm for this. proves quitte challenging.
2) Use the fact that a letter always encrypts to another letter
'''

'''
Beware soe ugly code. The function below does the frequency analysis and
contains the logic for the user interaction.
'''
def frequency_analysis(text, n):
	print("""Iterative playfair cracker based on bigram frequency analysis.
IMPORTANT:
\t 1) Make sure that the ciphertext is encrypted using the playfair cipher
\t 2) It is assumed that 'j' is replaced by 'i'
\t 3) It is assumed that 'x' is used to resolve duplicates
\t 4) Used frequencies are for the English lanuage only
SYNTAX:
\t 1) Ciphertext is in lowercase
\t 2) Plaintext is in capitals and highlighted
\t 3) Text with a blue background is the selected bigram
USAGE:
\t 1) [0-9] for selecting mapping
\t 2) b for going back
\t 3) enter text to override
PRESS A KEY TO CONTINUE
----------------------------------------------------------------------""")
	input()
	bigram_count = ngram(text, 2, False)[0]
	_len = float(len(text) / 2)
	bigram_sorted = sorted(bigram_count, key=bigram_count.get)[::-1]
	kf = playfairbigramfrequencies.getFrequencies()
	mapping = []
	plaintexts = []
	usedsymbols = {}
	index = 0
	while index != len(bigram_count):
		print("Current mapping:\n%s\n%s" % (bigram_sorted[:index], mapping))
		bigram_c = bigram_sorted[index]
		freq_bigram_c = bigram_count[bigram_c] / _len
		rev_bigram_c = bigram_c[::-1]
		freq_rev_bigram_c = 0.0
		if rev_bigram_c in bigram_count:
			freq_rev_bigram_c = bigram_count[rev_bigram_c] / _len
		# get differences between bigram frequency and known bigram frequencies, sort on key, ascending
		diffs = { x: abs(freq_bigram_c - kf[x]) + abs(freq_rev_bigram_c - kf[x[::-1]]) for x in kf }
		sorted_diffs =  [x for x in sorted(diffs, key=diffs.get) if x not in mapping and x[0] != bigram_c[0] and x[1] != bigram_c[1]]
		# ask the user for input
		print("possible values for %s:" % (bigram_c))
		for i in range(n):
			bigram_p = sorted_diffs[i]
			s = "%d: %s\t\tFitness score: %f\t\t" % (i, bigram_p, diffs[bigram_p])
			# in the same square
			if bigram_c[0] not in bigram_p and bigram_c[1] not in bigram_p:
				freq_bigram_p = 0.0
				if bigram_p in bigram_count:
					freq_bigram_p = bigram_count[bigram_p] / _len
				rev_bigram_p = bigram_p[::-1]
				freq_rev_bigram_p = 0.0
				if rev_bigram_p in bigram_count:
					freq_rev_bigram_p = bigram_count[rev_bigram_p] / _len
				s += "In the square, score: %f" % (abs(freq_bigram_p - kf[bigram_c]) + abs(freq_rev_bigram_p - kf[bigram_c[::-1]]) )
				#s += "In the square, score: %f" % (abs(freq_bigram_p - kf[bigram_c]))
			else:
				s += "In the same row or column"
			print(s)
		printtext = replace(text, bigram_c, "\033[44;33m" + bigram_c + "\033[m")
		for m in mapping:
			printtext = printtext.replace(m.upper(), "\033[47;30m" + m.upper() + "\033[m")
		print(printtext)
		print("Select replacement(default=0, b=go 1 step back)")
		user_input = input()
		if user_input == "b":
			if index == 0:
				exit(0)
			index -= 1
			text = plaintexts.pop()
			mapping.pop()
		else:
			if user_input in kf and user_input not in mapping and user_input[0] != bigram_c[0] and user_input[1] != bigram_c[1]:
				bigram_p = user_input
			else:
				selection = 0
				try:
					selection = int(user_input)
				except:
					None
				bigram_p = sorted_diffs[selection]
			plaintexts.append(copy.deepcopy(text))
			text = replace(text, bigram_c, bigram_p.upper())
			mapping.append(bigram_p)
			index += 1
			if index >= 10:
				print_key(bigram_sorted[:index], mapping)

'''
replace bigram c with p in text. 
p doesn't have to be a bigram but usually is
'''
def replace(text, c, p):
	newtext = ""
	for i in range(0, len(text), 2):
		t = text[i:i+2]
		if c == t:
			newtext += p
		else:
			newtext += t
	return newtext

'''
Counts ngrams in the text
'''
def ngram(text, n=2, overlap=True):
	counts = {}
	startindices = {}
	if overlap:
		_range = range(0, len(text) - n + 1)
	else:
		_range = range(0, len(text), n)
	for i in _range:
		subtext = text[i:i+n]
		if len(subtext) == n:
			if subtext not in counts:
				counts[subtext] = 0
				startindices[subtext] = []
			counts[subtext] += 1
			startindices[subtext].append(i)
	return [counts, startindices]

'''
sanitizes input.
'''
def sanitize(text, alphabet="abcdefghijklmnopqrstuvwxyz"):
	text = text.lower()
	return "".join([t if t in alphabet else "" for t in text])

def main():
	try:
		filename = sys.argv[1]
		try:
			n = int(sys.argv[2])
		except:
			n = 10
		with open(filename) as f:
			text = sanitize(f.read())
			frequency_analysis(text, n=n)
	except:
		print("Usage: python3 iterative_frequency_analysis.py [ciphertext filename] [n]")

if __name__== "__main__":
	main()