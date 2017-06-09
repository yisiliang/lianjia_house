import urllib
import gzip
import time
from bs4 import BeautifulSoup

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "lianjia_uuid=6fb3dbc5-11dd-4844-a99a-5a21e2eb8503; select_city=310000; cityCode=sh; _gat=1; _gat_u=1; gr_user_id=1cf33e13-3767-4650-86ba-4799177b79a5; _ga=GA1.2.1280411231.1496932060; gr_session_id_970bc0baee7301fa=8df6fa73-f8bd-4743-acb1-00426e91be4d; lianjia_ssid=0fb253ee-29fe-4d32-b61f-bf5880d4008d; ubt_load_interval_b=1496932067419; ubt_load_interval_c=1496932067419; ubta=2299869246.1906553635.1496932061571.1496932066624.1496932067845.2; ubtb=2299869246.1906553635.1496932067847.13F7285058F66F69CE6FB7599A38F0E1; ubtc=2299869246.1906553635.1496932067847.13F7285058F66F69CE6FB7599A38F0E1; ubtd=2",
    "Host": "sh.lianjia.com",
    "Referer": "http//sh.lianjia.com/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def get_content_from_url(url: str):
    try:
        req = urllib.request.Request(url, None, headers)
        rsp = urllib.request.urlopen(req)
    except:
        return ''

    encoding: str = rsp.info().get('Content-Type')
    encoding = encoding.lower()[encoding.lower().find('charset=') + len('charset='):]
    if encoding is None:
        encoding = 'utf-8'

    if rsp.info().get('Content-Encoding') == 'gzip':
        try:
            html = gzip.decompress(rsp.read()).decode(encoding)
        except:
            html = rsp.read().decode(encoding)

    else:
        html = rsp.read().decode(encoding)

    return html


start_index: int = 1

base_url = 'http://sh.lianjia.com/ershoufang/d'

file_name = 'result_' + time.strftime('%Y%m%d%H%M%S') + '.txt'
file = open(file_name, 'w')

total_house: int = 0

while True:

    html_context = get_content_from_url(base_url + str(start_index))

    if len(html_context) <= 100:
        break

    start_index = start_index + 1

    soup = BeautifulSoup(html_context, 'lxml')

    ele_list = soup.select('#js-ershoufangList > div.content-wrapper > div.content > div.m-list > ul > li')

    if len(ele_list) <= 0:
        break

    for ele in ele_list:
        title = ele.select_one('.js_fanglist_title').text
        title = title.replace('\t', '').replace('\n', '').replace(' ', '').replace('|', '')

        size: str = ele.select_one('.info-table > .info-row > .row1-text').text
        size = size.replace('\t', '').replace('\n', '').replace(' ', '')

        sizes = size.split('|')

        split_string = '|||'

        if len(sizes) < 4:
            size = size + split_string[0:4 - len(sizes)]

        price: str = ele.select_one('.info-table > .info-row > .price-item').text
        price = price.replace('\t', '').replace('\n', '').replace(' ', '')

        position_ele = ele.select_one('.info-table > .info-row > .row2-text')
        age = position_ele.text
        age = age.replace('\t', '').replace('\n', '').replace(' ', '')

        price_item = ele.select_one('.info-table > .info-row > .minor').text
        price_item = price_item.replace('\t', '').replace('\n', '').replace(' ', '').replace('|', '')

        file.write(title + '|' + size + '|' + price + '|' + age + '|' + price_item + '\n')

        total_house = total_house + 1
        if total_house % 100 == 0:
            print(str(total_house) + ' ' + str(start_index))

# time.sleep(5)
file.close()
print(str(total_house) + ' ' + str(start_index))

