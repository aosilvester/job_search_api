import scrapy
from datetime import datetime, timedelta
import json
import time

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com',]
    start_urls = ['http://indeed.com/']

    def parse(self, response):
        # 1240 zipcodes in Virginia
        #  88 counties in Virginia
        counties = open('virginia_counties.json', 'r')
        counties_json = json.loads(counties.read())
        counties_json = counties_json[0:5]
        for county in counties_json:
            county = county.replace(' ', '+')
            url = "https://www.indeed.com/jobs?q=Social+Worker&l={}%2C+VA&radius=0"
            url = url.format(county)
            yield scrapy.Request(
                url=url,
                callback=self.get_data,
                meta={'search_parameter': county}
            )
        # zipcodes = open('virginia_zipcodes.json', 'r')
        # zipcodes_json = json.loads(zipcodes.read())
        # for zipcode in zipcodes_json:
            # url_template = 'https://www.indeed.com/jobs?q=Social+Worker&l={}&radius=0'
            # url = url_template.format(zipcode)
        # print('end?')

    def get_data(self, response):
        time.sleep(5)
        job_postings = response.css('div.jobsearch-SerpJobCard')
        scraped_postings = []
        for posting in job_postings:
            item = {}
            item['jobsite'] = 'indeed.com'
            item["posting_details_url"] = 'https://www.indeed.com'+self.get_value(posting,'h2.title > a::attr(href)')
            item["job_title"] = self.get_value(posting, 'h2.title > a ::text')
            item["company"] = self.get_value(posting,'span.company ::text')
            item["city"] = self.get_city(response, posting)
            item["search_parameter"] = response.meta.get('search_parameter')
            item["salary"] = self.get_value(posting,'span.salary ::text')
            item['summary'] = self.get_summary(posting)
            item["posting_age"] = self.get_posting_age(posting).strip()
            item["date_scraped"] = str(datetime.today())
            for key, value in item.items():
                if item[key] is None:
                    # print('*******', key, ' this is empty')
                    item[key] = 'None'
            scraped_postings.append(item)
            
        self.write_to_json(scraped_postings)
        yield self.next_page(response)


    def get_summary(self, posting):
        summary = posting.css('div.summary ::text').extract()
        return ''.join(summary[2:])

    def get_value(self, posting, selector_path):
        value = posting.css(selector_path).extract()
        if value:
            return ''.join(value).strip()
        return None

    def next_page(self, response):
        next_page_url = response.css('ul.pagination-list > li:last-of-type > a::attr(href)').extract_first()
        if next_page_url:      
            return scrapy.Request(
                url='https://www.indeed.com'+next_page_url,
                callback=self.get_data,
            )
        pass

    def get_city(self, response, posting):
        city = posting.css('div.location ::text').extract()
        return ''.join(city)

    def get_posting_age(self, posting):
        relative_date = posting.css('span.date ::text').extract_first()
        relative_date = relative_date.split()[0]
        try:
            if '+' in relative_date:
                relative_date = relative_date[:-1]
            if 'Today' in relative_date:
                relative_date = 0
            time_code = datetime.today() - timedelta(days=int(relative_date))
            posting_date, _ = str(time_code).split()
            return posting_date
        except:
            return relative_date


    initial_posting = True
    def write_to_json(self, scraped_postings):
        for posting in scraped_postings:
            if self.initial_posting:
                write_scraped_file = open('indeed_scraped_postings.json', 'w')
                write_scraped_file.write('[')
                write_scraped_file.write(str(json.dumps(posting)))
                write_scraped_file.write(']')
                self.initial_posting = False
                write_scraped_file.close()
            else:
                read_scraped_file = open('indeed_scraped_postings.json', 'r')
                existing_postings = json.loads(read_scraped_file.read())
                existing_postings.append(posting)
                read_scraped_file.close()
                write_scraped_file = open('indeed_scraped_postings.json', 'w')
                write_scraped_file.write(str(json.dumps(existing_postings)))
                write_scraped_file.close()
