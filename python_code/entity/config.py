import os
from util.commonUtil import YamlManager


# 用于保存系统的部分配置数据
class ConfigManagerSys:
    def __init__(self):
        self.YamlManager_sys = YamlManager('config/sys.yaml')

    # 获取属性，如果为空，添加默认值
    def get_default_if_none(self, key, default_val):
        if self.YamlManager_sys.get(key) is None:
            self.YamlManager_sys.set(key, default_val)
        return self.YamlManager_sys.get(key)

    # 获取模型配置文件所在路径
    def get_hparams_file(self):
        return self.get_default_if_none('hparams_file', './model/config.json')

    # 获取模型文件所在路径
    def get_model_path(self):
        return self.get_default_if_none('model_path', './model/G_953000.pth')

    # 获取默认选中的插件
    def get_selected_article_plugins(self):
        return self.get_default_if_none('selected_article_plugins', [])

    # 保存默认选中的插件
    def set_selected_article_plugins(self, val):
        self.YamlManager_sys.set('selected_article_plugins', val)

    # 获取抓取文件的间隔时间
    def get_fetch_interval(self):
        return self.get_default_if_none('fetch_interval', 5)

    # 保存抓取文件的间隔时间
    def set_fetch_interval(self, val):
        self.YamlManager_sys.set('fetch_interval', val)

    # 获取抓取文件的间隔时间
    def get_speaker_candidates(self):
        return self.get_default_if_none('speaker_candidates', [])

    # 保存抓取文件的间隔时间
    def set_speaker_candidates(self, val):
        self.YamlManager_sys.set('speaker_candidates', val)

    # 获取抓取文件的间隔时间
    def get_temp_dir(self):
        return self.get_default_if_none('temp_dir', 'temp')

    # 获取音频转换前，文本的预处理方法
    def get_default_text_deal_with_before_convert(self):
        return self.get_default_if_none('default_text_deal_with_before_convert', '不处理')

    # 保存音频转换前，文本的预处理方法
    def set_default_text_deal_with_before_convert(self, val):
        self.YamlManager_sys.set('default_text_deal_with_before_convert', val)

    # 获取转换后音频的默认处理方法
    def get_default_audio_deal_with_after_convert(self):
        return self.get_default_if_none('default_audio_deal_with_after_convert', '不处理')

    # 保存转换后音频的默认处理方法
    def set_default_audio_deal_with_after_convert(self, val):
        self.YamlManager_sys.set('default_audio_deal_with_after_convert', val)

    # 获取默认的音频格式
    def get_default_audio_format(self):
        return self.get_default_if_none('default_audio_format', 'mp3')

    # 保存默认的音频格式
    def set_default_audio_format(self, val):
        self.YamlManager_sys.set('default_audio_format', val)

    # 获取默认排序字段
    def get_sort_column(self):
        return self.get_default_if_none('sort_column', 'create_time')

    # 获取升降序
    def get_sort_desc(self):
        return self.get_default_if_none('sort_column', 'sort_desc')

    # 获取是否音频留档
    def get_save_mp3(self):
        return self.get_default_if_none('save_mp3', False)

    # 保存是否音频留档
    def set_save_mp3(self, val):
        self.YamlManager_sys.set('save_mp3', val)

    # 获取是否清空输出目录
    def get_clear_output_path(self):
        return self.get_default_if_none('clear_output_path', False)

    # 保存是否清空输出目录
    def set_clear_output_path(self, val):
        self.YamlManager_sys.set('clear_output_path', val)

    # 获取朗读转换模式
    def get_speak_convert_mode(self):
        return self.get_default_if_none('speak_convert_mode', 'random')

    # 保存朗读转换模式
    def set_speak_convert_mode(self, val):
        self.YamlManager_sys.set('speak_convert_mode', val)

    # 获取齿音弱化设置
    def get_tooth_sound_weakening(self):
        return self.get_default_if_none('tooth_sound_weakening', False)

    # 保存齿音弱化设置
    def set_tooth_sound_weakening(self, val):
        self.YamlManager_sys.set('tooth_sound_weakening', val)

    # 获取过滤文章字符数标准
    def get_filter_article_characters_number(self):
        return self.get_default_if_none('filter_article_characters_number', 300)

    # 保存过滤文章字符数标准
    def set_filter_article_characters_number(self, val):
        self.YamlManager_sys.set('filter_article_characters_number', val)

    # 获取音频朗读格式
    def get_speak_content_format(self, default_speak_content_format):
        return self.get_default_if_none('speak_content_format', default_speak_content_format)

    # 保存音频朗读格式
    def set_speak_content_format(self, val):
        self.YamlManager_sys.set('speak_content_format', val)


# 用于保存部分用户可调整的配置数据
class ConfigManagerConfig:
    def __init__(self):
        self.YamlManager_config = YamlManager('config.yaml')

    # 获取属性，如果为空，添加默认值
    def get_default_if_none(self, key, default_val):
        if self.YamlManager_config.get(key) is None:
            self.YamlManager_config.set(key, default_val)
        return self.YamlManager_config.get(key)

    # 获取vits推理设置，cpu或gpu
    def get_device_type(self):
        return self.get_default_if_none('device_type', 'cpu')

    # 获取文章的存放路径
    def get_article_path(self):
        return self.get_default_if_none('article_path', '../vits-articles')

    # 获取默认的音频输出路径
    def get_default_output_path(self):
        return self.get_default_if_none('default_output_path', 'outputs')

    # 获取文章切片长度：字数
    def get_article_slicing_length(self):
        return self.get_default_if_none('article_slicing_length', 200)

    # 保存文章切片长度：字数
    def set_article_slicing_length(self, val):
        self.YamlManager_config.set('article_slicing_length', val)


class ConfigManager:

    def __init__(self):
        self.ConfigManagerSys_1 = ConfigManagerSys()
        self.ConfigManagerConfig_1 = ConfigManagerConfig()
