from es_connection import create_index
from uuid import uuid4


class Book:
    def __init__(self, es_connection_object, index_name="books"):
        self.index_name = index_name
        self.es = es_connection_object

        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "tags": {"type": "keyword"},
                    "url": {"type": "text"},
                }
            }
        }
        # Create index if it doesn't exist
        create_index(self.index_name, mapping)

    def add_book(self, title, description, tags=[], url="", book_id=None):
        if not book_id:
            book_id = str(uuid4())  # Generate a UUID if book_id is not provided
        doc = {
            "title": title,
            "description": description,
            "tags": tags,
            "url": url,
        }
        self.es.index(index=self.index_name, id=book_id, body=doc)

    def search_books(self, query):
        search_body = {"query": {"match": {"title": query}}}
        result = self.es.search(index=self.index_name, body=search_body)
        return result["hits"]["hits"]

    def get_book_details(self, book_id):
        result = self.es.get(index=self.index_name, id=book_id)
        return result["_source"]


# # Initialize Book object
# book_manager = Book()

# # Add a book
# # book_manager.add_book('The Great Gatsby', 'A novel by F. Scott Fitzgerald', ['novel', 'fiction'], '123')

# # Search for books
# results = book_manager.search_books('Gatsby')
# for hit in results:
#     print("hits")
#     print(hit['_source'])

# # Get book details
# book_details = book_manager.get_book_details('123')
# print("book details", book_details)

# book_manager.add_book('The Hunger Games', 'A thriller novel', ['novel', 'thriller'], '456')
