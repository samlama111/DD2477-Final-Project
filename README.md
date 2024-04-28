# DD2477-Final-Project
Final project for DD2477

## Installation

To install the app, install the required packages by running the following command:
```
pip install -r requirements.txt
``` 

## Running the app

To run the app, run the following command:
```
flask --app app run
```


## Running tests

To run tests in `tests` folder, run the following command:
```
python -m unittest {test_file_name}
```

E.g. `python -m unittest connection_test.py`.


## Structure of data stored in Elasticsearch
Two indexes are maintained INSERT INDEX NAMES HERE. 

The index for books stores the books as dictionaries with the structure:
```
{
  "title": str,
  "author": str,
  "abstract": str,
  "genres": [str],
  "rating": float,
  "n_ratings": int,
  "n_reviews": int,
  "book_id": str,
  "url": str,
  "img_url": str,
}
```
The index for the user profiles stores the profiles as dictionaries with the structure:

```
{
  "name": str
  "books": [str]
  "gen_weight": dict(str, float)
  "abs_weight": dict(str, float)
}
```
