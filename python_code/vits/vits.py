# coding=utf-8
from pickle import TRUE
import time
import os
import sys
import gradio as gr

module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_dir)

import utils
import argparse
import commons
from models import SynthesizerTrn
from text import text_to_sequence
import torch
from torch import no_grad, LongTensor
import webbrowser
import logging
import soundfile as sf
from playsound import playsound
import time

logging.getLogger('numba').setLevel(logging.WARNING)
limitation = os.getenv("SYSTEM") == "spaces"  # limit text and audio length in huggingface spaces


class Vits:
    def __init__(self, device_type, hparams_file, model_path):
        self.hps_ms = None
        self.speakers = []
        self.net_g_ms = None
        self.device = None
        self.load(device_type, hparams_file, model_path)

    def load(self, device_type, hparams_file, model_path):
        device_type = 'cpu' if device_type is None else device_type
        parser = argparse.ArgumentParser()
        parser.add_argument('--device', type=str, default=device_type)
        # parser.add_argument('--api', action="store_true", default=False)
        # parser.add_argument("--share", action="store_true", default=False, help="share gradio app")
        # parser.add_argument("--colab", action="store_true", default=False, help="share gradio app")
        args = parser.parse_args()
        device = torch.device(args.device)

        hps_ms = utils.get_hparams_from_file(r'{}'.format(hparams_file))
        net_g_ms = SynthesizerTrn(
            len(hps_ms.symbols),
            hps_ms.data.filter_length // 2 + 1,
            hps_ms.train.segment_size // hps_ms.data.hop_length,
            n_speakers=hps_ms.data.n_speakers,
            **hps_ms.model)
        _ = net_g_ms.eval().to(device)
        speakers = hps_ms.speakers
        model, optimizer, learning_rate, epochs = utils.load_checkpoint(r'{}'.format(model_path), net_g_ms, None)

        self.hps_ms = hps_ms
        self.net_g_ms = net_g_ms
        self.speakers = speakers
        self.device = device

    def vits(self, index, text, language, speaker_id, noise_scale, noise_scale_w, length_scale, dir_temp):
        # print(f"text={text};language={language};speaker_id={speaker_id};noise_scale={noise_scale};noise_scale_w={noise_scale_w};length_scale={length_scale}")
        start = time.perf_counter()
        if not len(text):
            return "输入文本不能为空！", None, None
        text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
        if language == 0:
            text = f"[ZH]{text}[ZH]"
        elif language == 1:
            text = f"[JA]{text}[JA]"
        else:
            text = f"{text}"
        stn_tst, clean_text = self.get_text(text, self.hps_ms)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(self.device)
            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(self.device)
            speaker_id = LongTensor([speaker_id]).to(self.device)
            audio = \
                self.net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale,
                                    noise_scale_w=noise_scale_w,
                                    length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

            # set the desired sampling rate
            sampling_rate = 22050
            sf.write(dir_temp + '/' + str(index) + ".wav", audio, sampling_rate)
            # time.sleep(1) # 暂停1秒
            # 播放音频文件
            # playsound('output.wav')

    def get_text(self, text, hps):
        text_norm, clean_text = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = LongTensor(text_norm)
        return text_norm, clean_text
