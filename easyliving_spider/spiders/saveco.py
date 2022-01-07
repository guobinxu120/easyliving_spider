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
    name = "saveco"
    start_urls = ['https://shop.saveco.com/']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//a[text()="Departments"]/parent::li//div[@class="box"]')
        for p_cat in categorys:
            cat = p_cat.xpath('./div[@class="title"]/strong/a/text()').extract_first()

            sub_lis = p_cat.xpath('//ul[@class="subcategories"]/li/a')
            for sub_tag in sub_lis:
                url = sub_tag.xpath('./@href').extract_first()
                sub_cat = sub_tag.xpath('./@title').extract_first()
                yield Request (response.urljoin(url), self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):
        total_url = response.xpath('//a[text()="View All"]/@href').extract_first()
        if total_url:
            yield Request(total_url, self.parse1, meta= response.meta)
        else:

            product_url = response.xpath('//div[@class="item-box"]//h2[@class="product-title"]/a/@href').extract()
            for url in product_url:
                yield Request(response.urljoin(url), callback=self.parse2, meta=response.meta)

            next_url = response.xpath('//li[@class="next-page"]/a/@href').extract_first()
            if next_url:
                yield Request(response.urljoin(next_url), self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first().strip()
        img_url = response.xpath('//a[@data-gallery="lightbox-pd"]/@href').extract_first()
        item['Brand'] = ''
        item['Product Code'] = response.xpath('//span[@itemprop="sku"]/text()').extract_first()

        item['Tags'] = ''
        price = response.xpath('//span[@itemprop="price"]/text()').re('[\d.]+')
        if price:
            item['Price'] = price[-1]
        else:
            item['Price'] = ''

        image_path = "./Images/{}/".format(self.name)

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if 'png' in img_url.lower():
            extension = 'png'
        elif 'jpeg' in img_url.lower():
            extension = 'jpeg'
        else:
            extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename
        download(response.urljoin(img_url), image_path+filename)
        yield item








