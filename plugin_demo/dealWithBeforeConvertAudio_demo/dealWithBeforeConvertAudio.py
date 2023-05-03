import re


# 描述插件的作用
def description():
    return '音频转换前，处理文本内容演示demo'


# 是否启用自定义插件
def open_param():
    return True


# 自定义插件列表
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


# 处理文本内容
# content 待处理的文本内容
# Article_1 文章信息
# param_values 自定义参数
def deal_with_article_content(content, Article_1, param_values):
    print(description())
    print(f'content={content}')
    print(f'Article_1={Article_1.__dict__}')
    print(f'param_values={param_values}')
    return '处理后的文本：' + content
