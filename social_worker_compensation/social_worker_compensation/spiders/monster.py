import scrapy
from datetime import datetime, timedelta
import json
import time
import bz2

class MonsterSpider(scrapy.Spider):
    name = 'monster'
    allowed_domains = ['monster.com']
    start_urls = ['http://monster.com/']

    def parse(self, response):
        # 1240 zipcodes in Virginia
        #  88 counties in Virginia
        counties = open('virginia_counties.json', 'r')
        counties_json = json.loads(counties.read())
        for county in counties_json:
            county = county.replace(' ', '-')
            url = 'https://www.monster.com/jobs/search/?q=social-worker&where={}__2C-Va&intcid=skr_navigation_nhpso_searchMain'
            url = url.format(county)
            yield scrapy.Request(
                url=url,
                callback=self.get_postings,
                meta={'search_parameter': county}
            )

        # county = counties_json[0].replace(' ','-')
        # url = 'https://www.monster.com/jobs/search/?q=social-worker&where={}__2C-Va&intcid=skr_navigation_nhpso_searchMain'
        # url = url.format(county)
        # yield scrapy.Request(
        #     url=url,
        #     callback=self.get_postings,
        #     meta={'search_parameter': county}
        # )



    def get_postings(self, response):
        posting_cards = response.css('section.card-content')
        for card in posting_cards:
            if card.css('*::attr(data-ssr)'):
                # eliminates promoted jobs not from search parameters
                continue
            url = card.css('h2.title > a::attr(href)').extract_first()
            if not url:
                continue
            yield scrapy.Request(
                url=url,
                callback=self.get_data,
                meta=response.meta
        )

    def get_data(self, response):
        item = {}
        item['jobsite'] = 'monster.com'
        item["posting_details_url"] = response.url
        item["job_title"] = self.get_value(response, 'h1.title ::text')
        item["company"] = self.get_company(response)
        item["city"] = self.get_value(response, 'h2.subtitle::text')
        item["search_parameter"] = response.meta.get('search_parameter')
        item["job_type"] = "None"
        item["salary"] = 'None'
        item['summary'] = self.get_summary(response)
        item["posting_age"] = self.get_posting_age(response)
        item["date_scraped"] = str(datetime.today())
        # scraped_postings.append(item)
        # print(item)
        yield self.write_to_json(item)


    def get_value(self, posting, selector_path):
        value = posting.css(selector_path).extract()
        if value:
            return ''.join(value).strip()
        return None


    def get_company(self, response):
        company = response.css('h1.title ::text').extract_first()
        try:
            _, company = company.split('at ')
        except:
            _, company = company.split('from ')
            # print(response.url)
        return company.strip()
    
    def get_summary(self, posting):
        summary = posting.xpath(".//div[@class='details-content is-preformated']//*[contains(text(),'license')]/text()").extract()
        for item in summary:
            if '\xa0' in item:
                item = item.replace(u'\xa0', u' ')
            if '•    ' in item:
                item = item.replace('•    ', '\n')
        return '\n'.join(summary)

    def get_posting_age(self, posting):
        relative_date = posting.xpath(".//dt[contains(text(),'Posted')]/following-sibling::*/text()").extract_first()
        # print(date_posted)
        relative_date = relative_date.split()[0]
        try:
            if '+' in relative_date:
                relative_date = relative_date.replace('+', '')
            if 'Today' in relative_date:
                relative_date = 0
            time_code = datetime.today() - timedelta(days=int(relative_date))
            posting_date, _ = str(time_code).split()
            return posting_date
        except:
            return relative_date



    initial_posting = True

    def write_to_json(self, posting):
        # write_scraped_file = open('monster_scraped_postings.json', 'w')
        # read_scraped_file = open('monster_scraped_postings.json', 'r')
        # append_scraped_file = open('monster_scraped_postings.json','a')


        # try:
        #     json_file = read_scraped_file.read()
        #     print(json_file)
        #     if '][' in json_file:
        #         json_file.replace('][', ',')
        #     if "'" in json_file:
        #         json_file.replace("'", '"')
        #     print(type(json_file))
        #     json_file = json.loads(json_file)
        # except:
            # print(type([posting]))
            # print('exception')
            # posting_list = []
            # posting_list.append(posting)
            # print(posting_list)
            # stringed_posting_dict = str([posting])
            # stringed_posting_dict.replace("'", '"')

            # print(json.loads(stringed_posting_dict))
            # write_scraped_file.write(str(json.dumps(posting)))
        if self.initial_posting:
            write_scraped_file = open('monster_scraped_postings.json', 'w')
            write_scraped_file.write('[')
            write_scraped_file.write(str(json.dumps(posting)))
            write_scraped_file.write(']')
            self.initial_posting = False
            write_scraped_file.close()
        else:
            read_scraped_file = open('monster_scraped_postings.json', 'r')
            existing_postings = json.loads(read_scraped_file.read())
            existing_postings.append(posting)
            read_scraped_file.close()
            write_scraped_file = open('monster_scraped_postings.json', 'w')
            write_scraped_file.write(str(json.dumps(existing_postings)))
            write_scraped_file.close()

