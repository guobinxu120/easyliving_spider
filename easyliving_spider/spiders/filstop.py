# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
from urlparse import urlparse
import sys
import re, os, requests, urllib
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time
from shutil import copyfile
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
    name = "filstop"
    start_urls = ['https://www.filstop.com/']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//ul[@class="main-menu-top"]/li')

        for i, p_cat in enumerate(categorys):
            if i == 0: continue
            cat = p_cat.xpath('./a/text()').extract_first()
            subs = p_cat.xpath('.//a[@class="menu-link second-level"]')
            for sub in subs:
                url = sub.xpath('./@href').extract_first()
                sub_cat = sub.xpath('./text()').extract_first()
                if not url: continue
                yield Request (response.urljoin(url), self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):
        products = response.xpath('//table[@summary="Products list"]//td/div/div/a/@href').extract()
        for product in products:
            yield Request(response.urljoin(product), self.parse2, meta=response.meta)

        next_url = response.xpath('//a[@class="right-arrow"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//h1[@class="producttitle"]/text()').extract_first()
        img_url = response.xpath('//div[@class="image-box"]/img/@src').extract_first()
        item['Brand'] = response.xpath('//th[text()="Brand"]/parent::tr/td/a/text()').extract_first()
        item['Product Code'] = response.xpath('.//span[@id="product_code"]/text()').extract_first()
        item['Tags'] = ''
        # item['Price'] = product.xpath('.//span[@class="new_price"]/text()').extract_first()
        image_path = "./Images/{}/".format(self.name)

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if 'png' in img_url.lower():
            extension = 'png'
        else:
            extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename
        download(response.urljoin(img_url.replace('size2', 'original')), image_path + filename)
        yield item













