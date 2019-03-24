import asyncio
import os
import time

import aiohttp
import aiomysql
import re
from lxml import etree

__author__ = 'Yan'
__date__ = '2019/3/24 18:19'

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
            html = etree.HTML(html)
            seen_urls.add(url)
            parse_url_html(html)


def parse_article_html(html):
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
    return title, support_nums, collection_nums, comment_nums


def parse_url_html(html):
    '''
        解析页码html
    '''
    article_tags = html.xpath('//div[@id="archive"]//div[contains(@class, "floated-thumb")]')
    for article_tag in article_tags:
        url = article_tag.xpath('div[@class="post-meta"]/p//a[@class="archive-title"]/@href')[0]
        print("url: ", url)
        wait_urls.append(url)
    try:
        next_page_url = html.xpath('//div[contains(@class, "navigation")]//a[contains(@class, "next")]/@href')[0]
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
        html = etree.HTML(html)
        re_match = re.match('http://blog.jobbole.com/all-posts/page/\d+/', url)
        if re_match:
            parse_url_html(html)
        else:
            title, support_nums, collection_nums, comment_nums = parse_article_html(html)
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
        html = etree.HTML(html)
        seen_urls.add(start_url)
        parse_url_html(html)

    asyncio.ensure_future(consumer(pool))


if __name__ == '__main__':
    start_time = time.time()
    nums = 0
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(loop))
    loop.run_forever()

    # time cost: 26.639267206192017s
