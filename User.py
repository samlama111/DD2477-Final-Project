from es_connection import create_index
from elasticsearch.helpers import bulk
import math


class UserProfile:
    def __init__(self, es_connection_object, index_name="user_profiles"):
        self.es = es_connection_object
        self.index_name = index_name

        mapping = {
            "mappings": {
                "properties": {
                    "username": {"type": "text"},
                    "password": {"type": "text"},
                    "books": {"type": "keyword"},
                    "abs_weights": {"type": "object"},
                    "gen_weights": {"type": "object"},
                }
            }
        }
        create_index(index_name, mapping)

    def create_user_profile(self, username, password):
        """Create a user profile with initial empty books and tags."""
        user_data = {
            "username": username,
            "password": password,  # Ideally, this should be hashed
            "books": [],
            "abs_weights": {},
            "gen_weights": {},
        }
        response = self.es.index(index=self.index_name, id=username, document=user_data)
        return response

    def add_book(self, username, book_id):
        """Add a book to the user's read list and optionally update tags."""
        #self.delete_user_profile(username)
        self.es.update(
            index=self.index_name,
            id=username,
            body={
                "script": {
                    "source": """
                    if (!ctx._source.books.contains(params.books)) {
                        ctx._source.books.add(params.books);
                    }
                    """,
                    "params": {"books": book_id},
                }
            },
        )
        book = self.es.search(index="books", query={"match": {"book_id": book_id}})['hits']['hits'][0]
        self.add_genre(username, book)
        self.add_abstract(username, book)
        
    def add_abstract(self, username, book):
        abstract = book["_source"]['description']
        abstract = abstract.strip().split()
        self.bulk_actions = []
        
        for abs in abstract: 
    
            # TF
            tf_dt = len([i for i in abstract if i==abs])
            
            # IDF
            N = 1000
            df_t = len(self.es.search(index="books", body={"query": {"match": {"description": abs}}, "size": 1000})['hits']['hits'])
            idf_t = math.log(N/(df_t + 1))
            
            len_d = len(abstract)
            
            weight = (tf_dt * idf_t) / len_d
            
            print(abs)
            
            update_action = {
                "_index": self.index_name,
                "_id": username,
                "_op_type": "update",
                "script": {
                    "source": """
                    if (ctx._source.abs_weights.containsKey(params.abs)) {
                        ctx._source.abs_weights[params.abs] += params.weight;
                    } else {
                        ctx._source.abs_weights[params.abs] = params.weight;
                    }
                    """,
                    "params": {"abs": abs, "weight": weight}
                }
            }
            self.bulk_actions.append(update_action)
            
        # Bulk insert
        bulk(self.es, self.bulk_actions)
        
    def add_genre(self, username, book):
        genres = book["_source"]['genres']
        self.bulk_actions = []
        
        for genre in genres: 
            
            # TF
            tf_dt = len([i for i in genres if i==genre])
            
            # IDF
            N = 1000
            df_t = len(self.es.search(index="books", body={"query": {"match": {"genres": genre}}, "size": 1000})['hits']['hits'])
            idf_t = math.log(N/(df_t + 1))
            
            len_d = len(genres)
            
            weight = (tf_dt * idf_t) / len_d
            
            update_action = {
                "_index": self.index_name,
                "_id": username,
                "_op_type": "update",
                "script": {
                    "source": """
                    if (ctx._source.gen_weights.containsKey(params.gen)) {
                        ctx._source.gen_weights[params.gen] += params.weight;
                    } else {
                        ctx._source.gen_weights[params.gen] = params.weight;
                    }
                    """,
                    "params": {"gen": genre, "weight": weight}
                }
            }
            self.bulk_actions.append(update_action)
            
        # Bulk insert
        bulk(self.es, self.bulk_actions)

    def get_user_profile(self, username):
        """Retrieve a user profile by username."""
        return self.es.search(
            index=self.index_name, body={"query": {"match": {"username": username}}}
        )

    def delete_user_profile(self, username):
        """Delete a user profile from the index"""
        response = self.es.delete(index=self.index_name, id=username)
        return response

    def list_all_usernames(self):
        """Retrieve all user profiles and print usernames"""
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {"match_all": {}},
                "size": 10,  # Adjust size based on your expected number of users
            },
        )
        usernames = [hit["_source"]["username"] for hit in response["hits"]["hits"]]
        return usernames

    def get_books_read_by_user(self, username):
        """Retrieve all books read by a specific user"""
        response = self.es.get(index=self.index_name, id=username)
        if response["found"]:
            return response["_source"].get("books", [])
        return []

    def get_abs_weights(self, username):
        """Retrieve all tags and their corresponding weights for a specific user"""
        response = self.es.get(index="user_profiles", id=username)
        if response["found"]:
            return response["_source"].get("abs_weights", {})
        return {}

    def get_gen_weights(self, username):
        """Retrieve all tags and their corresponding weights for a specific user"""
        response = self.es.get(index="user_profiles", id=username)
        if response["found"]:
            return response["_source"].get("gen_weights", {})
        return {}

    def remove_book(self, username, book_id):
        """Remove a book from the user's read list if it exists."""
        self.es.update(
            index=self.index_name,
            id=username,
            body={
                "script": {
                    "source": """
                    if (ctx._source.books.contains(params.books)) {
                        ctx._source.books.remove(ctx._source.books.indexOf(params.books));
                    }
                    """,
                    "params": {"books": book_id},
                }
            },
        )