USER_TABLE = "user_profiles"
DESCRIPTION_TABLE = "description_tf_idf"
GENRE_TABLE = "genre_tf_idf"


class UserProfile:
    def __init__(self, postgres_connection_object, es_connection_object):
        self.pg = postgres_connection_object
        self.es = es_connection_object

    def create_user_profile(self, username, password):
        """Create a user profile with initial empty book_ids and tags."""
        user_data = {
            "username": username,
            "password": password,  # Ideally, this should be hashed
            "book_ids": [],
        }
        return self.pg.table(USER_TABLE).insert(user_data).execute()

    def get_user_profile(self, username):
        """Retrieve a user profile by username."""
        return self.pg.table(USER_TABLE).select("*").eq("username", username).execute()

    def delete_user_profile(self, username):
        """Delete a user profile from the index"""
        return self.pg.table(USER_TABLE).delete().eq("username", username).execute()

    def get_books_read_by_user(self, username):
        """Retrieve all books read by a specific user"""
        book_ids = self.get_user_profile(username).data[0].get("book_ids", [])
        # TODO: Get the book data from the books ES index

        return book_ids

    def remove_book(self, username, book_id):
        """Remove a book from the user's read list if it exists."""
        user_data = self.get_user_profile(username)
        book_ids = user_data.data[0].get("book_ids", [])
        if book_id in book_ids:
            book_ids.remove(book_id)
            self.pg.table(USER_TABLE).update({"book_ids": book_ids}).eq(
                "username", username
            ).execute()

    def add_book(self, username, book_id):
        """Add a book to the user's read list and optionally update tags."""
        # self.delete_user_profile(username)

        # Get the user's current book_ids
        user_data = self.get_user_profile(username)
        book_ids = user_data.data[0].get("book_ids", [])
        if book_id not in book_ids:
            book_ids.append(book_id)
            # Update the user's book_ids
            self.pg.table(USER_TABLE).update({"book_ids": book_ids}).eq(
                "username", username
            ).execute()

        self.add_genre(username, book_id)
        self.add_abstract(username, book_id)

    def get_field_tf_idf_score(self, field, book_id, max_terms=500):
        # Make request to GET /my-index-000001/_termvectors/1?fields=message
        term_vector_response = self.es.termvectors(
            index="books",
            id=book_id,
            body={
                "fields": [field],
                "offsets": False,
                "term_statistics": True,
                "field_statistics": True,
                "positions": False,
                # TODO: Check params - Do we ever expect more than 500?
                # Do we ever want to disregard low tf-idf terms?
                "filter": {"max_num_terms": max_terms},
            },
        )
        if not term_vector_response["found"]:
            print("Book not found")
            return None
        term_vector_list = term_vector_response["term_vectors"][field]["terms"]
        return term_vector_list

    def add_tf_idf_entry(self, username, field, table_name, book_id):
        term_vector_list = self.get_field_tf_idf_score(field, book_id)

        # Get the existing weight, with username and term being the PK
        all_existing_weights = (
            self.pg.table(table_name)
            .select("*")
            .eq("user_username", username)
            .execute()
        ).data

        # Convert the list of dictionaries to a dictionary
        existing_weights_dict = {
            item["term"]: item["weight"] for item in all_existing_weights
        }

        updates = []
        inserts = []

        for term, term_data in term_vector_list.items():
            weight = term_data["score"]

            # If the term already exists, update the weight
            if term in existing_weights_dict:
                new_weight = existing_weights_dict[term] + weight
                updates.append(
                    {"user_username": username, "term": term, "weight": new_weight}
                )
            # Otherwise, insert a new row
            else:
                inserts.append(
                    {"user_username": username, "term": term, "weight": weight}
                )

        for update in updates:
            self.pg.table(table_name).update(update).eq("user_username", username).eq(
                "term", update["term"]
            ).execute()

        for insert in inserts:
            self.pg.table(table_name).insert(insert).execute()

    def add_abstract(self, username, book_id):
        self.add_tf_idf_entry(username, "description", DESCRIPTION_TABLE, book_id)

    def add_genre(self, username, book_id):
        self.add_tf_idf_entry(username, "genres", GENRE_TABLE, book_id)
