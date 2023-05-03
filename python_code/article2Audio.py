import os.path
import shutil
import random

from entity.article import ArticleManager
from entity.config import ConfigManager
from entity.plugins import PluginsManager
from entity.role import RoleManager
from entity.article_search_save import ArticleSearchSave
from entity.article import RoleVoice
from entity.article import ArticleVoice
from entity.vits_manager import VitsManager
from entity.util.commonUtil import Util
import time
from pydub import AudioSegment


class RoleRandom:
    def __init__(self, Role_list):
        self.has_speak = []
        self.Role_list = Role_list

    # 随机挑选一个朗读人，确保在所有朗读人朗读一遍之前，不会重复
    def get_random_role(self):
        if len(self.has_speak) == len(self.Role_list):
            self.has_speak = []
        randomIndex = 0
        while True:
            if randomIndex in self.has_speak:
                randomIndex = random.randint(0, len(self.Role_list) - 1)
            else:
                self.has_speak.append(randomIndex)
                break
        return self.Role_list[randomIndex]


class Article2Audio:
    __instance = None

    def __init__(self):
        if Article2Audio.__instance is not None:
            raise Exception("Cannot create multiple instances of Article2Audio singleton class")
        else:
            self.ConfigManager_1 = ConfigManager()  # 配置文件管理
            self.PluginsManager_1 = PluginsManager()  # 插件管理
            self.ArticleSearchSave_1 = ArticleSearchSave(
                self.ConfigManager_1.ConfigManagerConfig_1.get_article_path())  # 文章管理
            self.RoleManager_1 = RoleManager()  # 演讲角色管理
            device_type = self.ConfigManager_1.ConfigManagerConfig_1.get_device_type()
            hparams_file = self.ConfigManager_1.ConfigManagerSys_1.get_hparams_file()
            model_path = self.ConfigManager_1.ConfigManagerSys_1.get_model_path()
            self.VitsManager_1 = VitsManager(device_type, hparams_file, model_path)  # vits管理
            Article2Audio.__instance = self

    @staticmethod
    def get_instance():
        if not Article2Audio.__instance:
            Article2Audio()
        return Article2Audio.__instance

    # 根据文章抓取插件，抓取文章
    # articlePluginsName 插件名称
    # fetchInterval 抓取间隔
    def fetch_articles_by_plugins(self, articlePluginsName, fetchInterval, is_filter_article,
                                  filter_article_characters_number, param_values):
        # 保证最短文章抓取间隔为2秒
        if fetchInterval < 2:
            fetchInterval = 2
        # 实际抓取的文件列表
        Article_newList = []
        # 获取文章抓取插件
        ArticleFetchPlugins_1 = self.PluginsManager_1.get_article_fetch_plugins_by_name(articlePluginsName)
        # 调用插件的文章列表抓取接口，获取可抓取的文章列表
        article_list = []
        try:
            article_list = ArticleFetchPlugins_1.fetch_article_list()
        except Exception as e:
            print(f'{articlePluginsName}抓取文章列表时发生异常：{e}')
        print(f"抓取到的文章列表长度：{len(article_list)}")
        for article in article_list:
            article_id = article["id"]
            try:
                print(f'开始抓取内容 文章内容：{article["id"]}')
                # 根据文章id和插件名称，检查文章是否已经被抓取过，如果已经抓取，则跳过
                if self.ArticleSearchSave_1.exists_article(article_id, articlePluginsName) \
                        or self.ArticleSearchSave_1.exists_delete_article(article_id, articlePluginsName):
                    print("文章已存在，跳过")
                    continue
                # 调用插件的文章抓取文章接口，获取文章对象
                Article_new = ArticleFetchPlugins_1.fetch_article(article_id, article, article_list,
                                                                  self.ConfigManager_1.ConfigManagerConfig_1.get_article_path(),
                                                                  param_values)
                if is_filter_article:
                    if Article_new.size > filter_article_characters_number:
                        Article_newList.append(Article_new)
                        # 将文章持久化到本地文件
                        self.ArticleSearchSave_1.add_article(Article_new)
                    else:
                        print(f'文章字符数{Article_new.size}低于标准{filter_article_characters_number}，过滤')
                else:
                    Article_newList.append(Article_new)
                    # 将文章持久化到本地文件
                    self.ArticleSearchSave_1.add_article(Article_new)

                # 休眠fetchInterval秒，防止高频抓取可能导致的负面效果
                print(f'间隔时间：{fetchInterval}')
                time.sleep(fetchInterval)
            except Exception as e:
                print(f'{articlePluginsName}抓取文章{article_id}时，发生异常：{e}')
                # 休眠fetchInterval秒，防止高频抓取可能导致的负面效果
                print(f'间隔时间：{fetchInterval}')
                time.sleep(fetchInterval)

        return Article_newList

    # 开始启动文章抓取
    # selectedArticlePluginses 选中的文章抓取插件
    # dealwithAfterFetchAllArticlePlugins 选中的文章后处理插件
    # uploadTxtFilePaths 选中的本地txt文件
    # fetchInterval 文章抓取间隔
    def start_fetch_articles(self, selectedArticlePluginses, batch_param_values, dealwithAfterFetchAllArticlePlugins,
                             uploadTxtFilePaths,
                             fetchInterval, is_filter_article, filter_article_characters_number):
        print(f'batch_param_values={batch_param_values}')
        # 开始计时
        start_time = time.time()
        # 抓取文章列表
        Article_list = []
        # 提示信息
        tips = []
        # 抓取文章总数
        count = 0

        # 如果选中了文章抓取插件，执行
        if len(selectedArticlePluginses) > 0:
            for articlePlugins in selectedArticlePluginses:
                # 抓取此插件下的文章列表
                param_values = get_param_values_by_plugin_name(batch_param_values, articlePlugins)
                Article_temps = self.fetch_articles_by_plugins(articlePlugins, fetchInterval, is_filter_article,
                                                               filter_article_characters_number, param_values)
                Article_list.append(Article_temps)
                tips.append(f'平台类型：{articlePlugins}，抓取数量：{len(Article_temps)}')
                count = count + len(Article_temps)

        # 如果上传了本地的txt文件
        if len(uploadTxtFilePaths) > 0:
            Article_temps = self.ArticleSearchSave_1.convert_txt(uploadTxtFilePaths)
            Article_list.append(Article_temps)
            tips.append(f'上传本地文件数量：{len(Article_temps)}')

        # 如果选择了文章后处理插件
        if dealwithAfterFetchAllArticlePlugins != '不处理':
            # 获取文章后处理插件
            DealWithAfterFetchAllArticlePlugins_1 = self.PluginsManager_1.get_deal_with_after_fetch_all_article_plugins(
                dealwithAfterFetchAllArticlePlugins)
            # 执行文章处理
            DealWithAfterFetchAllArticlePlugins_1.deal_with_article(Article_list)
            # 将处理后的文章持久化到本地
            self.ArticleSearchSave_1.save_article_list(Article_list)

        self.ArticleSearchSave_1.sort_article()

        # 获取执行总秒数
        end_time = time.time()
        total_time = end_time - start_time
        total_seconds = int(total_time)
        return f'处理完毕,共耗时：{total_seconds}秒，抓取文章数量{count},{"；".join(tips)}'

    # 开始抓取单个或数个文章
    def start_fetch_single_article(self, article_plugin, single_param_values, article_ids):
        # 开始计时
        start_time = time.time()
        # 抓取此插件下的文章列表
        fetchInterval = 2
        # 实际抓取的文件列表
        Article_newList = []
        # 获取文章抓取插件
        ArticleFetchPlugins_1 = self.PluginsManager_1.get_article_fetch_plugins_by_name(article_plugin)
        article_list = [{'id': article_id} for article_id in article_ids.split(',')]
        for article in article_list:
            article_id = article.get('id')
            try:
                print(f'文章内容：{article_id}')
                # 根据文章id和插件名称，检查文章是否已经被抓取过，如果已经抓取，则跳过
                if self.ArticleSearchSave_1.exists_article(article_id, article_plugin):
                    print("文章已存在，跳过")
                    continue
                # 调用插件的文章抓取文章接口，获取文章对象
                param_values = get_param_values_by_plugin_name(single_param_values, article_plugin)
                Article_new = ArticleFetchPlugins_1.fetch_article(article_id, article, article_list,
                                                                  self.ConfigManager_1.ConfigManagerConfig_1.get_article_path(),
                                                                  param_values)
                Article_newList.append(Article_new)
                print('开始抓取内容')
                # 将文章持久化到本地文件
                self.ArticleSearchSave_1.add_article(Article_new)
                # 休眠fetchInterval秒，防止高频抓取可能导致的负面效果
                print(f'间隔时间：{fetchInterval}')
                time.sleep(fetchInterval)
            except Exception as e:
                print(f'{article_plugin}抓取文章{article_id}时，发生异常：{e}')
                # 休眠fetchInterval秒，防止高频抓取可能导致的负面效果
                print(f'间隔时间：{fetchInterval}')
                time.sleep(fetchInterval)

        self.ArticleSearchSave_1.sort_article()
        # 获取执行总秒数
        end_time = time.time()
        total_time = end_time - start_time
        total_seconds = int(total_time)
        return f'处理完毕,共耗时：{total_seconds}秒，抓取文章数量{len(Article_newList)}'

    # 获取文章抓取插件列表
    def get_all_article_plugins_list(self):
        plugins_name_list = []
        for plugins in self.PluginsManager_1.ArticleFetchPlugins_list:
            plugins_name_list.append(plugins.name)
        return plugins_name_list

    # 获取转换音频前，文章预处理插件列表
    def get_all_deal_with_before_convert_audio_plugins_list(self):
        plugins_name_list = []
        for plugins in self.PluginsManager_1.DealWithBeforeConvertAudioPlugins_list:
            plugins_name_list.append(plugins.name)
        return plugins_name_list

    # 获取转换后，音频处理插件列表
    def get_all_deal_with_after_convert_audio_plugins_list(self):
        plugins_name_list = []
        for plugins in self.PluginsManager_1.DealWithAfterConvertAudioPlugins_list:
            plugins_name_list.append(plugins.name)
        return plugins_name_list

    # 启动音频转换
    def start_convert(self, article_slicing_length, Role_list, speak_convert_mode, Article_list,
                      default_text_deal_with_before_convert, DealWithBeforeConvertAudioPlugins_param_values,
                      default_audio_deal_with_after_convert, DealWithAfterConvertAudioPlugins_param_values,
                      default_audio_format,
                      default_output_path, save_mp3, clear_output_path, tooth_sound_weakening, speak_content_format):
        # 开始计时
        start_time = time.time()
        # 生成的音频数量
        count = 0
        # 获取转换前，文本处理插件
        DealWithBeforeConvertAudioPlugins_1 = self.PluginsManager_1.get_deal_with_before_convert_audio_plugins_by_name(
            default_text_deal_with_before_convert)
        # print(f'文章预处理插件：{default_text_deal_with_before_convert};{DealWithBeforeConvertAudioPlugins_1}')
        # 获取转换后，音频处理插件
        DealWithAfterConvertAudioPlugins_1 = self.PluginsManager_1.get_deal_with_after_convert_audio_plugins_by_name(
            default_audio_deal_with_after_convert)
        # print(f'音频处理插件：{default_audio_deal_with_after_convert};{DealWithAfterConvertAudioPlugins_1}')
        # 音频处理结果列表
        ArticleVoice_list = []
        # 生成音频时，使用的临时目录
        dir_temp = self.ConfigManager_1.ConfigManagerSys_1.get_temp_dir()
        Util.create_dir(dir_temp)
        # 随机朗读人
        RoleRandom_1 = RoleRandom(Role_list)
        # print('文章列表')
        # print(Article_list)
        # 遍历文章
        cur_has_convert_count = 0
        for article in Article_list:
            try:
                # 获取文章内容
                content = article.load_content()
                if DealWithBeforeConvertAudioPlugins_1 is not None:
                    # 如果选择了文本预处理，则执行
                    content = DealWithBeforeConvertAudioPlugins_1.deal_with_article_content(article,
                                                                                            DealWithBeforeConvertAudioPlugins_param_values)
                # 文章对应的朗读人和生成音频的信息列表
                RoleVoice_list = []
                if speak_convert_mode == 'all':
                    all_count = len(Article_list) * len(Role_list)
                    # 如果是每个朗读人都讲一遍
                    for role in Role_list:
                        RoleVoice_1 = RoleVoice(role, article)
                        # 转换音频
                        self.VitsManager_1.convert_txt_2_wav(RoleVoice_1, content, article_slicing_length,
                                                             dir_temp, tooth_sound_weakening, speak_content_format,
                                                             cur_has_convert_count+1, all_count)
                        cur_has_convert_count += 1
                        RoleVoice_list.append(RoleVoice_1)
                else:
                    # 随机挑选一个朗读人，确保在所有朗读人朗读一遍之前，不会重复
                    role = RoleRandom_1.get_random_role()
                    RoleVoice_1 = RoleVoice(role, article)
                    self.VitsManager_1.convert_txt_2_wav(RoleVoice_1, content, article_slicing_length,
                                                         dir_temp, tooth_sound_weakening, speak_content_format,
                                                         cur_has_convert_count+1, len(Article_list))
                    cur_has_convert_count += 1
                    RoleVoice_list.append(RoleVoice_1)
                # 添加音频转换结果
                ArticleVoice_list.append(ArticleVoice(article, RoleVoice_list))
            except Exception as e:
                print(f'文章{article.title}音频转换发生异常：', e)

        # 生成留档的mp3音频
        for av in ArticleVoice_list:
            for rv in av.RoleVoice_list:
                # 读取 WAV 文件
                sound = AudioSegment.from_wav(rv.get_wav_file_path())
                # 将 WAV 文件导出为 MP3 文件
                sound.export(rv.get_mp3_file_path(), format="mp3")

        # 创建输出目录
        Util.create_dir(default_output_path)
        if clear_output_path:
            # 清空输出目录
            Util.delete_dir_file(default_output_path)
        if DealWithAfterConvertAudioPlugins_1 is not None:
            # 调用音频处理插件，处理结果
            count = DealWithAfterConvertAudioPlugins_1.deal_with_audio(ArticleVoice_list,
                                                                       DealWithAfterConvertAudioPlugins_param_values,
                                                                       default_output_path,
                                                                       default_audio_format)
        else:
            for av in ArticleVoice_list:
                for rv in av.RoleVoice_list:
                    count = count + 1
                    # 将生成的音频转移到输出目录
                    if default_audio_format == 'wav':
                        shutil.move(rv.get_wav_file_path(),
                                    os.path.join(default_output_path, os.path.basename(rv.get_wav_file_path())))
                    else:
                        shutil.copy(rv.get_mp3_file_path(),
                                    os.path.join(default_output_path, os.path.basename(rv.get_mp3_file_path())))

        # 删除掉生成的wav音频
        for av in ArticleVoice_list:
            for rv in av.RoleVoice_list:
                if os.path.exists(rv.get_wav_file_path()):
                    os.remove(rv.get_wav_file_path())
                if not save_mp3:
                    if os.path.exists(rv.get_mp3_file_path()):
                        os.remove(rv.get_mp3_file_path())

        # 获取执行总秒数
        end_time = time.time()
        total_time = end_time - start_time
        total_seconds = int(total_time)
        return f'处理完毕,共耗时：{total_seconds}秒，生成音频数量：{count}'

    def delete_article_list(self, Article_list):
        for article in Article_list:
            self.ArticleSearchSave_1.delete_article(article)

    def collect_all_select(self, Article_list):
        self.ArticleSearchSave_1.collect_all_select(Article_list)

    def cancel_collect_all_select(self, Article_list):
        self.ArticleSearchSave_1.cancel_collect_all_select(Article_list)


def get_param_values_by_plugin_name(param_values, plugin_name):
    print(param_values)
    temp_list = [param['values'] for param in param_values if param['plugin_name'] == plugin_name]
    return temp_list[0] if len(temp_list) > 0 else None
