import scrapy


class ZipcodeGeneratorSpider(scrapy.Spider):
    name = 'zipcode_generator'
    allowed_domains = ['https://www.unitedstateszipcodes.org/']
    start_urls = ['http://www.unitedstateszipcodes.org/va/']

    def parse(self, response):
        print('parse')
        zipcodes = response.css('div.list-group-item div.col-xs-12:first-of-type > a::text').extract()


        # pass
