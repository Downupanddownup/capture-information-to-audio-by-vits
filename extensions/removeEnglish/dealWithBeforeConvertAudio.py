import re


def description():
    return '移除文本中的所有英文字符'


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


def deal_with_article_content(content, Article_1, param_values):
    # print(f'英文字符过滤插件接收参数{param_values}')
    print('开始执行英文字符过滤')
    pattern = r'[a-zA-Z]'  # 匹配所有的英文字符的正则表达式
    txt = re.sub(pattern, '', content)  # 使用空字符串替换匹配的字符
    return txt
