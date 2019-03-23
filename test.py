__author__ = 'larry'
__date__ = '2019/3/23 17:53'

# from concurrent.futures import ProcessPoolExecutor
# from multiprocessing import Manager, Pool

# queue = Manager().Queue()


# def task(name):
#     print("name", name)


# def task1():
#     ret = queue.get()
#     print(ret)


# if __name__ == "__main__":
#     pool = Pool(4)
#     for i in range(5):
#         pool.apply_async(task, "safly%d" % i)
from threading import Thread
import time
import os

def test():
    for i in range(100):
        if i > 10:
            os._exit(0)
        print(i)



th = Thread(target=test)
th.start()
time.sleep(2)
th2 = Thread(target=test)
th2.start()
th.join()
th2.join()
