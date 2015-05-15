__author__ = 'ben'

import logging
import httplib2
import re
import json
import time
import xml.etree.ElementTree as ET
from multiprocessing.dummy import Pool as ThreadPool

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    filename='network.log',
                    filemode='a')


class WeChatNetWork(object):
    def _get_xml_data(self, o_id):
        try:
            ht = httplib2.Http()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
                'HOST': 'weixin.sogou.com',
                'Referer': 'http://weixin.sogou.com/'}
            url = 'http://weixin.sogou.com/gzhjs?openid=%s&page=1&t=%s' % (o_id, int(time.time() * 1000))
            response, content = ht.request(url, 'GET', headers=headers)
            logging.info('网站返回状态值为：%s' % response.status)
            logging.info('程序已获取数据')
            print(content)
            return content
        except Exception as err:
            logging.debug('访问网站失败：')
            logging.info(err)


    def _get_item(self, content):
        try:
            json_content = re.search(r'gzh\((.+)\)', content.decode()).group(1)
            logging.info('解析XML数据成功')
            return json.loads(json_content)['items']
        except Exception as err:
            logging.debug('解析XML数据失败：')
            logging.debug(err)

    def _json_handle(self, data):
        try:
            json_list = []
            for n in range(len(data)):
                xml_text = data[n]
                tree = ET.fromstring(xml_text)
                title = tree[1][3].find('title').text
                url = tree[1][3].find('url').text
                img_link = tree[1][3].find('imglink').text
                json_list.append({'title': title, 'url': url, 'img_link': img_link})
            o_tree = ET.fromstring(data[0])
            o_date = o_tree[1][3].find('date').text
            o_source_name = o_tree[1][3].find('sourcename').text
            logging.info('处理JSON成功')
            return {'source': o_source_name, 'date': o_date, 'data': json_list,
                    'create': time().strftime("%Y-%m-%d %H:%M:%S")}
        except Exception as err:
            logging.debug('json处理失败')
            logging.debug(err)

    def _get_id_handle(self, wx_list):
        return [wx['id'] for wx in wx_list]

    def main(self, o_id):
        data = self._get_xml_data(o_id)
        logging.info('OK完一条，睡3s')
        time.sleep(3)
        return self._json_handle(self._get_item(data))

    def start(self, wx_list):
        logging.info('开始运行')
        id_list = self._get_id_handle(wx_list)
        pool = ThreadPool(7)
        content = pool.map(self.main, id_list)
        pool.close()
        pool.join()
        logging.info('End\n\n-------------- ----------------\n')
        return content


if __name__ == '__main__':
    wx_list = [{'name': '掌上珠海', 'id': 'oIWsFt3u6USV7pSzaKRDrrIkwNTw', 'status': 'true'},
               {'name': '珠海网', 'id': 'oIWsFt8TeMmDIecx3g-uOldwGinA', 'status': 'true'},
               {'name': '珠海特区报', 'id': 'oIWsFt8UggF7k8BJIzxrkZbn7Scc', 'status': 'true'},
               {'name': '南都珠海', 'id': 'oIWsFt1SWYKcTtsOlFn4mi6Vpr_k', 'status': 'true'},
               {'name': '珠海交警', 'id': 'oIWsFt-h49xnmQ_Q0roQfE4NDBY4', 'status': 'true'},
               {'name': '珠海搜房', 'id': 'oIWsFt99Qbyg7AuHKM1PTRaEHXe8', 'status': 'true'},
               {'name': '珠海香洲', 'id': 'oIWsFt1F9bbQXe3NyIR8xNCWQdoE', 'status': 'true'},
               {'name': '珠海人社', 'id': 'oIWsFt22JpmuGfI0bVaWlA9BQzP4', 'status': 'true'},
               {'name': '珠海公安', 'id': 'oIWsFt-uNXAuxZEUMY3HwNiIOQVI', 'status': 'true'},
               {'name': '珠海金湾', 'id': 'oIWsFt7v4V4P5LYvK0BqmewKar3M', 'status': 'true'},
               {'name': '珠海电台交通875', 'id': 'oIWsFt3EkMYg_SbqqNTccmfCGD1Q', 'status': 'true'},
               {'name': '珠海交通执法', 'id': 'oIWsFt_Fnc-GBcmT9FyxHyHhA67A', 'status': 'true'},
               {'name': '文明珠海', 'id': 'oIWsFt_xJARt5eP9WR0mBQa43DJA', 'status': 'true'}]  # 公众列表
    wc = WeChatNetWork()
    data = wc.start(wx_list)
    print(data)
