from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager
from bs4 import BeautifulSoup
import requests
import pymysql
import re

url_queue = Manager().Queue()
data_queue = Manager().Queue()
html_queue = Manager().Queue()


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

    def parse_article_html(self, bs):
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

    def parse_url_html(self, bs):
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

    def parse_html(self):
        '''
            解析文章详情页html
        '''
        while html_queue:
            html = html_queue.get()
            bs = BeautifulSoup(html, "html.parser")
            try:
                self.parse_article_html(bs)
            except Exception:
                self.parse_url_html(bs)

    def insert_to_mysql(self):
        '''
            将数据插入到数据库中
        '''
        while data_queue:
            title, support_nums, collection_nums, comment_nums = data_queue.get()
            insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{}', {}, {}, {})".format(title, support_nums, collection_nums, comment_nums)
            self.cursor.execute(insert_sql)
            self.connect.commit()


if __name__ == "__main__":
    fetch = Fetch()
    url_queue.put('http://blog.jobbole.com/all-posts/')
    executor = ProcessPoolExecutor(max_workers=5)
    for _ in range(3):
        executor.submit(fetch.get_url)
    executor.submit(fetch.parse_html)
    executor.submit(fetch.insert_to_mysql)
