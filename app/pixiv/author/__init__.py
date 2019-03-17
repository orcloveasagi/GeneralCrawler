# -*- mode: python -*-
from core.spider import CoreSpider
from scrapy.http.response.html import HtmlResponse
from app.pixiv.core import PixivAuthRequests
from app.pixiv.core import PageData
from scrapy import Spider, Request, FormRequest
import json
from urllib.parse import urlencode
import app.pixiv.core.items as DataItem
from app.pixiv.core.illusts import IllustRoute


class Main(CoreSpider):
    name = "pixiv_author"
    custom_settings = {
        # 'LOG_LEVEL': 'CRITICAL',
        'DOWNLOADER_MIDDLEWARES': {
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,
            # 'app.pixiv.pipelines.HttpbinProxyMiddleware': 2,
        },
        # 'CURLOPT_SSL_VERIFYPEER':False,
        'ITEM_PIPELINES': {
            'app.pixiv.core.pipelines.AuthorMetaPipeline': 90,
            'app.pixiv.core.pipelines.WorkMetaPipeline': 100,
            'app.pixiv.core.pipelines.ResourcePipeline': 110,
        },
    }

    @classmethod
    def update_settings(cls, settings):
        cls.custom_settings["FILES_STORE"] = "E:\\pixiv\\space"
        super(Main, cls).update_settings(settings)

    @classmethod
    def start_requests(cls):
        pass
        url = 'https://www.pixiv.net/member_illust.php?id=16712573'
        meta = {}
        yield from PixivAuthRequests.check(url=url, meta=meta, callback=cls.author_main)

    @classmethod
    def author_main(cls, response: HtmlResponse):





        author_data = PageData.author_data(response)
        author_meta_item = DataItem.AuthorMetaItem({
            'id': author_data['userId'],
            'name': author_data['name'],
            'url': response.url
        })

        yield author_meta_item
        response.meta['author'] = author_meta_item
        url = 'https://www.pixiv.net/ajax/user/%s/profile/all' % author_meta_item['id']
        yield Request(url=url, meta=response.meta, callback=cls.author_illust)

    @classmethod
    def author_illust(cls, response: HtmlResponse):
        illusts_data = json.loads(response.text)
        illusts = []
        if len(illusts_data['body']['illusts']) > 0:
            for item in illusts_data['body']['illusts'].keys():
                illusts.append(item)

        if len(illusts_data['body']['manga']) > 0:
            for item in illusts_data['body']['manga'].keys():
                illusts.append(item)

        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]

        for chunk in chunks(illusts, 96):
            params = {
                'ids[]': chunk,
                'is_manga_top': 0
            }
            url = 'https://www.pixiv.net/ajax/user/%s/profile/illusts?%s' % (response.meta['author']['id'], urlencode(params, True))
            yield Request(url=url, meta=response.meta, callback=cls.illusts)

    @classmethod
    def illusts(cls, response: HtmlResponse):
        illusts = json.loads(response.text)
        for work_item in illusts['body']['works'].items():
            work = work_item[1]
            url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s" % work['id']
            yield Request(url=url, meta=response.meta, callback=cls.illust_detail)

    @classmethod
    def illust_detail(cls, response: HtmlResponse):
        illust = PageData.illust_data(response)
        illust_meta_item = {
            'id': illust['illustId'],
            'name': illust['illustTitle'],
            'url': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s' % illust['illustId'],
            'resource_total': illust['pageCount'],
            'tags': [tag_data['tag'] for tag_data in illust['tags']['tags']],
            'caption': illust['illustComment'],
            'type': None,
            'author': response.meta['author'],
            'series': None,
        }
        if illust['seriesNavData'] is not None:
            illust_meta_item['series'] = {
                'id': illust['seriesNavData']['seriesId'],
                'title': illust['seriesNavData']['title']
            }

        illust['work_meta_item'] = DataItem.WorkMetaItem(illust_meta_item)
        illust['referer'] = response.url
        yield illust['work_meta_item']
        illust_process = IllustRoute.route(illust)
        if illust_process is not None:
            yield from illust_process
