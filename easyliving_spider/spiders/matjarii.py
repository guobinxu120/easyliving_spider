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
    name = "matjarii"
    start_urls = ['https://matjarii.com/']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//main//li[@class="item level0  level-top parent"]')
        for p_cat in categorys:
            cat = p_cat.xpath('./a[@class="menu-link"]/span/text()').extract_first()
            sub_lis = p_cat.xpath('.//p[@class="groupdrop-title"]/a')
            for sub_tag in sub_lis:
                url = sub_tag.xpath('./@href').extract_first()
                sub_cat = sub_tag.xpath('./text()').extract_first()
                yield Request (url, self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):
        total_url = response.xpath('//li[@class="item product product-item"]//a[@class="product-item-link"]/@href').extract()
        for url in total_url:
            yield Request(url, callback=self.parse2, meta=response.meta)

        next_url = response.xpath('//a[@title="Next"]/@href').extract_first()
        if next_url:
            yield Request(next_url, self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
        img_url = json.loads('[' + response.body.split('"data": [')[-1].split('],')[0] +']')[0]['img']
        item['Brand'] = ''
        item['Product Code'] = response.xpath('//div[@itemprop="sku"]/text()').extract_first()
        item['Tags'] = ''
        item['Price'] = response.xpath('//span[@data-price-type="finalPrice"]/@data-price-amount').extract_first()
        # if price:
        #     item['Price'] = price[0]
        # else:
        #     item['Price'] = ''

        image_path = "./Images/{}/".format(self.name)

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        if 'png' in img_url.lower():
            extension = 'png'
        else:
            extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename
        download(img_url, image_path+filename)
        yield item








