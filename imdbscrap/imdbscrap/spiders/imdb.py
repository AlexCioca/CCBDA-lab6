import scrapy
import re
from urllib.parse import urlparse, urlunparse


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
            parsed_url = urlparse(actor_url)
           
            actor_path = parsed_url.path.rstrip('/') + '/fullcredits'
            cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, actor_path, '', '', ''))
            
            
           
            bio_path = parsed_url.path.rstrip('/') + '/bio/'
            bio_url = urlunparse((parsed_url.scheme, parsed_url.netloc, bio_path, '', '', ''))
            
            if cleaned_url is not None:
                yield response.follow(cleaned_url, callback=self.parse_actor)
            
            yield response.follow(bio_url, callback=self.parse_bio)
                            
    def parse_actor(self, response):
  
        filmography_xpath = '//*[@id="filmography"]/div[4]'

        
        for movie in response.xpath(f'{filmography_xpath}/div[contains(@class, "filmo-row")]'):
            movie_year_text = movie.xpath('./span[@class="year_column"]/text()').get().strip()
            movie_year = self.extract_year_from_text(movie_year_text)

            if movie_year and 1980 <= movie_year <= 1990:

                movie_title = movie.xpath('.//b/a/text()').get().strip()
                movie_url = movie.xpath('.//b/a/@href').get()
                
                yield {
                    'movie_url': response.urljoin(movie_url),
                    'movie_title': movie_title,
                    'movie_year': movie_year,
                }

    def extract_year_from_text(self, year_text):
        # Convert the year text to an integer.
        try:
            return int(year_text)
        except ValueError:
            return None
        
        
    def parse_bio(self, response):
        actor_name = response.xpath('//*[@id="__next"]/main/div/section/section/div[3]/section/section/div[2]/hgroup/h2/text()').get().strip()
        
        height_raw = response.xpath('//*[@id="height"]/div/div/div/text()').get()
        height_in_meters = self.extract_height_in_meters(height_raw)
        
        if not height_in_meters is None: 
            yield {
                'actor_name': actor_name,
                'height_in_meters': height_in_meters,
            
                }
        
    def extract_height_in_meters(self, height_raw):

        if height_raw:
            match = re.search(r'\((\d+\.\d+) m\)', height_raw)
            if match:
                return float(match.group(1))
        return None