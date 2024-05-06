"""
This script is to be run separate from the main implementation.
The intent of this script (through a rudimentary UI) lets a tester load the preferences
of a user and give a query to grade its relevance.

The user will be shown book names, authors and abstracts and will be asked to rank their interest of the book
on a scale of 0 to 3, the ranking should be as follows
3: Fits with their query and seems relatively similar to previously read books
2: Fits the spirit of the query okay and has similarities to read books
1: Fits the query okay or is fairly similar to read books
0: Does not fit the query or previously read books at all
"""
import sys
import os
sys.path.insert(1, os.getcwd()) # Assumption that app is run from DD2477-Final-Project directory
from searcher import Searcher
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError
from dotenv import load_dotenv

from User import UserProfile
from Books import Book
from postgres_connection import supabase

import json
import nDCG_calculator
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QLineEdit, QPushButton, QMessageBox

load_dotenv()
CLOUD_ID = os.getenv("CLOUD_ID")
API_KEY = os.getenv("API_KEY")
es = Elasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)
# BOOK_INDEX = "books"
# PROFILE_INDEX = "user_profiles"

BETAS = [0.01, 0.1, 0.75]
G_BOOSTS = [5, 10, 25, 50]
MAX_HITS = 20

def generate_book_list(query, username):
	user_manager = UserProfile(supabase, es)
	book_manager = Book(supabase, es)
	book_manager.searcher.MAX_HITS = MAX_HITS
	user_profile = user_manager.get_user_profile(username)

	books = []
	added_book_ids = set()

	# Check if ratings have already been given for this query and user, if so those ratings will be used (saving time)
	path = f'./relevance_tests/data/{username}.json'
	if os.path.isfile(path):
		with open(path) as json_file:
			data = json.load(json_file)
			if query in data:
				print("Loading ratings from memory")
				ratings = data[query]['ratings']
			else:
				ratings = {}
	else:
		ratings = {}

	# Dictionary storing the ranked results (in the form of book_ids) for a given beta and genre boost
	# in the form of a nested dict {beta: {g_boost : [ids]}
	ranked_results = {}
	for beta in BETAS:
		book_manager.searcher.BETA = beta
		ranked_results[beta] = {}
		for g_boost in G_BOOSTS:
			book_manager.searcher.GENRE_BOOST = g_boost
			results = book_manager.search_books(query, user_profile.data[0])
			for res in results:
				if res['_source']['book_id'] not in added_book_ids:
					books.append(res['_source'])
					added_book_ids.add(res['_source']['book_id'])
			ranked_results[beta][g_boost] = [res['_source']['book_id'] for res in results]
	return books, ranked_results, ratings

class BookRankerApp(QMainWindow):
	def __init__(self, query, username):
		super().__init__()
		self.setWindowTitle("Text Ranker")

		self.username = username
		self.query = query

		self.books, self.ranked_results, self.ratings = generate_book_list(query, username)
		self.book_index = 0
		self.current_book = None

		self.create_widgets()

	def create_widgets(self):
		self.text_label = QLabel(self)
		self.text_label.setText("Book to be Rated:")
		self.text_label.setGeometry(20, 20, 300, 20)

		self.textbox = QTextEdit(self)
		self.textbox.setReadOnly(True)
		self.textbox.setGeometry(20, 40, 650, 580)
		self.display_text()

		self.rating_label = QLabel(self)
		self.rating_label.setText("Rate this text (0-3):")
		self.rating_label.setGeometry(20, 640, 300, 20)

		self.rating_entry = QLineEdit(self)
		self.rating_entry.setGeometry(150, 640, 50, 20)

		self.submit_button = QPushButton("Submit", self)
		self.submit_button.setGeometry(210, 635, 80, 30)
		self.submit_button.clicked.connect(self.submit_rating)

	def display_text(self):
		while True:
			if self.book_index >= len(self.books):
				QMessageBox.information(self, "Finished", "All books have been ranked.")
				self.save_data()
				self.close()
				return
			self.current_book = self.books[self.book_index]
			if self.current_book['book_id'] in self.ratings:
				self.book_index += 1
			else:
				break
		text = f'{self.current_book["title"]} ({self.book_index+1}/{len(self.books)})\n{self.current_book["author"]}\n\n{self.current_book["description"]}\n\n{", ".join(self.current_book["genres"])}'
		self.textbox.setPlainText(text)

	def submit_rating(self):
		try:
			rating = int(self.rating_entry.text())
			if rating < 0 or rating > 3:
				raise ValueError
		except ValueError:
			QMessageBox.critical(self, "Error", "Please enter a valid rating (0-3).")
			return

		# Store rating
		self.ratings[self.books[self.book_index]['book_id']] = rating
		self.rating_entry.setText("")

		# Move to the next book or finish if all books are ranked
		self.book_index += 1
		if self.book_index < len(self.books):
			self.display_text()
		else:
			QMessageBox.information(self, "Finished", "All books have been ranked.")
			self.save_data()
			self.close()

	def save_data(self):
		path = f'./relevance_tests/data/{self.username}.json'

		# Load data
		if os.path.isfile(path):
			with open(path) as json_file:
				data = json.load(json_file)
		else:
			data = {}

		# Add new data
		data[self.query] = {
			'ratings': self.ratings,
			'results': self.ranked_results,
		}

		# Save updated data to file
		with open(path, "w") as outfile: 
			json.dump(data, outfile)


def main():
	username = input('Username: ')
	query = input('Query: ')
	app = QApplication(sys.argv)
	window = BookRankerApp(query, username)
	window.setGeometry(100, 100, 700, 700)
	window.show()
	app.exec_() # sys.exit(app.exec_())
	try:
		nDCG_calculator.plot_ndcg(username, query)
		best_betas, best_boosts = nDCG_calculator.best_params(username, query, k=10, n=3)
		nDCG_calculator.plot_ndcg(username, query, collective_beta_and_boosts=zip(best_betas, best_boosts), suffix='best', legend_shift=False, last_dashed=False)
		nDCG_calculator.plot_ndcg(username, query, collective_beta_and_boosts=[("0.75", "50"), ("0.1", "50"), ("0.01", "50"), ("0.01", "5"), ("0.01", "10"), ("0.01", "25")], suffix='compare', legend_shift=False, last_dashed=True)
	except FileNotFoundError:
		print("File not found")
	except IndexError:
		print("Query not found")

if __name__ == "__main__":
	main()