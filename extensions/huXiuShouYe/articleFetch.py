# -*- coding: utf-8 -*-

import requests
import re
import time
import os
from bs4 import BeautifulSoup
from datetime import datetime


def _get_header():
    return {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34',
        'referer': 'https://cn.bing.com/'
    }


def description():
    return '获取虎嗅首页资讯'


def open_param():
    return False


def plugin_param_list():
    return [
        {
            'param_type': 'Number',
            'param_key': 'test_param_1',
            'label': '这是测试参数数字1',
            'value': 101,
        },
        {
            'param_type': 'Dropdown',
            'param_key': 'test_param_2',
            'label': '这是测试参数下拉2',
            'default_value': '哈哈',
            'multiselect': True,
            'choices': ['呵呵', '哈哈', '花花']
        },
        {
            'param_type': 'Dropdown',
            'param_key': 'test_param_3',
            'label': '这是测试参数下拉3',
            'default_value': '花花2',
            'multiselect': False,
            'choices': ['呵呵2', '哈哈2', '花花2']
        },
    ]


def fetch_article(article_id, article, article_list, param_values):
    print(f'虎嗅接收到的参数：{param_values}')
    print(f'开始抓取文章{article_id}')
    article_url = "https://www.huxiu.com/article/" + article_id + ".html"
    response = requests.get(article_url, headers=_get_header())
    soup = BeautifulSoup(response.content, 'html.parser')

    article_read_wrap = soup.find('div', {'id': 'js-article-read-wrap'})
    text = article_read_wrap.get_text(strip=True)

    title_wrap = soup.find('h1', {'class': 'article__title'})
    title = title_wrap.text.strip()

    text = text.replace(title, '', 1)

    title = title.replace("|", "").replace("?", "")

    publish_date_wrap = soup.find('span', {'class': 'article__time'})
    publish_date = publish_date_wrap.text.strip()

    text = text.replace(publish_date, '', 1)

    date_time = datetime.strptime(publish_date, '%Y-%m-%d %H:%M')
    formatted_date = date_time.strftime('%Y年%m月%d日')

    # 定义正则表达式，匹配 "作者：" 后的任意非空白字符
    pattern_author = r'作者：\s*([a-zA-Z0-9\u4e00-\u9fa5]+)'
    # 在每个字符串中搜索匹配的部分
    author_match = re.search(pattern_author, text)

    print(f'finish{title}article get,publish date = {formatted_date}')
    # print('未知' if not author_match else author_match.group(1))
    # print(text)

    return {
        'article_id': article_id,
        'title': title,
        'author': '未知' if not author_match else author_match.group(1),
        'publish_date': formatted_date,
        'content': text,
        'link': article_url,
        'extra': '',
    }


# fetch_article('1362295', None, None, None)


def fetch_article_list():
    print('开始抓取文章列表')
    url = "https://www.huxiu.com/"
    response = requests.get(url, headers=_get_header())
    html_data = response.text

    # print(html_data)

    pattern = r'"aid":"(\d+)"'

    matches = re.findall(pattern, html_data)

    print(f'find all : {len(matches)}articles')

    i = 0

    ids = []

    for article_id in matches:
        ids.append({"id": article_id})

    print(f'虎嗅中已经抓取到的文章列表：{ids}')

    return ids
