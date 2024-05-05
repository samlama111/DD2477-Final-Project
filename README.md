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
  "gen_weights": dict(str, float)
  "abs_weights": dict(str, float)
}
```

## Relevance tests

Relevance tests can be run for any registered user. From main directory the script is started through the command
```
python relevance_tests/relevance_checker.py
```
The user will be prompted to enter the username of a registered user along with a query to run relevance tests for. After which a GUI will open and let the user rank the suggested books on a scale of 0 to 3:

- 3: Fits with the query and seems relatively similar to previously read books
- 2: Fits the spirit of the query okay and has similarities to read books
- 1: Fits the query okay or is fairly similar to read books
- 0: Does not fit the query or previously read books at all

The raw data of the users relevance scoring for the query along with the search results for different hyperparameters of the searcher class is stored in a json file in `relevance_tests/data`. A graphical representation of the nDCG for different hyperparameters is stored in `relevance_tests/plots`.

Note: These scripts are for testing only and bypass password requirements for the user, should not be accessible by users.