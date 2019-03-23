import asyncio
import time
import bs4
from urllib.parse import urlparse
import socket

url_list = []
movie_list = []
movie_rates = []
finnal_result = []


class Fetch(object):
    async def get_html(self):
        while True:
            try:
                self.client.send("GET {url} HTTP/1.1\r\nHost:{host}\r\nUser-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36\r\nAccept:*/*\r\nConnection:close\r\n\r\n".format(url=self.spider_url,host=self.host).encode('utf-8'))
                break
            except OSError as e:
                continue

    async def parse_html(self, url):
        result = b""
        self.spider_url = url
        self.url = urlparse(url)
        self.host = self.url.netloc
        self.client = socket.socket()
        self.client.setblocking(False)
        try:
            self.client.connect((self.host, 80))
        except BlockingIOError as e:
            pass

        await self.get_html()

        while True:
            try:
                data = self.client.recv(1024)
            except BlockingIOError as e:
                continue

            if data:
                result += data
            else:
                break

        result = result.decode("utf-8")
        result = result.split('\r\n\r\n')[1]
        print(result)

        bs_res = bs4.BeautifulSoup(result, 'html.parser')
        movie_nodes = bs_res.select('.grid_view li')
        for node in movie_nodes:
            bs_node = bs4.BeautifulSoup(str(node), 'html.parser')
            try:
                movie_name = bs_node.select('.title')[0].getText()
                movie_rate = bs_node.select('.rating_num')[0].getText()
                movie_list.append(movie_name)
                movie_rates.append(movie_rate)
            except IndexError:
                pass

        for i in range(len(movie_list)):
            try:
                finnal = movie_list[i] + '--' + movie_rates[i]
                finnal_result.append(finnal)
            except IndexError:
                pass

        print(finnal_result)

def get_urls():
    for i in range(10):
        url = 'https://movie.douban.com/top250?start=' + str(25 * i) + '&filter='
        url_list.append(url)
    return url_list

if __name__ == "__main__":
    fetch = Fetch()
    start_time = time.time()
    loop = asyncio.get_event_loop()
    tasks = [fetch.parse_html(url) for url in get_urls()]
    loop.run_until_complete(asyncio.wait(tasks))
    print(time.time() - start_time)
