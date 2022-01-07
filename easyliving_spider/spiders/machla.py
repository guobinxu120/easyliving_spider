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
    name = "machla"
    start_urls = ['https://machla.bh/']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//div[@class="wrapper"]/div[3]/div/div[2]/div//h1[@class="title"]/a')
        for p_cat in categorys:
            cat = p_cat.xpath('./@title').extract_first()
            url = p_cat.xpath('./@href').extract_first()
            yield Request(url, self.parse_subcat, meta={'cat':cat})
    def parse_subcat(self, response):
        sub_lis = response.xpath('//div[@class="section category-section"]/div/div')
        for sub_tag in sub_lis:
            url = sub_tag.xpath('.//h4[@class="title"]/a/@href').extract_first()
            sub_cat = sub_tag.xpath('.//h4[@class="title"]/a/text()').extract_first().split(')')[0].strip()
            yield Request (url, self.parse1, meta={'cat':response.meta['cat'], 'sub_cat':sub_cat})
    def parse1(self, response):
        total_url = response.xpath('//a[text()="View All"]/@href').extract_first()
        if total_url:
            yield Request(total_url, self.parse1, meta= response.meta)
        else:

            product_url = response.xpath('//div[@id="product"]//h4[@class="title"]/a/@href').extract()
            for url in product_url:
                yield Request(url, callback=self.parse2, meta=response.meta)

            # next_url = response.xpath('//a[@title="Next"]/@href').extract_first()
            # if next_url:
            #     yield Request(next_url, self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//div[@class="product-name"]/h1/text()').extract_first()
        img_url = response.xpath('//div[@class="zoomer"]/img/@src').extract_first()
        item['Brand'] = ''
        try:
            item['Product Code'] = response.xpath('//img[contains(@src,"barcode")]/@src').re('[\d]+')[0]
        except:
            item['Product Code'] = response.url.split('product_id=')[-1]
        item['Tags'] = ''
        price = response.xpath('//h4[@class="new special-price"]/b/text()').re('[\d.]+')
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








