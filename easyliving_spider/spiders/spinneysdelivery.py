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
    name = "spinneysdelivery"
    start_urls = ['http://www.spinneysdelivery.com/onlinedelivery/Default.aspx']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//td[@class="menuIcon"]')
        for i, p_cat in enumerate(categorys):
            cat = p_cat.xpath('.//table/tr/td/text()').extract()[-1]
            sub_lis = p_cat.xpath('./div/div[@class="smartMenu"]/ul/li/a')
            for j, sub_tag in enumerate(sub_lis):
                url = sub_tag.xpath('./@href').extract_first()
                sub_cat = sub_tag.xpath('./text()').extract_first()
                yield Request (response.urljoin(url), self.parse1, meta={'cat':cat, 'sub_cat':sub_cat})
                # yield Request('http://www.spinneysdelivery.com/onlinedelivery/ProductsListing.aspx?CatID=51', self.parse1, meta={'cat': cat, 'sub_cat': sub_cat})
                # break
            # break
    def parse1(self, response):
        products = response.xpath('//td[@class="productListing"]/ul/li')
        for product in products:

            item = OrderedDict()
            item['Category'] = response.meta['cat']
            item['Subcategory'] = response.meta['sub_cat']
            name = product.xpath('.//div[@class="promoTitle margBottom7"]/a/text()').extract_first()
            unit = name.strip().split(' ')[-1]
            unit_numbers = re.findall('[\d.,]+', unit)
            if len(unit_numbers) > 0:
                unit_number = unit_numbers[0]
                unit = unit.replace(unit_number, '')

            else:
                try:
                    unit_number = re.findall('[\d.,]+', name.strip().split(' ')[-2])[0]
                except:
                    unit_number = ''
            name = name.replace(unit_number+unit, '').replace(unit_number+' '+unit, '').strip()
            item['Product Name'] = name
            price = product.xpath('.//div[@class="promoPrice margBottom7"]/text()').extract_first()
            if '/' in price:
                try:
                    real_price = re.findall('[\d.,]+', price.split('/')[0])[0]
                    item['Price'] = real_price
                    item['Measurement'] = price.split('/')[-1].replace(re.findall('[\d.,]+', price.split('/')[-1])[0],'')
                    item['Measurement Value'] = re.findall('[\d.,]+', price.split('/')[-1])[0]
                except:
                    pass
            else:
                try:
                    real_price = re.findall('[\d.,]+', price)[0]
                    item['Price'] = real_price
                    item['Measurement'] = unit
                    item['Measurement Value'] = unit_number
                except:
                    pass

            img_url = product.xpath('.//td[@class="promoPicContainer"]//img/@src').extract_first()

            image_path = "./Images/{}/".format(self.name)

            if not os.path.exists(image_path):
                os.makedirs(image_path)

            if 'png' in img_url.lower():
                extension = 'png'
            else:
                extension = 'jpg'
            filename = item['Product Name'] + "." + extension
            item['Image'] = filename
            download(img_url, image_path + filename)
            yield item

        next_url = response.xpath('//a[@id="btnNext"]')
        if next_url:
            url = response.url
            VIEWSTATE = response.xpath('//input[@name="__VIEWSTATE"]/@value').extract_first()
            if not VIEWSTATE:
                VIEWSTATE = response.body.split('__VIEWSTATE|')[-1].split('|')[0]
            VIEWSTATEGENERATOR = response.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').extract_first()
            if not VIEWSTATEGENERATOR:
                VIEWSTATEGENERATOR = response.body.split('__VIEWSTATEGENERATOR|')[-1].split('|')[0]
            EVENTVALIDATION = response.xpath('//input[@name="__EVENTVALIDATION"]/@value').extract_first()
            if not EVENTVALIDATION:
                EVENTVALIDATION = response.body.split('__EVENTVALIDATION|')[-1].split('|')[0]
            fromdata = {
                'scrptmgr': 'updtpnlList|btnNext',
                'header$txtKeyword1': '',
                'header$ddlTag': '0',
                'ddlFilter': 'Name',
                'txtfocus':'',
                'footer$txtEmail': 'Enter your email address',
                '__LASTFOCUS': '',
                '__EVENTTARGET': 'btnNext',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': VIEWSTATE,
                '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                '__EVENTVALIDATION': EVENTVALIDATION,
                '__ASYNCPOST': 'true'
            }

            yield FormRequest(url, self.parse1, formdata=fromdata, meta=response.meta)











