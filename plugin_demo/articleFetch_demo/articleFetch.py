# -*- coding: gbk -*-
import requests
import re
import time
import datetime
import os
from bs4 import BeautifulSoup


# 插件资讯描述
def description():
    return '文章抓取demo'


# 是否开启自定义参数
def open_param():
    return True


# 自定义参数列表
def plugin_param_list():
    return [
        {
            'param_type': 'Number',  # 数字输入
            'param_key': 'test_param_1',
            'label': '这是测试参数数字1',
            'value': 101,
        },
        {
            'param_type': 'Dropdown',  # 下拉
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


# 抓取文章内容
def fetch_article(article_id, article, article_list, param_values):
    print(description())
    print(f'article_id：{article_id}')
    print(f'article：{article}')
    print(f'article_list：{article_list}')
    print(f'param_values：{param_values}')
    return {
        'article_id': article_id,
        'title': '文章标题',
        'author': '未知',
        'publish_date': '2023年05月03日',
        'content': '文章内容',
        'link': 'https://www.bilibili.com/',
        'extra': '',
    }


# 获取文章列表
def fetch_article_list():
    return [{'id': 'id1'}, {'id': 'id2'}]
