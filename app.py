from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    make_response,
)
from werkzeug.security import generate_password_hash, check_password_hash
from Books import *
from User import *
from Books import ScrapedBook
from es_connection import es, check_connection
from postgres_connection import supabase


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"

user_manager = UserProfile(supabase, es)

book_manager = Book(supabase, es)

check_connection()


@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return redirect(url_for("register"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Search user in Elasticsearch
        response = user_manager.get_user_profile(username)
        if response.data:  # Check if the list is not empty
            user = response.data[0]  # Get the first user
            if check_password_hash(user["password"], password):
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("addbooks"))
        return "Login Failed"
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method="pbkdf2")

        # Check if user already exists
        response = user_manager.get_user_profile(username)
        if response.data.__len__() == 0:
            # Add new user to Elasticsearch
            user_manager.create_user_profile(username, hashed_password)
            return redirect(url_for("login"))
        return "Username already exists"
    return render_template("register.html")


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    username = session["username"]
    user_profile = user_manager.get_user_profile(username)

    if query:
        # TODO: previously this returned a list of dictionaries where each books data was found thru '_source' key.
        #       the new implementation returns the book data directly, removing the '_source' go between.
        #       I'm not fully clear on how make_response handles this, cannot check until users have desired format. -Theo
        books = book_manager.search_books(query, user_profile.data[0])
        res = make_response(jsonify(books), 200)
        # for book in books:
        #     print(book['_source']["title"] + " - " + book['_source']['description'])

        return res
    return render_template("search.html")


@app.route("/addbooks", methods=["GET"])
def addbooks():
    query = request.args.get("query", "")
    if query:
        books = book_manager.search_book_titles(query)
        res = make_response(jsonify(books), 200)
        return res
    return render_template("addbooks.html")


@app.route("/handle_add_book", methods=["POST"])
def handle_add_book():
    book_id = request.json["book_id"]
    username = session["username"]
    user_manager.add_book(username, book_id)
    res = make_response(jsonify({"message": "Book added successfully!"}), 200)
    return res

@app.route("/my-profile", methods=["GET"])
def get_profile():
    return render_template("profile.html")

@app.route("/user_books", methods=["GET"])
def get_user_books():
    book_ids = user_manager.get_books_read_by_user(session['username'])
    # print("books_ids: ", book_ids)
    books = []
    for i in range(len(book_ids)):
        book_details = book_manager.get_book_details(book_ids[i])
        # print(book_details)
        books.append(book_details)
    res = make_response(jsonify(books), 200)
    # print("books: ", jsonify(books))
    # print(res.json)

    return res

@app.route("/user_name", methods=["GET"])
def get_user_name():
    username = session['username']
    # print("username: ", username)
    if username:
        return username, 200
    else:
        return "Error: Username not found", 404

@app.route("/scraper/addbook", methods=["POST"])
def add_book():
    id = request.json["id"]
    name = request.json["name"]
    author = request.json["author"]
    description = request.json["description"]
    rating = request.json["rating"]
    num_ratings = request.json["num_ratings"]
    num_reviews = request.json["num_reviews"]
    genres = request.json["genres"]
    url = request.json["url"]
    image_url = request.json["image_url"]

    new_book = ScrapedBook(
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
    )

    book_manager.add_book(id, new_book)
    return jsonify({"message": f"Book '{name}' added successfully!"})


if __name__ == "__main__":
    app.run(debug=True)
