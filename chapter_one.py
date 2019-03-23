# import collections
# import random

# this is __getitem__ method introduce
'''

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck(object):
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split(' ')

    def __init__(self):
        self._card = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
    
    def __len__(self):
        return len(self._card)

    def __getitem__(self, position):
        return self._card[position]

beer_card = FrenchDeck()
print(len(beer_card))
print(beer_card[0:2])
print(random.choice(beer_card))

'''


# this is three kinds of method of class
'''

class Animal(object):
    @classmethod
    def old(cls):
        print('this is old function')

    def new(self):
        print('this is new functino')

    @staticmethod
    def middle():
        print('this is middle function')

Animal.old()
Animal.middle()

'''

# 抽象基类
'''
import abc

class Animal(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_name(self):
        return 'animal'

class Cat(Animal):
    def get_name(self):
        return 'cat'

cat = Cat()
'''

# isinstance type
'''
class A(object):
    pass

class B(object):
    pass

b = B()
print(type(b) == B)
print(type(b) == A)
print(isinstance(b ,A))
'''

# 类变量 实例变量
'''
class A:
    name = 'shiyue'

a = A()
print(A.name)
print(a.name)
a.name = 'qiyue'
print(a.name)
print(A.name)
'''

# python对象的自省机制
'''
class Animal:
    name = 'animal'

    def __init__(self):
        self.age = 10

cat = Animal()
print(cat.__dict__)
print(Animal.__dict__)
print(dir(cat))
'''

# 使得类可以像字典一样访问
'''
from collections.abc import MutableMapping

class Animal(MutableMapping):
    def __init__(self):
        self._headers = {}

    def __len__(self):
        return len(self._headers)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        return iter(self)

    def __getitem__(self, item):
        print(item)
        return self._headers.get(item)

    def __setitem__(self, key, value):
        print(key, value)
        self._headers[key] = value

    def __delitem__(self, key):
        pass

a = Animal()
a['name'] = 'shiyue'
print(a['name'])
print(a.get('name'))
'''

# __getattr__与__getattritube__的区别
'''
class Animal:
    def __init__(self, name):
        self.name = name
        self.age = 10

    def __getattr__(self, item):
        return 'not found attritube ' + item + ', please input new attribute'

    def __getattribute__(self, item):
        # return 'not found attritube ' + item
        raise AttributeError

cat = Animal('cat')
cat.age = 20
print(cat.age)
'''

# 属性描述符
'''
class IntField:
    # def __get__(self, instance, owner):
    #     print(instance)
    #     print(owner)
    
    def __set__(self, instance, value):
        print(instance)
        print(value)

    # def __delete__(self, instance):
    #     print(instance)

class User:
    age = IntField()

user = User()
user.age = 10
'''

# __new__ __init__
'''
class Animal:
    def __new__(cls, *args, **kwargs):
        print('in __new__')
        return super().__new__(cls)
    
    def __init__(self, name):
        print("in __init__")
        self.name = name

cat = Animal('shiyue')
print(cat.name)
'''

# 元类
'''
class MetaClass(type):
    def __new__(cls, *args, **kwargs):
        # for arg in args:
        print(args)
        return super().__new__(cls, *args, **kwargs)

class User(object, metaclass=MetaClass):
    def __init__(self, name):
        self.name = name

user = User('shiyue')
print(user.name)
'''

# 自己实现Django的ORM
'''
import numbers
import pymysql

def judge_int(value):
    if not isinstance(value, numbers.Integral):
        raise ValueError("value must input int")
    if value < 0:
        raise ValueError("value input positive number")

def judge_str(value):
    if not isinstance(value, str):
        raise ValueError("please input str")

class Field:
    pass

class CharField(Field):
    def __init__(self, db_column, min_length=0, max_length=0):
        self._value = ""
        self.db_column = db_column

        self.min_length = min_length
        self.max_length = max_length

        judge_int(self.min_length)
        judge_int(self.max_length)
        if self.min_length > self.max_length:
            raise ValueError("max_length must great than min_length")

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        judge_str(value)
        if len(value) < self.min_length or len(value) > self.max_length:
            raise ValueError("value length must between min_length and max_length")
        self._value = value


class IntField(Field):
    def __init__(self, db_column, min_value=0, max_value=100):
        self._value = 0
        self.db_column = db_column

        self.max_value = max_value
        self.min_value = min_value

        judge_int(self.min_value)
        judge_int(self.max_value)
        if self.min_value > self.max_value:
            raise ValueError("max_value must great than min_value")

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        judge_int(value)
        if value < self.min_value or value > self.max_value:
            raise ValueError("value must between min_value and max_value")
        self._value = value

class UserMetaClass(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        if name == "BaseModel":
            return super().__new__(cls, name, bases, attrs, **kwargs)
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        db_table = name.lower()
        _meta = {}
        attrs_meta = attrs.get("Meta", None)
        if attrs_meta is not None:
            table = getattr(attrs_meta, "db_table", None)
            if table is not None:
                db_table = table
        
        _meta["db_table"] = db_table

        attrs['fields'] = fields
        attrs['_meta'] = _meta
        del attrs['Meta']

        return super().__new__(cls, name, bases, attrs, **kwargs)

class BaseModel(metaclass=UserMetaClass):
    def __init__(self, *args, **kwargs):
        self.connect = pymysql.Connect(host="localhost", port=3306, user="root", passwd="root", db="test.py")
        self.cursor = self.connect.cursor()

        for key, value in kwargs:
            setattr(self, key, value)
        return super().__init__()
    
    def save(self):
        fields = []
        values = []
        db_table = self._meta["db_table"]
        for key, value in self.fields.items():
            db_column = getattr(value, "db_column")
            if db_column is None:
                db_column = key.lower()
            fields.append(db_column)
            value = getattr(value, "_value")
            values.append(str(value))
        
        value = "%s," * len(values)
        value = value[:-1]
        
        insert_sql = "insert into {db_table}({fields}) values({value})".format(db_table=db_table, fields=",".join(fields), value=value)

        self.cursor.execute(insert_sql, values)
        self.connect.commit()
        print('insert sucess')
        self.cursor.close()
        self.connect.close()


class User(BaseModel):
    name = CharField(db_column="name", max_length=10)
    age = IntField(db_column="age", min_value=0, max_value=100)

    class Meta:
        db_table = "user"

user = User()
user.name = 'shiyue'
user.age = 10
user.save()
'''

# 实现自己的迭代器
'''
from collections.abc import Iterator

class MyIterator:
    def __init__(self, employee):
        self.employee = employee
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            content = self.employee[self.index]
        except IndexError as e:
            raise StopIteration
        self.index += 1
        return content

my_iterator = MyIterator(['shiyue', 'qiyue'])
print(isinstance(my_iterator, Iterator))

for i in my_iterator:
    print(i)
'''

# 生成器 栈帧
'''
import inspect
import dis

frame = None

def func2():
    func1()

def func1():
    global frame
    frame = inspect.currentframe()

func2()
print(frame.f_code.co_name)
frame_callback = frame.f_back
print(frame_callback.f_code.co_name)

def gen_func():
    yield 1
    name = "shiyue"
    yield 2
    age = 24
    return "qiyue"

gen = gen_func()
dis.dis(gen)
print(gen.gi_frame.f_lasti)
print(gen.gi_frame.f_locals)
print(next(gen))
print(gen.gi_frame.f_lasti)
print(gen.gi_frame.f_locals)
print(next(gen))
print(gen.gi_frame.f_lasti)
print(gen.gi_frame.f_locals)
'''

# 多线程 通信 Queue
'''
import threading
from queue import Queue

queue = Queue(maxsize=2)
queue.put('shiyue')
for i in range(10):
    queue.put_nowait(i)
'''

# condition
'''
import threading

class Mary(threading.Thread):
    def __init__(self, condition):
        self.condition = condition
        super().__init__(name="Mary")
    
    def run(self):
        with self.condition:
            self.condition.wait()
            print("草色遥看近却无。")
            self.condition.notify()
            self.condition.wait()
            print("绝胜烟柳满皇都。")

class Jane(threading.Thread):
    def __init__(self, condition):
        self.condition = condition
        super().__init__(name="Jane")
    
    def run(self):
        with self.condition:
            print("天街小雨润如酥，")
            self.condition.notify()
            self.condition.wait()
            print("最是一年春好处，")
            self.condition.notify()


condition = threading.Condition()
mary = Mary(condition)
jane = Jane(condition)
mary.start()
jane.start()
'''

# 线程池
'''
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor

def get_html(url):
    print('qiyue')
    return 'shiyue'

if __name__ == '__main__':
    url = 'https://www.baidu.com'
    pool = multiprocessing.Pool(4)
    result = pool.apply_async(get_html, args=(url,))
    result = pool.apply_async(get_html, args=(url,))
    print(type(result))
    pool.close()
    pool.join()
    print(result.get())
'''

# 进程之间的通信
'''
from multiprocessing import Queue, Process, Pool, Manager, Pipe
import time

def producer(queue):
    queue.put("shiyue")
    time.sleep(2)

def consumer(queue):
    time.sleep(2)
    result = queue.get()
    print(result)

if __name__ == '__main__':
    queue = Manager().Queue()
    process1 = Process(target=producer, args=(queue,))
    process2 = Process(target=consumer, args=(queue,))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
    # pool = Pool()
    # pool.apply_async(producer, args=(queue, ))
    # pool.apply_async(consumer, args=(queue, ))
    # pool.close()
    # pool.join()
    print("end")
'''

# 进程通信之Pipe
'''
from multiprocessing import Pipe, Process

def producer(pipe):
    pipe.send("shiyue")

def consumer(pipe):
    result = pipe.recv()
    print(result)

if __name__ == "__main__":
    recv_pipe, send_pipe = Pipe()
    process1 = Process(target=producer, args=(send_pipe,))
    process2 = Process(target=consumer, args=(recv_pipe,))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
    print("end")
'''

# 进程通信之Manager
'''
from multiprocessing import Manager, Process

def producer(p_dict, key, value):
    p_dict[key] = value

def consumer(p_dict, key, value):
    p_dict[key] = value

if __name__ == "__main__":
    process_dict = Manager().dict()
    process1 = Process(target=producer, args=(process_dict, 'name', 'shiyue'))
    process2 = Process(target=consumer, args=(process_dict, 'age', 23))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
    print(process_dict)
'''

# 使用socket模拟http请求(阻塞)
'''
import socket
from urllib.parse import urlparse

def get_html(url):
    url = urlparse(url)
    host = url.netloc
    path = url.path
    if path == "":
        path = '/'

    client = socket.socket()
    client.connect((host, 80))
    client.send("GET {path} HTTP/1.1\r\nHost:{host}\r\nConnection:close\r\n\r\n".format(path=path, host=host).encode('utf-8'))

    result = b""
    while True:
        data = client.recv(1024)
        if data:
            result += data
        else:
            break

    result = result.decode("utf-8")
    result = result.split('\r\n\r\n')[1]
    print(result)
    client.close()

if __name__ == "__main__":
    get_html("https://www.baidu.com")
'''

# 使用socket模拟http请求（非阻塞IO）
'''
import socket
from urllib.parse import urlparse

def get_html(url):
    url = urlparse(url)
    host = url.netloc
    path = url.path
    if path == "":
        path = '/'

    client = socket.socket()
    client.setblocking(False)
    try:
        client.connect((host, 80))
    except BlockingIOError as e:
        pass
    
    while True:
        try:
            client.send("GET {path} HTTP/1.1\r\nHost:{host}\r\nConnection:close\r\n\r\n".format(path=path, host=host).encode('utf-8'))
            break
        except OSError as e:
            continue

    result = b""
    while True:
        # 等待数据返回
        try:
            data = client.recv(1024)
        except BlockingIOError as e:
            continue

        if data:
            result += data
        else:
            break

    result = result.decode("utf-8")
    result = result.split('\r\n\r\n')[1]
    print(result)
    client.close()

if __name__ == "__main__":
    get_html("https://www.baidu.com")
'''

# 使用select + 事件循环 + 回调实现http请求
'''
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from urllib.parse import urlparse
import socket

selector = DefaultSelector()
urls = ["https://www.baidu.com", "https://www.zhihu.com"]
Sign = False

class Fecth:
    def connected(self, key):
        selector.unregister(key.fd)
        self.client.send("GET {path} HTTP/1.1\r\nHost:{host}\r\nConnection:close\r\n\r\n".format(path=self.path,host=self.host).encode('utf-8'))
        selector.register(self.client.fileno(), EVENT_READ, self.read)

    def read(self, key):
        data = self.client.recv(1024)

        if data:
            self.result += data
        else:
            selector.unregister(key.fd)
            self.result = self.result.decode("utf-8")
            self.result = self.result.split('\r\n\r\n')[1]
            print(self.result)
            self.client.close()
            urls.remove(self.spider_url)
            if not urls:
                global Sign
                Sign = True

    def get_html(self, url):
        self.spider_url = url
        self.result = b""
        url = urlparse(url)
        self.host = url.netloc
        self.path = url.path
        if self.path == "":
            self.path = '/'

        self.client = socket.socket()
        self.client.setblocking(False)
        try:
            self.client.connect((self.host, 80))
        except BlockingIOError as e:
            pass

        selector.register(self.client.fileno(), EVENT_WRITE, self.connected)

def loop():
    while not Sign:
        ready = selector.select()
        for key, mask in ready:
            call_back = key.data
            call_back(key)


if __name__ == "__main__":
    for url in urls:
        fetch = Fecth()
        fetch.get_html(url)
    loop()
'''

# generator
'''
def gen_func():
    html = yield "https://www.baidu.com"
    print(html)
    yield "qiyue"

gen = gen_func()
print(gen.send(None))
# print(next(gen))
print(gen.send("shiyue"))
'''

# yield and yield from
'''
def gen_one():
    yield range(10)

def gen_two():
    yield from range(10)

gen_one = gen_one()
gen_two = gen_two()

for item in gen_one:
    print(item)
for item in gen_two:
    print(item)
'''

# yield from
'''
def gen_func():
    result = 0
    while True:
        x = yield
        if not x:
            break
        result = result + x
    return result

def gen_fun():
    result = yield from gen_func()
    yield result

def main():
    gen = gen_fun()
    gen.send(None)
    gen.send(100)
    gen.send(200)
    gen.send(300)
    print(gen.send(None))

main()
'''

# yield from 源码
'''
# 一些说明
# _i：子生成器，同时也是一个迭代器
# _y：子生成器生产的值
# _r：yield from 表达式最终的值
# _s：调用方通过send()发送的值
# _e：异常对象

_i = iter(EXPR)
try:
    _y = next(_i)
except StopIteration as _e:
    _r = _e.value
else:
    while 1:
        try:
            _s = yield _y
        except GeneratorExit as _e:
            try:
                _m = _i.close
            except AttributeError:
                pass
            else:
                _m()
            raise _e
        except BaseException as _e:
            _x = sys.exc_info()
            try:
                _m = _i.throw
            except AttributeError:
                raise _e
            else:
                try:
                    _y = _m(*_x)
                except StopIteration as _e:
                    _r = _e.value
                    break
        else:
            try:
                if _s is None:
                    _y = next(_i)
                else:
                    _y = _i.send(_s)
            except StopIteration as _e:
                _r = _e.value
                break
RESULT = _r
'''

# asyncio
'''
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
'''
