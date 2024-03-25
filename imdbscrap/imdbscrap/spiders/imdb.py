import scrapy
import re


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["www.imdb.com"]
    start_urls = ["https://www.imdb.com/title/tt0120815/fullcredits"]
    custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'AUTOTHROTTLE_ENABLED': True,}

    def parse(self, response):
        movie_id = response.xpath('//meta[@property="pageId"]/@content').get()
        movie_name = response.xpath('//h3[@itemprop="name"]/a/text()').get().strip()
        movie_year_dirty = response.xpath('//h3[@itemprop="name"]/span[@class="nobr"]/text()').get()
        movie_year_matches = re.search(r'\((\d{4})\)', movie_year_dirty)
        movie_year = movie_year_matches.group(1) if movie_year_matches else "Unknown"


        for row in response.xpath('//tr[contains(@class, "odd")] | //tr[contains(@class, "even")]'):
            actor_url = row.xpath('.//td[2]/a/@href').get() 
            yield {
            "url" : actor_url,    
            "movie_id": movie_id,
            "movie_name" : movie_name,
            "movie_year" : movie_year,
            "actor_name" : row.xpath('.//td[2]/a/text()').get().strip(),
            "role_name" : row.xpath('.//td[@class="character"]/a/text()').get().strip()
            }
            next_page = actor_url
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse_actor)
                
    def parse_actor(self, response):
       
        section_xpath = '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/div[4]/section[2]'
        
        for movie in response.xpath(f'{section_xpath}//div[contains(@id, "accordion-item-producer-previous-projects")]/div/ul/li'):
            movie_title = movie.xpath('./a/@aria-label').get()
            movie_url = movie.xpath('./a/@href').get()
            movie_year_xpath = './div[2]/div[2]/ul/li/span/text()'
            movie_year_text = movie.xpath(movie_year_xpath).get()
            movie_year = self.extract_year_from_text(movie_year_text)  


            if movie_year and 1980 <= movie_year <= 1989:
                yield {
                    'movie_url': response.urljoin(movie_url),
                    'movie_title': movie_title,
                    'movie_year': movie_year,
                }
    def extract_year_from_text(self, year_text):
    # Assuming the year text is directly the year, convert to integer
        try:
            return int(year_text)
        except ValueError:
            # Log or handle cases where year_text does not convert cleanly
            return None