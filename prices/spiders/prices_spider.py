import requests
import re
import urlparse
from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Item
from scrapy.linkextractors import LinkExtractor


class PricesSpider(CrawlSpider):
    name = "prices"
    allowed_domains = ['mysmartprice.com']
    start_urls =['http://www.mysmartprice.com']
    rules = (
        Rule(LinkExtractor(allow=('msp\d+')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('.*')))
    )


    def get_store_url(self, url):
        resp = requests.get(url)
        parsed_html = BeautifulSoup(resp.text)
        a = parsed_html.find('a', attrs={'class': 'store-link'})
        parsed_url = urlparse.urlparse(a['href'])
        store_url = urlparse.parse_qs(parsed_url.query)
        if 'url' in store_url:
            return store_url['url'][0]
        return a['href']


    def parse_item(self, response):
        # Store info
        prices = response.xpath("//span[@class='prc-grid__prc-val']/text()").extract()
        shipping = response.xpath("//div[@class='prc-grid__shpng']/span/text()").extract()
        delivery = response.xpath("//div[@class='prc-grid__clmn-2']/div[contains(@class, 'js-str-dlvry')]/text()").extract()
        emi = response.xpath("//div[@class='prc-grid__clmn-2']/div[contains(@class, 'js-str-emi')]/span/text()").extract()
        store_redirect_urls = response.xpath("//div[@class='prc-grid__clmn-4']/div/@data-url").extract()
        parsed_urls = map(lambda x: urlparse.urlparse(x), store_redirect_urls)
        if not parsed_urls:
            return {}
        stores = map(lambda x: urlparse.parse_qs(x.query)['store'][0], parsed_urls)
        store_urls = map(lambda x: self.get_store_url(x), store_redirect_urls)
        specs_key = response.xpath("//table[@class='tchncl-spcftn__tbl']//td[@class='tchncl-spcftn__item-key']/text()").extract()
        specs_value = response.xpath("//table[@class='tchncl-spcftn__tbl']//td[@class='tchncl-spcftn__item-val']/text()").extract()

        # MySmartPrice Product info
        product_category = urlparse.parse_qs(parsed_urls[0].query)['category'][0]
        name = response.xpath("//div[@class='prdct-dtl__rght']/h1[@itemprop='name']/text()").extract()[0].strip()
        sub_name = response.xpath("//div[@class='prdct-dtl__rght']/span/text()").extract()
        if sub_name:
            name += " " + sub_name[0].strip()
        # Create JSON object
        product = {}
        product['name'] = name
        product['category'] = product_category
        product['url'] = response.url
        product['stores'] = {}
        for i in range(len(stores)):
            product['stores'][stores[i]] = {'price': prices[i].strip().strip(u'\u20b9'),
                                            'shipping': shipping[i].strip(),
                                            'delivery': delivery[i].strip() if len(delivery) > i else 'Out of stock',
                                            'emi': emi[i].strip() if len(emi) > i else '',
                                            'url': store_urls[i]}
        product['specs'] = {}
        for i in range(len(specs_key)):
            product['specs'][specs_key[i]] = specs_value[i]

        return product
