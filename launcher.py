# -*- mode: python -*-
from scrapy.crawler import CrawlerProcess
import multiprocessing
# from core.system import System
import os
import sys
from core.system import DataCache
from core.system import RuntimeData
import csv
from app.pixiv.author import Main


def crawler():
    # DataCache.set('auth',{
    #
    # })
    # appInstance, bootstrap = None
    # System.load_config(os.path.join(u'config.json'))
    # main_class = appInstance.main_class()
    # main_class.bootstrap = bootstrap
    # RuntimeData.data_cache["11"] = 1
    process = CrawlerProcess({})
    process.crawl(Main)
    process.start()


if __name__ == '__main__':

    # print([1,2,3,4,5][::2])
    # exit()

    # multiprocessing.freeze_support()
    # if hasattr(sys, "_MEIPASS"):
    #     sys.path.append(sys._MEIPASS)
    # sys.path.append(os.path.dirname(sys.argv[0]))
    # while True:
    #     System.load_config(os.path.join(u'config.json'))
    #     main_app = System.app()
    #     bootstrap = None
    #     if "bootstrap" in main_app.appInstance.config():
    #         bootstrap = main_app.appInstance.config().get('bootstrap')

    runProcess = multiprocessing.Process(target=crawler)
    runProcess.start()
    runProcess.join()
    # args = (main_app.appInstance, bootstrap())
    #     runProcess.start()
    #     runProcess.join()
    #     if main_app.appInstance.loop() is False:
    #         break
