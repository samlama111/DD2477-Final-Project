import json
import re
import scrapy
from goodreads.items import GoodreadsItem


# Goodreads spider scraping books from the "Best Books Ever" list
class GoodreadsSpider(scrapy.Spider):
    name = "goodreads"
    allowed_domains = ["goodreads.com"]
    list_url = "https://www.goodreads.com/list/show/1.Best_Books_Ever"

    def start_requests(self):
        # Range should approximately match the size of the Davis dataset (17478 documents).
        # With each page being 100 books, we should go through (at least) 175 iterations.
        for i in range(1, 10):
            yield scrapy.Request(
                url=f"{self.list_url}?page={i}",
                callback=self.parse_book_list,
            )

    def parse_book_list(self, response):
        # Get all tr (table) elements, to get all book URLs
        # then parse each book page
        tr_elements = response.xpath("//tr")
        for tr in tr_elements:
            url = tr.xpath(".//a/@href").get()
            # TODO: Investigate error with wrong ID in
            # https://www.goodreads.com/book/show/19351490-grimm-s-fairy-tales
            yield scrapy.Request(
                url=f"https://www.goodreads.com{url}",
                callback=self.parse_book,
            )

    def parse_book(self, response):
        item = GoodreadsItem()
        
        book_name = response.css("h1.Text::text").get()
        if not book_name:
            # If the book url is faulty, we can't extract anything
            return
        
        # Static content, we can extract directly using CSS or XPath selectors
        item["name"] = book_name
        description_text = response.xpath(
            '//div[contains(@class, "BookPageMetadataSection__description")]//span[@class="Formatted"]/text()'
        ).getall()
        item["description"] = "".join(description_text)
        item["author"] = response.css("a.ContributorLink span::text").get()
        rating = response.css("div.RatingStatistics__rating::text").get()
        item["rating"] = float(rating) if rating else None
        statistics_spans = response.css(
            "div.BookPageMetadataSection div.RatingStatistics__meta span"
        )
        item["num_ratings"] = int(
            statistics_spans[0].xpath(".//text()").get().replace(",", "")
        )
        item["num_reviews"] = int(
            statistics_spans[1].xpath(".//text()").get().replace(",", "")
        )
        # item["pages"] = int(
        #     response.css("div.FeaturedDetails p[data-testid='pagesFormat']::text").get().split()[0]
        # )

        genres = []
        # Goodreads item pages have a huge script with all the relevant data
        # used to render the page. We can extract the JSON data from the script
        # directly, which is necessary for some dynamically loaded content (e.g. genres)
        json_data = self.parse_json_script(response)
        # Try to get genres from the JSON data
        if json_data:
            raw_legacy_book_id = json_data["props"]["pageProps"]["params"]["book_id"]
            # Legacy book ID
            legacy_id = raw_legacy_book_id.split("-")[0].split(".")[0]
            # Key used to get the book ID by legacy ID
            legacy_id_key = 'getBookByLegacyId({"legacyId":"' + legacy_id + '"})'
            # Actual book ID used by Goodreads
            amazon_book_id = json_data["props"]["pageProps"]["apolloState"][
                "ROOT_QUERY"
            ][legacy_id_key]["__ref"]
            raw_genres = json_data["props"]["pageProps"]["apolloState"][amazon_book_id][
                "bookGenres"
            ]
            # Get only name key from raw_generes
            genres = [raw_genre["genre"]["name"] for raw_genre in raw_genres]
        # Fallback to parsing genres from the static content
        else:
            genre_spans = response.css("span.BookPageMetadataSection__genreButton")
            for genre_span in genre_spans:
                genres.append(genre_span.css("a span::text").get())

        item["genres"] = genres

        # TODO: Get the ISBN from the script at the bottom of the page
        # Not every book has an ISBN, so we can't guarantee it as an ID

        yield item

    def parse_json_script(self, response):
        script_text = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        # Using regex to extract JSON string
        json_data_match = re.search(r"({.*})", script_text)
        if json_data_match:
            json_data = json_data_match.group(1)
            data = json.loads(json_data)
            return data
        return None
