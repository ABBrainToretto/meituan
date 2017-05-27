#_*_ coding:utf-8 _*_
import requests
from lxml import etree
import json
import sys
import time
import useip
import random
import MySQLdb

##------保证内容为utf-8编码---------##
reload(sys)
sys.setdefaultencoding("utf-8")


##--------储存到mysql数据库,这种键值对的字段可以考虑储存在mongodb中-------##
##--------封装储存数据库的class，后面直接调用就可以插入-------------------##
class Sql():
    def __init__(self):
        self.conn = MySQLdb.connect(
                host = "localhost",
                port = 3306,
                user = "root",
                passwd = "123321",
                db = "book",
                charset = "utf8"
            )
        self.cur = self.conn.cursor()
    def mysqldata(self,city,food,tag_field,name_field,geo_field,phone_field):
        sql = "insert INTO chongqing_food(`city`,`food`,`tag_field`,`name_field`,`geo_field`,`phone_field`) VALUES (%s,%s,%s,%s,%s,%s)"
        param = (city,food,tag_field,name_field,geo_field,phone_field)
        self.cur.execute(sql,param)
        self.conn.commit()
        return

##---------------------美团爬取的class--------------------##
class Meituan():
    def __init__(self):
        self.items = []
        self.shop_url = 'http://cq.meituan.com/shop/'
        self.url = 'http://cq.meituan.com/category/haixian'
        self.user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
        ]
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Host':'cq.meituan.com',
            'Pragma':'no-cache',
            'Referer':'http://cq.meituan.com/category/xiangcai?mtt=1.index%2Ffloornew.nc.10.j361zqc4',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }


##---------------- 调用代理ip（useip.py） ---------------##
    def ip_provide(self):
        mysql = useip.Sql()
        proxy = mysql.mysqldata()
        return proxy

##---------------- 获取商铺urls ---------------##
    def shoplist(self):
        # UA = random.choice(self.user_agent_list)
        proxy = Meituan().ip_provide()
        print proxy
        shop_html = requests.get(self.url,headers=self.headers,proxies=proxy)
        print shop_html.status_code
        shop_html = shop_html.content
        shop_selector = etree.HTML(shop_html)
        shop_fields = shop_selector.xpath('//div[@class="J-scrollloader cf J-hub"]/@data-async-params')[0]
        shop = json.loads(shop_fields)
        shop_item = shop.get('data').encode('utf-8')
        shop_item = json.loads(shop_item)
        shop_item = shop_item.get("poiidList")
        print len(shop_item)
        print shop_item
        return shop_item

##-----------------获取商店信息并保存excel（#号打开就是储存excel的代码）----------------##
##-----------------获取商店信息并保存数据库----------------##
    def item_list(self):
        proxy = Meituan().ip_provide()
        shop_item = Meituan().shoplist()
        # UA = random.choice(self.user_agent_list)
        # headers = {'User-Agent':UA}
        # head = [u'城市',u'一级分类',u'美食种类',u'商家名',u'商家地址',u'商家电话']
        # wbk = xlwt.Workbook()
        # sheet = wbk.add_sheet(u'chongqing_food',cell_overwrite_ok=True)
        row = 0
        mysql = Sql()
        for i in shop_item:
            # proxy = Meituan().ip_provide()
            url = self.shop_url + str(i)

            item_html = requests.get(url,headers=self.headers)
            item_html = item_html.content
            item_selector = etree.HTML(item_html)
            tag_field = item_selector.xpath('//a[@class="tag"]/text()')
            geo_field = item_selector.xpath('//span[@class="geo"]/text()')
            name_field = item_selector.xpath('//div[@class="fs-section__left"]/h2/span[@class="title"]/text()')
            phone_field = item_selector.xpath('//div[@class="fs-section__left"]/p[@class="under-title"][2]/text()')
            # print tag_field[0]
            # print geo_field[0]
            # print name_field[0]
            # print phone_field[0]
        #     try:
        #         ii=0
        #         for testhand in head:
        #             sheet.write(0,ii,testhand)
        #             ii += 1
        #         sheet.write(row,0,u'重庆')
        #         sheet.write(row,1,u'美食')
        #         sheet.write(row,2,tag_field[0].decode('utf-8'))
        #         sheet.write(row,3,name_field[0].decode('utf-8'))
        #         sheet.write(row,4,geo_field[0].decode('utf-8'))
        #         sheet.write(row,5,phone_field[0].decode('utf-8'))
        #         row += 1
        #         print '正在爬取第%s条：%s' %(row-1,name_field[0])
        #         time.sleep(random.uniform(2.0,10.0))
        #     except IndexError:
        #         print u'%s出错啦，但别理我' %i
        #         continue
        # wbk.save(u'chongqing_food.xls')
        #     print '正在插入%s' % name_field[0]
            row += 1
            try:
                mysql.mysqldata(u"重庆",u"美食",tag_field[0].decode('utf-8'),name_field[0].decode('utf-8'),geo_field[0].decode('utf-8'),phone_field[0].decode('utf-8'))
                print '正在插入第%s条：%s' % (row,name_field[0])
            except IndexError:
                print u"haha,又是你！！"
                continue

            time.sleep(random.uniform(2.0,10.0))
        mysql.cur.close()
        mysql.conn.close()
        return

vip = Meituan()
vip.item_list()

