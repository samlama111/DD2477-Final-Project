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
		sum += ratings[result] / np.log2(2 + i)
	return Z[k-1] * sum

def calc_nDCG(results, ratings, Z):
	return [nDCG(results, ratings, Z, k) for k in range(1, len(results)+1)]

def calc_Z(n):
	Z_inv = []
	for i in range(100):
		if not Z_inv:
			value = 3 / np.log2(2)
			Z_inv.append(value)
			continue
		
		value = 3 / np.log2(2 + i)
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

def best_params(username, query, k=10, n=3):
	path = f'./relevance_tests/data/{username}.json'
	
	Z = calc_Z(100)

	result_collection, ratings = get_query_data(username, query)

	betas = list(result_collection.keys())
	max_ndcgs = [0] * n
	best_betas = [None] * n
	best_boosts = [None] * n
	for beta in betas:
		g_boosts = list(result_collection[beta].keys())
		for g_boost in g_boosts:
			results = result_collection[beta][g_boost]
			ndcg = nDCG(results, ratings, Z, k)
			for i in range(n):
				if ndcg > max_ndcgs[i]:
					max_ndcgs.insert(i, ndcg)
					best_betas.insert(i, beta)
					best_boosts.insert(i, g_boost)
					max_ndcgs = max_ndcgs[:n]
					best_betas = best_betas[:n]
					best_boosts = best_boosts[:n]
					break
	
	return [str(beta) for beta in best_betas], [str(boost) for boost in best_boosts]
			


def plot_ndcg(username, query, betas=None, g_boosts=None, suffix='all', legend_shift=True, collective_beta_and_boosts = None, last_dashed=True):
	path = f'./relevance_tests/data/{username}.json'
	
	Z = calc_Z(100)

	result_collection, ratings = get_query_data(username, query)

	fig = plt.figure(figsize=(9,6))
	ax = plt.subplot(111)

	if collective_beta_and_boosts is not None:
		for i, (beta, g_boost) in enumerate(collective_beta_and_boosts):
			results = result_collection[beta][g_boost]
			ndcgs = calc_nDCG(results, ratings, Z)
			ks = list(range(1, len(ndcgs)+1))
			if last_dashed and (i == len(collective_beta_and_boosts) - 1):
				fmt = "--k"
			else:
				fmt = "-"
			ax.plot(ks, ndcgs, fmt, label=rf'$\beta = {beta:4}$ : ' + r'$w_{gen} = $' + f'{g_boost}')
	else:
		if betas is None:
			betas = list(result_collection.keys())
		for beta in betas:
			if g_boosts is None:
				g_boosts = list(result_collection[beta].keys())
			for g_boost in g_boosts:
				results = result_collection[beta][g_boost]
				ndcgs = calc_nDCG(results, ratings, Z)
				ks = list(range(1, len(ndcgs)+1))
				ax.plot(ks, ndcgs, label=rf'$\beta = {beta:4}$ : ' + r'$w_{gen} = $' + f'{g_boost}')

	# Shrink current axis by 18%
	if legend_shift:
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.82, box.height])

	# Put a legend to the right of the current axis
	if legend_shift:
		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	else:
		ax.legend()
	plt.xlabel('k')
	plt.ylabel('nDCG(k)')
	plt.xticks(ks)
	plt.savefig(f'./relevance_tests/plots/{username}-{"_".join(query.split(" "))}_{suffix}.png')
	