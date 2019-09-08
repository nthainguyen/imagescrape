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
        maps = json.loads(json_data)
        for map in maps:
            yield scrapy.Request('https://digitalcollections.nypl.org/items/' + map['item']['id'],\
                 callback= self.parse_item)

        next_page_url = response.css(".next_page::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_item(self, response):
    	if response.status == 404:
    		yield {
    			'src': response.url,
    			'links': 'Error 404 - This page does not exist'
    		}
    	else:
		    data_items = response.css('div#item-carousel::attr(data-items)').get()
		    if data_items:
		        original_link = response.css('div.original > a::attr(href)').get()
		        data = json.loads(data_items)
		        for i in data:
		            yield {
		            	'image_id': i['image_id'],
		            	'title': i['title'],
		            	'src': response.url,
		                'links': "https://images.nypl.org/index.php?id={0}&t=g&download=1".format(i['image_id'])
		            }
		    else:
		        data_item = response.css('div#bigimage > img::attr(data-item)').get()
		        data = json.loads(data_item)
		        yield {
		        	'image_id': data['image_id'],
		        	'title': data['title'],
		        	'src': response.url,
		            'links': "https://images.nypl.org/index.php?id={0}&t=g&download=1".format(data['image_id'])
		        }
