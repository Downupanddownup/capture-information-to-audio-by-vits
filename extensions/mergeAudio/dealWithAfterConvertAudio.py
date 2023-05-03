import os
import glob
import wave
import uuid
from pydub import AudioSegment


def description():
    return '将输出音频合并成一段音频'


def open_param():
    return False


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


def deal_with_audio(wav_path_list, ArticleVoice_list, param_values, default_output_path, default_audio_format):
    # print(f'音频合并插件，接收到的参数{param_values}')
    print('开始执行音频合并插件')
    # 获取音频文件的基本参数
    with wave.open(wav_path_list[0], 'rb') as f:
        params = f.getparams()

    unique_string = str(uuid.uuid4())

    target_wav = default_output_path + '/' + unique_string + '.wav'
    target_mp3 = default_output_path + '/' + unique_string + '.mp3'

    # 创建一个新的音频文件A.wav
    with wave.open(target_wav, 'wb') as f:
        f.setparams(params)

        # 逐个读取所有音频文件，并写入A.wav文件中
        for wav_file in wav_path_list:
            with wave.open(wav_file, 'rb') as f1:
                frames = f1.readframes(f1.getnframes())
                f.writeframes(frames)

    if default_audio_format == 'mp3':
        # 读取 WAV 文件
        sound = AudioSegment.from_wav(target_wav)
        # 将 WAV 文件导出为 MP3 文件
        sound.export(target_mp3, format="mp3")
        # 删除wav文件
        os.remove(target_wav)

    print(f'合并完成：输出音频为{target_mp3}')
