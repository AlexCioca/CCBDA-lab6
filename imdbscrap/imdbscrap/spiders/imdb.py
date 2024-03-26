import scrapy
import re
from scrapy.exceptions import CloseSpider


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["www.imdb.com"]
    start_urls = [
        "https://www.imdb.com/title/tt0096463/fullcredits/"
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'AUTOTHROTTLE_ENABLED': True,
    }
    seen_actors = set()  # Track visited actors to avoid duplicates
    seen_movies = set()  # Track visited movies to avoid duplicates

    def parse(self, response):
        movie_id = response.xpath('//meta[@property="pageId"]/@content').get()
        if movie_id not in self.seen_movies:
            # Add current movie to seen list
            self.seen_movies.add(movie_id)

            movie_name = response.xpath('//h3[@itemprop="name"]/a/text()').get().strip()
            movie_year_dirty = response.xpath('//h3[@itemprop="name"]/span[@class="nobr"]/text()').get()
            movie_year_matches = re.search(r'\((\d{4})\)', movie_year_dirty)
            movie_year = movie_year_matches.group(1) if movie_year_matches else "Unknown"

            # check if movie is in the 80's
            if movie_year != "Unknown"  and 1980 <= int(movie_year) <= 1989:
                # Extracting actors information
                actors = response.xpath('//table[@class="cast_list"]//tr')[1:]  # Skipping the header row
                for actor in actors:
                    try:
                        actor_name = actor.xpath('.//td[2]/a/text()').get().strip()
                        actor_id = actor.xpath('.//td[2]/a/@href').re_first(r'/name/(\w+)/.*')
                        role_name = actor.xpath('.//td[4]/a/text()').get().strip()
                    except Exception as e:
                        print(e)
                    
                    yield {
                        "movie_id": movie_id,
                        "movie_name": movie_name,
                        "movie_year": movie_year,
                        "actor_name": actor_name,
                        "actor_id": actor_id,
                        "role_name": role_name
                    }

                    # Scraping actor's page for movies
                    if actor_id not in self.seen_actors:
                        # add current actor to seen actors
                        self.seen_actors.add(actor_id) 
                        actor_url = response.urljoin(actor.xpath('.//td[2]/a/@href').get())
                        yield scrapy.Request(actor_url, callback=self.parse_actor_page)

    def parse_actor_page(self, response):
        # Extracting movies from filmography (recursive parsing)
        movies = response.xpath('//div[@id="accordion-item-actor-previous-projects"]//li[@class="ipc-metadata-list-summary-item"]')[1:]
        if len(movies) == 0:
            movies = response.xpath('//div[@id="accordion-item-actress-previous-projects"]//li')[1:]

        for movie in movies:
            movie_url = response.urljoin(movie.xpath('.//div[@class="ipc-metadata-list-summary-item__tc"]/a/@href').get())
            if 'title' in str(movie_url):
                movie_url = re.sub(r'\?ref_=.+?$', 'fullcredits', movie_url)
                yield scrapy.Request(movie_url, callback=self.parse)