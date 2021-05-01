# scrapy crawl glassdoor --logfile=localtest.log --set=ROBOTSTXT_OBEY='False'
import scrapy
from datetime import datetime, timedelta
import json
import time
import bz2

class GlassdoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['glassdoor.com']
    start_urls = ['http://glassdoor.com/']

    def parse(self, response):
        # 1240 zipcodes in Virginia
        #  88 counties in Virginia
        # counties = open('virginia_counties.json', 'r')
        # counties_json = json.loads(counties.read())
        # for county in counties_json:
        #     # county, _ = county.split()
        #     county = county[:-7]
        #     # print(county)
        #     url = 'https://www.glassdoor.com/findPopularLocationAjax.htm?term={}&maxLocationsToReturn='
        #     yield scrapy.Request(
        #         url=url.format(county),
        #         callback=self.scrape_by_location_info,
        #         meta={'search_parameter': county}
        #     )
        cities = open('virginia_cities.json', 'r')
        cities_json = json.loads(cities.read())

        # cities_json = [cities_json[0]]

        for city in cities_json:
            url = 'https://www.glassdoor.com/findPopularLocationAjax.htm?term={}&maxLocationsToReturn='
            
            yield scrapy.Request(
                url=url.format(city),
                callback=self.scrape_by_location_info,
                meta={'search_parameter': city}
            )

    def scrape_by_location_info(self, response):
        location_json = json.loads(response.body)
        selected_dicts = []
        for location in location_json:
            if ', VA' in location.get('label'):
                selected_dicts.append(location)
        for item in selected_dicts:
            url_template = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword=social%20worker&locT={}&locId={}'
            loc_t = item.get('locationType')
            loc_id = str(item.get('locationId'))
            url = url_template.format(loc_t, loc_id)
            
            yield scrapy.Request(
                url=url,
                callback=self.get_postings,
                meta=response.meta
            )

    page_index = 1
    def get_postings(self, response):
        # print('get postings')
        postings = response.css('li.react-job-listing > div:first-of-type > a::attr(href)').extract()
        if postings:
        # print(response.url)
            time.sleep(5)
            for posting in postings:
                url = 'https://www.glassdoor.com' + posting
                yield scrapy.Request(
                    url=url,
                    callback=self.get_data,
                    meta = response.meta
                )
        else:
            print('this is the end')
            return None
        # next_page_url = response.xpath(".//a[@data-test='pagination-next']/@href").extract_first()

        # if next_page_url:
            # url = 'https://www.glassdoor.com' + next_page_url
        self.page_index += 1
        next_page_template = 'https://www.glassdoor.com/Job/alexandria-social-worker-jobs-SRCH_IL.0,10_IC1130334_KO11,24_IP{}.htm?includeNoSalaryJobs=true'
        url = next_page_template.format(self.page_index)
        # print(url)

        yield scrapy.Request(
            url=url,
            callback=self.get_postings,
            meta=response.meta
        )

    def get_data(self, response):
        item = {}
        item['jobsite'] = 'glassdoor.com'
        item["job_title"] = self.get_xpath_value(response, ['//*[@id="JobView"]/div[1]/div[2]/div/div/div[2]/div/div[1]/div[2]/div/div/div[2]//text()', '//*[@id="JobView"]/div[1]/div[2]/div/div/div[2]/div/div[1]/div/div/div/div[2]/text()'])
        item['job_type'] = self.get_xpath_value(response, [".//div[@id='PageContent']//span[contains(text(),'Job Type')]/following-sibling::*[2]/text()"])
        item["city"] = self.get_value(response, 'h2.subtitle::text')
        item["search_parameter"] = response.meta.get('search_parameter')
        item["salary"] = self.get_salary(response)
        item['summary'] = self.get_summary(response)
        item["date_scraped"] = str(datetime.today())
        item["posting_details_url"] = response.url
        # print(response.url)
        json_items = self.grab_from_json(response)
        if json_items:
            for key, value in json_items.items():
                item[key] = value
        print(item.get('job_title'))
        yield self.write_to_json(item)

    def get_value(self, posting, selector_path):
        value = posting.css(selector_path).extract()
        if value:
            return ''.join(value).strip()
        return None

    def get_xpath_value(self, posting, selector_paths):
        for path in selector_paths:
            value = posting.xpath(path).extract_first()
            if value:
                return value
        return None

    def get_salary(self, response):
        salary =self.get_xpath_value(response, [".//div[contains(@class,'desc ')]/*[contains(text(),'$')]/text()"])
        if salary:
            return salary[5:]
        return None

    def grab_from_json(self, response):
        item = response.xpath(".//script[@type='application/ld+json']/text()").extract_first()
        try:
            posting_json = json.loads(item)
            posting_age = posting_json.get('datePosted')
            city = posting_json.get('jobLocation').get('address').get('addressLocality')
            company = posting_json.get('hiringOrganization').get('name')
            return {'posting_age': posting_age, 'city': city, 'company':company}
        except:
            return None

    def get_summary(self, response):
        return ' '.join(response.xpath(".//div[contains(@class,'desc')]//*[contains(text(),'icense')]/text()").extract())


    initial_posting = True
    def write_to_json(self, posting):
        if self.initial_posting:
            write_scraped_file = open('glassdoor_scraped_postings.json', 'w')
            write_scraped_file.write('[')
            write_scraped_file.write(str(json.dumps(posting)))
            write_scraped_file.write(']')
            self.initial_posting = False
            write_scraped_file.close()
        else:
            read_scraped_file = open('glassdoor_scraped_postings.json', 'r')
            existing_postings = json.loads(read_scraped_file.read())
            existing_postings.append(posting)
            read_scraped_file.close()
            write_scraped_file = open('glassdoor_scraped_postings.json', 'w')
            write_scraped_file.write(str(json.dumps(existing_postings)))
            write_scraped_file.close()

