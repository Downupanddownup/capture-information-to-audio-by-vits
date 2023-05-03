# -*- coding: gbk -*-
import requests
import re
import time
import datetime
import os
from bs4 import BeautifulSoup


# �����Ѷ����
def description():
    return '����ץȡdemo'


# �Ƿ����Զ������
def open_param():
    return True


# �Զ�������б�
def plugin_param_list():
    return [
        {
            'param_type': 'Number',  # ��������
            'param_key': 'test_param_1',
            'label': '���ǲ��Բ�������1',
            'value': 101,
        },
        {
            'param_type': 'Dropdown',  # ����
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


# ץȡ��������
def fetch_article(article_id, article, article_list, param_values):
    print(description())
    print(f'article_id��{article_id}')
    print(f'article��{article}')
    print(f'article_list��{article_list}')
    print(f'param_values��{param_values}')
    return {
        'article_id': article_id,
        'title': '���±���',
        'author': 'δ֪',
        'publish_date': '2023��05��03��',
        'content': '��������',
        'link': 'https://www.bilibili.com/',
        'extra': '',
    }


# ��ȡ�����б�
def fetch_article_list():
    return [{'id': 'id1'}, {'id': 'id2'}]
