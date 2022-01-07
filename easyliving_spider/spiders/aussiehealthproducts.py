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
    name = "aussiehealthproducts"
    start_urls = ['https://www.aussiehealthproducts.com.au']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//li[@class="mickey"]')
        for i, p_cat in enumerate(categorys):
            cat = p_cat.xpath('./a/text()').extract_first()
            sub_lis = p_cat.xpath('./div/div[@class="dropdown-cats"][1]/ul/li/a')
            for j, sub_tag in enumerate(sub_lis):
                # if j == 0: continue
                url = sub_tag.xpath('./@href').extract_first()
                sub_cat = sub_tag.xpath('./text()').extract_first()
                if not url: continue
                yield Request (response.urljoin(url), self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):
        products = response.xpath('//div[@class="product"]/a/@href').extract()
        for product in products:
            yield Request(response.urljoin(product), self.parse2, meta=response.meta)
        next_url = response.xpath('//div[@id="pages"]//a[contains(text(), "Next")]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//title/text()').extract_first()
        img_url = response.xpath('//div[@id="product-photo"]/div/img/@src').extract_first()
        item['Brand'] = response.xpath('//h1/span[@class="fn"]/span/text()').extract_first()
        item['Product Code'] = response.xpath('//p[@class="identifier"]/span[@class="value"]/text()').extract_first()
        image_path = "./Images/{}/".format(self.name)

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if 'png' in img_url.lower():
            extension = 'png'
        else:
            extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename
        download(img_url, image_path + filename)
        yield item













