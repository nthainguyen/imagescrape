import scrapy
import json
import wget
import requests
class Crawler(scrapy.Spider):
    name = "spiderone"
    start_urls = [
        'https://digitalcollections.nypl.org/search/index?filters%5BphysicalLocation_mtxt_s%5D%5B%5D=Map+Division&format=html&keywords=&per_page=250&page=1',
    ]

    def parse(self, response):
        pattern = r'\bvar\s+search_results\s*=\s*(\[.*?\])\s*;\s*\n'
        json_data = response.css('script::text').re_first(pattern)
        print(json_data)
        maps = json.loads(json_data)
        for map in maps:
            yield scrapy.Request('https://digitalcollections.nypl.org/items/' + map['item']['id'],\
                 callback= self.parse_item)

        next_page_url = response.css(".next_page::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_item(self, response):
        data_items = response.css('div.carousel-widget::attr(data_items)').get()
        if data_items:
            sub_imgs = json.loads(data_items)
            for img in sub_imgs:
                yield img['high_res_link']
        else:
            original = response.css('div.original > a::attr(href)').get()
            wget.download(original)
            yield {
                'id': original
            }