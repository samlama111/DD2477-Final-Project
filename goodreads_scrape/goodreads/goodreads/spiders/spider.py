import scrapy
from goodreads.items import GoodreadsItem


# Goodreads spider scraping books from the "Best Books Ever" list
class GoodreadsSpider(scrapy.Spider):
    name = "goodreads"
    allowed_domains = ["goodreads.com"]
    list_url = "https://www.goodreads.com/list/show/1.Best_Books_Ever"

    def start_requests(self):
        # Range can be arbitrary
        for i in range(1, 10):
            yield scrapy.Request(
                url=f"{self.list_url}?page={i}",
                callback=self.parse_list,
            )

    def parse_list(self, response):
        # Get all tr (table) elements
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
        item["name"] = response.css("h1.Text::text").get()
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
        # TODO: We currently don't get the "Get more" genres
        # Could be done by parsing the script at the bottom
        genre_spans = response.css("span.BookPageMetadataSection__genreButton")
        genres = []
        for genre_span in genre_spans:
            genres.append(genre_span.css("a span::text").get())

        item["genres"] = genres
        item["pages"] = response.css("div.FeaturedDetails p::text").get().split()[0]
        # TODO: Get the ISBN from the script at the bottom of the page

        yield item
