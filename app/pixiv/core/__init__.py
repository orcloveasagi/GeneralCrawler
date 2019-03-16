# -*- mode: python -*-
from scrapy import Spider, Request, FormRequest
from scrapy.http.response.html import HtmlResponse
import json
from http.cookies import SimpleCookie
from core.system import RuntimeData
import time
from core.utils import get_params
import demjson


class IllustRoute(object):
    processing_pool = {}

    @classmethod
    def import_processing(cls, processings):
        cls.processing_pool[processings.__name__] = processings

    @classmethod
    def route(cls, detail):
        for processor in cls.processing_pool.values():
            if processor.is_this(detail):
                return processor.processing(detail)


class PageData(object):

    @classmethod
    def is_guest(cls, response):
        if isinstance(response, HtmlResponse):
            return len(response.xpath('//*[contains(@class,"newindex-signup")]').extract()) > 0
        return False

    @classmethod
    def page_data(cls, response: HtmlResponse):
        resource_match = response.xpath('//*').re(r'\(({token:.*)\)')
        return demjson.decode(resource_match[0])

    @classmethod
    def author_data(cls, response: HtmlResponse):
        page_data = cls.page_data(response)
        params = get_params(response.url)
        illust_id = int(params['id'])
        author = page_data['preload']['user'][illust_id]
        return author

    @classmethod
    def illust_data(cls, response: HtmlResponse):
        page_data = cls.page_data(response)
        params = get_params(response.url)
        illust_id = int(params['illust_id'])
        illust_data = page_data['preload']['illust'][illust_id]
        return illust_data


class PixivAuthRequests(object):
    auth_succes_data = {}

    @classmethod
    def check(cls, url, callback=None, headers=None, cookies=None, meta=None, **kwargs):
        cls.auth_succes_data = {
            'url': url,
            'callback': callback
        }
        auth_setting_url = 'https://www.pixiv.net/setting_user.php'

        cookies = {}
        if RuntimeData.has('cookies') is not None:
            cookies = RuntimeData.get('cookies')
        yield Request(url=auth_setting_url, callback=cls.valid, headers=headers, cookies=cookies, meta=meta, **kwargs)

    @classmethod
    def valid(cls, response: HtmlResponse):
        if response.url != 'https://www.pixiv.net/setting_user.php':
            yield Request(url='https://accounts.pixiv.net/login', callback=cls.login)
        else:
            yield Request(url=cls.auth_succes_data['url'], callback=cls.auth_succes_data['callback'])

    @classmethod
    def login(cls, response: HtmlResponse):
        _auth_info = json.loads(response.xpath('//input[@id="init-config"]/@value').extract()[0])
        # print(_auth_info)

        # # App.instance().queue().put("qerqerqerqer")
        formdata = {
            'captcha': '',
            'g_recaptcha_response': '',
            'post_key': _auth_info['pixivAccount.postKey'],
            'source': 'pc',
            'ref': 'wwwtop_accounts_index'
        }
        formdata.update({
            'pixiv_id': '',
            'password': '',
        })
        return FormRequest.from_response(
            response,
            formdata=formdata,
            callback=cls.success,
        )

    @classmethod
    def success(cls, response: HtmlResponse):
        cookie = response.request.headers.getlist('Cookie')[0]

        cookie = cookie.decode()
        cookie_simple_cookie = SimpleCookie()
        cookie_simple_cookie.load(cookie)
        cookie_datas = [
            {
                'domain': '.pixiv.net',
                'name': cookie_name,
                'path': '/',
                'value': cookie_item.value,
                'expriy': time.time() + 100000
            }
            for cookie_name, cookie_item in cookie_simple_cookie.items()
        ]
        RuntimeData.set('cookies', cookie_datas)
