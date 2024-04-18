from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch([{"host":"localhost", "port":9200, "scheme": "https"}], basic_auth=('elastic', 'derpoVrWlzrjV*Au7e9r'), verify_certs=False)

print(es.ping())

# Input data - uncomment the following to index

# with open('output.json', 'r') as file:
#     data = json.load(file)

# index_name = "goodreads"
# bulk_data = []
# bookID = 0

# for obj in data:
#     name = obj["name"]
#     description = obj["description"]
#     author = obj["author"]
#     rating = obj["rating"]
#     num_ratings = obj["num_ratings"]
#     num_reviews = obj["num_reviews"]
#     genres = obj["genres"]

#     document={
#         'name': name,
#         'description': description,
#         'author': author,
#         'rating': rating,
#         'num_ratings': num_ratings,
#         'numreviews': num_reviews,
#         'genres': genres
#     }
#     bulk_data.append({
#         "_index": index_name,
#         "_id": bookID,
#         "_source": document
#     })
        
#     bookID += 1
    
# response = helpers.bulk(es, bulk_data, index=index_name)




# Perform search

result = es.search(index="*", query={"match": {"description": "christmas"}})

no_of_results = 0

for hit in result['hits']['hits']:
    no_of_results += 1
    print("\n")
    print("Result", no_of_results)
    print("Book: ", hit["_source"]['name'])
print("\n")