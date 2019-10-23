import scrapy

from scrapyManga.items import MetaFileItem
from scrapyManga.spiders import CliSpider


class MangaHereSpider(CliSpider):
    name = "mangapark"
    base_site = "https://mangapark.net"

    start_urls = [""]

    custom_settings = {"HTTPCACHE_ENABLED": False}

    def parse_url(self, url):
        urls = url.split("/")
        if len(urls) < 5:
            self.logger.info("ERROR bad url " + url)
            return "", "", ""
        volume = urls[-3]
        chapter = urls[-2]
        number = urls[-1].zfill(4)
        return volume, chapter, number

    def parse_image(self, response):
        volume, chapter, number = self.parse_url(response.url)
        chapter = response.meta["number"]
        chapter_id = response.meta["current_id"]
        self.logger.debug("PARSING: %s %s %s", volume, chapter, number)
        script_urls = response.xpath("/html/body/script/text()").extract()
        url_data = self.extract_script_from_html(
            "".join(script_urls), "var _load_pages"
        )
        self.logger.debug("data %s", url_data)
        if url_data:
            image_url = url_data[0]["u"]
        else:
            self.logger.error("No data for %s", response.url)
            return
        title = response.meta["title"]
        file_path = "/".join(
            [self.name, title, str(chapter).zfill(4), number.zfill(4) + ".jpg"]
        )
        if image_url:  # There might be ad pages
            if "http" not in image_url:
                image_url = "https:" + image_url
            yield MetaFileItem(file_urls=[image_url], file_path=file_path, verbose=True)
        next_url = response.xpath('//a[text()="Next▶"]/@href').extract_first()

        if next_url and chapter_id in next_url:
            yield scrapy.Request(
                self.base_site + next_url, callback=self.parse_image, meta=response.meta
            )

    def create_url(self, title, chapter_id):
        return f"https://mangapark.net/manga/{title}/{chapter_id}/1"

    def parse_api(self, response):
        url_data = self.extract_script_from_html(response.text, "var _json_bok")
        for chapter_number, chapter_id_data in enumerate(url_data[0]["l"]):
            new_meta = response.meta
            chapter_id = chapter_id_data["l"]
            url = self.create_url(response.meta["title"], chapter_id)
            new_meta["current_id"] = chapter_id
            new_meta["number"] = chapter_number + 1
            yield scrapy.Request(url, callback=self.parse_image, meta=new_meta)

    def parse(self, response):
        title = response.url.split("/")[4]
        # yield scrapy.Request(response.url, callback=self.parse_image)
        current_chapter = response.url.split("/")[5]
        api_url = response.xpath(
            '//script[contains(@src, "/book-list/")]/@src'
        ).extract()
        meta = {"current_id": current_chapter, "title": title}
        yield scrapy.Request("https:" + api_url[0], callback=self.parse_api, meta=meta)
