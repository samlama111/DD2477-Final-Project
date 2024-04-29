from es_connection import create_index


class Book:
    def __init__(self, es_connection_object, index_name="books"):
        self.index_name = index_name
        self.es = es_connection_object

        # delete_index(self.index_name)
        """"
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
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "author": {"type": "text"},
                    "description": {"type": "text"},
                    "genres": {"type": "keyword"},  # Is this correct?
                    "rating": {"type": "float"},
                    "n_ratings": {"type": "integer"},
                    "n_reviews": {"type": "integer"},
                    "book_id": {"type": "keyword"},
                    "url": {"type": "text"},
                    "img_url": {"type": "text"},
                }
            }
        }
        # Create index if it doesn't exist
        create_index(self.index_name, mapping)

    def add_book(self, id, new_book):
        doc = {
            "title": new_book.title,
            "author": new_book.author,
            "description": new_book.description,
            "genres": new_book.genres,
            "rating": new_book.rating,
            "n_ratings": new_book.n_ratings,
            "n_reviews": new_book.n_reviews,
            "book_id": id,
            "url": new_book.url,
            "img_url": new_book.image_url,
        }
        # TODO: Check if book already exists
        self.es.index(index=self.index_name, id=id, body=doc)

    def search_books(self, query, user_profile):
        search_body = {"query": {"match": {"title": query}}}
        result = self.es.search(index=self.index_name, body=search_body)
        return result["hits"]["hits"]

    def get_book_details(self, book_id):
        result = self.es.get(index=self.index_name, id=book_id)
        return result["_source"]


class ScrapedBook:
    def __init__(
        self,
        id,
        name,
        author,
        description,
        rating,
        num_ratings,
        num_reviews,
        genres,
        url,
        image_url,
    ):
        self.book_id = id
        self.title = name
        self.author = author
        self.description = description
        self.rating = rating
        self.n_ratings = num_ratings
        self.n_reviews = num_reviews
        self.genres = genres
        self.url = url
        self.image_url = image_url
