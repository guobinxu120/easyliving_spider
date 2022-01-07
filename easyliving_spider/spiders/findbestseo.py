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
    name = "findbestseo"
    start_urls = ['https://findbestseo.com/directory/all']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//div[@class="directory-main-content-right"]/h2/a/@href').extract()
        for i, p_cat in enumerate(categorys):
            yield Request (response.urljoin(p_cat), self.parse1)

        next_url = response.xpath('//a[@title="Go to next page"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), self.parse, meta=response.meta)
    def parse1(self, response):

        item = OrderedDict()
        item['Domain Company'] = response.xpath('//p[@class="sidebar_website"]/a/text()').extract_first()
        item['Agency Name'] = response.xpath('//div[@class="striped-title"]/h2/text()').extract_first()
        item['Agency Phone'] = ''.join(response.xpath('//p[@class="sidebar_phone"]/text()').extract())
        item['Agency Logo'] = response.xpath('//a[@class="company-represent-logo"]/img/@src').extract_first()

        item['Agency Description'] = '\n'.join(response.xpath('//div[@class="field-item even"]/p/text()').extract())
        address = response.xpath('//p[@class="sidebar_address"]/text()').extract_first()
        if address:
            try:
                item['Address'] = address
                item['City'] = item['Address'].split(',')[1]
                item['State'] = item['Address'].split(',')[2]
            except:
                pass
        else:
            item['Address'] = ''
            item['City'] = ''
            item['State'] = ''
        item['Score'] = response.xpath('//div[@class="company-represent-score"]/h2/text()').extract_first()
        item['Facebook Link'] = response.xpath('//li[contains(@class,"field-item service-facebook")]/a/@href').extract_first()
        item['Twitter Link'] = response.xpath(
            '//li[contains(@class,"field-item service-twitter")]/a/@href').extract_first()
        item['Google Link'] = response.xpath(
            '//li[contains(@class,"field-item service-googleplus")]/a/@href').extract_first()
        item['Instagram Link'] = response.xpath(
            '//li[contains(@class,"field-item service-linkedin")]/a/@href').extract_first()
        item['Pinterest Link'] = response.xpath(
            '//li[contains(@class,"field-item service-pinterest")]/a/@href').extract_first()
        item['Youtube Link'] = response.xpath(
            '//li[contains(@class,"field-item service-youtube")]/a/@href').extract_first()
        item['Vimeo Link'] = response.xpath(
            '//li[contains(@class,"field-item service-vimeo")]/a/@href').extract_first()

        item['Services'] = ','.join(response.xpath('//div[@class="company-content-services"]/a/text()').extract())

        yield item













