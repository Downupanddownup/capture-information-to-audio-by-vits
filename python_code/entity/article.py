import os
import sys
import shutil

from datetime import datetime

# 将模块所在目录添加到 Python 模块搜索路径中
module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_dir)

from util.commonUtil import JSONFileManager
from util.commonUtil import TextFileManager
from util.commonUtil import Util


# 文章对象
class Article:
    # plugins_name 文章的来源，对应插件名称
    # article_id 文章的唯一表示
    # title 文章的唯一标识
    # author 文章作者
    # content 文章内容
    # link 文章链接
    # path 文章的本地存储目录，相对路径
    # collection 文章是否被收藏
    # publish_date 文章发布的日期
    # is_last_time 是否最近一次转换
    # size 文章内容的大小
    def __init__(self, article_path=None, plugins_name=None, article_id=None, title=None, author=None, content=None,
                 link=None,
                 publish_date=None, collection=None,
                 extra=None, create_time=None, is_last_time=False, size=0):
        if create_time is not None:
            formatted_date = create_time.strftime("%Y%m%d")
        else:
            formatted_date = datetime.now().strftime("%Y%m%d")

        self.plugins_name = plugins_name
        self.article_id = article_id
        self.title = title
        self.author = author
        self.content = content
        self.link = link
        self.path = f'{article_path}/{plugins_name}/{formatted_date}/{Util.filter_file_name(title)}_{article_id}'
        self.collection = collection
        self.extra = extra
        self.create_time = create_time
        self.publish_date = publish_date
        self.is_last_time = is_last_time
        self.size = size

    def is_equals(self, Article_other):
        return self.plugins_name == Article_other.plugins_name and self.article_id == Article_other.article_id

    def get_base_attar_obj(self):
        return {
            "plugins_name": self.plugins_name,
            "article_id": self.article_id,
            "title": self.title,
            "author": self.author,
            "link": self.link,
            "create_time": self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "publish_date": self.publish_date,
            "collection": self.collection,
            "size": self.size
        }

    def get_delete_attar_obj(self):
        return {
            "plugins_name": self.plugins_name,
            "article_id": self.article_id,
            "title": self.title,
        }

    def get_collection_txt(self):
        return '已收藏' if self.collection else '未收藏'

    def get_all_attar_but_content_obj(self):
        return {
            "plugins_name": self.plugins_name,
            "article_id": self.article_id,
            "title": self.title,
            "author": self.author,
            "link": self.link,
            "create_time": self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "collection": self.collection,
            "extra": self.extra,
            "size": self.size,
        }

    def get_json_path(self):
        return f'{self.path}/{self.article_id}.json'

    def get_txt_path(self):
        return f'{self.path}/{self.title}.txt'

    # 加载文章内容
    def load_content(self):
        if self.content is None:
            self.content = TextFileManager.read_from_file(self.get_txt_path())
            self.size = len(self.content)
        return self.content


# 角色朗读信息
class RoleVoice:
    def __init__(self, Role_1, Article_1):
        self.Role_1 = Role_1
        self.Article_1 = Article_1
        self.wav_file_path = None  # wav音频文件存储地址

    def get_base_name(self):
        return self.Article_1.title + "-" + self.Role_1.get_specker_info()

    def get_wav_file_path(self):
        self.wav_file_path = f'{self.Article_1.path}/{self.get_base_name()}.wav'
        return self.wav_file_path

    def get_mp3_file_path(self):
        return f'{self.Article_1.path}/{self.get_base_name()}.mp3'


# 文章音频转换后的对象
class ArticleVoice:
    def __init__(self, Article_1, RoleVoice_list):
        self.Article_1 = Article_1
        self.RoleVoice_list = RoleVoice_list


# 文章管理类
class ArticleManager:
    def __init__(self, article_path):
        self.article_path = article_path
        self.Article_normal_list = []  # 正常的文章列表
        self.Article_deleted_list = []  # 已删除的文章
        Util.create_dir(self.article_path)
        self.load_normal_articles()
        self.load_delete_articles()

    def get_normal_articles_json_path(self):
        return self.article_path + '/all_normal_articles.json'

    def get_delete_articles_json_path(self):
        return self.article_path + '/delete_articles.json'

    # 加载历史文章
    def load_normal_articles(self):
        path = self.get_normal_articles_json_path()
        if not os.path.exists(path):
            JSONFileManager.write_to_file(path, [])
        array = JSONFileManager.read_from_file(path)
        for item in array:
            self.Article_normal_list.append(Article(
                article_path=self.article_path,
                plugins_name=item['plugins_name'],
                article_id=item['article_id'],
                title=item['title'],
                author=item['author'],
                link=item['link'],
                publish_date=item['publish_date'],
                collection=item['collection'],
                size=item.get('size', 0),
                create_time=datetime.strptime(item['create_time'], '%Y-%m-%d %H:%M:%S')
            ))
        # 文章排序
        self.Article_normal_list.sort(key=lambda x: x.create_time, reverse=True)

    # 加载已删除的文章
    def load_delete_articles(self):
        path = self.get_delete_articles_json_path()
        if not os.path.exists(path):
            JSONFileManager.write_to_file(path, [])
        array = JSONFileManager.read_from_file(path)
        for item in array:
            self.Article_deleted_list.append(Article(
                article_path=self.article_path,
                plugins_name=item['plugins_name'],
                article_id=item['article_id'],
                title=item['title']
            ))

    # 将上传的文本转化为文章对象
    # uploadTxtFilePaths 上传文件txt的绝对路径
    def convert_txt(self, upload_txt_file_paths):
        Article_list = []
        for temp_file in upload_txt_file_paths:
            file_path = temp_file.name
            print(file_path)
            file_name_with_ext = os.path.basename(file_path)  # 获取文件名，包含扩展名
            file_name, ext = os.path.splitext(file_name_with_ext)  # 分离文件名和扩展名
            if 'txt' not in ext:
                print(f'文件{file_path}，并非txt格式，跳过')
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                Article_new = Article(
                    article_path=self.article_path,
                    plugins_name='local',
                    article_id=file_name,
                    title=file_name,
                    author='未知',
                    content=content,
                    link=None,
                    publish_date=None,
                    collection=False,
                    extra=None,
                    is_last_time=True,
                    create_time=datetime.now(),
                    size=len(content)
                )
                self.add_article(Article_new)
                Article_list.append(Article_new)
        return Article_list

    # 判断文章是否已存在
    # articleId 文章唯一标识符
    # articlePluginsName 插件名称
    def exists_article(self, article_id, plugins_name):
        for article in self.Article_normal_list:
            if article.plugins_name == plugins_name and article.article_id == article_id:
                return True
        return False

    # 判断文章是否已存在
    # articleId 文章唯一标识符
    # articlePluginsName 插件名称
    def exists_delete_article(self, article_id, plugins_name):
        for article in self.Article_deleted_list:
            if article.plugins_name == plugins_name and article.article_id == article_id:
                return True
        return False

    # 新增文章，并持久化到本地
    # Article_new 新增文章对象
    def add_article(self, Article_new):
        self.save_one_article(Article_new)
        self.Article_normal_list.append(Article_new)
        self.save_all_normal_list()

    # 将文章对象更新到本地
    # Article_list文章列表
    def save_article_list(self, Article_list):
        for Article_item in Article_list:
            self.save_one_article(Article_item)
        self.save_all_normal_list()

    # 保存单个文件
    def save_one_article(self, Article_1):
        Util.create_dir(Article_1.path)
        # print(f'创建目录：{Article_1.path}')
        JSONFileManager.write_to_file(Article_1.get_json_path(), Article_1.get_all_attar_but_content_obj())
        TextFileManager.write_to_file(Article_1.get_txt_path(), Article_1.content)

    # 更新列表数据
    def save_all_normal_list(self):
        array = []
        for article in self.Article_normal_list:
            array.append(article.get_base_attar_obj())
        JSONFileManager.write_to_file(self.get_normal_articles_json_path(), array)

    # 更新列表数据
    def save_deleted_article_list(self):
        array = []
        for article in self.Article_deleted_list:
            array.append(article.get_delete_attar_obj())
        JSONFileManager.write_to_file(self.get_delete_articles_json_path(), array)

    def delete_article(self, Article_1):
        shutil.rmtree(Article_1.path)
        self.remove_from_normal_list(Article_1)
        self.add_delete_articles(Article_1)

    def remove_from_normal_list(self, Article_1):
        temp_list = []
        for article in self.Article_normal_list:
            if not article.is_equals(Article_1):
                temp_list.append(article)
        self.Article_normal_list = temp_list
        self.save_all_normal_list()

    def add_delete_articles(self, Article_1):
        self.Article_deleted_list.append(Article_1)
        self.save_deleted_article_list()
