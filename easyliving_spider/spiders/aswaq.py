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
	name = "aswaq"
	start_urls = ['https://www.aswaq.com/en/']

	use_selenium = False
	count = 0
	total = 0
	pageIndex = 1
	reload(sys)
	sys.setdefaultencoding('utf-8')

	def parse(self, response):
		categorys = response.xpath('//ul[@class="dropdown-menu"]/div/div[@class="row"]/div')
		for i, p_cat in enumerate(categorys):
			cats = p_cat.xpath('./a/h5/text()').extract()
			sub_lis = p_cat.xpath('./ul')
			for j, sub_tag in enumerate(sub_lis):
				if j > len(cats)-1 : continue
				cat = cats[j]
				subs = sub_tag.xpath('./li/a')
				for sub in subs:
					url = sub.xpath('./@href').extract_first()
					sub_cat = sub.xpath('./text()').extract_first()
					if not url: continue
					yield Request (url, self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
	def parse1(self, response):
		products = response.xpath('//div[@class="slide"]')
		for product in products:
			item = OrderedDict()
			item['Category'] = response.meta['cat']
			item['Subcategory'] = response.meta['sub_cat']
			item['Product Name'] = product.xpath('.//a[@class="product-title"]/@title').extract_first().strip()
			img_url = product.xpath('.//img[@alt="featured-product-img"]/@data-src').extract_first()
			item['Brand'] = product.xpath('.//div[@id="productTrackingParams"]/@data-brand-name').extract_first()
			item['Product Code'] = product.xpath('.//li[@class="masking_addcart"]/a/@data-product-upc').extract_first()
			item['Tags'] = ''
			item['Price'] = product.xpath('.//span[@class="new_price"]/text()').extract_first()
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

		next_url = response.xpath('//li[@class="next"]/form')
		if next_url:
			url = response.xpath('//li[@class="next"]/form/@action').extract_first()
			page = response.xpath('//li[@class="next"]/form/input[@name="page"]/@value').extract_first()
			url = response.url.split('?')[0]+url+'page={}'.format(page)
			yield Request(url, self.parse1, meta=response.meta)











