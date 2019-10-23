# ScrapyManga

## Usage

`scrapy crawl SpiderName -a start_url=URL1,URL2`

or 

`python3 start.py crawl SpiderName` (More for debug)

## Accepted urls
* Only mangarock accept the serie `https://mangarock.com/manga/mrs-serie-1111` or the chapter `https://mangarock.com/manga/mrs-serie-1111/chapter/mrs-chapter-100`
* Others spiders will only take an url chapter

## Available spiders
* mangapark
* mangarock
* mangazuki.online

## Notes
* Output path is set in `settings.py` see **FILES_STORE**
* Default log level is `INFO`

## Bonus

`start.sh spiderName url1,url2`