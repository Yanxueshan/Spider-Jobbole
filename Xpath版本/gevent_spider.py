from gevent import monkey; monkey.patch_all()
import gevent
import time
import re
import os
import pymysql
import requests
from queue import Queue
from lxml import etree

__author__ = 'Yan'
__date__ = '2019/3/24 18:01'


def get_url(url, queue):
    html = requests.get(url).text
    html = etree.HTML(html)
    re_match = re.match('http://blog.jobbole.com/all-posts/page/\d+/', url)
    if re_match:
        parse_url_html(html, queue)
    else:
        parse_article_html(html, queue)


def parse_article_html(html, queue):
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
    queue.put((title, support_nums, collection_nums, comment_nums))


def parse_url_html(html, queue):
    '''
        解析页码html
    '''
    works = []
    article_tags = html.xpath('//div[@id="archive"]//div[contains(@class, "floated-thumb")]')
    for article_tag in article_tags:
        url = article_tag.xpath('div[@class="post-meta"]/p//a[@class="archive-title"]/@href')[0]
        print("url: ", url)
        works.append(gevent.spawn(get_url, url, queue))
    try:
        next_page_url = html.xpath('//div[contains(@class, "navigation")]//a[contains(@class, "next")]/@href')[0]
        print("next_page_url: ", next_page_url)
        works.append(gevent.spawn(get_url, next_page_url, queue))
        gevent.joinall(works)
    except Exception:
        pass


def insert_to_mysql(queue):
    '''
        将数据插入到数据库中
    '''
    global nums
    global start_time
    connect = pymysql.connect(host='localhost', user='root', password='root', db='jobbole', charset='utf8')
    cursor = connect.cursor()
    while True:
        if queue is None:
            continue
        nums += 1
        title, support_nums, collection_nums, comment_nums = queue.get()
        insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{}', {}, {}, {})".format(title, support_nums, collection_nums, comment_nums)        
        cursor.execute(insert_sql)
        connect.commit()
        if nums >= 1000:
            print(time.time()-start_time)
            os._exit(0)


if __name__ == "__main__":
    workers = []
    start_time = time.time()
    nums = 0
    queue = Queue()
    start_url = 'http://blog.jobbole.com/all-posts/page/1/'
    workers.append(gevent.spawn(get_url, start_url, queue))
    workers.append(gevent.spawn(insert_to_mysql, queue))
    gevent.joinall(workers)

