import importlib
import os
from article import Article
from datetime import datetime


class PluginParamDropdown:
    def __init__(self, param_obj):
        self.label = param_obj.get('label', '下拉类型参数')
        self.value = param_obj.get('default_value', '')
        self.choices = param_obj.get('choices', [])
        self.multiselect = param_obj.get('multiselect', False)

    def get_value(self):
        return self.value


class PluginParamNumber:
    def __init__(self, param_obj):
        self.label = param_obj.get('label', '数字类型参数')
        self.value = param_obj.get('value', 0)

    def get_value(self):
        return self.value


# 插件自定义参数
class PluginParam:
    def __init__(self, param_obj):
        self.type = param_obj.get('param_type', '')  # 参数类型：Number Dropdown
        self.key = param_obj.get('param_key', '')  # 参数key
        self.param = None
        self.value = None
        if self.type == 'Number':
            self.param = PluginParamNumber(param_obj)
        elif self.type == 'Dropdown':
            self.param = PluginParamDropdown(param_obj)
        if self.param is not None:
            self.value = self.param.get_value()


# 文章抓取插件
class ArticleFetchPlugins:
    def __init__(self, name, plugin_module):
        self.name = name
        self.plugin_module = plugin_module
        self.description = self.load_description()
        self.open_param = self.load_open_param()
        self.PluginParam_list = self.load_plugin_param()

    # 获取插件说明
    def load_description(self):
        method = getattr(self.plugin_module, "description")
        return method()

    # 获取是否设置自定义参数 True或者False
    def load_open_param(self):
        method = getattr(self.plugin_module, "open_param")
        return method()

    # 加载自定义插件参数列表
    def load_plugin_param(self):
        method = getattr(self.plugin_module, "plugin_param_list")
        param_list = method()
        return [PluginParam(param) for param in param_list]

    # 抓取文章列表
    # 返回一个数组，由文章的唯一标识构成
    def fetch_article_list(self):
        method = getattr(self.plugin_module, "fetch_article_list")
        return method()

    # 抓取具体文章
    def fetch_article(self, article_id, article, article_list, article_path, param_values):
        method = getattr(self.plugin_module, "fetch_article")
        article_obj = method(article_id, article, article_list, param_values)
        return Article(
            article_path=article_path,
            plugins_name=self.name,
            article_id=article_obj['article_id'],
            title=article_obj['title'],
            author=article_obj['author'],
            content=article_obj['content'],
            link=article_obj['link'],
            publish_date=article_obj['publish_date'],
            collection=False,
            extra=article_obj['extra'],
            is_last_time=True,
            create_time=datetime.now(),
            size=len(article_obj['content'])
        )


# 完成所有文章抓取后，进行文章处理插件
class DealWithAfterFetchAllArticlePlugins:
    def __init__(self, name, plugin_module):
        self.name = name
        self.plugin_module = plugin_module

    # 处理抓取后的文章
    # Article_list 文章列表
    # 返回数据 Article_list
    def deal_with_article(self, Article_list):
        method = getattr(self.plugin_module, "deal_with_article_list")
        return method(Article_list)


# 在文章转换音频之前，进行处理的插件
class DealWithBeforeConvertAudioPlugins:
    def __init__(self, name, plugin_module):
        self.name = name
        self.plugin_module = plugin_module
        self.description = self.load_description()
        self.open_param = self.load_open_param()
        self.PluginParam_list = self.load_plugin_param()

    # 获取插件说明
    def load_description(self):
        method = getattr(self.plugin_module, "description")
        return method()

    # 获取是否设置自定义参数 True或者False
    def load_open_param(self):
        method = getattr(self.plugin_module, "open_param")
        return method()

    # 加载自定义插件参数列表
    def load_plugin_param(self):
        method = getattr(self.plugin_module, "plugin_param_list")
        param_list = method()
        return [PluginParam(param) for param in param_list]

    # 处理文章内容，返回文章内容即可
    def deal_with_article_content(self, Article_1, DealWithBeforeConvertAudioPlugins_param_values):
        method = getattr(self.plugin_module, "deal_with_article_content")
        return method(Article_1.content, Article_1, DealWithBeforeConvertAudioPlugins_param_values)


# 在文章转换音频之后，进行处理的插件
class DealWithAfterConvertAudioPlugins:
    def __init__(self, name, plugin_module):
        self.name = name
        self.plugin_module = plugin_module
        self.description = self.load_description()
        self.open_param = self.load_open_param()
        self.PluginParam_list = self.load_plugin_param()

    # 获取插件说明
    def load_description(self):
        method = getattr(self.plugin_module, "description")
        return method()

    # 获取是否设置自定义参数 True或者False
    def load_open_param(self):
        method = getattr(self.plugin_module, "open_param")
        return method()

    # 加载自定义插件参数列表
    def load_plugin_param(self):
        method = getattr(self.plugin_module, "plugin_param_list")
        param_list = method()
        return [PluginParam(param) for param in param_list]

    # 处理生成的音频，返回处理完毕后，音频的数量
    def deal_with_audio(self, ArticleVoice_list, DealWithAfterConvertAudioPlugins_param_values, default_output_path,
                        default_audio_format):
        method = getattr(self.plugin_module, "deal_with_audio")
        wav_path_list = []
        for articleVoice in ArticleVoice_list:
            for roleVoice in articleVoice.RoleVoice_list:
                wav_path_list.append(roleVoice.get_wav_file_path())
        return method(wav_path_list, ArticleVoice_list, DealWithAfterConvertAudioPlugins_param_values,
                      default_output_path, default_audio_format)


# 插件管理对象
class PluginsManager:
    def __init__(self):
        self.extensions_path = 'extensions'
        self.ArticleFetchPlugins_list = []
        self.DealWithAfterFetchAllArticlePlugins_list = []
        self.DealWithBeforeConvertAudioPlugins_list = []
        self.DealWithAfterConvertAudioPlugins_list = []
        self.load_plugins()

    # 加载各类插件
    def load_plugins(self):
        self.load_article_fetch_plugins()
        self.load_deal_with_after_fetch_all_article_plugins_list()
        self.load_deal_with_before_convert_audio_plugins_list()
        self.load_deal_with_after_convert_audio_plugins_list()

    # 根据模块类型，加载插件
    def load_plugins_by_module_type(self, func, mode_type):
        plugins_list = self.get_plugins_path(mode_type)
        for module_name in plugins_list:
            plugin_module = importlib.import_module(f'{self.extensions_path}.{module_name}.{mode_type}')
            func(module_name, plugin_module)

    # 根据插件类型，获取插件目录
    def get_plugins_path(self, moduleType):
        plugins_list = []
        for root, dirs, files in os.walk(self.extensions_path):
            for file in files:
                if file == moduleType + '.py':
                    plugins_list.append(os.path.basename(root))
        return plugins_list

    # 加载文章抓取插件
    def load_article_fetch_plugins(self):
        module_type = 'articleFetch'
        self.load_plugins_by_module_type(
            lambda module_name, plugin: self.ArticleFetchPlugins_list.append(ArticleFetchPlugins(module_name, plugin)),
            module_type)

    # 加载文章后处理插件
    def load_deal_with_after_fetch_all_article_plugins_list(self):
        module_type = 'dealWithAfterFetchAllArticle'
        self.load_plugins_by_module_type(
            lambda module_name, plugin: self.DealWithAfterFetchAllArticlePlugins_list.append(
                DealWithAfterFetchAllArticlePlugins(module_name, plugin)),
            module_type)

    # 加载音频转换前的预处理插件
    def load_deal_with_before_convert_audio_plugins_list(self):
        module_type = 'dealWithBeforeConvertAudio'
        self.load_plugins_by_module_type(
            lambda module_name, plugin: self.DealWithBeforeConvertAudioPlugins_list.append(
                DealWithBeforeConvertAudioPlugins(module_name, plugin)),
            module_type)

    # 加载音频后处理插件
    def load_deal_with_after_convert_audio_plugins_list(self):
        module_type = 'dealWithAfterConvertAudio'
        self.load_plugins_by_module_type(
            lambda module_name, plugin: self.DealWithAfterConvertAudioPlugins_list.append(
                DealWithAfterConvertAudioPlugins(module_name, plugin)),
            module_type)

    # 根据插件名称，获取文章后处理插件
    # name 插件名称
    def get_deal_with_after_fetch_all_article_plugins(self, plugins_name):
        for plugins in self.DealWithAfterFetchAllArticlePlugins_list:
            if plugins.name == plugins_name:
                return plugins
        return None

    # 根据插件名称，获取文章抓取插件
    def get_article_fetch_plugins_by_name(self, plugins_name):
        for plugins in self.ArticleFetchPlugins_list:
            if plugins.name == plugins_name:
                return plugins
        return None

    # 根据插件名称，获取音频转换前，文章处理插件
    def get_deal_with_before_convert_audio_plugins_by_name(self, plugins_name):
        for plugins in self.DealWithBeforeConvertAudioPlugins_list:
            if plugins.name == plugins_name:
                return plugins
        return None

    # 根据插件名称，获取音频转换前，文章处理插件
    def get_deal_with_after_convert_audio_plugins_by_name(self, plugins_name):
        for plugins in self.DealWithAfterConvertAudioPlugins_list:
            if plugins.name == plugins_name:
                return plugins
        return None
