# -*- mode: python -*-
from .items import AuthorMetaItem, WorkMetaItem, ResourceItem
from scrapy.pipelines.files import FileException, FilesPipeline
from scrapy import Request
import os
import json
from core.utils import path_format
import csv


class AuthorMetaPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, AuthorMetaItem):
            meta_path = os.path.join(
                spider.settings.get('FILES_STORE'),
                path_format("%s_%s" % (item.get('name'), item.get('id'))),
                "author_meta.json"
            )
            os.makedirs(os.path.dirname(meta_path), exist_ok=True)
            with open(meta_path, 'wb')as file:
                file.write(json.dumps(dict(item), ensure_ascii=False).encode("utf-8"))
        return item


#
#
class WorkMetaPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, WorkMetaItem):
            meta_path = os.path.join(
                spider.settings.get('FILES_STORE'),
                path_format("%s_%s" % (item.get('author').get('name'), item.get('author').get('id'))),
                path_format("%s_%s" % (item.get('name'), item.get('id'))),
                "work_meta.json"
            )
            os.makedirs(os.path.dirname(meta_path), exist_ok=True)
            with open(meta_path, 'wb')as file:
                work = dict(item)
                work['author'] = dict(work['author'])
                file.write(json.dumps(work, ensure_ascii=False).encode("utf-8"))

        return item


#
#
class ResourcePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        if isinstance(item, ResourceItem):
            yield Request(item['resource_url'], headers={
                'Referer': item['referer']
            }, meta=item)

    def file_path(self, request, response=None, info=None):
        item = request.meta
        resource_path = os.path.join(
            path_format(
                "%s_%s" % (item.get('work').get('author').get('name'), item.get('work').get('author').get('id'))),
            path_format("%s_%s" % (item.get('work').get('name'), item.get('work').get('id'))),
            item['resource_url'].split('/')[-1]
        )
        return resource_path

    def item_completed(self, results, item, info):
        item_completed = super().item_completed(results, item, info)
        if isinstance(item, ResourceItem):
            result = results[0]
            if result[0]:
                info.spider.logger.critical("下载完成 %s" % result[1]['path'])
            else:
                info.spider.logger.critical("下载失败%s" % json.dumps(result[1], ensure_ascii=False))
        return item_completed
