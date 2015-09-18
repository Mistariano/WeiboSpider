__author__ = 'MisT'
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from weibo_crawler.items import WeiboItem
import weibo_login
import sys
import cookielib
from scrapy import log

class WeiboSpider(scrapy.Spider):
    name="weibo"
    allowed_domains = ["weibo.com"]


    def start_requests(self):
        log.msg("start" , level=log.INFO)
        try:
            hot_list_url = "http://d.weibo.com/102803?topnav=1&mod=logo&wvr=6"
            login()
            self.login_cookie = read_cookie()
            yield Request(url=hot_list_url,cookies=self.login_cookie,callback=self.parse_hot)
        except Exception, e:
            log.msg("Fail to start" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)

    def parse_hot(self,response):
        log.msg("parse_hot: " + response.url, level=log.INFO)
        try:
            content = response.body
            sel = Selector(text=content)
            html = sel.xpath('//script/text()').re(r'FM.view\({"ns":"pl.content.homeFeed.index".*"html":"(.*)"')[0]
            html = clean_html(html)
            sel = Selector(text=html)
            users=sel.xpath('//div[@class="WB_info"]/a/@usercard').extract()
            #print links
            #os.system("pause")
            for user in users:
                user=user.replace('id=','')
                url='http://www.weibo.com/'+user
                yield Request(url=url,cookies=self.login_cookie,callback=self.parse_user,meta={'url':url})

        except Exception, e:
            log.msg("Error for parse_hot: " + response.url, level=log.ERROR)
            log.msg(str(e), level=log.ERROR)
###
    def parse_user(self,response):
        log.msg("parse_user: " + response.url, level=log.INFO)
        try:
            url_self=response.meta['url']
            content=response.body
            sel=Selector(text=content)
            html=sel.xpath('//script/text()').re(r'FM.view.{"ns":"pl.content.homeFeed.index".*"html":"(.*)"')[0]
            content=clean_html(content)
            #sel=Selector(text=content)
            #texts=sel.xpath('//text()').extract()
            texts=sel.re(r'href="(.*?)\?from=.*?&mod=weibotime"')
            for text in texts:
                yield Request(url='http://www.weibo.com'+text,cookies=self.login_cookie,callback=self.parse_page)
                yield item
            url_follow=url_self+'/follow?'
            url_fans=url_self+'/follow?relate=fans'
            yield Request(url=url_follow,cookies=self.login_cookie,callback=self.parse_get_user)
            yield Request(url=url_fans,cookies=self.login_cookie,callback=self.parse_get_user)

        except Exception, e:
            log.msg("Error for parse_user: " + response.url, level=log.ERROR)
            log.msg(str(e), level=log.ERROR)


    def parse_get_user(self,response):
        log.msg("parse_get_user: " + response.url, level=log.INFO)
        try:
            content = response.body
            sel = Selector(text=content)
            users=sel.re(r'usercard.."id=(.*?)\\"')
            for user in users:
                url='http://www.weibo.com/'+user
                yield Request(url=url,cookies=self.login_cookie,callback=self.parse_user,meta={'url':url})
        except Exception, e:
            log.msg("Error for parse_get_user: " + response.url, level=log.ERROR)
            log.msg(str(e), level=log.ERROR)



    def parse_page(self, response):
        log.msg("parse_page: " + response.url, level=log.INFO)
        try:
            #user=response.meta['user']
            content = response.body
            sel = Selector(text=content)
            html = sel.xpath('//script/text()').re(r'FM.view\({"ns":"pl.content.weiboDetail.index".*"html":"(.*)"')[0]
            html = clean_html(html)
            sel = Selector(text=html)
            text = ''.join(sel.xpath('//div[@class="WB_text W_f14"]').re('>(.*?)<'))
            text=text.replace(' ', '')
            weibo_item = WeiboItem(text=text)
            yield weibo_item
        except Exception, e:
            log.msg("Error for parse_weibo_page: " + response.url, level=log.ERROR)
            log.msg(str(e), level=log.ERROR)


def login():
    log.msg("login... " , level=log.INFO)
    username = 'mist_weibo_1@163.com'
    pwd = 'hdlhdl'
    cookie_file = 'weibo_login_cookies.dat'
    return weibo_login.login(username, pwd, cookie_file)


def read_cookie():
    log.msg("reading cookie... " , level=log.INFO)
    cookie_file = "weibo_login_cookies.dat"
    cookie_jar = cookielib.LWPCookieJar(cookie_file)
    cookie_jar.load(ignore_discard=True, ignore_expires=True)
    cookie = dict()
    for ck in cookie_jar:
        cookie[ck.name] = ck.value
    log.msg("done " , level=log.INFO)
    return cookie
def clean_html(html):
    html = html.replace('\\t', '')
    html = html.replace('\\r', '')
    html = html.replace('\\n', '')
    html = html.replace('\\', '')
    return html





