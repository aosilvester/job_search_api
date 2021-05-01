import scrapy
from datetime import datetime, timedelta
import json
import time

class LinkedinSpider(scrapy.Spider):
    name = 'linkedin'
    allowed_domains = ['linkedin.com']
    start_urls = ['http://linkedin.com/']

    def parse(self, response):
        # 1240 zipcodes in Virginia
        #  88 counties in Virginia
        counties = open('virginia_counties.json', 'r')
        counties_json = json.loads(counties.read())
        for county in counties_json:
            county = county.replace(' ', '%20')
            url = "https://www.linkedin.com/jobs/search?keywords=Social%20Worker&location={}%2C%20Virginia%2C%20United%20States&geoId=104532226&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0"
    
    # https://www.linkedin.com/jobs/search?keywords=Social%20Worker&location=Arlington%20County%2C%20Virginia%2C%20United%20States&geoId=104532226&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0
            url = url.format(county)
    
            yield scrapy.Request(
                url=url,
                callback=self.get_data,
                meta={'search_parameter': county}
            )


    def get_data(self, response):
        print(response)