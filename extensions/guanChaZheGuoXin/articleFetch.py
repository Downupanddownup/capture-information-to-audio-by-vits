# -*- coding: gbk -*-
import requests
import re
import time
import datetime
import os
from bs4 import BeautifulSoup


def _get_header():
    return {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34',
        'referer': 'https://cn.bing.com/'
    }


def description():
    return '��ȡ����ͽ���Ĺ۲��߹���������Ѷ'


def open_param():
    return False


def plugin_param_list():
    return [
        {
            'param_type': 'Number',
            'param_key': 'test_param_1',
            'label': '���ǲ��Բ�������1',
            'value': 101,
        },
        {
            'param_type': 'Dropdown',
            'param_key': 'test_param_2',
            'label': '���ǲ��Բ�������2',
            'default_value': '����',
            'multiselect': True,
            'choices': ['�Ǻ�', '����', '����']
        },
        {
            'param_type': 'Dropdown',
            'param_key': 'test_param_3',
            'label': '���ǲ��Բ�������3',
            'default_value': '����2',
            'multiselect': False,
            'choices': ['�Ǻ�2', '����2', '����2']
        },
    ]


def fetch_article(article_id, article, article_list, param_values):
    print(f'�۲������յ��Ĳ�����{param_values}')
    article_url = 'https://www.guancha.cn/internation/' + article_id + '.shtml'
    response = requests.get(article_url, headers=_get_header())
    soup = BeautifulSoup(response.content, 'html.parser')

    article_read_wrap = soup.find('div', {'class': 'content all-txt'})
    text = article_read_wrap.get_text(strip=True)

    # print(text)

    title_wrap = soup.find('h3')
    title = title_wrap.text.strip()

    title = title.replace("|", "").replace("?", "")

    content = f'{str(text)}'

    publish_date_wrap = soup.find('div', {'class': 'time'}).find('span', recursive=False)
    publish_date = publish_date_wrap.text.strip()

    # print(f'publish_date={publish_date}')

    date_time = datetime.datetime.strptime(publish_date, '%Y-%m-%d %H:%M:%S')
    formatted_date = date_time.strftime('%Y��%m��%d��')

    # print(f'formatted_date={formatted_date}')

    return {
        'article_id': article_id,
        'title': title,
        'author': 'δ֪',
        'publish_date': formatted_date,
        'content': content,
        'link': article_url,
        'extra': '',
    }


# fetch_article('2023_04_29_690389',None,None,None)

# if __name__ == '__main__':
def fetch_article_list():
    url = "https://www.guancha.cn/internation?s=dhguoji"
    response = requests.get(url, headers=_get_header())
    html_data = response.text

    # print(html_data)

    today = datetime.date.today()
    date_string = today.strftime('%Y_%m_%d')
    # date_string = '2023_04_22'

    yesterday = today - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y_%m_%d')

    # print(f'date_string={date_string};yesterday_str={yesterday_str}')

    # print(html_data)

    ids = []

    ids.extend(get_list_by_date(date_string, html_data))
    ids.extend(get_list_by_date(yesterday_str, html_data))

    return ids


def get_list_by_date(date_string, html_data):
    # pattern = r"internation/(\d{4}_\d{2}_\d{2}_\w+)\.shtml"
    pattern = r"internation/({0}_\w+)\.shtml".format(date_string)

    print(pattern)

    matches = re.findall(pattern, html_data)

    matches = list(set(matches))

    ids = []

    for article_id in matches:
        print(article_id)
        ids.append({"id": article_id})

    return ids
