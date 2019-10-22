import json
import string
from os import path

import scrapy
import re
from scrapyManga.items import MetaFileItem
from scrapyManga.spiders import CliSpider


class MangaReaderSpider(CliSpider):
    name = "mangazuki"
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    start_urls = [""]

    def extract_from_url(self, url):
        split_url = [i for i in filter(None, url.split("/"))]
        chapter = split_url[-1]
        name = split_url[-2]
        return name, chapter

    def parse_chapter(self, response):
        images = response.xpath('//img[starts-with(@id, "image-")]/@src')
        meta = response.meta
        for image in images:
            image_url = image.extract().strip()
            name = meta["name"]
            chapter = meta["chapter"]
            image_name = image_url.split("/")[-1].zfill(3)
            image_path = self.zfill_integer(path.join(name, chapter, image_name))
            yield MetaFileItem(
                file_urls=[image_url], file_path=image_path, verbose=True
            )

    def parse(self, response):
        all_chapters = response.xpath(
            '//select[@class="selectpicker single-chapter-select"]//@data-redirect'
        )
        # To parse current chapter
        self.parse_chapter(response)
        for url_chapter in all_chapters:
            clean_url = url_chapter.extract()
            name, chapter = self.extract_from_url(clean_url)
            meta = {"name": name, "chapter": chapter}
            yield scrapy.Request(
                url=clean_url, callback=self.parse_chapter, meta=meta, dont_filter=True
            )
