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


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"

user_manager = UserProfile(es)

book_manager = Book(es)

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
        res = user_manager.get_user_profile(username)
        if res["hits"]["total"]["value"] > 0:
            user = res["hits"]["hits"][0]["_source"]
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
        hashed_password = generate_password_hash(password, method='pbkdf2')

        # Check if user already exists
        res = user_manager.get_user_profile(username)
        if res["hits"]["total"]["value"] == 0:
            # Add new user to Elasticsearch
            user_manager.create_user_profile(username, hashed_password)
            return redirect(url_for("login"))
        return "Username already exists"
    return render_template("register.html")


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    username = session["username"]
    print("username in search: ", username)
    user_profile = user_manager.get_user_profile(username)
    user_profile_source = user_profile["hits"]["hits"][0]["_source"]

    if query:
        books = book_manager.search_books(query, user_profile_source)
        res = make_response(jsonify(books), 200)
        # TODOOO
        return res
    return render_template("search.html")


@app.route("/addbooks", methods=["GET"])
def addbooks():
    query = request.args.get("query", "")
    if query:
        books = book_manager.search_books(query)
        res = make_response(jsonify(books), 200)
        # for book in books:
        #     print(book['_source']["title"] + " - " + book['_source']['description'])

        return res
    return render_template("addbooks.html")


@app.route("/handle_add_book", methods=["POST"])
def handle_add_book():
    book_title = request.json['title']
    username = session["username"]
    user_manager.add_book(username, book_title)
    print("inside handle add book", book_title, username )
    res = make_response(jsonify({"message": "Book added successfully!"}), 200)
    return res


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
