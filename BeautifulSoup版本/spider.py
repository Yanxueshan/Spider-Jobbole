import requests
import re
import time
import os
import pymysql
from bs4 import BeautifulSoup


class Fetch:
    def __init__(self, urls):
        self.connect = pymysql.connect(host='localhost', user='root', password='lingtian..1021', db='jobbole', charset='utf8')
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
        html = requests.get(url).text
        bs = BeautifulSoup(html, 'html.parser')
        re_match = re.match('http://blog.jobbole.com/all-posts/page/\d+/', url)
        if re_match:
            self.parse_url_html(bs)
        else:
            self.parse_article_html(bs)

    def parse_article_html(self, bs):
        '''
            解析文章详情页html
        '''
        global nums
        global start_time
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
        insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{}', {}, {}, {})".format(title, support_nums, collection_nums, comment_nums)        
        self.cursor.execute(insert_sql)
        self.connect.commit()
        nums += 1
        if nums >= 1000:
            print('time cost: ', time.time()-start_time)
            os._exit(0)

    def parse_url_html(self, bs):
        '''
            解析页码html
        '''
        article_tags = bs.select('#archive .floated-thumb')
        for article_tag in article_tags:
            url = article_tag.select('.post-meta a')[0].get('href')
            print("url: ", url)
            self.urls.append(url)
        try:
            next_page_url = bs.select('.navigation a.next.page-numbers')[0].get('href')
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

    # time cost:  1062.5993554592133s
