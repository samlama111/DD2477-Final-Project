"""
This script is to be run separate from the main implementation.
The intent of this script (through a rudimentary UI) lets a tester load the preferences
of a user and give a query to grade its relevance.

The user will be shown book names, authors and abstracts and will be asked to rank their interest of the book
on a scale of 0 to 3
"""
import sys
import os
sys.path.insert(1, os.getcwd()) # Assumption that app is run from DD2477-Final-Project directory
from searcher import Searcher
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError
from dotenv import load_dotenv

load_dotenv()
CLOUD_ID = os.getenv("CLOUD_ID")
API_KEY = os.getenv("API_KEY")
es = Elasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)
BOOK_INDEX = "books"
PROFILE_INDEX = "user_profiles"

BETAS = [0.01, 0.03, 0.1, 0.3, 0.75]
G_BOOSTS = [1, 5, 10, 50]
MAX_HITS = 20

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QLineEdit, QPushButton, QMessageBox

def generate_book_list(query, username):
	searcher = Searcher(es, BOOK_INDEX)
	searcher.ABSTRACT_BOOST = 1
	searcher.ALPHA = 1.0
	user_profile = es.get(index=PROFILE_INDEX, id=username)["_source"]

	books = []

	# Dictionary storing the ranked results (in the form of book_ids) for a given beta and genre boost
	# in the form of a tuple (beta, g_boost) : [ids]
	ranked_results = {}
	for beta in BETAS:
		searcher.BETA = beta
		for g_boost in G_BOOSTS:
			searcher.GENRE_BOOST = g_boost
			results, _ = searcher.query(query, user_profile)

			books.extend([res['_source'] for res in results])
			ranked_results[(beta, g_boost)] = [res['_source']['book_id'] for res in results]
	return books, ranked_results


class BookRankerApp(QMainWindow):
	def __init__(self, query, username):
		super().__init__()
		self.setWindowTitle("Text Ranker")

		self.ratings = {}
		self.books, self.ranked_results = generate_book_list(query, username)
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
			self.current_book = self.books[self.book_index]
			if self.current_book['book_id'] in self.ratings:
				self.book_index += 1
				if self.book_index >= len(self.books):
					QMessageBox.information(self, "Finished", "All books have been ranked.")
					self.close()
			else:
				break
		text = f'{self.current_book["title"]}\n{self.current_book["author"]}\n\n{self.current_book["description"]}'
		self.textbox.setPlainText(text)

	def submit_rating(self):
		try:
			rating = int(self.rating_entry.text())
			if rating < 0 or rating > 3:
				raise ValueError
		except ValueError:
			QMessageBox.critical(self, "Error", "Please enter a valid rating (0-3).")
			return

		# Store rating (you can implement this part according to your requirement)
		print(f"Book {self.books[self.book_index]['title']} rating: {rating}")
		self.rating_entry.setText("")

		# Move to the next book or finish if all books are ranked
		self.book_index += 1
		if self.book_index < len(self.books):
			self.display_text()
		else:
			QMessageBox.information(self, "Finished", "All books have been ranked.")
			self.close()
		

def main():
	app = QApplication(sys.argv)
	window = BookRankerApp('test', 'theoi')
	window.setGeometry(100, 100, 700, 700)
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
	

if __name__ == '__main__':
	main()