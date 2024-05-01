from elasticsearch import Elasticsearch

"""
Format of book documents in ES:
{
	"title": str,
	"author": str,
	"abstract": str,
	"genres": [str],
	"rating": float,
	"n_ratings": int,
	"n_reviews": int,
	"book_id": str,
	"url": str,
	"img_url": str,
}

"""

class Searcher:
	"""
	Main class for handling recommendation queries for new books.
	"""
	ALPHA = 1.0
	BETA = 0.75
	GENRE_BOOST = 5
	ABSTRACT_BOOST = 1
	SCORE_FUNCTION = "sigmoid(doc['n_reviews'].value, 2, 1) * doc['rating'].value"
	MAX_HITS = 100
	RELEVANCE_THRESHOLD = 1e-4

	def __init__(self, client: Elasticsearch, book_index) -> None:
		self.client = client
		self.book_index = book_index

	def query(self, query: str, user_profile: dict) -> tuple[list[dict], list[float]]:
		"""
		Generates a list of book recommendations from the given query with recommendations tailored to users previously read books

		Necessary fields in user_profile:
		{
			"books": [str]
			"gen_weight": dict(str, float)
			"abs_weight": dict(str, float)
		}

		:param query: Query in string form from user
		:param user_profile: User data on the form des

		:return: Results in an ordered list along with their respective scores in a second
		"""
		# Construct query
		q_genre = self._construct_query_string(query, user_profile["gen_weight"], len(user_profile["books"]))
		q_abstract = self._construct_query_string(query, user_profile["abs_weight"], len(user_profile["books"]))
		query_body = {
			"query" : {
				"function_score" : {
					"query": {
						"bool" : {"should" : [
							{"query_string": {
								"query": q_genre,
								"default_field": "genres",
								"boost": self.GENRE_BOOST
								}
							},
							{"query_string": {
								"query": q_abstract,
								"default_field": "abstract",
								"boost": self.ABSTRACT_BOOST
								}
							},
							],
							"must_not": [
								{
									"ids": {
										"values": user_profile["books"]
									}
								}
							],
						},
					},
					"script_score": {
						"script": {
							"source": self.SCORE_FUNCTION
						}}
					}
				}
			}
		
		# Query Elasticsearch
		resp = self.client.search(index=self.book_index, body=query_body)
		
		# Filter results
		results = []
		scores = []
		i = 0
		hits = resp["hits"]["hits"]
		while (len(results) < self.MAX_HITS) and (i < len(hits)):
			if hits[i]["_score"] < self.RELEVANCE_THRESHOLD:
				break
			results.append(hits[i]["_source"])
			scores.append(hits[i]["_score"])
			i += 1

		return results, scores
		

	def _construct_query_string(self, q0, br, abs_Br):
		query_list = [f'({t})^{w * self.BETA / abs_Br}' for t, w in br.items()]
		query_list.append(f'({q0})^{self.ALPHA}')
		return " ".join(query_list)
