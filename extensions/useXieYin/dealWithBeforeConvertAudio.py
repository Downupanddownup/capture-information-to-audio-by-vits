import re
import os
import json
import regex

_base_path = './extensions/useXieYin'


class ReplaceItem:
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def get_json(self):
        return {
            'old': self.old,
            'new': self.new,
        }


class ReplaceUtil:
    def __init__(self):
        self.ReplaceItem_list = []
        self._load_match_words()

    def _load_match_words(self):
        file_path = f'{_base_path}/match_words.json'
        if not os.path.isfile(file_path):
            with open(file_path, "w") as f:
                json.dump([], f)
        with open(file_path, encoding='utf-8') as f:
            array = json.load(f)
            for item in array:
                ReplaceItem_1 = ReplaceItem(item['old'], item['new'])
                self.ReplaceItem_list.append(ReplaceItem_1)

    # def match_words(self, word):
    #     for item in self.ReplaceItem_list:
    #         pattern = re.compile(fr'^{re.escape(item.old)}')
    #         if pattern.match(word):
    #             return True
    #     return False

    def match_words(self, word):
        for item in self.ReplaceItem_list:
            if word in item.old:
                return True
        return False


def description():
    return f'使用对照表替换原英文单词，如果需要扩充对照表内容，请在{_base_path}/match_words.json，添加新的转换组'


def open_param():
    return True


def plugin_param_list():
    return [
        {
            'param_type': 'Dropdown',
            'param_key': 'is_output_file',
            'label': '是否输出每篇文章未匹配的英文单词？',
            'default_value': '不输出',
            'multiselect': False,
            'choices': ['不输出', '输出']
        },
    ]


def get_value_by_key(param_values,key):
    for param in param_values:
        if param.get('key') == key:
            return param.get('value')
    return None


def deal_with_article_content(content, Article_1, param_values):
    # 定义字符边界 常规分隔符或中文或中文标点
    character_boundary = '\\b|[\\u4e00-\\u9fa5\\u3000-\\u303f\\uff00-\\uffef]'

    # test_content = re.sub(r'(?P<b1>{0}){1}(?P<b2>{0})'.format(character_boundary, 'is a sample'),
    #                       '\g<b1>\g<b2>', content,
    #                       flags=re.IGNORECASE)
    # print(f'test_content={test_content}')

    # print(f'英文字符过滤插件接收参数{param_values}')
    print(f'开始执行{description()}')

    new_content = content
    # 加载匹配字段
    ReplaceUtil_1 = ReplaceUtil()
    # 匹配配置文件中设置的字符对

    for item in ReplaceUtil_1.ReplaceItem_list:
        new_content = re.sub(r'(?P<b1>{0}){1}(?P<b2>{0})'.format(character_boundary, item.old), f'\g<b1>{item.new}\g<b2>', new_content,
                             flags=re.IGNORECASE)

    # 定义一个正则表达式，用于匹配所有的英文单词
    word_pattern = re.compile(r'({0})([a-zA-Z]+)({0})'.format(character_boundary))
    # 从字符串中匹配所有的英文单词
    matches = word_pattern.findall(new_content)
    # 遍历匹配结果，并将每个单词替换为带有后缀“_0”的新字符串

    ReplaceItem_list = []

    for match_result in matches:
        match = match_result[1]
        # print(match)
        if ReplaceUtil_1.match_words(match):
            pass
        else:
            # print(f'不存在的：{match}')
            ReplaceItem_list.append(ReplaceItem(match, ''))
            new_content = re.sub(r'(?P<b1>{0}){1}(?P<b2>{0})'.format(character_boundary, match), '\g<b1>\g<b2>', new_content)
        # new_content = new_content.replace(match, match + "_0")
        # new_content = re.sub(r'\b{}\b'.format(match), '{}_0'.format(match), new_content)

    # print(new_content)

    is_output_file = get_value_by_key(param_values,'is_output_file')
    if is_output_file == '输出':
        with open(f'{_base_path}/{Article_1.title}.json', 'w', encoding='utf-8') as f:
            file_json = [item.get_json() for item in ReplaceItem_list]
            json.dump(file_json, f, indent=4)

        with open(f'{_base_path}/{Article_1.title}.txt', 'w', encoding='utf-8') as f:
            f.write(new_content)

    return new_content


# deal_with_article_content("This 你好is a sample花花 text for testing purpose.", None, None)

# character_boundary = '\\b|[\\u4e00-\\u9fa5\\u3000-\\u303f\\uff00-\\uffef]'
#
# new_content = '在离职并加入OpenAI之前，'
#
# word_pattern = re.compile(r'({0})([a-zA-Z]+)({0})'.format(character_boundary))
# # 从字符串中匹配所有的英文单词
# matches = word_pattern.findall(new_content)
# # 遍历匹配结果，并将每个单词替换为带有后缀“_0”的新字符串
#
# for match in matches:
#     print(match[1])