from elasticsearch import Elasticsearch

class Searcher:
	"""
	Main class for handling recommendation queries for new books.
	"""
	MAIN_INDEX_NAME = "books" # The name of the ES index where book data is stored
	USER_INDEX_NAME = "users" # The name of the ES index where user data is stored
	def __init__(self, client: Elasticsearch) -> None:
		self.client = client
	
	def query_category(self, query_terms: dict[str, float], category: str) -> list[dict]:
		"""
		Constructs and runs a query with the given weighted terms for the given category

		:param query_terms: Dictionary with keys being the query terms and values being the weight attributed to them
		:param category: Category which the query should match

		:return: Ranked results in a list
		"""
		pass

	def query_full(self, query_terms: dict[str, float]) -> list[dict]:
		"""
		Constructs and runs a query with the given weighted terms over all categories

		:param query_terms: Dictionary with keys being the query terms and values being the weight attributed to them

		:return: Ranked results in a list
		"""
		pass

	def query(self, query: str, user_id: str) -> list[dict]:
		"""
		Generates a list of book recommendations from the given query with recommendations tailored to users previously read books

		:param query: Query in string form from user
		:param user_id: Unique user ID used as id for 'user' index in ES database

		:return: Ranked results in a list
		"""
		pass

	def get_user(user_id: str) -> dict:
		"""
		Retrieves user data from ES. 
		TODO: Unsure if output will be a list of book_ids or a dict/class containing more relevant user data

		:param user_id: Unique user ID used as id for 'user' index in ES database

		:return: User data
		"""
		pass
