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
    name = "fishpond"
    start_urls = ['https://www.fishpond.co.nz/']

    use_selenium = False
    count = 0
    total = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def parse(self, response):
        categorys = response.xpath('//div[@id="menu-mobile"]//li[@class="main-menu__categories-dropdown-item"]/a')
        for i, p_cat in enumerate(categorys):
            cats = p_cat.xpath('./text()').extract_first()
            url = p_cat.xpath('./@href').extract_first()
            yield Request(response.urljoin(url), self.pase_subcat, meta = {'cat': cats})
    def pase_subcat(self, response):

        sub_lis = json.loads(response.body.split('id="categories">')[-1].split('</script>')[0])
        for sub_tag in sub_lis:
            url = sub_tag['name']
            sub_cat = sub_tag['url']
            yield Request (response.urljoin(sub_cat), self.parse1, meta={'cat':response.meta['cat'], 'sub_cat':url})
    def parse1(self, response):
        try:
            products = json.loads(response.body.split('id="browse">')[-1].split('</script>')[0])
            for product in products:
                item = OrderedDict()
                item['Category'] = response.meta['cat']
                item['Subcategory'] = response.meta['sub_cat']
                item['Product Name'] = product['name']
                item['Product Code'] = product['gtin13']
                img_url = product['image']
                item['Brand'] = ''
                item['Tags'] = ''
                # item['Price'] = product.xpath('.//span[@class="new_price"]/text()').extract_first()
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

            states = json.loads(response.body.split('id="state">')[-1].split('</script>')[0])
            current = int(states['currentPage'])
            totoal = int(states['totalPages'])
            if current < totoal:
                url = response.url.split('?page=')[0]+'?page={}'.format(current+1)

                yield Request(url, self.parse1, meta=response.meta)
        except:
            pass











