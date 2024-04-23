from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from elasticsearch import Elasticsearch
from werkzeug.security import generate_password_hash, check_password_hash
from Books import *
from User import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Setup Elasticsearch connection
es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}], basic_auth=('elastic', 'l0F4vPc0pD=0kYYD-oq5'), verify_certs=False)

user_manager = UserProfile()

book_manager = Book()

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Search user in Elasticsearch
        res = es.search(index="user_profiles", body={"query": {"match": {"username": username}}})
        if res['hits']['total']['value'] > 0:
            user = res['hits']['hits'][0]['_source']
            if check_password_hash(user['password'], password):
                session['logged_in'] = True
                return redirect(url_for('addbooks'))
        return 'Login Failed'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        # Check if user already exists
        res = es.search(index="user_profiles", body={"query": {"match": {"username": username}}})
        if res['hits']['total']['value'] == 0:
            # Add new user to Elasticsearch
            es.index(index="user_profiles", body={"username": username, "password": hashed_password})
            return redirect(url_for('login'))
        return 'Username already exists'
    return render_template('register.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        books = book_manager.search_books(query)
        res = make_response(jsonify(books), 200)
        # for book in books:
        #     print(book['_source']["title"] + " - " + book['_source']['description'])

        return res
    return render_template('search.html')

@app.route('/addbooks', methods=['GET'])
def addbooks():
    query = request.args.get('query', '')
    if query:
        books = book_manager.search_books(query)
        res = make_response(jsonify(books), 200)
        # for book in books:
        #     print(book['_source']["title"] + " - " + book['_source']['description'])

        return res
    return render_template('addbooks.html')

@app.route('/handle_add_book', methods=['POST'])
def handle_add_book():
    # book_title = request.json['title']
    # add_book_to_user(book_title)
    print("inside handle add book")
    res = make_response(jsonify({"message": "Book added successfully!"}), 200)
    return res

if __name__ == '__main__':
    app.run(debug=True)
