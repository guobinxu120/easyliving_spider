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
    name = "easyliving"
    start_urls = ['http://www.easyliving.ae']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # myFile1 = open('countries.csv', 'wb')
    # with myFile1:
    #     with open('easyliving.csv') as myFile:
    #         reader = csv.DictReader(myFile)
    #         fieldes = reader.fieldnames
    #         writer = csv.DictWriter(myFile1, fieldnames=fieldes)
    #         writer.writeheader()
    #         for row in reader:
    #             row['Image'] = row['Product Code'].replace(' ', '_') + '.jpg'
    #             writer.writerow(row)



    def parse(self, response):
        categorys = response.xpath('//ul[@class="box-category treeview-list treeview"]/li')
        for p_cat in categorys:
            cat = p_cat.xpath('./a/text()').extract_first()
            sub_lis = p_cat.xpath('./ul/li')
            for sub_tag in sub_lis:
                url = sub_tag.xpath('./a/@href').extract_first()
                sub_cat = sub_tag.xpath('./a/text()').extract_first()
                yield Request (url, self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
    def parse1(self, response):

        product_url = response.xpath('//ul[@class="product-list"]/li//div[@class="name"]/a/@href').extract()
        for url in product_url:
            yield Request(url, callback=self.parse2, meta=response.meta)

        next_url = response.xpath('//div[@class="pagination"]//a[text()=">"]/@href').extract_first()
        if next_url:
            yield Request(next_url, self.parse1, meta=response.meta)

    def parse2(self, response):
        item = OrderedDict()
        item['Category'] = response.meta['cat']
        item['Subcategory'] = response.meta['sub_cat']
        item['Product Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        img_url = response.xpath('//span[@class="image"]/img/@data-zoom-image').extract_first()
        item['Brand'] = response.xpath('//meta[@itemprop="manufacturer"]/@content').extract_first()
        item['Product Code'] = response.xpath('//meta[@itemprop="model"]/@content').extract_first()
        extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename

        item['Tags'] = ', '.join(response.xpath('//div[@class="tags product-info-tags"]/a/text()').extract())
        item['Price'] = response.xpath('//meta[@itemprop="price"]/@content').extract_first()
        if item['Price']:
            item['Price'] = item['Price'].replace('AED', '').strip()

        image_path = "./Images/{}/".self.name

        if not os.path.exists(image_path):
            os.makedirs(image_path)



        download(img_url, image_path+filename)
        yield item








