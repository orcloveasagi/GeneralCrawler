# -*- mode: python -*-
from . import IllustRoute
from .items import ResourceItem
from scrapy import Request
import json


class Illustration(object):
    @classmethod
    def is_this(cls, detail):
        return detail['pageCount'] == 1 and detail['illustType'] != 2

    @classmethod
    def processing(cls, detail):
        yield ResourceItem({
            "work": detail['work_meta_item'],
            "referer": detail['referer'],
            "resource_url": detail['urls']['original']
        })


# class Manga(object):
#     @classmethod
#     def resources(cls, response):
#         resources = response.xpath('//*').re(r'pixiv.context.originalImages\[\d*\]\s*=\s*"(\S*)"')
#         for responseUrl in resources:
#             responseUrl = responseUrl.replace('\/', '/')
#             yield ResourceItem({
#                 "work": response.meta['detail']['work_meta_item'],
#                 "referer": response.url,
#                 "resource_url": responseUrl,
#             })


class IllustrationMultiple(object):

    @classmethod
    def is_this(cls, detail):
        return detail['pageCount'] > 1

    # @classmethod
    # def processing(cls, detail):
    #     url = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=%s' % detail['illustId']
    #     yield Request(
    #         url=url,
    #         meta={
    #             'detail': detail
    #         },
    #         callback=cls.resources
    #     )

    # @classmethod
    # def resources(cls, response):
    #     is_manga = str(response.body).find("member_illust_manga")
    #     if is_manga > -1:
    #         resources = response.xpath(
    #             '//*[@class="item-container"]//a[contains(@class,"full-size-container")]/@href').extract()
    #         for responsePage in resources:
    #             url = 'https://www.pixiv.net%s' % responsePage
    #             yield Request(
    #                 url=url,
    #                 meta=response.meta,
    #                 callback=cls.resource
    #             )
    #     else:
    #         yield from Manga.resources(response)

    @classmethod
    def processing(cls, detail):
        url = 'https://www.pixiv.net/ajax/illust/%s/pages' % detail['illustId']
        yield Request(
            url=url,
            meta={
                'detail': detail
            },
            callback=cls.resources
        )

    @classmethod
    def resources(cls, response):
        resources = (json.loads(response.text))['body']
        referer = response.meta['detail']['work_meta_item']['url']
        for imgs in resources:
            url = imgs['urls']['original']
            yield ResourceItem({
                "work": response.meta['detail']['work_meta_item'],
                "referer": referer,
                "resource_url": url,
            })


class Ugoira(object):
    @classmethod
    def is_this(cls, detail):
        return detail['illustType'] == 2

    @classmethod
    def processing(cls, detail):
        url = 'https://www.pixiv.net/ajax/illust/%s/ugoira_meta' % detail['illustId']
        yield Request(
            url=url,
            headers={
                'Referer': detail['referer']
            },
            meta={
                'detail': detail,
                'Referer': detail['referer'],
            },
            callback=cls.resources
        )

    @classmethod
    def resources(cls, response):
        resource = json.loads(response.body)
        yield ResourceItem({
            "work": response.meta['detail']['work_meta_item'],
            "referer": response.meta['Referer'],
            "resource_url": resource['body']['originalSrc'],
        })


IllustRoute.import_processing(Illustration)
IllustRoute.import_processing(IllustrationMultiple)
IllustRoute.import_processing(Ugoira)
