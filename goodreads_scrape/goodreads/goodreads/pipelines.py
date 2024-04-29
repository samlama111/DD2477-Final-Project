# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import requests


class GoodreadsPipeline:
    def process_item(self, item, spider):
        api_url = "http://localhost:5000/"
        api_endpoint = "scraper/addbook"
        full_url = api_url + api_endpoint
        requests.post(full_url, json=dict(item))
        return item
