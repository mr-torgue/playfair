'''
A set with common mutations on strings.
No checking is done in these functions.
'''

'''
Swaps s[i] with s[j]
'''
def swap(s, i, j):
	lst = list(s)
	lst[i], lst[j] = lst[j], lst[i]
	return ''.join(lst)

'''
Swaps row i with row j
rsize specifies how long a row is
'''
def swap_row(s, i, j, rsize=5):
	lst = list(s)
	lst[i*rsize:(i+1)*rsize], lst[j*rsize:(j+1)*rsize] = lst[j*rsize:(j+1)*rsize], lst[i*rsize:(i+1)*rsize]
	return ''.join(lst)

'''
Swaps col i with col j
'''
def swap_col(s, i, j, rsize=5):
	lst = list(s)
	lst[i:len(s):rsize], lst[j:len(s):rsize] = lst[j:len(s):rsize], lst[i:len(s):rsize]
	return ''.join(lst)

'''
Shifts i to the right
'''
def shift(s, i):
	return s[-i:] + s[:-i]

'''
Reverses s
'''
def reverse(s):
	return s[::-1]

'''
Reverses row i
'''
def reverse_row(s, i, rsize=5):
	return s[:i*rsize] + s[i*rsize:(i+1)*rsize][::-1] + s[(i+1)*rsize:]

'''
Reverses col i
'''
def reverse_col(s, i, rsize=5):
	col = s[i:len(s):rsize]
	lst = list(s)
	lst[i:len(s):rsize] = col[::-1]
	return ''.join(lst)

'''
Shifts row i n to the right
'''
def shift_row(s, i, n, rsize=5):
	row = s[i*rsize:(i+1)*rsize]
	return s[:i*rsize] + row[-n:] + row[:-n] + s[(i+1)*rsize:]

'''
Shifts col i n to the right
'''
def shift_col(s, i, n, rsize=5):
	col = s[i:len(s):rsize]
	lst = list(s)
	lst[i:len(s):rsize] = col[-n:] + col[:-n]
	return ''.join(lst)