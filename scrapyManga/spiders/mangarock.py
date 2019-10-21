import json
import string

import scrapy
import re
from metascrapy.items import MetaFileItem
from metascrapy.spiders import CliSpider


class MangaReaderSpider(CliSpider):
    name = "mangarock"
    query_version = "401"
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    start_urls = [
        "https://mangarock.com/manga/mrs-serie-100050716/chapter/mrs-chapter-100050777"
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            "metascrapy.metaPipeline.MetaFilePipeline": 1,
        },
        'DOWNLOAD_DELAY': 0.1
    }

    def create_url_series(self, series_oid):
        return f"https://api.mangarockhd.com/query/web{self.query_version}/info?oid={series_oid}&last=0"

    def create_url_chapter(self, chapter_oid):
        return f"https://api.mangarockhd.com/query/web{self.query_version}/pages?oid={chapter_oid}"

    def parse_chapter(self, response):
        data_series = json.loads(response.text)
        mri_images = data_series["data"]
        chapter = response.meta["number"]
        series_name = response.meta["name"]
        count = 0
        for mri_image in mri_images:
            file_path = "/".join([self.name,
                                  series_name,
                                  "Chapter " + str(chapter).zfill(3),
                                  str(count).zfill(3) + ".mri"])
            count += 1
            yield MetaFileItem(file_urls=[mri_image], file_path=file_path, verbose=True)

    def parse_series(self, response):
        start_chapter = response.meta['start']
        data_series = json.loads(response.text)
        chapters = data_series["data"]["chapters"]
        series_name = data_series["data"]["name"]
        series_name_clean = ''.join(c for c in series_name if c in self.valid_chars)
        # If chapter if first we take everything
        found = start_chapter == 'first'
        for chapter in chapters:
            oid = chapter["oid"]
            num = chapter["order"] + 1
            if found or oid == start_chapter:
                found = True
                url_chapter = self.create_url_chapter(oid)
                yield scrapy.Request(url=url_chapter, callback=self.parse_chapter, meta={"number": num,
                                                                                         "name": series_name_clean})
        if not found:
            self.logger.warn("Nothing found for " + response.url)

    def parse(self, response):
        if "/chapter/" not in response.url:
            new_url = response.url + '/chapter/first'
            yield scrapy.Request(url=new_url, callback=self.parse)
        else:
            self.logger.info("MAIN CHAPTER %s", response.url)
            series_id, chapter_id = re.match(r"https://mangarock.com/manga/(.*)/chapter/(.*)/?", response.url).groups()

            series_url = self.create_url_series(series_id)
            yield scrapy.Request(url=series_url, callback=self.parse_series, meta={'start': chapter_id})
