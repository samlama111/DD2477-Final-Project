# Goodreads scraper

Built using Python and Scrapy.

## How to run

Assuming you have a working Python environment, you can run the scraper by following these steps:
1. Install the required packages by running `pip install -r requirements.txt` (recommended is to install in a virtual environment)
2. To run the spider (scraper), go to the `goodreads/goodreads/spiders` directory and run `scrapy crawl goodreads`. This will print the scraped data to the console. Alternatively, the output can be saved to a file by running `scrapy crawl goodreads -o output.json` (or any other file format supported by Scrapy).