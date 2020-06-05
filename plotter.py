import matplotlib.pyplot as plt
import pickle
import numpy as np

base = "out.log_2019-08-17_17:39:34_"
for i in range(10):
	filename = base + str(i) +".pickle"
	with open(filename, "rb") as f:
		result = pickle.load(f)
		result = np.array(result)
		data = result[0]
		means = [d[0] for d in data]
		x = range(len(means))
		plt.plot(x, means)
		plt.ylabel('Mean')
		plt.xlabel('Iteration')
		plt.show()
