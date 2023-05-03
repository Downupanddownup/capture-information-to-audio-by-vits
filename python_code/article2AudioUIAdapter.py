import random
import os
from entity.article_search_save import SearchParam, Page


# 适配器，用来连接UI和article2audio对象
class ArticleDownloadAdapter:
    __instance = None

    def __init__(self, Article2Audio_1):
        if ArticleDownloadAdapter.__instance is not None:
            raise Exception("Cannot create multiple instances of ArticleDownloadAdapter singleton class")
        else:
            self.Article2Audio_1 = Article2Audio_1
            ConfigManagerSys_1 = self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1
            ConfigManagerConfig_1 = self.Article2Audio_1.ConfigManager_1.ConfigManagerConfig_1
            self.article_save_path = ConfigManagerConfig_1.get_article_path()  # 文件存放路径
            self.all_article_plugins = self.Article2Audio_1.get_all_article_plugins_list()  # 获取所有文章抓取插件
            self.selected_article_plugins = ConfigManagerSys_1.get_selected_article_plugins()  # 选择文章插件
            self.upload_txt = False  # 是否选择上传文章插件
            self.upload_txt_file_paths = []  # 上传文件路径的集合
            self.fetch_interval = ConfigManagerSys_1.get_fetch_interval()  # 文章抓取间隔：秒
            self.fetch_type_list = ValueTipsConvert([
                ['batch', '批量抓取'],
                ['single', '单个抓取'],
            ])
            self.fetch_type = 'batch'  # 默认抓取类型
            self.selected_single_article_plugin = None  # 单个文章抓取时，对应插件
            self.fetch_article_ids = None  # 待抓取的文章id数量
            self.is_filter_article = False  # 是否过滤文章抓取
            self.filter_article_characters_number = ConfigManagerSys_1.get_filter_article_characters_number()  # 文章过滤字符数量标准
            ArticleDownloadAdapter.__instance = self

    @staticmethod
    def get_instance(Article2Audio_1):
        if not ArticleDownloadAdapter.__instance:
            ArticleDownloadAdapter(Article2Audio_1)
        return ArticleDownloadAdapter.__instance

    def get_config_config(self):
        return self.Article2Audio_1.ConfigManager_1.ConfigManagerConfig_1

    def get_sys_config(self):
        return self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1

    # 保存当前选中的插件列表
    def save_selected_article_plugins(self, selects):
        self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1.set_selected_article_plugins(selects)
        self.selected_article_plugins = selects

    # 修改上传文本的状态
    def change_upload_txt(self, val):
        self.upload_txt = val

    # 上传文件列表
    def change_upload_txt_files(self, files):
        self.upload_txt_file_paths = files

    # 修改文章抓取间隔
    def change_fetch_interval(self, fetch_interval):
        self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1.set_fetch_interval(fetch_interval)
        self.fetch_interval = fetch_interval

    def save_filter_article_characters_number(self, filter_article_characters_number):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_filter_article_characters_number(filter_article_characters_number)
        self.filter_article_characters_number = filter_article_characters_number

    # 开始抓取
    def start_fetch_articles(self, batch_param_values, single_param_values):
        if self.fetch_type == 'batch':
            if len(self.selected_article_plugins) == 0 and not self.upload_txt:
                return '请选择抓取插件，或上传txt文件'
            if self.upload_txt:
                if len(self.upload_txt_file_paths) == 0:
                    return '请选择上传txt文件'
            return self.Article2Audio_1.start_fetch_articles(
                self.selected_article_plugins,
                batch_param_values,
                '不处理',
                self.upload_txt_file_paths,
                self.fetch_interval,
                self.is_filter_article,
                self.filter_article_characters_number,
            )
        elif self.fetch_type == 'single':
            if self.selected_single_article_plugin is None or len(self.selected_single_article_plugin) == 0:
                return '请选择插件'
            if self.fetch_article_ids is None or len(self.fetch_article_ids) == 0:
                return '请输入文章id'
            return self.Article2Audio_1.start_fetch_single_article(
                self.selected_single_article_plugin,
                single_param_values,
                self.fetch_article_ids
            )


class ArticleDataframeColumn:
    def __init__(self, header_id, header_name, column_type):
        self.header_id = header_id
        self.header_name = header_name
        self.column_type = column_type


class ArticleDataframe:
    def __init__(self):
        self.columns = []
        self.columns.append(ArticleDataframeColumn('title', '文章标题', 'str'))
        self.columns.append(ArticleDataframeColumn('打开目录', '打开目录', 'str'))
        self.columns.append(ArticleDataframeColumn('打开txt', '打开txt', 'str'))
        self.columns.append(ArticleDataframeColumn('author', '文章作者', 'str'))
        self.columns.append(ArticleDataframeColumn('publish_date', '发布日期', 'date'))
        self.columns.append(ArticleDataframeColumn('plugins_name', '来源插件', 'str'))
        self.columns.append(ArticleDataframeColumn('article_id', '文章id', 'str'))
        self.columns.append(ArticleDataframeColumn('size', '文章大小', 'number'))
        # self.columns.append(ArticleDataframeColumn('link', '文章链接', 'str'))
        self.columns.append(ArticleDataframeColumn('create_time', '抓取时间', 'date'))
        self.columns.append(ArticleDataframeColumn('get_collection_txt', '是否收藏', 'str'))
        self.selected_column_names = [column.header_name for column in self.columns]

    def change_selected_column_names(self, selected_column_names):
        self.selected_column_names = selected_column_names

    def get_header_names(self):
        return [column.header_name for column in self.columns if column.header_name in self.selected_column_names]

    def get_column_types(self):
        return [column.column_type for column in self.columns if column.header_name in self.selected_column_names]

    def get_header_ids(self):
        return [column.header_id for column in self.columns if column.header_name in self.selected_column_names]

    def get_column_values(self, Article_list):
        header_ids = self.get_header_ids()
        column_values = []
        for article in Article_list:
            column = []
            for header_id in header_ids:
                value = None
                attar = getattr(article, header_id, header_id)
                if callable(attar):
                    value = attar()
                else:
                    value = attar
                column.append(value)
            column_values.append(column)
        if len(column_values) == 0:
            return [self.selected_column_names]
        return column_values
        # return [[getattr(article, header_id, header_id) for header_id in header_ids] for article in Article_list]


class ValueTips:
    def __init__(self, value, text):
        self.value = value
        self.text = text


class ValueTipsConvert:
    def __init__(self, array):
        self.ValueTips_list = [ValueTips(item[0], item[1]) for item in array]

    def get_value_by_text(self, text):
        return [item.value for item in self.ValueTips_list if item.text == text][0]

    def get_all_text_list(self):
        return [item.text for item in self.ValueTips_list]

    def get_text_by_value(self, value):
        temp_list = [item.text for item in self.ValueTips_list if item.value == value]
        return None if len(temp_list) == 0 else temp_list[0]


class Article2AudioAdapter:
    __instance = None

    def __init__(self, Article2Audio_1):
        if Article2AudioAdapter.__instance is not None:
            raise Exception("Cannot create multiple instances of Article2AudioAdapter singleton class")
        else:
            self.Article2Audio_1 = Article2Audio_1
            ConfigManagerSys_1 = self.get_sys_config()
            ConfigManagerConfig_1 = self.get_config_config()
            self.article_slicing_length = ConfigManagerConfig_1.get_article_slicing_length()  # 文章切片长度：字数
            self.speaker_candidates = [role.role for role in
                                       self.Article2Audio_1.RoleManager_1.roles] if len(
                ConfigManagerSys_1.get_speaker_candidates()) == 0 else ConfigManagerSys_1.get_speaker_candidates()  # 文章朗读候选人
            self.text_deal_with_before_convert = self.Article2Audio_1.get_all_deal_with_before_convert_audio_plugins_list()
            self.text_deal_with_before_convert.insert(0, '不处理')  # 在转换前，可选的文本处理方法
            self.default_text_deal_with_before_convert = ConfigManagerSys_1.get_default_text_deal_with_before_convert()
            self.audio_deal_with_after_convert = self.Article2Audio_1.get_all_deal_with_after_convert_audio_plugins_list()  # 完成音频转换之后，对音频的处理方式
            self.audio_deal_with_after_convert.insert(0, '不处理')
            self.default_audio_deal_with_after_convert = ConfigManagerSys_1.get_default_audio_deal_with_after_convert()
            self.audio_format = ['wav', 'mp3']  # 输出音频格式
            self.default_audio_format = ConfigManagerSys_1.get_default_audio_format()
            self.default_output_path = ConfigManagerConfig_1.get_default_output_path()
            self.all_article_source = self.Article2Audio_1.ArticleSearchSave_1.get_all_article_source()
            self.all_article_source.insert(0, '全部')
            self.selected_source = "全部"
            self.all_tabs = [
                {'text': '刚才转换的文章', 'value': 'is_last_time'},
                {'text': '今天转换的文章', 'value': 'today'},
                {'text': '所有文章', 'value': 'all'},
                {'text': '收藏的文章', 'value': 'collection'},
            ]  # 搜索条件
            self.selected_tab = '收藏的文章'
            self.selected_article_list = []  # 选中的文章列表
            self.search_article_id = None  # 文章id
            self.search_title = None  # 文章标题搜索
            self.search_author = None  # 文章作者搜索
            self.Page_1 = Page()  # 当前页码
            [Page_1, choice_list] = self.search_articles_tab(self.selected_tab)
            self.first_article_page = choice_list
            self.ArticleDataframe_1 = ArticleDataframe()
            self.sort_column_list = ValueTipsConvert([
                ['create_time', '抓取时间'],
                ['publish_date', '发布时间'],
                ['size', '文章字符数'],
            ])
            self.sort_desc_list = ValueTipsConvert([
                ['desc', '降序'],
                ['asc', '升序'],
            ])
            self.save_mp3 = ConfigManagerSys_1.get_save_mp3()  # 是否音频留档
            self.clear_output_path = ConfigManagerSys_1.get_clear_output_path()  # 输出音频前，是否清空输出目录
            self.speak_convert_mode_list = ValueTipsConvert([
                ['random', '随机一位朗读'],
                ['all', '每位都读一遍'],
            ])
            self.speak_convert_mode = ConfigManagerSys_1.get_speak_convert_mode()
            self.tooth_sound_weakening = ConfigManagerSys_1.get_tooth_sound_weakening()  # 齿音弱化
            self.default_speak_content_format = '标题：{title}，作者：{author}，日期：{publish_date}，朗读：{role}，{content}'  # 默认音频朗读格式
            self.speak_content_format = ConfigManagerSys_1.get_speak_content_format(
                self.default_speak_content_format)  # 获取音频朗读格式
            Article2AudioAdapter.__instance = self

    @staticmethod
    def get_instance(Article2Audio_1):
        if not Article2AudioAdapter.__instance:
            Article2AudioAdapter(Article2Audio_1)
        return Article2AudioAdapter.__instance

    def get_config_config(self):
        return self.Article2Audio_1.ConfigManager_1.ConfigManagerConfig_1

    def get_sys_config(self):
        return self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1

    def get_all_tabs(self):
        return [tab['text'] for tab in self.all_tabs]

    # 保存齿音弱化设置
    def save_tooth_sound_weakening(self, tooth_sound_weakening):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_tooth_sound_weakening(tooth_sound_weakening)
        self.tooth_sound_weakening = tooth_sound_weakening

    # 保存音频朗读格式
    def save_speak_content_format(self, speak_content_format):
        ConfigManagerSys_1 = self.get_sys_config()
        if speak_content_format is None or len(speak_content_format) == 0:
            speak_content_format = self.default_speak_content_format
        ConfigManagerSys_1.set_speak_content_format(speak_content_format)
        self.speak_content_format = speak_content_format
        return speak_content_format

    # 保存文章切片长度
    def save_article_slicing_length(self, length):
        ConfigManagerConfig_1 = self.get_config_config()
        ConfigManagerConfig_1.set_article_slicing_length(length)
        self.article_slicing_length = length

    # 获取演讲者列表
    def get_all_speaker_list(self):
        return [role.role for role in self.Article2Audio_1.RoleManager_1.roles]

    # 保存演讲的候选人名单
    def save_speaker_candidates(self, speakers):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_speaker_candidates(speakers)
        self.speaker_candidates = speakers

    # 保存文本预处理方法
    def save_text_deal_with_before_convert(self, way):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_default_text_deal_with_before_convert(way)
        self.default_text_deal_with_before_convert = way

    # 保存音频处理方法
    def save_audio_deal_with_after_convert(self, way):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_default_audio_deal_with_after_convert(way)
        self.default_audio_deal_with_after_convert = way

    # 保存音频格式
    def save_audio_format(self, audio_format):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_default_audio_format(audio_format)
        self.default_audio_format = audio_format

    # 保存默认的音频输出路径
    def save_default_output_path(self, path):
        self.default_output_path = path

    # 音频是否留档
    def update_save_mp3(self, save_mp3):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_save_mp3(save_mp3)
        self.save_mp3 = save_mp3

    # 输出音频前，是否清空目录下
    def save_clear_output_path(self, clear_output_path):
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_clear_output_path(clear_output_path)
        self.clear_output_path = clear_output_path

    # 朗读转换模式
    def save_speak_convert_mode(self, text):
        speak_convert_mode = self.speak_convert_mode_list.get_value_by_text(text)
        ConfigManagerSys_1 = self.get_sys_config()
        ConfigManagerSys_1.set_speak_convert_mode(speak_convert_mode)
        self.speak_convert_mode = speak_convert_mode

    # 更改当前页码
    def change_page_no(self, page_no):
        page_no = int(page_no)
        if page_no < 1:
            self.Page_1.page_no = 1
        elif page_no > self.Page_1.get_all_page():
            self.Page_1.page_no = self.Page_1.get_all_page()
        else:
            self.Page_1.page_no = page_no
        return self.Page_1

    # 跳向下一页
    def go_to_next_page(self):
        self.change_page_no(self.Page_1.page_no + 1)
        return self.get_current_search_article_list()

    # 跳向上一页
    def go_to_pre_page(self):
        self.change_page_no(self.Page_1.page_no - 1)
        return self.get_current_search_article_list()

    # 切换tab搜索文章
    def search_articles_tab(self, tab):
        self.selected_tab = tab
        return self.get_current_search_article_list()

    # 切换source搜索文章
    def search_articles_source(self, source):
        self.selected_source = source
        return self.get_current_search_article_list()

    # 当前查询条件下，当前分页能获取到的数据
    def get_current_search_article_list(self):
        SearchParam_1 = self.get_search_param()
        [Page_1, article_list] = self.Article2Audio_1.ArticleSearchSave_1.search_article(SearchParam_1, self.Page_1)
        return [Page_1, [article.title for article in article_list]]

    # 当前查询条件下，所有数据，不分页
    def get_current_search_all_article_list(self):
        SearchParam_1 = self.get_search_param()
        Page_1 = Page(page_no=1, page_size=9999999999)
        [Page_2, article_list] = self.Article2Audio_1.ArticleSearchSave_1.search_article(SearchParam_1, Page_1)
        return [article.title for article in article_list]

    def get_select_articles(self, article_title_list):
        self.selected_article_list = article_title_list
        return [article for article in
                self.Article2Audio_1.ArticleSearchSave_1.get_all_article_normal_list() if
                article.title in article_title_list]

    def get_select_article_row(self, row):
        return [article for article in
                self.Article2Audio_1.ArticleSearchSave_1.get_all_article_normal_list() if
                article.title in self.selected_article_list][row]

    def get_select_article_header_id(self, column):
        return self.ArticleDataframe_1.get_header_ids()[column]

    # 启动转换音频
    def start_convert(self, DealWithBeforeConvertAudioPlugins_param_values,
                      DealWithAfterConvertAudioPlugins_param_values):

        Role_list = [role for role in self.Article2Audio_1.RoleManager_1.roles if role.role in self.speaker_candidates]

        article_list = [article for article in self.Article2Audio_1.ArticleSearchSave_1.get_all_article_normal_list() if
                        article.title in self.selected_article_list]
        result_txt = self.Article2Audio_1.start_convert(self.article_slicing_length, Role_list, self.speak_convert_mode,
                                                        article_list,
                                                        self.default_text_deal_with_before_convert,
                                                        DealWithBeforeConvertAudioPlugins_param_values,
                                                        self.default_audio_deal_with_after_convert,
                                                        DealWithAfterConvertAudioPlugins_param_values,
                                                        self.default_audio_format,
                                                        self.default_output_path,
                                                        self.save_mp3,
                                                        self.clear_output_path,
                                                        self.tooth_sound_weakening,
                                                        self.speak_content_format,
                                                        )
        os.startfile(self.default_output_path)
        return result_txt

    def get_search_param(self):
        search_type = next(item['value'] for item in self.all_tabs if item['text'] == self.selected_tab)
        SearchParam_1 = SearchParam(search_type=search_type, plugins_name=self.selected_source,
                                    article_id=self.search_article_id, title=self.search_title,
                                    author=self.search_author)
        return SearchParam_1

    def get_select_article_list(self):
        return [article for article in
                self.Article2Audio_1.ArticleSearchSave_1.get_all_article_normal_list() if
                article.title in self.selected_article_list]

    def delete_all_select(self):
        self.Article2Audio_1.delete_article_list(self.get_select_article_list())
        self.selected_article_list = []

    def collect_all_select(self):
        self.Article2Audio_1.collect_all_select(self.get_select_article_list())

    def cancel_collect_all_select(self):
        self.Article2Audio_1.cancel_collect_all_select(self.get_select_article_list())


# 适配器，用来连接UI和article2audio对象
class VoiceDemoAdapter:
    __instance = None

    def __init__(self, Article2Audio_1):
        if VoiceDemoAdapter.__instance is not None:
            raise Exception("Cannot create multiple instances of VoiceDemoAdapter singleton class")
        else:
            self.Article2Audio_1 = Article2Audio_1
            ConfigManagerSys_1 = self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1
            ConfigManagerConfig_1 = self.Article2Audio_1.ConfigManager_1.ConfigManagerConfig_1
            self.article_save_path = ConfigManagerConfig_1.get_article_path()  # 文件存放路径

            VoiceDemoAdapter.__instance = self

    @staticmethod
    def get_instance(Article2Audio_1):
        if not VoiceDemoAdapter.__instance:
            VoiceDemoAdapter(Article2Audio_1)
        return VoiceDemoAdapter.__instance


# 适配器，用来连接UI和article2audio对象
class SpeakerAdapter:
    __instance = None

    def __init__(self, Article2Audio_1):
        if SpeakerAdapter.__instance is not None:
            raise Exception("Cannot create multiple instances of SpeakerAdapter singleton class")
        else:
            self.Article2Audio_1 = Article2Audio_1
            ConfigManagerSys_1 = self.Article2Audio_1.ConfigManager_1.ConfigManagerSys_1
            ConfigManagerConfig_1 = self.Article2Audio_1.ConfigManager_1.ConfigManagerConfig_1
            self.article_save_path = ConfigManagerConfig_1.get_article_path()  # 文件存放路径

            SpeakerAdapter.__instance = self

    @staticmethod
    def get_instance(Article2Audio_1):
        if not SpeakerAdapter.__instance:
            SpeakerAdapter(Article2Audio_1)
        return SpeakerAdapter.__instance
