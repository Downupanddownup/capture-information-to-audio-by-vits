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
    return '获取量子位资讯'


def open_param():
    return False


def plugin_param_list():
    return []


def fetch_article(article_id, article, article_list, param_values):
    print(f'量子位接收到的参数：{param_values}')
    print(f'开始抓取文章{article_id}')

    article_url = "https://www.qbitai.com/" + article_id.replace('-', '/') + ".html"
    response = requests.get(article_url, headers=_get_header())
    soup = BeautifulSoup(response.content, 'html.parser')

    article_read_wrap = soup.find('div', {'class': 'article'})
    text = article_read_wrap.get_text(strip=True)

    title_wrap = soup.find('div', {'class': 'article'}).find('h1', recursive=False)
    title = title_wrap.text.strip()

    text = text.replace(title, '', 1)

    title = title.replace("|", "").replace("?", "")

    publish_date_wrap = soup.find('span', {'class': 'date'})
    publish_date = publish_date_wrap.text.strip()

    publish_time_wrap = soup.find('span', {'class': 'time'})
    publish_time = publish_time_wrap.text.strip()

    text = text.replace(publish_date, '', 1)
    text = text.replace(publish_time, '', 1)

    date_time = datetime.strptime(publish_date, '%Y-%m-%d')
    formatted_date = date_time.strftime('%Y年%m月%d日')

    author_wrap = soup.find('a', {'rel': 'author'})
    author = author_wrap.text.strip()

    print(f'finish{title}article get,publish date = {formatted_date}')
    # print('未知' if not author_match else author_match.group(1))
    # print(text)

    return {
        'article_id': article_id,
        'title': title,
        'author': author,
        'publish_date': formatted_date,
        'content': text,
        'link': article_url,
        'extra': '',
    }


# fetch_article('1362295', None, None, None)


def fetch_article_list():
    print('开始抓取文章列表')
    url = "https://www.qbitai.com/"
    response = requests.get(url, headers=_get_header())
    html_data = response.text

    # print(html_data)

    pattern = r'https://www\.qbitai\.com/(\d{4}/\d{2}/\d{5})\.html'

    matches = re.findall(pattern, html_data)

    print(f'find all : {len(matches)}articles')

    ids = []

    for article_id in matches:
        ids.append({"id": article_id.replace('/', '-')})

    print(f'量子位中已经抓取到的文章列表：{ids}')

    return ids
