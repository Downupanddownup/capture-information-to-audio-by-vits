# -*- coding: utf-8 -*-
from pickle import TRUE
from random import choices
import time
import os
import sys
import gradio as gr

# 将模块所在目录添加到 Python 模块搜索路径中
module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_dir)

from vits import utils
import argparse
from article2AudioUIAdapter import ArticleDownloadAdapter
from article2AudioUIAdapter import Article2AudioAdapter
from article2AudioUIAdapter import VoiceDemoAdapter
from article2AudioUIAdapter import SpeakerAdapter
from article2Audio import Article2Audio
from vits import commons
from vits.models import SynthesizerTrn
from vits.text import text_to_sequence
import torch
from torch import no_grad, LongTensor
import webbrowser
import logging
import soundfile as sf
from playsound import playsound
import numpy as np
import time

logging.getLogger('numba').setLevel(logging.WARNING)
limitation = os.getenv("SYSTEM") == "spaces"  # limit text and audio length in huggingface spaces

download_audio_js = """
() =>{{
    let root = document.querySelector("body > gradio-app");
    if (root.shadowRoot != null)
        root = root.shadowRoot;
    let audio = root.querySelector("#tts-audio").querySelector("audio");
    let text = root.querySelector("#input-text").querySelector("textarea");
    if (audio == undefined)
        return;
    text = text.value;
    if (text == undefined)
        text = Math.floor(Math.random()*100000000);
    audio = audio.src;
    let oA = document.createElement("a");
    oA.download = text.substr(0, 20)+'.wav';
    oA.href = audio;
    document.body.appendChild(oA);
    oA.click();
    oA.remove();
}}
"""


class PluginParamItem:
    def __init__(self, PluginParam_1):
        self.PluginParam_1 = PluginParam_1
        self.key = PluginParam_1.key
        self.type = PluginParam_1.type
        self.value = PluginParam_1.value

    def save_value(self, value):
        self.value = value


class PluginParams:
    def __init__(self, plugin_name, plugin_description, open_param, PluginParam_list):
        self.plugin_name = plugin_name
        self.plugin_description = plugin_description
        self.open_param = open_param
        self.PluginParamItem_list = [PluginParamItem(param) for param in PluginParam_list]
        self.accordion = None

    def draw_ui(self, select_plugin_name_list):
        accordion = gr.Accordion(f'{self.plugin_name}：{self.plugin_description}',
                                 visible=self.plugin_name in select_plugin_name_list)
        with accordion:
            if self.open_param:
                for param in self.PluginParamItem_list:
                    param_obj = param.PluginParam_1.param
                    if param.type == 'Number':
                        temp_n = gr.Number(label=param_obj.label, value=param.value)
                        temp_n.change(param.save_value, inputs=[temp_n], outputs=[])
                    elif param.type == 'Dropdown':
                        temp_d = gr.Dropdown(label=param_obj.label, choices=param_obj.choices,
                                             multiselect=param_obj.multiselect,
                                             value=param.value)
                        temp_d.change(param.save_value, inputs=[temp_d], outputs=[])
            else:
                pass
        self.accordion = accordion
        return accordion


class PluginUI:
    def __init__(self, plugin_list):
        self.PluginParams_list = [
            PluginParams(plugin.name, plugin.description, plugin.open_param, plugin.PluginParam_list) for
            plugin in plugin_list]

    def draw_ui(self, select_plugin_name_list):
        return [item.draw_ui(select_plugin_name_list) for item in self.PluginParams_list]

    def get_accordion_list(self):
        temp_list = [item.accordion for item in self.PluginParams_list]
        return temp_list[0] if len(temp_list) == 1 else temp_list

    def change_accordion_list(self, plugin_name_list):
        temp_list = [gr.Accordion.update(visible=(item.plugin_name in plugin_name_list)) for item in
                     self.PluginParams_list]
        return temp_list[0] if len(temp_list) == 1 else temp_list

    def get_param_value_list(self):
        return [{
            'plugin_name': PluginParams_1.plugin_name,
            'values': [{
                'key': item.key,
                'value': item.value,
            } for item in PluginParams_1.PluginParamItem_list]
        } for PluginParams_1 in self.PluginParams_list if PluginParams_1.open_param]

    def get_param_values_by_plugin_name(self, plugin_name):
        temp_list = [param['values'] for param in self.get_param_value_list() if param['plugin_name'] == plugin_name]
        return temp_list[0] if len(temp_list) > 0 else None


class ArticleDownloadTab:
    def __init__(self, Adapter_1):
        self.Adapter_1 = Adapter_1
        self.PluginUI_ArticleFetchPlugins_1 = None
        self.PluginUI_ArticleFetchPlugins_2 = None

    def draw_ui(self):
        with gr.Row():
            with gr.Column():
                gr.Textbox(label="文章存放路径", value=self.Adapter_1.article_save_path)

                d2 = gr.Dropdown(label='抓取类型', choices=self.Adapter_1.fetch_type_list.get_all_text_list(),
                                 value=self.Adapter_1.fetch_type_list.get_text_by_value(self.Adapter_1.fetch_type))

                box1 = gr.Box()
                with box1:
                    self.PluginUI_ArticleFetchPlugins_1 = PluginUI(
                        self.Adapter_1.Article2Audio_1.PluginsManager_1.ArticleFetchPlugins_list)
                    dd = gr.Dropdown(label="文章抓取", choices=self.Adapter_1.all_article_plugins,
                                     value=self.Adapter_1.selected_article_plugins, multiselect=True,
                                     info="请选择需要执行的网页爬虫工具")
                    self.PluginUI_ArticleFetchPlugins_1.draw_ui(self.Adapter_1.selected_article_plugins)
                    cb2 = gr.Checkbox(label="文章过滤", info="勾了，抓取时，就过滤满足特定条件的文章",
                                      value=self.Adapter_1.is_filter_article)
                    n1 = gr.Number(label="过滤字符数低于N的文章", value=self.Adapter_1.filter_article_characters_number,
                                   visible=False)
                    cb = gr.Checkbox(label="本地文件", info="勾了，就上传本地TXT文件；否则不用",
                                     value=self.Adapter_1.upload_txt)
                    files = gr.Files(label="本地文件", visible=False)
                    sd = gr.Slider(2, 10, step=1, value=self.Adapter_1.fetch_interval, label="抓取间隔：秒",
                                   info="控制抓取频率")

                box2 = gr.Box(visible=False)
                with box2:
                    self.PluginUI_ArticleFetchPlugins_2 = PluginUI(
                        self.Adapter_1.Article2Audio_1.PluginsManager_1.ArticleFetchPlugins_list)
                    d3 = gr.Dropdown(label='文章抓取', choices=self.Adapter_1.all_article_plugins,
                                     value=self.Adapter_1.selected_single_article_plugin)
                    self.PluginUI_ArticleFetchPlugins_2.draw_ui([self.Adapter_1.selected_single_article_plugin])
                    tb2 = gr.Textbox(label="文章id，英文逗号分割", value=self.Adapter_1.fetch_article_ids)

                btn = gr.Button(value="开始执行")
            with gr.Column():
                o1 = gr.Textbox(label="执行结果")
            dd.change(self.save_selected_article_plugins, inputs=[dd],
                      outputs=self.PluginUI_ArticleFetchPlugins_1.get_accordion_list())
            files.change(self.Adapter_1.change_upload_txt_files, inputs=[files], outputs=[])
            cb.change(self.change_upload_txt, inputs=cb, outputs=[files])
            sd.change(self.Adapter_1.change_fetch_interval, inputs=[sd], outputs=[])
            btn.click(self.start_fetch_articles, inputs=[], outputs=[o1])
            d2.change(self.change_box, inputs=[d2], outputs=[box1, box2])
            d3.change(self.save_selected_single_article_plugin, inputs=[d3],
                      outputs=self.PluginUI_ArticleFetchPlugins_2.get_accordion_list())
            tb2.change(self.save_fetch_article_ids, inputs=[tb2], outputs=[])
            cb2.change(self.save_is_filter_article, inputs=[cb2], outputs=[n1])
            n1.change(self.Adapter_1.save_filter_article_characters_number, inputs=[n1], outputs=[])

    def start_fetch_articles(self):
        return self.Adapter_1.start_fetch_articles(self.PluginUI_ArticleFetchPlugins_1.get_param_value_list(),
                                                   self.PluginUI_ArticleFetchPlugins_2.get_param_value_list())

    def save_selected_article_plugins(self, selects):
        self.Adapter_1.save_selected_article_plugins(selects)
        return self.PluginUI_ArticleFetchPlugins_1.change_accordion_list(selects)

    def save_is_filter_article(self, is_filter_article):
        self.Adapter_1.is_filter_article = is_filter_article
        return gr.Number.update(visible=is_filter_article)

    def save_fetch_article_ids(self, fetch_article_ids):
        self.Adapter_1.fetch_article_ids = fetch_article_ids

    def save_selected_single_article_plugin(self, plugin):
        self.Adapter_1.selected_single_article_plugin = plugin
        return self.PluginUI_ArticleFetchPlugins_2.change_accordion_list([plugin])

    def change_upload_txt(self, val):
        self.Adapter_1.change_upload_txt(val)
        return gr.Files.update(visible=val)

    def change_box(self, select_type):
        self.Adapter_1.fetch_type = self.Adapter_1.fetch_type_list.get_value_by_text(select_type)
        return [gr.Box.update(visible=select_type == '批量抓取'), gr.Box.update(visible=select_type == '单个抓取')]


class Article2AudioTab:
    def __init__(self, Adapter_1):
        self.Adapter_1 = Adapter_1
        self.select_dataframe_evt = None  # 防止列表事件重复触发
        self.PluginUI_DealWithBeforeConvertAudioPlugins_1 = None
        self.PluginUI_DealWithAfterConvertAudioPlugins_1 = None

    def is_equals_dataframe_evt(self, evt):
        if self.select_dataframe_evt is None:
            return False
        # print(
        #     f"evt.target={evt.target == 'dataframe'};equals={np.array_equal(self.select_dataframe_evt.index, evt.index)}")
        if type(self.select_dataframe_evt.target) == type(evt.target) and np.array_equal(
                self.select_dataframe_evt.index, evt.index):
            return True
        return False

    def draw_ui(self):
        with gr.Accordion("文章搜索"):
            r1 = gr.Radio(self.Adapter_1.get_all_tabs(), value=self.Adapter_1.selected_tab, show_label=False)
            r2 = gr.Radio(self.Adapter_1.all_article_source, value=self.Adapter_1.selected_source, show_label=False)
            with gr.Row():
                d5 = gr.Dropdown(label='排序字段', choices=self.Adapter_1.sort_column_list.get_all_text_list(),
                                 value=self.Adapter_1.sort_column_list.get_text_by_value(
                                     self.Adapter_1.Page_1.sort_column), show_label=False)
                d6 = gr.Dropdown(label='升降序', choices=self.Adapter_1.sort_desc_list.get_all_text_list(),
                                 value=self.Adapter_1.sort_desc_list.get_text_by_value(self.Adapter_1.Page_1.sort_desc),
                                 show_label=False)
                bt8 = gr.Button(value='全选')
                bt9 = gr.Button(value='清空')
                bt10 = gr.Button(value='选中当页')
                bt11 = gr.Button(value='取消当页')

            with gr.Row():
                with gr.Accordion("查看更多选择", open=False):
                    text_article_id = gr.Textbox(label="文章id", value=self.Adapter_1.search_article_id)
                    text_title = gr.Textbox(label="文章标题", value=self.Adapter_1.search_title)
                    text_author = gr.Textbox(label="文章作者", value=self.Adapter_1.search_author)
                    btn_search = gr.Button(value="查询")
                    btn_clear = gr.Button(value="重置")

                    text_article_id.change(self.save_search_article_id, inputs=[text_article_id], outputs=[])
                    text_title.change(self.save_search_title, inputs=[text_title], outputs=[])
                    text_author.change(self.save_search_author, inputs=[text_author], outputs=[])

            cbg = gr.CheckboxGroup(self.Adapter_1.first_article_page,
                                   label="文章列表",
                                   info="请选择需要转换的文件")
            with gr.Row():
                bt2 = gr.Button(value=f"共{self.Adapter_1.Page_1.length}条记录，上一页")
                nb2 = gr.Number(value=self.Adapter_1.Page_1.page_size, show_label=False, label='每页大小')
                nb1 = gr.Number(value=self.Adapter_1.Page_1.page_no, show_label=False, label='当前页数')
                bt3 = gr.Button(
                    value=f"共{self.Adapter_1.Page_1.get_all_page()}页，跳转第{self.Adapter_1.Page_1.page_no + 1}页")
        with gr.Accordion("音频转换设置参数", open=False):
            sd = gr.Slider(10, 3000, value=self.Adapter_1.article_slicing_length, label="文章切片大小：字数",
                           info="根据显存大小调整")
            d0 = gr.Dropdown(label="选择朗读角色", multiselect=True, choices=self.Adapter_1.get_all_speaker_list(),
                             value=self.Adapter_1.speaker_candidates)

            d7 = gr.Dropdown(label="朗读转换模式",
                             choices=self.Adapter_1.speak_convert_mode_list.get_all_text_list(),
                             value=self.Adapter_1.speak_convert_mode_list.get_text_by_value(
                                 self.Adapter_1.speak_convert_mode))

            tb3 = gr.Textbox(label="朗读内容格式", value=self.Adapter_1.speak_content_format)

            cb3 = gr.Checkbox(label="齿音弱化", info="勾了，会执行齿音弱化，但转换性能可能会下降一倍",
                              value=self.Adapter_1.tooth_sound_weakening)

            d1 = gr.Dropdown(label="在开始转换音频前，处理文本",
                             choices=self.Adapter_1.text_deal_with_before_convert,
                             value=self.Adapter_1.default_text_deal_with_before_convert)

            self.PluginUI_DealWithBeforeConvertAudioPlugins_1 = PluginUI(
                self.Adapter_1.Article2Audio_1.PluginsManager_1.DealWithBeforeConvertAudioPlugins_list)
            self.PluginUI_DealWithBeforeConvertAudioPlugins_1.draw_ui(
                [self.Adapter_1.default_text_deal_with_before_convert])

            d3 = gr.Dropdown(label="完成所有音频转换之后，处理音频",
                             choices=self.Adapter_1.audio_deal_with_after_convert,
                             value=self.Adapter_1.default_audio_deal_with_after_convert)

            self.PluginUI_DealWithAfterConvertAudioPlugins_1 = PluginUI(
                self.Adapter_1.Article2Audio_1.PluginsManager_1.DealWithAfterConvertAudioPlugins_list)
            self.PluginUI_DealWithAfterConvertAudioPlugins_1.draw_ui(
                [self.Adapter_1.default_audio_deal_with_after_convert])

            d2 = gr.Dropdown(label="输出音频格式", choices=self.Adapter_1.audio_format,
                             value=self.Adapter_1.default_audio_format)
            cb = gr.Checkbox(label="音频留档", info="勾了，就在文章目录下保留转换后的mp3格式的音频",
                             value=self.Adapter_1.save_mp3)
            gr.Textbox(label="音频的输出路径", value=self.Adapter_1.default_output_path)
            cb2 = gr.Checkbox(label="是否清空输出路径下的文件？", info="勾了，在转换前，会先删除输出路径下的文件",
                              value=self.Adapter_1.clear_output_path)

            sd.change(self.Adapter_1.save_article_slicing_length, inputs=[sd], outputs=[])
            d0.change(self.Adapter_1.save_speaker_candidates, inputs=d0, outputs=[])
            d1.change(self.save_text_deal_with_before_convert, inputs=d1,
                      outputs=self.PluginUI_DealWithBeforeConvertAudioPlugins_1.get_accordion_list())
            d2.change(self.Adapter_1.save_audio_format, inputs=d2, outputs=[])
            d3.change(self.save_audio_deal_with_after_convert, inputs=d3,
                      outputs=self.PluginUI_DealWithAfterConvertAudioPlugins_1.get_accordion_list())
            # d4.change(self.Adapter_1.save_default_output_path, inputs=d4, outputs=[])
            cb.change(self.Adapter_1.update_save_mp3, inputs=[cb], outputs=[])
            cb2.change(self.Adapter_1.save_clear_output_path, inputs=[cb2], outputs=[])
            d7.change(self.Adapter_1.save_speak_convert_mode, inputs=[d7], outputs=[])
            cb3.change(self.Adapter_1.save_tooth_sound_weakening, inputs=[cb3], outputs=[])
            tb3.change(self.Adapter_1.save_speak_content_format, inputs=[tb3], outputs=[tb3])

        bt = gr.Button(value="开始转换")
        tb = gr.Textbox(label="执行结果")

        with gr.Row():
            bt4 = gr.Button(value=f"清空")
            bt5 = gr.Button(value=f"删除全部")
            bt6 = gr.Button(value=f"收藏全部")
            bt7 = gr.Button(value=f"取消收藏")

        df = gr.Dataframe(
            headers=self.Adapter_1.ArticleDataframe_1.get_header_names(),
            datatype=self.Adapter_1.ArticleDataframe_1.get_column_types(),
        )

        bt.click(self.start_convert, inputs=[], outputs=[tb])

        r1.change(self.search_articles_tab, inputs=r1, outputs=[cbg, bt2, nb1, bt3])
        r2.change(self.search_articles_source, inputs=r2, outputs=[cbg, bt2, nb1, bt3])
        cbg.change(self.change_select_articles, inputs=[cbg], outputs=[df])
        df.select(self.select_dataframe, inputs=[], outputs=[])

        btn_search.click(self.search_by_more, inputs=[], outputs=[cbg, bt2, nb1, bt3])
        btn_clear.click(self.search_by_clear, inputs=[], outputs=[cbg, bt2, nb1, bt3])

        bt2.click(self.go_to_pre_page, inputs=[], outputs=[cbg, bt2, nb1, bt3])
        nb1.change(self.change_page_no, inputs=[nb1], outputs=[bt3])
        nb2.change(self.change_page_size, inputs=[nb2], outputs=[cbg, bt2, nb1, bt3])
        bt3.click(self.go_to_next_page, inputs=[], outputs=[cbg, bt2, nb1, bt3])

        bt4.click(self.clear_all_select, inputs=[], outputs=[cbg, df, tb])
        bt5.click(self.delete_all_select, inputs=[], outputs=[cbg, df, tb])
        bt6.click(self.collect_all_select, inputs=[], outputs=[cbg, df, tb])
        bt7.click(self.cancel_collect_all_select, inputs=[], outputs=[cbg, df, tb])

        bt8.click(self.choose_all, inputs=[], outputs=[cbg, df])
        bt9.click(self.clear_all_select, inputs=[], outputs=[cbg, df, tb])
        bt10.click(self.choose_current_page, inputs=[], outputs=[cbg, df])
        bt11.click(self.cancel_current_page, inputs=[], outputs=[cbg, df])

        d5.change(self.save_sort_column, inputs=[d5], outputs=[cbg, bt2, nb1, bt3])
        d6.change(self.save_sort_desc, inputs=[d6], outputs=[cbg, bt2, nb1, bt3])

    def save_search_article_id(self, value):
        self.Adapter_1.search_article_id = value

    def save_search_title(self, value):
        self.Adapter_1.search_title = value

    def save_search_author(self, value):
        self.Adapter_1.search_author = value

    def start_convert(self):
        DealWithBeforeConvertAudioPlugins_param_values = None
        if self.Adapter_1.default_text_deal_with_before_convert != '不处理':
            DealWithBeforeConvertAudioPlugins_param_values = self.PluginUI_DealWithBeforeConvertAudioPlugins_1.get_param_values_by_plugin_name(
                self.Adapter_1.default_text_deal_with_before_convert)
        DealWithAfterConvertAudioPlugins_param_values = None
        if self.Adapter_1.default_audio_deal_with_after_convert != '不处理':
            DealWithAfterConvertAudioPlugins_param_values = self.PluginUI_DealWithAfterConvertAudioPlugins_1.get_param_values_by_plugin_name(
                self.Adapter_1.default_audio_deal_with_after_convert)
        return self.Adapter_1.start_convert(DealWithBeforeConvertAudioPlugins_param_values,
                                            DealWithAfterConvertAudioPlugins_param_values)

    def save_audio_deal_with_after_convert(self, way):
        self.Adapter_1.save_audio_deal_with_after_convert(way)
        return self.PluginUI_DealWithAfterConvertAudioPlugins_1.change_accordion_list([way])

    def save_text_deal_with_before_convert(self, way):
        self.Adapter_1.save_text_deal_with_before_convert(way)
        # print(self.PluginUI_DealWithBeforeConvertAudioPlugins_1.get_accordion_list())
        return self.PluginUI_DealWithBeforeConvertAudioPlugins_1.change_accordion_list([way])

    # 保存升降序字段
    def save_sort_desc(self, sort_desc_text):
        self.Adapter_1.Page_1.sort_desc = self.Adapter_1.sort_desc_list.get_value_by_text(sort_desc_text)
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    # 保存排序字段
    def save_sort_column(self, sort_column_text):
        self.Adapter_1.Page_1.sort_column = self.Adapter_1.sort_column_list.get_value_by_text(sort_column_text)
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def clear_all_select(self):
        txt = f'清空选中文件{len(self.Adapter_1.selected_article_list)}个'
        self.Adapter_1.selected_article_list = []
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            ),
            txt
        ]

    # 移除当前页下所有文章
    def cancel_current_page(self):
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        self.Adapter_1.selected_article_list = [title for title in self.Adapter_1.selected_article_list if
                                                title not in choice_list]
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            )
        ]

    # 选中当前页下所有文章
    def choose_current_page(self):
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        self.Adapter_1.selected_article_list.extend(choice_list)
        self.Adapter_1.selected_article_list = list(set(self.Adapter_1.selected_article_list))
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            )
        ]

    # 选中所有文章
    def choose_all(self):
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        all_choice_list = self.Adapter_1.get_current_search_all_article_list()
        self.Adapter_1.selected_article_list = all_choice_list
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            )
        ]

    # 删除所有选中的文章
    def delete_all_select(self):
        # 首先拿出选中的文章
        # 然后从加载的文章列表中，将选中的文章移除
        # 将选中文章的对应目录，删除掉，先删除目录，然后在更新文章数据，最后更新删除文件
        txt = f'删除选中文件{len(self.Adapter_1.selected_article_list)}个'
        self.Adapter_1.delete_all_select()
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            ),
            txt
        ]

    def collect_all_select(self):
        txt = f'收藏文件{len(self.Adapter_1.selected_article_list)}个'
        self.Adapter_1.collect_all_select()
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            ),
            txt
        ]

    def cancel_collect_all_select(self):
        txt = f'取消收藏文件{len(self.Adapter_1.selected_article_list)}个'
        self.Adapter_1.cancel_collect_all_select()
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return [
            gr.CheckboxGroup.update(choices=choice_list, value=self.Adapter_1.selected_article_list),
            gr.Dataframe.update(
                value=self.Adapter_1.ArticleDataframe_1.get_column_values(
                    self.Adapter_1.get_select_articles(self.Adapter_1.selected_article_list))
            ),
            txt
        ]

    def select_dataframe(self, evt: gr.SelectData):
        # 所有关联控件的变动会重复触发最后一次选中单元格事件，所以此处做了过滤，
        # 会有一些副作用，比如同一个单元格，点击一次之后不会再做出反应，需要切换其他单元格，再切换此单元格才能触发事件
        if self.is_equals_dataframe_evt(evt):
            return
        # print(f"You selected {evt.value} at {evt.index} from {evt.target}")
        self.select_dataframe_evt = evt

        Article_row = self.Adapter_1.get_select_article_row(evt.index[0])
        header_id = self.Adapter_1.get_select_article_header_id(evt.index[1])

        print(f'当前目录：{os.getcwd()}')
        if header_id in ['title', 'link']:
            webbrowser.open(Article_row.link)
        elif header_id == '打开目录':
            # 利用相对路径打开上级目录失败，原因未知
            # os.startfile(Article_row.path)
            absolute_path = os.path.abspath(Article_row.path)
            os.startfile(absolute_path)
        elif header_id == '打开txt':
            # 利用相对路径打开上级目录失败，原因未知
            # os.startfile(Article_row.get_txt_path())
            absolute_path = os.path.abspath(Article_row.get_txt_path())
            os.startfile(absolute_path)

    def change_page_no(self, page_no):
        Page_1 = self.Adapter_1.change_page_no(page_no)
        return gr.Button.update(value=f"共{Page_1.get_all_page()}页，跳转第{Page_1.page_no + 1}页")

    def reload_article_list(self):
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def search_by_more(self):
        self.Adapter_1.Page_1.page_no = 1
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def search_by_clear(self):
        self.Adapter_1.search_article_id = None
        self.Adapter_1.search_title = None
        self.Adapter_1.search_author = None
        self.Adapter_1.Page_1.page_no = 1
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def refresh_checkbox_article_list(self, Page_1, choice_list):
        return [
            gr.CheckboxGroup.update(choices=choice_list),
            gr.Button.update(value=f"共{Page_1.length}条记录，上一页"),
            gr.Number.update(value=Page_1.page_no),
            gr.Button.update(value=f"共{Page_1.get_all_page()}页，跳转第{Page_1.page_no + 1}页"),
        ]

    def change_page_size(self, page_size):
        print(f'page_size={page_size}')
        self.Adapter_1.Page_1.page_size = int(page_size)
        [Page_1, choice_list] = self.Adapter_1.get_current_search_article_list()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def go_to_pre_page(self):
        [Page_1, choice_list] = self.Adapter_1.go_to_pre_page()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def go_to_next_page(self):
        [Page_1, choice_list] = self.Adapter_1.go_to_next_page()
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def change_select_articles(self, article):
        return gr.Dataframe.update(
            value=self.Adapter_1.ArticleDataframe_1.get_column_values(self.Adapter_1.get_select_articles(article)))

    def search_articles_tab(self, tab):
        self.Adapter_1.Page_1.page_no = 1
        [Page_1, choice_list] = self.Adapter_1.search_articles_tab(tab)
        return self.refresh_checkbox_article_list(Page_1, choice_list)

    def search_articles_source(self, source):
        self.Adapter_1.Page_1.page_no = 1
        [Page_1, choice_list] = self.Adapter_1.search_articles_source(source)
        return self.refresh_checkbox_article_list(Page_1, choice_list)


class VoiceDemoTab:
    def __init__(self, Adapter_1):
        self.Adapter_1 = Adapter_1

    def draw_ui(self):
        Vits_1 = self.Adapter_1.Article2Audio_1.VitsManager_1.Vits_1
        with gr.Row():
            with gr.Column():
                sample_text = "其次，生活的意义还在于“交流”，你要开口说话！要和你的爱人、孩子、父母互动！他们是证明你活在设个社会上的鲜活的存在，是你人生的意义和动力。你要认识社会上的朋友，他们和你的交集在于志趣、性格、爱好，而不是工作。你要去社交，去和真实的人与世界互动，去尝试新鲜的东西、去没去过的地方——这种生活的“浸泡感”会让你在工作之外也显得很忙，但是会让你觉得生活有意义——和妻子裹在被窝里看看肥皂剧、和孩子一起晚上画画儿童画，去小区公园滑滑板，和爸妈坐在一张桌子上吃晚饭，听老爸乱侃国家大事、和球场上认识的损友出去喝啤酒吃小龙虾……"
                input_text = gr.Textbox(label="Text (100 words limitation) " if limitation else "Text", lines=5,
                                        value=sample_text, elem_id=f"input-text")
                lang = gr.Dropdown(label="Language", choices=["中文", "日语",
                                                              "中日混合（中文用[ZH][ZH]包裹起来，日文用[JA][JA]包裹起来）"],
                                   type="index", value="中文")
                btn = gr.Button(value="Submit1")
                with gr.Row():
                    search = gr.Textbox(label="Search Speaker", lines=1)
                    btn2 = gr.Button(value="Search")
                sid = gr.Dropdown(label="Speaker", choices=Vits_1.speakers, type="index", value=Vits_1.speakers[228])
                with gr.Row():
                    ns = gr.Slider(label="noise_scale(控制感情变化程度)", minimum=0.1, maximum=1.0, step=0.1,
                                   value=0.6, interactive=True)
                    nsw = gr.Slider(label="noise_scale_w(控制音素发音长度)", minimum=0.1, maximum=1.0, step=0.1,
                                    value=0.668, interactive=True)
                    ls = gr.Slider(label="length_scale(控制整体语速)", minimum=0.1, maximum=2.0, step=0.1,
                                   value=1.2, interactive=True)
            with gr.Column():
                o1 = gr.Textbox(label="Output Message")
                o2 = gr.Audio(label="Output Audio", elem_id=f"tts-audio")
                o3 = gr.Textbox(label="Extra Info")
                download = gr.Button("Download Audio")
            btn.click(self.vits, inputs=[input_text, lang, sid, ns, nsw, ls], outputs=[o1, o2, o3])
            download.click(None, [], [], _js=download_audio_js.format())
            btn2.click(self.search_speaker, inputs=[search], outputs=[sid])
            lang.change(self.change_lang, inputs=[lang], outputs=[ns, nsw, ls])

    def search_speaker(self, search_value):
        Vits_1 = self.Adapter_1.Article2Audio_1.VitsManager_1.Vits_1
        for s in Vits_1.speakers:
            if search_value == s:
                return s
        for s in Vits_1.speakers:
            if search_value in s:
                return s

    def vits(self, text, language, speaker_id, noise_scale, noise_scale_w, length_scale):
        Vits_1 = self.Adapter_1.Article2Audio_1.VitsManager_1.Vits_1
        print(
            f"text={text};language={language};speaker_id={speaker_id};noise_scale={noise_scale};noise_scale_w={noise_scale_w};length_scale={length_scale}")
        start = time.perf_counter()
        if not len(text):
            return "输入文本不能为空！", None, None
        text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
        if len(text) > 1000 and limitation:
            return f"输入文字过长！{len(text)}>1000", None, None
        if language == 0:
            text = f"[ZH]{text}[ZH]"
        elif language == 1:
            text = f"[JA]{text}[JA]"
        else:
            text = f"{text}"
        stn_tst, clean_text = Vits_1.get_text(text, Vits_1.hps_ms)
        with no_grad():
            try:
                x_tst = stn_tst.unsqueeze(0).to(Vits_1.device)
                x_tst_lengths = LongTensor([stn_tst.size(0)]).to(Vits_1.device)
                speaker_id = LongTensor([speaker_id]).to(Vits_1.device)
                audio = \
                    Vits_1.net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale,
                                          noise_scale_w=noise_scale_w,
                                          length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

                # set the desired sampling rate
                # sampling_rate = 22050
                # sf.write("output.wav", audio, sampling_rate)
                # time.sleep(1) # 暂停1秒
                # 播放音频文件
                # playsound('output.wav')

            except Exception as e:
                print('异常', e)

        return "生成成功!", (22050, audio), f"生成耗时 {round(time.perf_counter() - start, 2)} s"

    def change_lang(self, language):
        if language == 0:
            return 0.6, 0.668, 1.2
        else:
            return 0.6, 0.668, 1.1


class SpeakerTab:
    def __init__(self, Adapter_1):
        self.Adapter_1 = Adapter_1

    def draw_ui(self):
        Vits_1 = self.Adapter_1.Article2Audio_1.VitsManager_1.Vits_1
        gr.Radio(label="Speaker", choices=Vits_1.speakers, interactive=False, type="index")


# if __name__ == '__main__':
def load_ui():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', action="store_true", default=False)
    parser.add_argument("--share", action="store_true", default=False, help="share gradio app")
    parser.add_argument("--colab", action="store_true", default=False, help="share gradio app")
    args = parser.parse_args()

    with gr.Blocks() as app:
        gr.Markdown(
            "# <center> VITS语音合成\n"
            "# <center> 严禁将模型用于任何商业项目，否则后果自负\n"
            '<div align="center"><a href="https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai"><font color="#dd0000">此项目是基于huggingface网站上zomehwh所提供的vits项目vits-uma-genshin-honkai，二次开发而来</font></a></div>'
            # "<div align='center'>主要有赛马娘，原神中文，原神日语，崩坏3的音色</div>"
            # '<div align="center"><a><font color="#dd0000">结果有随机性，语调可能很奇怪，可多次生成取最佳效果</font></a></div>'
            # '<div align="center"><a><font color="#dd0000">标点符号会影响生成的结果</font></a></div>'
        )

        Article2Audio_1 = Article2Audio()

        tab1 = ArticleDownloadTab(ArticleDownloadAdapter.get_instance(Article2Audio_1))
        tab2 = Article2AudioTab(Article2AudioAdapter.get_instance(Article2Audio_1))
        tab3 = VoiceDemoTab(VoiceDemoAdapter.get_instance(Article2Audio_1))
        tab4 = SpeakerTab(SpeakerAdapter.get_instance(Article2Audio_1))

        with gr.Tabs():
            with gr.TabItem("文章获取"):
                tab1.draw_ui()
            with gr.TabItem("音频转换"):
                tab2.draw_ui()
            with gr.TabItem("vits"):
                tab3.draw_ui()
            with gr.TabItem("可用人物一览"):
                tab4.draw_ui()

    if args.colab:
        webbrowser.open("http://127.0.0.1:7860")
    app.queue(concurrency_count=1, api_open=args.api).launch(share=args.share)
