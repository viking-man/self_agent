from app.tts.gpt_tts_config import *
import soundfile as sf
import logging
from GPT_SoVITS.inference_webui import InferenceWebUI
from app.models import Audio
import time
from app.type import AudioType
from app import db
from pathlib import Path


class GptTTSModel:

    def __init__(self):
        super().__init__()
        self.init_models()

    def init_models(self):
        self.GPT_model_path = GPT_MODEL_PATH
        self.SoVITS_model_path = SOVITS_MODEL_PATH
        self.inference_model = InferenceWebUI(
            BERT_PATH,
            CNHUBERT_BASE_PATH,
            GPT_MODEL_PATH,
            SOVITS_MODEL_PATH)

        # gpt微调权重
        self.inference_model.change_gpt_weights(gpt_path=self.inference_model.gpt_path)
        # sovits微调权重
        self.inference_model.change_sovits_weights(sovits_path=self.inference_model.sovits_path)

    def text_to_speech(self, text: str, lang: str, file_path: str):
        # 生成wav
        synthesis_result = self.inference_model.get_tts_wav(ref_wav_path=EXAMPLE_WAV,
                                                            prompt_text=EXAMPLE_TEXT,
                                                            prompt_language=EXAMPLE_TEXT_LANG,
                                                            text=text,
                                                            text_language=lang)

        result_list = list(synthesis_result)
        if result_list:
            last_sampling_rate, last_audio_data = result_list[-1]
            sf.write(file_path, last_audio_data, last_sampling_rate)

        logging.info(f"合成完成！输出路径：{file_path}")


gptTTSModel = GptTTSModel()

import re


def contains_english(text):
    pattern = re.compile(r'[a-zA-Z]')
    return bool(pattern.search(text))


def convert_to_audio(user_id, chat_id, text_content):
    # convert text to speech
    if contains_english(text_content):
        lang = "all_zh"
    else:
        lang = "zh"

    # 定时任务清理
    file_path = str(Path("app/files/audio/output",
                         user_id + "_" + chat_id + "_" + str(int(time.time())) + ".wav").absolute())

    gptTTSModel.text_to_speech(text_content, lang, file_path)

    with open(file_path, 'rb') as f:
        audio_data = f.read()

    audio = Audio(chat_id=chat_id, type=AudioType.INPUT.name, audio_data=audio_data)
    db.session.add(audio)
    db.session.commit()
    return audio.id


if __name__ == "__main__":
    convert_to_audio("123", "456", "我是宁艺卓，我爱唱歌，爱大自然，爱一切充满生命力的东西，我爱蒋威")
