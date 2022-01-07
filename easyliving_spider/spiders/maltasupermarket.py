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
    name = "maltasupermarket"
    start_urls = ['http://www.maltasupermarket.com']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//div[@class="container"]//a[@href="#"]/parent::li')
        for p_cat in categorys:
            cat = p_cat.xpath('./a/text()').extract_first()
            sub_cats = p_cat.xpath('./ul/li/a')
            for sub in sub_cats:
                url = sub.xpath('./@href').extract_first()
                sub_cat = sub.xpath('./text()').extract_first()

                yield Request(response.urljoin(url), self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})

    def parse1(self, response):
        products = response.xpath('//div[@class="tab_content"]/ul/li[@class="itemli"]')
        for product in products:
            item = OrderedDict()
            item['Category'] = response.meta['cat']
            item['Subcategory'] = response.meta['sub_cat']
            item['Product Name'] = product.xpath('./div[@class="wrap-itemdescription"]/text()').extract_first()
            img_url = product.xpath('./div[@class="imgs"]/img/@src').extract_first().replace('/products/main/', '/items/enl/')
            item['Product Code'] = product.xpath('./div[@class="imgs"]/@data-itemcode').extract_first()
            item['Tags'] = ''
            price = product.xpath('./div[@class="add-product"]/strong/text()').re('[\d.]+')
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
            download(response.urljoin(img_url), image_path+filename)
            yield item








