from elasticsearch import Elasticsearch

class Book:
    def __init__(self, index_name='books', host='localhost', port=9200):
        self.index_name = index_name
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}], basic_auth=('elastic', 'l0F4vPc0pD=0kYYD-oq5'), verify_certs=False)


        # Create index if it doesn't exist
        if not self.es.indices.exists(index=self.index_name):
            self.create_index()

    def create_index(self):
        mapping = {
            'mappings': {
                'properties': {
                    'title': {'type': 'text'},
                    'description': {'type': 'text'},
                    'tags': {'type': 'keyword'}
                }
            }
        }
        self.es.indices.create(index=self.index_name, body=mapping)

    def add_book(self, title, description, tags=[], book_id=None):
        if not book_id:
            book_id = str(uuid4())  # Generate a UUID if book_id is not provided
        doc = {
            'title': title,
            'description': description,
            'tags': tags
        }
        self.es.index(index=self.index_name, id=book_id, body=doc)

    def search_books(self, query):
        search_body = {
            'query': {
                'match': {
                    'title': query
                }
            }
        }
        result = self.es.search(index=self.index_name, body=search_body)
        return result['hits']['hits']

    def get_book_details(self, book_id):
        result = self.es.get(index=self.index_name, id=book_id)
        return result['_source']


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
