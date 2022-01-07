# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
from urlparse import urlparse
import sys
import re, os, requests, urllib
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time
from scrapy.conf import settings
import json, re, csv,zipfile


def download(url, destfilename):
	if not os.path.exists(destfilename):
		print "Downloading from {} to {}...".format(url, destfilename)
		try:
			r = requests.get(url, stream=True)
			with open(destfilename, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024):
					if chunk:
						f.write(chunk)
						f.flush()
		except:
			print "Error downloading file."

class AngelSpider(Spider):
    name = "esajee"

    custom_settings = {
        'DOWNLOAD_DELAY': 2
    }

    start_urls = ['https://www.esajee.com/']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')



    def parse(self, response):
        categorys = response.xpath('//ul[@class="megamenu level0"]/li[contains(@class, "haschild")]')
        for p_cat in categorys:
            cat = p_cat.xpath('./a/@title').extract_first()
            sub_lis = p_cat.xpath('.//div[@class="group-title"]')
            for sub_tag in sub_lis:
                url = sub_tag.xpath('./a/@href').extract_first()
                sub_cat = sub_tag.xpath('./a/@title').extract_first()
                yield Request (url, self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):

        product_url = response.xpath('//ul[contains(@class,"products-grid")]/li//h5[@class="product-name"]/a/@href').extract()
        for url in product_url:
            yield Request(url, callback=self.parse2, meta=response.meta)

        next_url = response.xpath('//a[@title="Next"]/@href').extract_first()
        if next_url:
            yield Request(next_url, self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        img_url = response.xpath('//p[@class="product-image product-image-zoom"]/img/@src').extract_first()
        item['Brand'] = response.xpath('//meta[@itemprop="brand"]/@content').extract_first()
        item['Product Code'] = response.xpath('//meta[@itemprop="sku"]/@content').extract_first()
        item['Tags'] = ', '.join(response.xpath('//div[@class="tags product-info-tags"]/a/text()').extract())
        price = response.xpath('//span[@class="regular-price"]/text()').re('[\d.]+')
        if price:
            item['Price'] = price[0]
        else:
            item['Price'] = ''

        image_path = "./Images/{}/".format(self.name)

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename
        download(img_url, image_path+filename)
        yield item








