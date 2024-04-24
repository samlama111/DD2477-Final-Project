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
	MAIN_INDEX_NAME = "books" # The name of the ES index where book data is stored
	USER_INDEX_NAME = "users" # The name of the ES index where user data is stored
	ALPHA = 1.0
	BETA = 0.75
	GENRE_BOOST = 5
	ABSTRACT_BOOST = 1
	SCORE_FUNCTION = "sigmoid(doc['n_reviews'].value, 2, 1) * doc['rating'].value"
	MAX_HITS = 100
	RELEVANCE_THRESHOLD = 1e-4

	def __init__(self, client: Elasticsearch) -> None:
		self.client = client

	def query(self, query: str, user_id: str) -> tuple[list[dict], list[float]]:
		"""
		Generates a list of book recommendations from the given query with recommendations tailored to users previously read books

		:param query: Query in string form from user
		:param user_id: Unique user ID used as id for 'user' index in ES database

		:return: Results in an ordered list along with their respective scores in a second
		"""
		# Construct query
		profile = self.get_user(user_id)
		q_genre = self._construct_query_string(query, profile["gen_weight"], len(profile["books"]))
		q_abstract = self._construct_query_string(query, profile["abs_weight"], len(profile["books"]))
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
							]
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
		resp = self.client.search(index=self.MAIN_INDEX_NAME, body=query_body)
		
		# Filter results
		results = []
		scores = []
		i = 0
		hits = resp["hits"]["hits"]
		while (len(results) < self.MAX_HITS) and (i < len(hits)):
			if hits[i]["_score"] < self.RELEVANCE_THRESHOLD:
				break
			if not hits[i]["_source"]["book_id"] in profile["books"]:
				results.append(hits[i]["_source"])
				scores.append(hits[i]["_score"])
			i += 1

		return results, scores
		

	def _construct_query_string(self, q0, br, abs_Br):
		query_list = [f'({t})^{w * self.BETA / abs_Br}' for t, w in br.items()]
		query_list.append(f'({q0})^{self.ALPHA}')
		return " ".join(query_list)


	def get_user(self, user_id: str) -> dict:
		"""
		Retrieves user data from ES.
		Raises elasticsearch.NotFoundError if user_id does not exist in index.
		Expected format of user data:
		{
			"name": str
			"books": [str]
			"gen_weight": dict(str, float)
			"abs_weight": dict(str, float)
		}

		:param user_id: Unique user ID used as id for 'user' index in ES database

		:return: User data
		"""
		resp = self.client.get(index=self.USER_INDEX_NAME, id=user_id)
		return resp["_source"]
