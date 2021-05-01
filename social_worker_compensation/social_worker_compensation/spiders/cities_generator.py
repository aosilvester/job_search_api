import scrapy


class CitiesGeneratorSpider(scrapy.Spider):
    name = 'cities_generator'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/List_of_cities_and_counties_in_Virginia']

    def parse(self, response):
        cities = response.xpath(".//span[contains(text(),'List of independent cities')]/../following-sibling::*[1]//tbody/tr/th[1]/a/text()").extract()
        # print(cities)
        counties = response.xpath(".//span[contains(text(),'List of counties')]/../following-sibling::*[1]//tbody/tr/th[1]/a/text()").extract()
        print(cities)
