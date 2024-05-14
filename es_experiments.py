from elasticsearch import Elasticsearch

def get_client(password = 'lrFrrca77CLpFPZlxZwh'):
	return Elasticsearch([{"host":"localhost", "port":9200, "scheme": "https"}], 
						 basic_auth=('elastic', password), 
						 verify_certs=False,
						 ssl_show_warn=False)

def set_up_experiment_index(es_client: Elasticsearch):
	"""Generates index for experiments, should only be run once"""
	data1 = {
		'title': 'Space dragons I: The dragoning',
		'author': 'I. Ron Butterfly',
		'description': 'Eric was in space prison before he was rescued by the dragon Terra-axis, who was actually a CyDragon but we do not have time to get into it. Adventure awaits.',
		'genres': 'sci-fi, fantasy, dragons, dystopia',
		'rating': 0.2,
		'reviews': 20,
		'id': '1'
	}
	data2 = {
		'title': 'Space dragons II: Even spacier',
		'author': 'I. Ron Butterfly',
		'description': 'It had been five years since Eric was rescued from space prison, but now he and his dragon are out for revenge.',
		'genres': 'sci-fi, fantasy, dragons, dystopia',
		'rating': 0.1,
		'reviews': 100,
		'id': '2'
	}
	data3 = {
		'title': 'Tales of Duskendale',
		'author': 'Elias Fakinami',
		'description': 'The dragons have been gone for as long as anyone can remember, but just yesterday Delilah the dragon tamer claims she saw a dragon close to the dragon roost cavern. Gosh darn she likes dragons.',
		'genres': 'fantasy, romance',
		'rating': 4.0,
		'reviews': 20000,
		'id': '3'
	}
	data4 = {
		'title': 'Romance Academy 7: The Romancing',
		'author': 'Soos',
		'description': 'When the cherry blossoms of magic romance academy are in bloom... anything can happen. So true.',
		'genres': 'fantasy, romance, teen',
		'rating': 2.0,
		'reviews': 238,
		'id': '4'
	}

	for data in (data1, data2, data3, data4):
		resp = es_client.index(index=INDEX, document=data, id=data['id'])

def standard_search(es_client: Elasticsearch, query: str):
	"""Searches through the book description for a given query"""
	resp = es_client.search(index=INDEX,
							query={'match': {'description': {'query': query}}})
	return [result for result in resp['hits']['hits']]

def rated_search(es_client: Elasticsearch, query: str):
	query_body = {
		"query" : {
			"function_score" : {
				"query": {"match": {"description": query}},
				"script_score": {
					"script": {
						"source": "Math.log(doc['reviews'].value) * doc['rating'].value"
					}
				}
			}
		}
	}
		
	resp = es_client.search(index=INDEX, body=query_body)
	return [result for result in resp['hits']['hits']]

def _build_query(query_list, field, queries, boost):
	pass

def rated_and_weighted_search(es_client: Elasticsearch, weighted_queries: dict[str, float]):
	boolean_queries = []
	for q, w in weighted_queries.items():
		next = {
			"match": {"description": {"query": q, "boost": w}}
		}
		boolean_queries.append(next)
	
	query_body = {
		"query" : {
			"function_score" : {
				"query": {
					"bool" : {"should" : boolean_queries},
				},
				"script_score": {
					"script": {
						"source": "Math.log(doc['reviews'].value) * doc['rating'].value" # Math.log(doc['reviews'].value) * 
					}
				}
			}
		}
	}
		
	resp = es_client.search(index=INDEX, body=query_body)
	return [result for result in resp['hits']['hits']]

def rated_and_weighted_search_new(es_client: Elasticsearch, weighted_queries: dict[str, float]):
	query_terms = [f'{q}^{w}' for q, w in weighted_queries.items()]
	joint_query = " ".join(query_terms)

	query_body = {
		"query" : {
			"function_score" : {
				"query": {
					"query_string": {
						"query": joint_query,
						"default_field": "description",
					}
				},
				"script_score": {
					"script": {
						"source": "Math.log(doc['reviews'].value) * doc['rating'].value" # Math.log(doc['reviews'].value) * 
					}
				}
			}
		}
	}
		
	resp = es_client.search(index=INDEX, body=query_body)
	return [result for result in resp['hits']['hits']]

def rated_final(es_client: Elasticsearch, weighted_queries: dict[str, float], description_boost = 1, title_boost = 5):

	query_terms = [f'{q}^{w}' for q, w in weighted_queries.items()]
	joint_query = " ".join(query_terms)

	query_body = {
		"query" : {
			"function_score" : {
				"query": {
					"bool" : {"should" : [
							{"query_string": {
								"query": joint_query,
								"default_field": "description",
								"boost": description_boost
								}
							},
							{"query_string": {
								"query": joint_query,
								"default_field": "title",
								"boost": title_boost
								}
							},
						]
					},
				},
				"script_score": {
					"script": {
						"source": "sigmoid(doc['reviews'].value, 2, 1) * doc['rating'].value" # Math.log(doc['reviews'].value) * 
					}
				}
			}
		}
	}
		
	resp = es_client.search(index=INDEX, body=query_body)
	return [result for result in resp['hits']['hits']]

def show_results(results):
	for res in results:
		print(f'Title: {res["_source"]["title"]}')
		print(f'Author: {res["_source"]["author"]}')
		print(f'Rating: {res["_source"]["rating"]}')
		print(f'Reviews: {res["_source"]["reviews"]}')
		print(f'Score: {res["_score"]}')
		print()

def speed_test():
	from timeit import timeit
	import random as rn
	import matplotlib.pyplot as plt
	from tqdm import tqdm
	old_time = []
	new_time = []
	ns = []
	for i in tqdm(range(10, len(WORDS), 10)):
		data = {a : rn.uniform(0, 10) for a in WORDS[:i]}
		ns.append(i)
		old_time.append(timeit(lambda: rated_and_weighted_search(es_client, data), number=1000))
		new_time.append(timeit(lambda: rated_and_weighted_search_new(es_client, data), number=1000))
	plt.plot(ns, old_time, label="Boolean query")
	plt.plot(ns, new_time, label="String query")
	plt.xlabel('Words in query')
	plt.ylabel('Execution time [ms]')
	plt.legend()
	plt.show()

INDEX = 'experiment_index'
FIRST_TIME = False
def main():
	es_client = get_client()
	if FIRST_TIME:
		set_up_experiment_index(es_client)
	results = standard_search(es_client, 'dragon')

	results = rated_search(es_client, 'dragon')

	weighted_queries = {
		'dragon': 0.01,
		'space': 1.5,
		'romancing': 1
	}
	# results = rated_and_weighted_search(es_client, weighted_queries)
	# show_results(results)
	# print("\n---------------------------\n")
	# results = rated_and_weighted_search_new(es_client, weighted_queries)
	# show_results(results)
	results = rated_final(es_client, weighted_queries, description_boost=1, title_boost=5)
	show_results(results)
	print("\n---------------------------\n")
	results = rated_final(es_client, weighted_queries, description_boost=5, title_boost=0.1)
	print("\n---------------------------\n")
	results = rated_final(es_client, weighted_queries, description_boost=5, title_boost=0)
	show_results(results)


WORDS = [
	"abacus", "absurd", "abyss", "affix", "alchemy", "alias", "allure", "alpha", "amber", "amulet",
	"anarchy", "anomaly", "apex", "aplomb", "aptitude", "arcane", "aria", "artisan", "aspire", "augur",
	"aurora", "avid", "azure", "baffle", "balmy", "bamboo", "banjo", "baroque", "beacon", "bizarre",
	"bliss", "blossom", "blithe", "bonanza", "boon", "bounty", "bravado", "brisk", "bucolic", "buffoon",
	"burgeon", "cajole", "caliber", "calypso", "canopy", "caprice", "captivate", "cascade", "cello", "chalice",
	"chaos", "charisma", "chasm", "cherish", "chivalry", "chronicle", "citadel", "clarity", "clique", "cloying",
	"coalesce", "cobalt", "cocktail", "colossal", "comet", "commune", "compass", "concord", "conifer", "conjure",
	"conquest", "conundrum", "cordial", "cosmic", "cotton", "covert", "cozy", "crimson", "crystal", "curio",
	"cynosure", "dainty", "dandelion", "dapper", "dawn", "debut", "decadent", "decoy", "defer", "delight",
	"delta", "demure", "desire", "destiny", "devout", "dexterity", "diaphanous", "diffuse", "dilemma", "dimple",
	"discern", "discreet", "divine", "dossier", "dulcet", "ebony", "eclectic", "eclipse", "effervescent", "effigy",
	"elation", "elite", "eloquent", "elusive", "embrace", "emerald", "empathy", "empower", "enchant", "endeavor",
	"endure", "enigma", "enlighten", "epiphany", "equinox", "erudite", "ethereal", "euphoria", "evocative", "exalt",
	"exquisite", "extol", "fable", "facet", "fathom", "fauna", "fawn", "felicity", "fervent", "finesse",
	"flair", "flaxen", "flicker", "flora", "flourish", "flux", "forage", "foray", "forever", "fortitude",
	"fractal", "fragrant", "freedom", "frenzy", "frivolous", "frost", "fugitive", "gaiety", "gale", "garnet",
	"gazebo", "genesis", "gentle", "glisten", "glorious", "gossamer", "grandeur", "gravity", "grotto", "halcyon",
	"harbor", "harness", "haven", "hazelnut", "heavenly", "hedonist", "helix", "herald", "heresy", "hideaway",
	"highland", "hoopla", "horizon", "hybrid", "iceberg", "icon", "ignite", "illusion", "illuminate", "immaculate",
	"impulse", "incognito", "indigo", "infuse", "ingenious", "ingenuity", "inquisitive", "inspire", "instinct", "intrepid",
	"intrigue", "intuition", "inventive", "iris", "ivory", "jade", "jargon", "jazz", "jest", "jubilee",
	"juxtapose", "kaleidoscope", "keen", "kernel", "kindred", "kinetic", "labyrinth", "lagoon", "lantern", "lattice",
	"lava", "legacy", "legend", "leisure", "liberty", "limelight", "luminous", "luscious", "lyric", "magical",
	"magnolia", "mallet", "manifest", "marvel", "maverick", "meadow", "medley", "melody", "mesmerize", "metamorphosis",
	"mingle", "minuet", "miracle", "mirth", "mystic", "nirvana", "novel", "nurture", "oblivion", "obsidian",
	"oceanic", "opulent", "oracle", "orchid", "ornate", "outlandish", "overture", "oxygen", "pacific", "palette",
	"panacea", "paradigm", "paradox", "paragon", "pastiche", "patina", "peculiar", "penumbra", "perennial",
	"permeate", "pinnacle", "placid", "platinum", "plaudit", "plume", "poignant", "polish", "portal", "pristine",
	"profound", "prosper", "quaint", "quantum", "quartz", "quintessence", "quiver", "radiant", "rapture", "rarefied",
	"rebirth", "reverie", "rhapsody", "rift", "ripple", "rosy", "ruminate", "sapphire", "savor", "scintilla",
	"serendipity", "serene", "shimmer", "silhouette", "silken", "solace", "solar", "sonnet", "soothe", "spectral",
	"spellbound", "sphere", "splendid", "spontaneous", "stardust", "stellar", "sublime", "summit", "sumptuous", "sundown",
	"surreal", "synergy", "talisman", "tangible", "tapestry", "teeming", "tempest", "tender", "terra", "threshold",
	"thriving", "tranquil", "transcend", "traverse", "tribute", "triumph", "twilight", "umbra", "unicorn", "unison",
	"uplift", "utopia", "valor", "vanguard", "vapor", "velvet", "verdant", "versatile", "vibrant", "vigilant",
	"vintage", "virtue", "vivid", "vortex", "whimsical", "willow", "wisdom", "wonder", "xanadu", "zenith",
	"zephyr", "zeal"
]

	


if __name__ == '__main__':
	print(len(WORDS))
	main()