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
    name = "greens"
    start_urls = ['http://www.greens.com.mt']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//div[@id="imageMenuButtons"]/div/a')
        for i, p_cat in enumerate(categorys):
            cat = p_cat.xpath('./span/text()').extract_first()
            url = p_cat.xpath('./@href').extract_first()
            if not url: continue
            yield Request(response.urljoin(url), self.parse_sub, meta={'cat':cat}, )
            # break

    def parse_sub(self, response):
        options = response.xpath('//select[@id="KrystalCMSCore_ctl09_lstCatalog"]/option')
        for j, sub_tag in enumerate(options):
            sub_cat = sub_tag.xpath('./text()').extract_first()
            value = sub_tag.xpath('./@value').extract_first()
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            formdata={
                'KrystalCMSCore$ctl09$lstCatalog': value,
                '__EVENTTARGET': 'KrystalCMSCore$ctl09$lstCatalog',
                '__VIEWSTATE': response.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first(),
                '__VIEWSTATEGENERATOR' : response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
                '__EVENTVALIDATION': response.xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
            }

            yield FormRequest(response.url, formdata=formdata, callback=self.parse1, dont_filter=True, meta={'cat':response.meta['cat'], 'sub_cat':sub_cat, 'index': 1})
            # break

    def parse1(self, response):
        products = response.xpath('//div[@class="ProductBox"]')
        for product in products:
            item = OrderedDict()
            item['Category'] = response.meta['cat']
            item['Subcategory'] = response.meta['sub_cat']
            item['Product Name'] = product.xpath('./div[@class="ProductBoxDescription"]/a/text()').extract_first()
            img_url = product.xpath('./div[@class="ProductBoxImage"]/a/img/@alt').extract_first()

            item['Brand'] = ''
            item['Product Code'] = product.xpath('./a/@id').extract_first()
            item['Tags'] = ''
            # item['Price'] = product.xpath('//span[@class="ProductBoxPriceActual"]/text()').extract_first().replace('€', '')

            # yield item
            url = product.xpath('./div[@class="ProductBoxDescription"]/a/@href').extract_first()
            yield Request(response.urljoin(url), callback=self.parse2, meta={'item':item, 'img_url':img_url})

        next_url = response.xpath('//div[@class="CellProductPageManagement"]/a/text()').extract()
        index = response.meta['index']

        if next_url and index < int(next_url[-1]):
            index +=1
            next_url = response.url.split('?page=')[0] + '?page={}'.format(index)
            yield Request(next_url, self.parse1, meta={'cat':response.meta['cat'], 'sub_cat':response.meta['sub_cat'], 'index': index})

    def parse2(self, response):
        item = response.meta['item']
        try:
            code = response.xpath('//div[contains(text(),"Item Code:")]/text()').extract_first().split(':')[-1].strip()
            item['Product Code'] = code
        except:
            pass
        item['Brand'] = ''.join(response.xpath('//h2[text()="Brand"]/parent::td/text()').extract()).replace('-', '').strip()

        image_path = "./Images/{}/".format(self.name)

        if not os.path.exists(image_path):
            os.makedirs(image_path)
        img_url = response.meta['img_url']
        if 'png' in img_url.lower():
            extension = 'png'
        else:
            extension = 'jpg'
        filename = item['Product Code'].replace(' ', '_') + "." + extension
        item['Image'] = filename
        download(response.urljoin(img_url), image_path + filename)
        yield item








