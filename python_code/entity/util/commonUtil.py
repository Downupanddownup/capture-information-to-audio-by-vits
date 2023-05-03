import os
import json
import re
import yaml
import time


class Util:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 初始化方法
        pass

    @staticmethod
    def create_dir(target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

    @staticmethod
    def filter_file_name(file_name):
        # 删除所有非字母数字字符以外的特殊字符，但保留中文字符
        file_name = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', file_name).strip().lower()
        file_name = re.sub(r'[-\s]+', '-', file_name)
        return file_name

    # 指定要删除文件的目录路径
    @staticmethod
    def delete_dir_file(dir_path):
        # 使用 os 模块删除指定目录下的所有文件
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f'已删除文件：{file_path}')
                elif os.path.isdir(file_path):
                    print(f'跳过目录：{file_path}')
            except Exception as e:
                print(f'删除文件失败：{file_path}，{e}')


# 文本文件的读写工具类
class TextFileManager:
    # 写入文本文件数据
    @staticmethod
    def write_to_file(file_path, text_data):
        """将指定路径下的文本文件写入文本数据"""
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text_data)

    # 读取文本文件
    @staticmethod
    def read_from_file(file_path):
        """从指定路径下的文本文件中读取文本数据"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text_data = file.read()
        return text_data


# json文件读写工具类
class JSONFileManager:

    @staticmethod
    def write_to_file(file_path, data):
        """将指定路径下的 JSON 格式文件写入数据"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

    @staticmethod
    def read_from_file(file_path):
        """从指定路径下的 JSON 格式文件中读取数据"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data


# 配置YAML文件管理对象
class YamlManager:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        if not os.path.exists(self.filename):
            self.write_to_file({})
        self.read_from_file()

    def read_from_file(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def write_to_file(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.write_to_file(self.data)


# 自定义异常类型
class CustomError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Timer:
    def __init__(self, info=None):
        self.info = info
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def elapsed_time(self):
        if self.start_time is None:
            raise Exception("Timer is not started")
        if self.end_time is None:
            raise Exception("Timer is not stopped")
        return self.end_time - self.start_time

    def print_second_info(self):
        print(f"{self.info}: %.2f seconds" % self.elapsed_time())