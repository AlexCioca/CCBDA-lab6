import scrapy
import unidecode
import re

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))

class NytimesSpider(scrapy.Spider):
    name = 'nytimes'
    allowed_domains = ['www.nytimes.com']
    start_urls = ['https://www.nytimes.com/section/technology']

    def parse(self, response):
        for section in response.css("section#collection-highlights-container"):
            section_name = section.css('h2::text').get()
            for article in section.css("article"):
                #article_url = response.url[:-1] + article.css('a::attr(href)').extract_first()
                article_url = response.urljoin(article.css('a::attr(href)').get())
                yield {
                    'section': section_name,
                    'appears_ulr': response.url,
                    'title': cleanString(article.css('a::text, a span::text').extract_first()),
                    'article_url': article_url,
                    'summary': cleanString(''.join(article.css('p::text, ul li::text').extract())),
                }
                next_page = article_url
                if next_page is not None:
                    yield response.follow(next_page, callback=self.parse_article)
                    
    def parse_article(self, response):

        title = cleanString(' '.join(response.css("h1::text").getall()))
        authors = cleanString(', '.join(response.css("a.e1jsehar0::text").getall())) 
        contents = cleanString(' '.join(response.css("section[name='articleBody'] p::text").getall()))
        yield {
            'appears_ulr': response.url,
            'title': title,
            'authors': authors,
            'contents': contents,
                }