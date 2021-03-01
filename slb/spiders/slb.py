import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from slb.items import Article


class SlbSpider(scrapy.Spider):
    name = 'slb'
    start_urls = ['https://www.slb.ch/aktuelles/']

    def parse(self, response):
        articles = response.xpath('//div[@class="news__news-preview"]//a[@class="link--no-styles"]')
        for article in articles:
            link = article.xpath('./@href').get()
            date = article.xpath('.//div[@class="news-preview__time"]//text()').getall()
            if date:
                date = [text.strip() for text in date]
                date = " ".join(date)

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="page-header__title"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="container page page--post"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
