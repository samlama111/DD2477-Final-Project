import unittest
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()


class ElasticSearchConnectionTest(unittest.TestCase):
    # Test connection to elasticsearch
    def test_connection(self):
        # Get secrets
        CLOUD_ID = os.getenv("CLOUD_ID")
        API_KEY = os.getenv("API_KEY")

        client = Elasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)
        client_info = client.info()
        self.assertIsNotNone(client_info)


if __name__ == "__main__":
    unittest.main()
