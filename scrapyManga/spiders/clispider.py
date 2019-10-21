import json
import re

import scrapy


class CliSpider(scrapy.Spider):

    def start_requests(self):
        try:
            self.start_urls = self.start_url.split(",")
        except AttributeError:
            pass
        for url in self.start_urls:
            self.logger.info("Start URL %s", url)
            yield scrapy.Request(url=url, callback=self.parse)

    def extract_script_from_html(self, html_str, variable_name):

        if variable_name in html_str:
            regex_result = re.search(variable_name + r" += +(\[.*\])", html_str)
            return json.loads(regex_result[1])
        return []

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))
