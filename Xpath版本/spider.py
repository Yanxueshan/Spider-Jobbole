import requests
import re
import time
import os
import pymysql
from lxml import etree

__author__ = 'Yan'
__date__ = '2019/3/24 15:52'


class Fetch:
    def __init__(self, urls):
        self.connect = pymysql.connect(host='localhost', user='root', password='root', db='jobbole', charset='utf8')
        self.cursor = self.connect.cursor()
        self.urls = urls

    def start(self):
        while True:
            if len(self.urls) == 0:
                time.sleep(0.5)
                continue
            for url in self.urls:
                self.get_url(url)

    def get_url(self, url):
        resp = requests.get(url).text
        html = etree.HTML(resp)
        re_match = re.match('http://blog.jobbole.com/all-posts/page/\d+/', url)
        if re_match:
            self.parse_url_html(html)
        else:
            self.parse_article_html(html)

    def parse_article_html(self, html):
        '''
            解析文章详情页html
        '''
        global nums
        global start_time
        title = html.xpath('//div[@class="grid-8"]//div[@class="entry-header"]/h1/text()')[0]
        nums_tag = html.xpath('//div[@class="post-adds"]/span')
        if re.findall('\d+', nums_tag[0].xpath('h10/text()')[0]):
            support_nums = int(re.findall('\d+', nums_tag[0].xpath('h10/text()')[0])[0])
        else:
            support_nums = 0

        if re.findall('\d+', nums_tag[1].xpath('text()')[0]):
            collection_nums = int(re.findall('\d+', nums_tag[1].xpath('text()')[0])[0])
        else:
            collection_nums = 0
        res = html.xpath('//div[@class="post-adds"]/a/span/text()')[0]
        if re.findall('\d+', res):
            comment_nums = int(re.findall('\d+', res)[0])
        else:
            comment_nums = 0
        print(title, support_nums, collection_nums, comment_nums)
        insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{}', {}, {}, {})".format(title, support_nums, collection_nums, comment_nums)        
        self.cursor.execute(insert_sql)
        self.connect.commit()
        nums += 1
        if nums >= 1000:
            print('time cost: ', time.time()-start_time)
            os._exit(0)

    def parse_url_html(self, html):
        '''
            解析页码html
        '''
        article_tags = html.xpath('//div[@id="archive"]//div[contains(@class, "floated-thumb")]')
        for article_tag in article_tags:
            url = article_tag.xpath('div[@class="post-meta"]/p//a[@class="archive-title"]/@href')[0]
            print("url: ", url)
            self.urls.append(url)
        try:
            next_page_url = html.xpath('//div[contains(@class, "navigation")]//a[contains(@class, "next")]/@href')[0]
            print("next_page_url: ", next_page_url)
            self.urls.append(next_page_url)
        except Exception:
            pass


if __name__ == "__main__":
    urls = ['http://blog.jobbole.com/all-posts/page/1/']
    start_time = time.time()
    nums = 0
    fetch = Fetch(urls)
    fetch.start()

    # time cost:  313.4505832195282s
