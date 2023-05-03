from pydub import AudioSegment

import os
import sys
import re
import wave
import datetime
from python_code.vits.vits import Vits
from pydub.silence import split_on_silence
from util.commonUtil import CustomError
from util.commonUtil import Timer


# 将模块所在目录添加到 Python 模块搜索路径中
# module_dir = os.path.dirname(os.path.abspath(__file__))
# module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(module_dir)
# print('module_dir'+module_dir)

class VitsManager:
    def __init__(self, device_type, hparams_file, model_path):

        download_path_tips = ' 在启动本项目前，请先前往https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai/tree/main/model下载config.json和G_953000.pth文件，放入model目录下'
        # 检查文件是否存在
        temp_path = r'{}'.format(hparams_file)
        if not os.path.isfile(temp_path):
            raise CustomError(f'未找到文件：{temp_path}{download_path_tips}')
        temp_path = r'{}'.format(model_path)
        if not os.path.isfile(temp_path):
            raise CustomError(f'未找到文件：{temp_path}{download_path_tips}')

        # 初始化方法
        self.Vits_1 = Vits(device_type, hparams_file, model_path)

    # 合并wav音频
    def merge_wav_voice(self, RoleVoice_1, dir_temp, tooth_sound_weakening):
        # 合并之后的音频
        new_file_all_path_name = RoleVoice_1.get_wav_file_path()
        # 获取当前目录下的所有.wav文件
        wav_files = [f for f in os.listdir(dir_temp) if os.path.splitext(f)[1] == ".wav"]
        # 将文件名按照数字大小从小到大排序
        wav_files.sort(key=lambda x: int(x.split(".")[0]))
        # 获取音频文件的基本参数
        with wave.open(os.path.join(dir_temp, wav_files[0]), 'rb') as f:
            params = f.getparams()
        # 创建一个新的音频文件A.wav
        with wave.open(new_file_all_path_name, 'wb') as f:
            f.setparams(params)
            # 逐个读取所有音频文件，并写入A.wav文件中
            for wav_file in wav_files:
                with wave.open(os.path.join(dir_temp, wav_file), 'rb') as f1:
                    frames = f1.readframes(f1.getnframes())
                    f.writeframes(frames)
        if tooth_sound_weakening:
            self.weak_tooth_sound(new_file_all_path_name, new_file_all_path_name)

    # 弱化齿音
    def weak_tooth_sound(self, source_wav, target_wav):
        print('开始执行，齿音弱化')
        Timer_1 = Timer('齿音弱化耗时')
        Timer_1.start()
        # 加载音频文件
        sound_file = AudioSegment.from_wav(source_wav)
        # 拆分为音频片段
        audio_chunks = split_on_silence(sound_file, min_silence_len=1000, silence_thresh=-70)
        # 消除齿音
        clean_audio_chunks = []
        for chunk in audio_chunks:
            clean_audio_chunks.append(chunk.high_pass_filter(300).low_pass_filter(4000))
        # 合并音频片段
        output_audio = clean_audio_chunks[0]
        for chunk in clean_audio_chunks[1:]:
            output_audio += chunk
        # 保存音频文件
        output_audio.export(target_wav, format="wav")
        Timer_1.stop()
        Timer_1.print_second_info()

    # 将文本转换为wav音频
    def convert_txt_2_wav(self, RoleVoice_1, new_content, article_slicing_length, dir_temp, tooth_sound_weakening,
                          speak_content_format, cur_count, all_count):
        Article_1 = RoleVoice_1.Article_1
        Role_1 = RoleVoice_1.Role_1
        # 清空目录B下的所有文件
        for f in os.listdir(dir_temp):
            os.remove(os.path.join(dir_temp, f))
        if speak_content_format is None:
            content = f'文章标题：{Article_1.title},朗读者：{Role_1.role}。' + new_content
        else:
            content = self.get_speak_format_content(Article_1, Role_1, speak_content_format, new_content)
        print(f'文件{os.path.basename(Article_1.title)}的字符数为：{len(content)}，朗读{Role_1.role}')
        chunks = [content[i:i + article_slicing_length] for i in
                  range(0, len(content), article_slicing_length)]  # 分割字符串
        print(f"{Article_1.title}的切片长度：{len(chunks)}")  # 打印结果
        i = 0
        for item in chunks:
            self.role_speach(item, i, Role_1, dir_temp)
            print(f"已完成切片{i}({i + 1}/{len(chunks)})")
            i += 1
        print(f'{Article_1.title}，朗读{Role_1.role}转换结束,({cur_count}/{all_count})')
        self.merge_wav_voice(RoleVoice_1, dir_temp, tooth_sound_weakening)

    def get_speak_format_content(self, Article_1, Role_1, speak_content_format, new_content):
        author = '未知' if Article_1.author is None else Article_1.author
        publish_date = '未知' if Article_1.publish_date is None else Article_1.publish_date
        return speak_content_format.format(title=Article_1.title, author=author,
                                           publish_date=publish_date, role=Role_1.role, content=new_content)

    def role_speach(self, input_text, index, role, dir_b):
        language = role.language
        speaker_id = role.speaker_id
        noise_scale = role.noise_scale
        noise_scale_w = role.noise_scale_w
        length_scale = role.length_scale
        self.Vits_1.vits(index, input_text, language, speaker_id, noise_scale, noise_scale_w, length_scale, dir_b)
