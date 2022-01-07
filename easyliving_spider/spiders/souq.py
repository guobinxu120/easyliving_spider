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
    name = "souq"
    start_urls = ['https://uae.souq.com/kw-en/shop-all-categories/c/?ref=nav']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//div[@class="row shop-all-container"]/div')
        for i, p_cat in enumerate(categorys):
            if i == 0: continue
            cats = p_cat.xpath('./h3[@class="shop-all-title"]/text()').extract()
            sub_lis = p_cat.xpath('.//ul[@class="side-nav"]')
            for j, sub_tag in enumerate(sub_lis):
                cat = cats[j]
                subs = sub_tag.xpath('./li/a')
                for sub in subs:
                    url = sub.xpath('./@href').extract_first()
                    sub_cat = sub.xpath('./text()').extract_first()
                    if not url: continue
                    yield Request (url, self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):
        products = response.xpath('//div[@class="column column-block block-grid-large single-item"]//a[@class="itemLink block sPrimaryLink"]/@href').extract()
        for url in products:
            yield Request(url, callback=self.parse2, meta=response.meta)

        next_url = response.xpath('//li[@class="pagination-next goToPage"]/a/@href').extract_first()
        if next_url:
            yield Request(next_url, self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//div[@class="small-12 columns product-title"]/h1/text()').extract_first()
        img_url = response.xpath('//div[@class="img-bucket "]/img/@src').extract_first()
        if not img_url:
            img_url = response.xpath('//div[contains(@class,"img-bucket ")]/img/@src').extract_first()
        item['Brand'] = response.xpath('//div[@id="productTrackingParams"]/@data-brand-name').extract_first()
        item['Product Code'] = response.xpath('//div[@id="productTrackingParams"]/@data-ean').extract_first()
        item['Tags'] = ''
        item['Price'] = response.xpath('//div[@id="productTrackingParams"]/@data-price').extract_first()
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








