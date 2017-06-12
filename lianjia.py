import urllib
import urllib.request
import gzip
import time
import sys
import os
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

logging.basicConfig(filename='lianjia.log',
                    format='%(asctime)s -%(name)s-%(levelname)s-%(module)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %p',
                    level=logging.DEBUG)

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


def gzip_file(src : str, dst : str):
    fin = open(src, 'rb')
    fout = gzip.open(dst, 'wb')

    while True:
        buf = fin.read(1024 * 8)
        if len(buf) < 1:
            break
        fout.write(buf)

    fin.close()
    fout.close()


def send_file_to(attachment_file_name : str):
    _from = '********@163.com'
    _password = '********'

    msg = MIMEMultipart()
    msg['Subject'] = 'lianjia program'
    msg['From'] = _from
    msg['To'] = _from

    part = MIMEText('lianjia by program')
    msg.attach(part)

    part = MIMEApplication(open(attachment_file_name, 'rb').read())

    file_name = os.path.basename(attachment_file_name)

    part.add_header('Content-Disposition', 'attachment', filename=file_name)
    msg.attach(part)
    logging.info('start to connect to smtp.163.com.')
    smtplib.SMTP_SSL("smtp.163.com", port=465, timeout=30)
    logging.info('connected, start to login.')
    smtp.login(_from, _password)
    logging.info('logined, start to send ' + attachment_file_name)
    smtp.sendmail(_from, _from, msg.as_string())  # 发送邮件
    logging.info('sent completed.')
    smtp.close()


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


def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


start_index: int = 1


citys = ['sh' , 'bj', 'hz', 'sz', 'gz']

for city in citys:

    base_url = 'http://' + city + '.lianjia.com/ershoufang/d'

    file_name = cur_file_dir() + '/' + city + '_data_' + time.strftime('%Y%m%d%H%M%S') + '.txt'

    logging.info(file_name)
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
                logging.info('house = [' + str(total_house) + '], url = [' + base_url + str(start_index) + ']')


    # time.sleep(5)
    file.close()
    logging.info('total house = [' + str(total_house) + '], last url = [' + base_url + str(start_index) + ']')


    gzip_file(file_name, file_name + '.gz')

    send_file_to(file_name + '.gz')

    
    
    
