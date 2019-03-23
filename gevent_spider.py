from gevent import monkey; monkey.patch_all()
import gevent
import time
import re
import os
import pymysql
import requests
from queue import Queue
from bs4 import BeautifulSoup


def get_url(url, queue):
    html = requests.get(url).text
    bs = BeautifulSoup(html, 'html.parser')
    re_match = re.match('http://blog.jobbole.com/all-posts/page/\d+/', url)
    if re_match:
        parse_url_html(bs, queue)
    else:
        parse_article_html(bs, queue)


def parse_article_html(bs, queue):
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
    queue.put((title, support_nums, collection_nums, comment_nums))
    # workers.append(gevent.spawn(insert_to_mysql, (queue, )))


def parse_url_html(bs, queue):
    '''
        解析页码html
    '''
    works = []
    article_tags = bs.select('#archive .floated-thumb')
    for article_tag in article_tags:
        url = article_tag.select('.post-meta a')[0].get('href')
        print("url: ", url)
        works.append(gevent.spawn(get_url, url, queue))
        gevent.joinall(works)
    try:
        next_page_url = bs.select('.navigation a.next.page-numbers')[0].get('href')
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
    connect = pymysql.connect(host='localhost', user='root', password='lingtian..1021', db='jobbole', charset='utf8')
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

    # time cost: 297.9752986431122s
