from es_connection import check_connection, create_index


class UserProfile:
    def __init__(self, es_connection_object, index_name="user_profiles"):
        self.es = es_connection_object
        self.index_name = index_name

        check_connection()

        mapping = {
            "mappings": {
                "properties": {
                    "username": {"type": "text"},
                    "password": {"type": "text"},
                    "books": {"type": "keyword"},
                    "tags": {"type": "object"},
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
            "tags": {},
        }
        response = self.es.index(index=self.index_name, id=username, document=user_data)
        return response

    def add_book(self, username, book_name):
        """Add a book to the user's read list and optionally update tags."""
        self.es.update(
            index=self.index_name,
            id=username,
            body={
                "script": {
                    "source": """
                    if (!ctx._source.books.contains(params.book)) {
                        ctx._source.books.add(params.book);
                    }
                    """,
                    "params": {"book": book_name},
                }
            },
        )

    def add_tag_with_weight(self, username, tag, weight):
        """Add or update a tag and its weight for the user."""
        self.es.update(
            index=self.index_name,
            id=username,
            body={
                "script": {
                    "source": """
                    if (ctx._source.tags.containsKey(params.tag)) {
                        ctx._source.tags[params.tag] += params.weight;
                    } else {
                        ctx._source.tags[params.tag] = params.weight;
                    }
                    """,
                    "params": {"tag": tag, "weight": weight},
                }
            },
        )

    def update_tags_from_book(self, username, book_name, book_tags):
        """Update tags when a new book is added"""
        for tag in book_tags:
            self.add_tag_with_weight(
                username, tag, weight=1
            )  # Incremental weight update

    def get_user_profile(self, username):
        """Retrieve a user profile by username."""
        response = self.es.get(index=self.index_name, id=username)
        return response["_source"] if response["found"] else None

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

    def get_tags_and_weights(self, username):
        """Retrieve all tags and their corresponding weights for a specific user"""
        response = self.es.get(index=self.index_name, id=username)
        if response["found"]:
            return response["_source"].get("tags", {})
        return {}

    def remove_book(self, username, book_name):
        """Remove a book from the user's read list if it exists."""
        self.es.update(
            index=self.index_name,
            id=username,
            body={
                "script": {
                    "source": """
                    if (ctx._source.books.contains(params.book)) {
                        ctx._source.books.remove(ctx._source.books.indexOf(params.book));
                    }
                    """,
                    "params": {"book": book_name},
                }
            },
        )

    def get_normalized_tags(self, username):
        """Retrieve tags and their normalized weights for a specific user"""
        response = self.es.get(index=self.index_name, id=username)
        if not response["found"]:
            return {}  # Return an empty dictionary if the user is not found

        tags = response["_source"].get("tags", {})

        # Calculate the total weight of all tags
        total_weight = sum(tags.values())

        # Normalize the weights
        if total_weight > 0:
            normalized_tags = {
                tag: round(weight / total_weight, 2) for tag, weight in tags.items()
            }
        else:
            normalized_tags = {tag: 0 for tag in tags}

        return normalized_tags


# # Example usage
# user_manager = UserProfile()

# # Assuming 'john_doe' has tags with weights
# normalized_tags = user_manager.get_normalized_tags("john_doe")
# print("Normalized tags and weights for John Doe:", normalized_tags)


# # Initialize the UserProfile manager
# user_manager = UserProfile()

# # Create a new user profile
# # user_manager.create_user_profile('john_doe', 'secure_password123')

# # # Add a book to the user's profile
# user_manager.add_book("john_doe", "The Hunger Games")

# # # Add/update a tag with weight
# # user_manager.add_tag_with_weight('john_doe', 'dystopian', 5)

# # Retrieve user profile data
# user_profile = user_manager.get_user_profile("john_doe")
# print(user_profile)

# # Delete user profile
# # user_manager.delete_user_profile("john_doe")

# usernames = user_manager.list_all_usernames()
# print("Usernames:")
# print(usernames)

# books = user_manager.get_books_read_by_user("john_doe")
# print("books: ", books)

# tags = user_manager.get_tags_and_weights("john_doe")
# print("tags: ", tags)

# # user_manager.update_tags_from_book("john_doe", "The Hunger Games", ["thriller", "adventure fiction"])

# # user_manager.remove_book("john_doe", "The Hunger Games")

# normalized_tags = user_manager.get_normalized_tags("john_doe")
# print("Normalized tags and weights for John Doe:", normalized_tags)
