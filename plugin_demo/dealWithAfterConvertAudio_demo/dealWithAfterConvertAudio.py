import os
import glob
import wave
import uuid
from pydub import AudioSegment


# 描述插件作用
def description():
    return '处理输出后的音频demo'


# 是否开启自定义参数
def open_param():
    return True


# 自定义参数列表
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


# 处理音频
# wav_path_list 输出的wav音频文件所在路径的列表
# ArticleVoice_list 包含了文章、演讲人信息和每个演讲人转换后的wav音频所在路径
# param_values 自定义参数
# default_output_path 默认的音频输出路径
# default_audio_format 默认的音频输出格式，mp3或wav
def deal_with_audio(wav_path_list, ArticleVoice_list, param_values, default_output_path, default_audio_format):
    print(description())
    print(f'wav_path_list:{wav_path_list}')
    print(f'ArticleVoice_list"')
    print_array_props(ArticleVoice_list)
    print(f'param_values:{param_values}')
    print(f'default_output_path:{default_output_path}')
    print(f'default_audio_format:{default_audio_format}')
    print(f'完成音频处理')


def print_array_props(array):
    for obj in array:
        obj_dict = vars(obj)
        for key, value in obj_dict.items():
            if isinstance(value, list):
                for item in value:
                    print_dict_recursive(vars(item))
            else:
                if isinstance(value, str):
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: {value.__dict__}")


def print_dict_recursive(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            print_dict_recursive(value)
        else:
            if isinstance(value, str):
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value.__dict__}")
