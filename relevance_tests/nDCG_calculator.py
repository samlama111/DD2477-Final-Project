import sys
import os
sys.path.insert(1, os.getcwd()) # Assumption that app is run from DD2477-Final-Project directory

import json
import numpy as np
import matplotlib.pyplot as plt

def nDCG(results, ratings, Z, k):
	sum = 0
	for i, result in enumerate(results):
		if i == k:
			break
		if result not in ratings:
			print(f'"{result}" : ,')
			continue
		sum += (2**ratings[result] - 1) / np.log2(2 + i)
	return Z[k-1] * sum

def calc_nDCG(results, ratings, Z):
	return [nDCG(results, ratings, Z, k) for k in range(1, len(results)+1)]

def calc_Z(n):
	Z_inv = []
	for i in range(100):
		if not Z_inv:
			value = (2**3 - 1) / np.log2(2)
			Z_inv.append(value)
			continue
		
		value = (2**3 - 1) / np.log2(2 + i)
		Z_inv.append(value + Z_inv[-1])
			
	Z = [1/z for z in Z_inv]
	for i in range(len(Z) - 1):
		assert Z[i] > Z[i+1], f'Error at index {i}'

	return Z

def get_query_data(username, query):
	path = f'./relevance_tests/data/{username}.json'
	if os.path.isfile(path):
		with open(path) as json_file:
			data = json.load(json_file)
	else:
		raise FileNotFoundError('json file not found for given username and query')
	
	if query in data:
		query_data = data[query]
	else:
		raise IndexError('Given query not found in json file')

	result_collection = query_data['results']	
	ratings = query_data['ratings']
	return result_collection, ratings

def plot_ndcg(username, query, betas=None, g_boosts=None):
	path = f'./relevance_tests/data/{username}.json'
	
	Z = calc_Z(100)

	result_collection, ratings = get_query_data(username, query)

	fig = plt.figure(figsize=(9,6))
	ax = plt.subplot(111)

	if betas is None:
		betas = list(result_collection.keys())
	for beta in betas:
		if g_boosts is None:
			g_boosts = list(result_collection[beta].keys())
		for g_boost in g_boosts:
			results = result_collection[beta][g_boost]
			ndcgs = calc_nDCG(results, ratings, Z)
			ks = list(range(1, len(ndcgs)+1))
			ax.plot(ks, ndcgs, label=rf'$\beta = {beta:4}$ : boost = {g_boost}')

	# Shrink current axis by 18%
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.82, box.height])

	# Put a legend to the right of the current axis
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	plt.xlabel('k')
	plt.ylabel('nDCG(k)')
	plt.xticks(ks)
	plt.savefig(f'./relevance_tests/plots/{username}-{"_".join(query.split(" "))}.png')
