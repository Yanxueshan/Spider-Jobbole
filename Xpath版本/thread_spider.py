from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from lxml import etree
import requests
import pymysql
import re
import time
import os

__author__ = 'Yan'
__date__ = '2019/3/24 16:19'

url_queue = Queue()
data_queue = Queue()
html_queue = Queue()
nums = 0


class Fetch:
    '''
        爬取jobbole所有文章
    '''
    def __init__(self):
        self.connect = pymysql.connect(host='localhost', user='root', password='lingtian..1021', db='jobbole', charset='utf8')
        self.cursor = self.connect.cursor()

    def get_url(self):
        '''
            获取下一页的url
        '''
        while url_queue:
            url = url_queue.get()
            html = requests.get(url).text
            html_queue.put(html)

    def parse_article_html(self, html):
        '''
            解析文章详情页html
        '''
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
        data_queue.put((title, support_nums, collection_nums, comment_nums))

    def parse_url_html(self, html):
        '''
            解析页码html
        '''
        article_tags = html.xpath('//div[@id="archive"]//div[contains(@class, "floated-thumb")]')
        for article_tag in article_tags:
            url = article_tag.xpath('div[@class="post-meta"]/p//a[@class="archive-title"]/@href')[0]
            print("url: ", url)
            url_queue.put(url)
        try:
            next_page_url = html.xpath('//div[contains(@class, "navigation")]//a[contains(@class, "next")]/@href')[0]
            print("next_page_url: ", next_page_url)
            url_queue.put(next_page_url)
        except Exception:
            pass

    def parse_html(self):
        '''
            解析文章详情页html
        '''
        while html_queue:
            html = html_queue.get()
            html = etree.HTML(html)
            try:
                self.parse_article_html(html)
            except Exception:
                self.parse_url_html(html)

    def insert_to_mysql(self):
        '''
            将数据插入到数据库中
        '''
        global nums, start_time
        while data_queue:
            nums += 1
            title, support_nums, collection_nums, comment_nums = data_queue.get()
            insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{}', {}, {}, {})".format(title, support_nums, collection_nums, comment_nums)
            self.cursor.execute(insert_sql)
            self.connect.commit()
            if nums >= 1000:
                print(time.time()-start_time)
                os._exit(0)


if __name__ == "__main__":
    start_time = time.time()
    fetch = Fetch()
    url_queue.put('http://blog.jobbole.com/all-posts/')
    executor = ThreadPoolExecutor(max_workers=5)
    for _ in range(3):
        task = executor.submit(fetch.get_url)
    task1 = executor.submit(fetch.parse_html)
    task2 = executor.submit(fetch.insert_to_mysql)

    # time cost : 60.63394331932068s
