from elasticsearch import Elasticsearch

es = Elasticsearch([{"host":"localhost", "port":9200, "scheme": "https"}], basic_auth=('elastic', 'derpoVrWlzrjV*Au7e9r'), verify_certs=False)

print(es.ping())

# Input data

# es.index(
#  index='lord-of-the-rings',
#  document={
#   'character': 'Aragon',
#   'quote': 'It is not this day.'
#  })

# es.index(
#  index='lord-of-the-rings',
#  document={
#   'character': 'Gandalf',
#   'quote': 'A wizard is never late, nor is he early.'
#  })

# es.index(
#  index='lord-of-the-rings',
#  document={
#   'character': 'Frodo Baggins',
#   'quote': 'You are late'
#  })



result = es.search(index="*", query={"match": {"quote": "is"}})

no_of_results = 0
for hit in result['hits']['hits']:
    no_of_results += 1
    print("\n")
    print("Result", no_of_results)
    print("Book: ", hit["_index"])
    print("Sentence: ", hit["_source"]["quote"])
print("\n")