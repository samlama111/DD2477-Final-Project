from elasticsearch import Elasticsearch
import json

es = Elasticsearch([{"host":"localhost", "port":9200, "scheme": "https"}], basic_auth=('elastic', 'derpoVrWlzrjV*Au7e9r'), verify_certs=False)

print(es.ping())

# Input data - uncomment the following to index

# with open('output.json', 'r') as file:
#     data = json.load(file)

# bookID = 0
# for obj in data:
#     name = obj["name"]
#     description = obj["description"]
#     author = obj["author"]
#     rating = obj["rating"]
#     num_ratings = obj["num_ratings"]
#     num_reviews = obj["num_reviews"]
#     genres = obj["genres"]

#     es.index(
#         index=bookID,
#         document={
#         'name': name,
#         'description': description,
#         'author': author,
#         'rating': rating,
#         'num_ratings': num_ratings,
#         'numreviews': num_reviews,
#         'genres': genres
#     })
        
#     bookID += 1
    
    
# Perform search

result = es.search(index="*", query={"match": {"description": "christmas"}})

no_of_results = 0

for hit in result['hits']['hits']:
    no_of_results += 1
    print("\n")
    print("Result", no_of_results)
    print("Book: ", hit["_source"]['name'])
print("\n")