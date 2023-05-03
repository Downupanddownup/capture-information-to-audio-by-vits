import os
import sys
from math import ceil

# 将模块所在目录添加到 Python 模块搜索路径中
module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_dir)

from article import ArticleManager
import datetime


# 分页参数
class Page:
    def __init__(self, page_no=1, page_size=50, length=0, sort_column='create_time', sort_desc='desc'):
        self.page_no = page_no
        self.page_size = page_size
        self.length = length
        self.sort_column = sort_column  # 排序字段
        self.sort_desc = sort_desc  # 升降序，默认降序

    def get_all_page(self):
        return ceil(self.length / self.page_size)


# 文章搜索参数
class SearchParam:
    def __init__(self, search_type='last_time', plugins_name=None, article_id=None, title=None, author=None,
                 collection=None, publish_date_start=None, publish_date_end=None,
                 create_time_start=None, create_time_end=None):
        self.search_type = search_type  # 文章搜索类型 last_time最近一次；today 今天；all 所有；collection 收藏的
        self.plugins_name = plugins_name  # 文章来源的插件名称
        self.article_id = article_id  # 文章的唯一标识
        self.title = title  # 文章的标题
        self.author = author  # 文章的作者
        self.collection = collection  # 文章是否被收藏
        self.publish_date_start = publish_date_start  # 发布日期-开始日期
        self.publish_date_end = publish_date_end  # 发布日期-结束日期
        self.create_time_start = create_time_start  # 捕获时间
        self.create_time_end = create_time_end  # 创建时间

    def is_equal(self, other):
        # 比较所有属性是否相等
        return vars(self) == vars(other)


class ArticleSearchSave:
    def __init__(self, article_path):
        self.ArticleManager_1 = ArticleManager(article_path)
        self.SearchParam_1 = None
        self.Article_result_list = []
        self.sort_column = 'create_time'  # 排序字段
        self.sort_desc = 'desc'  # 升降序，默认降序

    def get_all_article_normal_list(self):
        return self.ArticleManager_1.Article_normal_list

    def get_all_article_source(self):
        sources = [article.plugins_name for article in self.ArticleManager_1.Article_normal_list]
        sources = list(set(sources))
        return sources

    # 根据条件搜索文章
    def search_article(self, SearchParam_1, Page_1):
        # print('开始搜索')
        # print(SearchParam_1.__dict__)
        # 如果查询条件一致，返回缓存结果
        if self.SearchParam_1 is not None and self.SearchParam_1.is_equal(SearchParam_1) and (
                self.sort_column == Page_1.sort_column and self.sort_desc == Page_1.sort_desc):
            return self.Article_result_list[(Page_1.page_no - 1) * Page_1.page_size:Page_1.page_no * Page_1.page_size]

        if self.sort_column != Page_1.sort_column or self.sort_desc != Page_1.sort_desc:
            self.sort_column = Page_1.sort_column
            self.sort_desc = Page_1.sort_desc
            self.sort_article()

        Article_result_list = []
        for article in self.ArticleManager_1.Article_normal_list:
            # 最近一次
            if SearchParam_1.search_type == 'is_last_time':
                if not article.is_last_time:
                    continue
            #  今天
            elif SearchParam_1.search_type == 'today':
                today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                if article.create_time is None:
                    print(f'文章{article.title}，抓取时间为空')
                    continue
                if article.create_time < today:
                    continue
            #  收藏的
            elif SearchParam_1.search_type == 'collection':
                if not article.collection:
                    continue
                # print(f'已收藏：{article.title}')
            # 过滤文章来源
            if SearchParam_1.plugins_name is not None and SearchParam_1.plugins_name != '全部':
                if SearchParam_1.plugins_name != article.plugins_name:
                    continue
            # 过滤文章id
            if SearchParam_1.article_id is not None and len(SearchParam_1.article_id) > 0:
                if SearchParam_1.article_id != article.article_id:
                    continue
            # 过滤文章标题
            if SearchParam_1.title is not None and len(SearchParam_1.title) > 0:
                if SearchParam_1.title not in article.title:
                    continue
            # 过滤文章作者
            if SearchParam_1.author is not None and len(SearchParam_1.author) > 0:
                if SearchParam_1.author not in article.author:
                    continue
            # 过滤发布时间
            if SearchParam_1.publish_date_start is not None:
                if SearchParam_1.publish_date_start > article.publish_date:
                    continue
            # 过滤发布时间
            if SearchParam_1.publish_date_end is not None:
                if SearchParam_1.publish_date_end < article.publish_date:
                    continue
            # 过滤捕获时间
            if SearchParam_1.create_time_start is not None:
                if SearchParam_1.create_time_start > article.create_time:
                    continue
            # 过滤捕获时间
            if SearchParam_1.create_time_end is not None:
                if SearchParam_1.create_time_end < article.create_time:
                    continue
            Article_result_list.append(article)
        self.Article_result_list = Article_result_list
        # print(self.Article_result_list)
        Page_1.length = len(Article_result_list)
        return [Page_1, Article_result_list[(Page_1.page_no - 1) * Page_1.page_size:Page_1.page_no * Page_1.page_size]]

    def exists_article(self, article_id, article_plugins_name):
        return self.ArticleManager_1.exists_article(article_id, article_plugins_name)

    def exists_delete_article(self, article_id, article_plugins_name):
        return self.ArticleManager_1.exists_delete_article(article_id, article_plugins_name)

    def add_article(self, Article_new):
        return self.ArticleManager_1.add_article(Article_new)

    def convert_txt(self, upload_txt_file_paths):
        return self.ArticleManager_1.convert_txt(upload_txt_file_paths)

    def save_article_list(self, Article_list):
        return self.ArticleManager_1.save_article_list(Article_list)

    def sort_article(self):
        # print(f'开始排序,getattr(x, self.sort_column)={self.sort_column};self.sort_desc == "desc":{self.sort_desc}')
        # 文章排序
        self.get_all_article_normal_list().sort(key=lambda x: getattr(x, self.sort_column),
                                                reverse=self.sort_desc == 'desc')

    def delete_article(self, Article_1):
        self.ArticleManager_1.delete_article(Article_1)

    def collect_all_select(self, Article_list):
        for article in self.ArticleManager_1.Article_normal_list:
            if len([item for item in Article_list if article.is_equals(item)]) > 0:
                article.collection = True
        self.ArticleManager_1.save_all_normal_list()

    def cancel_collect_all_select(self, Article_list):
        for article in self.ArticleManager_1.Article_normal_list:
            if len([item for item in Article_list if article.is_equals(item)]) > 0:
                article.collection = False
        self.ArticleManager_1.save_all_normal_list()
