import asyncio
import os
import time

import aiohttp
import aiomysql
import re
from bs4 import BeautifulSoup


wait_urls = []
seen_urls = set()


async def fetch(session, url):
    '''
        向URL发起请求，并返回Response
    '''
    try:
        async with session.get(url) as response:
            if response.status:
                return await response.text()
    except Exception as e:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, url)
            bs = BeautifulSoup(html, 'html.parser')
            seen_urls.add(url)
            parse_url_html(bs)


def parse_article_html(bs):
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
    return title, support_nums, collection_nums, comment_nums


def parse_url_html(bs):
    '''
        解析页码html
    '''
    article_tags = bs.select('#archive .floated-thumb')
    for article_tag in article_tags:
        url = article_tag.select('.post-meta a')[0].get('href')
        print("url: ", url)
        wait_urls.append(url)
    try:
        next_page_url = bs.select('.navigation a.next.page-numbers')[0].get('href')
        print("next_page_url: ", next_page_url)
        wait_urls.append(next_page_url)
    except Exception:
        pass

    return wait_urls


async def parse_url(session, url, pool):
    '''
        获取html源代码，从源代码中不断提取出想要的数据，并入库
    '''
    global nums, start_time
    html = await fetch(session, url)
    seen_urls.add(url)
    try:
        bs = BeautifulSoup(html, "html.parser")
        re_match = re.match('http://blog.jobbole.com/all-posts/page/\d+/', url)
        if re_match:
            parse_url_html(bs)
        else:
            title, support_nums, collection_nums, comment_nums = parse_article_html(bs)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    nums += 1
                    insert_sql = "insert into article(title, support_nums, collection_nums, comment_nums) values('{0}', {1}, {2}, {3})".format(title, support_nums, collection_nums, comment_nums)
                    await cur.execute(insert_sql)
                    if nums >= 1000:
                        print(time.time()-start_time)
                        os._exit(0)
    except TypeError:
        pass


async def consumer(pool):
    '''
        真正的执行逻辑，从wait_urls中获取url，然后将任务放入队列中
    '''
    async with aiohttp.ClientSession() as session:
        while True:
            if len(wait_urls) == 0:
                await asyncio.sleep(0.5)
                continue

            url = wait_urls.pop()
            if url not in seen_urls:
                asyncio.ensure_future(parse_url(session, url, pool))


async def main(loop):
    start_url = 'http://blog.jobbole.com/all-posts/'
    pool = await aiomysql.create_pool(host='127.0.0.1', port=3306,
                                      user='root', password='lingtian..1021',
                                      db='jobbole', loop=loop, charset='utf8', autocommit=True)

    async with aiohttp.ClientSession(loop=loop) as session:
        html = await fetch(session, start_url)
        bs = BeautifulSoup(html, 'html.parser')
        seen_urls.add(start_url)
        parse_url_html(bs)

    asyncio.ensure_future(consumer(pool))


if __name__ == '__main__':
    start_time = time.time()
    nums = 0
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(loop))
    loop.run_forever()

    # time cost: 243.34828853607178s
