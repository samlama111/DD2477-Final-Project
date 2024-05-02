"""
Rudimentary test code for searcher class, 
	not constructed as unittests but instead to run and see if the ouput makes sense.
"""

from searcher import Searcher
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError
from dotenv import load_dotenv
import os

load_dotenv()
CLOUD_ID = os.getenv("CLOUD_ID")
API_KEY = os.getenv("API_KEY")
es = Elasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)

BOOK_INDEX = "books"
PROFILE_INDEX = "user_profiles"

def build_booklist(client: Elasticsearch):
	book1 = {
		"title": "Yellowface",
		"author": "R.F. Kuang",
		"abstract": "White lies. Dark humor. Deadly consequences… Bestselling sensation Juniper Song is not who she says she is, she didn't write the book she claims she wrote, and she is most certainly not Asian American—in this chilling and hilariously cutting novel from R.F. Kuang, the #1 New York Times bestselling author of Babel.\nAuthors June Hayward and Athena Liu were supposed to be twin rising stars. But Athena's a literary darling. June Hayward is literally nobody. Who wants stories about basic white girls, June thinks.\nSo when June witnesses Athena's death in a freak accident, she acts on impulse: she steals Athena's just-finished masterpiece, an experimental novel about the unsung contributions of Chinese laborers during World War I.\nSo what if June edits Athena's novel and sends it to her agent as her own work? So what if she lets her new publisher rebrand her as Juniper Song—complete with an ambiguously ethnic author photo? Doesn't this piece of history deserve to be told, whoever the teller? That's what June claims, and the New York Times bestseller list seems to agree.\nBut June can't get away from Athena's shadow, and emerging evidence threatens to bring June's (stolen) success down around her. As June races to protect her secret, she discovers exactly how far she will go to keep what she thinks she deserves.\nWith its totally immersive first-person voice, Yellowface grapples with questions of diversity, racism, and cultural appropriation, as well as the terrifying alienation of social media. R.F. Kuang's novel is timely, razor-sharp, and eminently readable.",
		"genres": ["Fiction", "Contemporary", "Audiobook", "Literary Fiction", "Thriller", "Adult", "Mystery", "Adult Fiction", "Books About Books", "Mystery Thriller"],
		"rating": 3.8,
		"n_ratings": 441181,
		"n_reviews": 60604,
		"book_id": "62047984-yellowface",
		"url": "placeholder",
		"img_url": "placeholder",
	}
	book2 = {
		"title": "Hello Beautiful",
		"author": "Ann Napolitano",
		"abstract": "An emotionally layered and engrossing story of a family that asks: Can love make a broken person whole?\nWilliam Waters grew up in a house silenced by tragedy, where his parents could hardly bear to look at him, much less love him. So it's a relief when his skill on the basketball court earns him a scholarship to college, far away from his childhood home. He soon meets Julia Padavano, a spirited and ambitious young woman who surprises William with her appreciation of his quiet steadiness. With Julia comes her family; she is inseparable from her three younger sisters: Sylvie, the dreamer, is happiest with her nose in a book and imagines a future different from the expected path of wife and mother; Cecelia, the family's artist; and Emeline, who patiently takes care of all of them. Happily, the Padavanos fold Julia's new boyfriend into their loving, chaotic household.\nBut then darkness from William's past surfaces, jeopardizing not only Julia's carefully orchestrated plans for their future, but the sisters' unshakeable loyalty to one another. The result is a catastrophic family rift that changes their lives for generations. Will the loyalty that once rooted them be strong enough to draw them back together when it matters most?\nVibrating with tenderness, Hello Beautiful is a gorgeous, profoundly moving portrait of what's possible when we choose to love someone not in spite of who they are, but because of it.",
		"genres": ["Fiction", "Historical Fiction", "Audiobook", "Contemporary", "Romance", "Literary Fiction", "Family", "Book Club", "Adult", "Adult Fiction"],
		"rating": 4.18,
		"n_ratings": 304495,
		"n_reviews": 28845,
		"book_id": "61771675-hello-beautiful",
		"url": "placeholder",
		"img_url": "placeholder",
	}
	book3 = {
		"title": "The Wishing Game",
		"author": "Meg Shaffer",
		"abstract": "Make a wish....\nLucy Hart knows better than anyone what it's like to grow up without parents who loved her. In a childhood marked by neglect and loneliness, Lucy found her solace in books, namely the Clock Island series by Jack Masterson. Now a twenty-six-year-old teacher's aide, she is able to share her love of reading with bright, young students, especially seven-year-old Christopher Lamb, who was left orphaned after the tragic death of his parents. Lucy would give anything to adopt Christopher, but even the idea of becoming a family seems like an impossible dream without proper funds and stability.\nBut be careful what you wish for....\nJust when Lucy is about to give up, Jack Masterson announces he's finally written a new book. Even better, he's holding a contest at his home on the real Clock Island, and Lucy is one of the four lucky contestants chosen to compete to win the one and only copy.\nFor Lucy, the chance of winning the most sought-after book in the world means everything to her and Christopher. But first she must contend with ruthless book collectors, wily opponents, and the distractingly handsome (and grumpy) Hugo Reese, the illustrator of the Clock Island books. Meanwhile, Jack “the Mastermind” Masterson is plotting the ultimate twist ending that could change all their lives forever.\n... You might just get it.",
		"genres": ["Fiction", "Fantasy", "Romance", "Contemporary", "Books About Books", "Magical Realism", "Mystery", "Audiobook", "Adult", "Adult Fiction"],
		"rating": 4.12,
		"n_ratings": 107217,
		"n_reviews": 17123,
		"book_id": "62926992-the-wishing-game",
		"url": "placeholder",
		"img_url": "placeholder",
	}
	book4 = {
		"title": "In the Lives of Puppets",
		"author": "T.J. Klune",
		"abstract": "In a strange little home built into the branches of a grove of trees, live three robots—fatherly inventor android Giovanni Lawson, a pleasantly sadistic nurse machine, and a small vacuum desperate for love and attention. Victor Lawson, a human, lives there too. They're a family, hidden and safe.\nThe day Vic salvages and repairs an unfamiliar android labelled “HAP,” he learns of a shared dark past between Hap and Gio–a past spent hunting humans.\nWhen Hap unwittingly alerts robots from Gio's former life to their whereabouts, the family is no longer hidden and safe. Gio is captured and taken back to his old laboratory in the City of Electric Dreams. So together, the rest of Vic's assembled family must journey across an unforgiving and otherworldly country to rescue Gio from decommission, or worse, reprogramming.\nAlong the way to save Gio, amid conflicted feelings of betrayal and affection for Hap, Vic must decide for himself: Can he accept love with strings attached?\nInspired by Carlo Collodi's The Adventures of Pinocchio, and like Swiss Family Robinson meets Wall-E, In the Lives of Puppets is a masterful stand-alone fantasy adventure from the beloved author who brought you The House in the Cerulean Sea and Under the Whispering Door.",
		"genres": ["Fiction", "Fantasy", "Romance", "Contemporary", "Books About Books", "Magical Realism", "Mystery", "Audiobook", "Adult", "Adult Fiction"],
		"rating": 3.94,
		"n_ratings": 60123,
		"n_reviews": 11252,
		"book_id": "60784549-in-the-lives-of-puppets",
		"url": "placeholder",
		"img_url": "placeholder",
	}

	books = [book1, book2, book3, book4]
	for book in books:
		resp = client.index(index=BOOK_INDEX, document=book, id=book['book_id'])

def create_profile(client: Elasticsearch, username: str, book_ids: list[str]):
	"""
	Expected format of user data:
		{
			"name": str
			"books": [str]
			"gen_weights": dict(str, float)
			"abs_weights": dict(str, float)
		}
	"""
	books = []
	gen_weights = {}
	abs_weights = {}
	for book_id in book_ids:
		try:
			resp = client.get(index=BOOK_INDEX, id=book_id)
		except NotFoundError:
			print(f'Book id "{book_id}" not found.')
			continue
		book = resp["_source"]

		# Add to abs_weights
		split_abstract = book["abstract"].split()
		for tok in split_abstract:
			fixed_tok = ''.join(ch for ch in tok if ch.isalnum())
			if len(fixed_tok) > 0:
				abs_weights[fixed_tok] = abs_weights.get(fixed_tok, 0) + 1

		# Add to gen_weights
		genres = book["genres"]
		for genre in genres:
			gen_weights[genre] = gen_weights.get(genre, 0) + 1

		books.append(book_id)
	
	profile = {
		"name": username,
		"books": books,
		"gen_weights": gen_weights,
		"abs_weights": abs_weights
	}

	client.index(index=PROFILE_INDEX, document=profile, id=username)

def setup(client: Elasticsearch):
	build_booklist(client)
	create_profile(client, 'theoi', ['62047984-yellowface'])

def show_results(results, scores):
	for res, score in zip(results, scores):
		print(f'Title: {res["title"]}')
		print(f'Author: {res["author"]}')
		print(f'Rating: {res["rating"]}')
		print(f'Reviews: {res["n_reviews"]}')
		print(f'Score: {score}')
		print()

def get_client(password = 'lrFrrca77CLpFPZlxZwh'):
	return Elasticsearch([{"host":"localhost", "port":9200, "scheme": "https"}], 
						 basic_auth=('elastic', password), 
						 verify_certs=False,
						 ssl_show_warn=False)

first_time = False 
def test():
	searcher = Searcher(es, BOOK_INDEX)
	searcher.ABSTRACT_BOOST = 1
	searcher.GENRE_BOOST = 5
	searcher.ALPHA = 1.0
	searcher.BETA = 0.05

	user_profile = es.get(index=PROFILE_INDEX, id='theoi')["_source"]

	query = "family tragedy"
	results, scores = searcher.query(query, user_profile)
	show_results(results, scores)

if __name__ == '__main__':
	test()



