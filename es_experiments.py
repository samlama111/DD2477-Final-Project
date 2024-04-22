from elasticsearch import Elasticsearch

def get_client(password = 'lrFrrca77CLpFPZlxZwh'):
    return Elasticsearch([{"host":"localhost", "port":9200, "scheme": "https"}], 
                         basic_auth=('elastic', password), 
                         verify_certs=False,
                         ssl_show_warn=False)

def set_up_experiment_index(es_client: Elasticsearch):
    """Generates index for experiments, should only be run once"""
    data1 = {
        'title': 'Space dragons I: The dragoning',
        'author': 'I. Ron Butterfly',
        'description': 'Eric was in space prison before he was rescued by the dragon Terra-axis, who was actually a CyDragon but we do not have time to get into it. Adventure awaits.',
        'genres': 'sci-fi, fantasy, dragons, dystopia',
        'rating': 0.2,
        'reviews': 20,
        'id': '1'
    }
    data2 = {
        'title': 'Space dragons II: Even spacier',
        'author': 'I. Ron Butterfly',
        'description': 'It had been five years since Eric was rescued from space prison, but now he and his dragon are out for revenge.',
        'genres': 'sci-fi, fantasy, dragons, dystopia',
        'rating': 0.1,
        'reviews': 100,
        'id': '2'
    }
    data3 = {
        'title': 'Tales of Duskendale',
        'author': 'Elias Fakinami',
        'description': 'The dragons have been gone for as long as anyone can remember, but just yesterday Delilah the dragon tamer claims she saw a dragon close to the dragon roost cavern. Gosh darn she likes dragons.',
        'genres': 'fantasy, romance',
        'rating': 4.0,
        'reviews': 20000,
        'id': '3'
    }
    data4 = {
        'title': 'Romance Academy 7',
        'author': 'Soos',
        'description': 'When the cherry blossoms of magic romance academy are in bloom... anything can happen. So true.',
        'genres': 'fantasy, romance, teen',
        'rating': 2.0,
        'reviews': 238,
        'id': '4'
    }

    for data in (data1, data2, data3, data4):
        resp = es_client.index(index=INDEX, document=data, id=data['id'])

def standard_search(es_client: Elasticsearch, query: str):
    """Searches through the book description for a given query"""
    resp = es_client.search(index=INDEX,
                            query={'match': {'description': {'query': query}}})
    return [result for result in resp['hits']['hits']]

def rated_search(es_client: Elasticsearch, query: str):
    query_body = {
        "query" : {
            "function_score" : {
                "query": {"match": {"description": query}},
                "script_score": {
                    "script": {
                        "source": "Math.log(doc['reviews'].value) * doc['rating'].value"
                    }
                }
            }
        }
    }
        
    resp = es_client.search(index=INDEX, body=query_body)
    return [result for result in resp['hits']['hits']]

def _build_query(query_list, field, queries, boost):
    pass

def rated_and_weighted_search(es_client: Elasticsearch, weighted_queries: dict[str, float]):
    boolean_queries = []
    for q, w in weighted_queries.items():
        next = {
            "match": {"description": {"query": q, "boost": w}}
        }
        boolean_queries.append(next)
    
    query_body = {
        "query" : {
            "function_score" : {
                "query": {
                    "bool" : {"should" : boolean_queries},
                },
                "script_score": {
                    "script": {
                        "source": "Math.log(doc['reviews'].value) * doc['rating'].value" # Math.log(doc['reviews'].value) * 
                    }
                }
            }
        }
    }
        
    resp = es_client.search(index=INDEX, body=query_body)
    return [result for result in resp['hits']['hits']]

def show_results(results):
    for res in results:
        print(f'Title: {res["_source"]["title"]}')
        print(f'Author: {res["_source"]["author"]}')
        print(f'Rating: {res["_source"]["rating"]}')
        print(f'Reviews: {res["_source"]["reviews"]}')
        print(f'Score: {res["_score"]}')
        print()

INDEX = 'experiment_index'
FIRST_TIME = False
def main():
    es_client = get_client()
    if FIRST_TIME:
        set_up_experiment_index(es_client)
    results = standard_search(es_client, 'dragon')

    results = rated_search(es_client, 'dragon')

    weighted_queries = {
        'dragon': 0.1,
        'space': 1.5
    }
    results = rated_and_weighted_search(es_client, weighted_queries)
    show_results(results)
    
    
    


if __name__ == '__main__':
    main()