# DD2477-Final-Project
Final project for DD2477

## Installation

Assuming you have a working Python environment:
1. Install the required packages by running `pip install -r requirements.txt`.
2. Put the relevant credentials in a .env file in the main directory, with the content as specified in .env.example.
- Alternatively, put the entire .env in the main directory.
3. The application should now be ready to run.

## Running the app

To run the app, run the following command in the main directory:
```
flask --app app run
```

- This requires the previous steps to have been completed.

The app can be accessed at `http://localhost:5000/`.

Please note that the Elasticsearch deployed on Elastic Cloud, with the current credentials, is not guaranteed to be up and running past May 13th, 2024. 


## Running tests

To run tests in `tests` folder, run the following command:
```
python -m unittest {test_file_name}
```

E.g. `python -m unittest connection_test.py`.


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
