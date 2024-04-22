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
	def __init__(self, client: Elasticsearch) -> None:
		self.client = client

	def query(self, query: str, user_id: str) -> list[dict]:
		"""
		Generates a list of book recommendations from the given query with recommendations tailored to users previously read books

		:param query: Query in string form from user
		:param user_id: Unique user ID used as id for 'user' index in ES database

		:return: Results in an ordered list
		"""
		pass

	def get_user(user_id: str) -> dict:
		"""
		Retrieves user data from ES. 
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
		pass
