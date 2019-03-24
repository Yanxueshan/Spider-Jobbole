from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Pool
from bs4 import BeautifulSoup
import requests
import pymysql
import re
import os
import time

__author__ = 'Yan'
__date__ = '2019/3/23 22:58'


def get_url(url_queue, html_queue, nums):
    '''
        获取下一页的url
    '''
    while url_queue:
        if nums['numbers'] >= 1000:
            os._exit(0)
        url = url_queue.get()
        html = requests.get(url).text
        html_queue.put(html)


def parse_article_html(bs, data_queue):
    '''
        解析文章详情页html
    '''
    title = bs.select('.grid-8 .entry-header h1')[0].text
    nums_tag = bs.select('.post-adds > span')
    if re.findall('\d+', nums_tag[0].text):
        support_nums = int(re.findall('\d+', nums_tag[0].text)[0])
    else:
        support_nums = 0

    if re.findall('\d+', nums_tag[1].text):
        collection_nums = int(re.findall('\d+', nums_tag[1].text)[0])
    else:
        collection_nums = 0

    if re.findall('\d+', bs.select('.post-adds a span')[0].text):
        comment_nums = int(re.findall('\d+', bs.select('.post-adds a span')[0].text)[0])
    else:
        comment_nums = 0
    print(title, support_nums, collection_nums, comment_nums)
    data_queue.put((title, support_nums, collection_nums, comment_nums))


def parse_url_html(bs, url_queue):
    '''
        解析页码html
    '''
    article_tags = bs.select('#archive .floated-thumb')
    for article_tag in article_tags:
        url = article_tag.select('.post-meta a')[0].get('href')
        print("url: ", url)
        url_queue.put(url)
    try:
        next_page_url = bs.select('.navigation a.next.page-numbers')[0].get('href')
        print("next_page_url: ", next_page_url)
        url_queue.put(next_page_url)
    except Exception:
        pass


def parse_html(html_queue, url_queue, data_queue, nums):
    '''
        解析文章详情页html
    '''
    while html_queue:
        if nums['numbers'] >= 1000:
            os._exit(0)
        html = html_queue.get()
        bs = BeautifulSoup(html, "html.parser")
        try:
            parse_article_html(bs, data_queue)
        except Exception:
            parse_url_html(bs, url_queue)


def insert_to_mysql(data_queue, nums):
        '''
            将数据插入到数据库中
        '''
        connect = pymysql.connect(host='localhost', user='root', password='lingtian..1021', db='jobbole',
                                  charset='utf8')
        while data_queue:
            nums['numbers'] += 1
            title, support_nums, collection_nums, comment_nums = data_queue.get()
            insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{}', {}, {}, {})".format(title, support_nums, collection_nums, comment_nums)
            cursor = connect.cursor()
            cursor.execute(insert_sql)
            connect.commit()
            if nums['numbers'] >= 1000:
                print('time cost: ', time.time()-nums['start_time'])
                os._exit(0)


if __name__ == "__main__":
    url_queue = Manager().Queue()
    data_queue = Manager().Queue()
    html_queue = Manager().Queue()
    nums = Manager().dict()
    nums['numbers'] = 0
    nums['start_time'] = time.time()
    url_queue.put('http://blog.jobbole.com/all-posts/')

    pool = Pool(4)
    for _ in range(2):
        pool.apply_async(get_url, (url_queue, html_queue, nums))
    pool.apply_async(parse_html, (html_queue, url_queue, data_queue, nums))
    pool.apply_async(insert_to_mysql, (data_queue, nums))
    pool.close()
    pool.join()

    # time cost: 219.67393612861633s
