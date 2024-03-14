from app.open_ai.whisper_model import WhisperModel
from whisper.audio import load_audio
from whisper.utils import get_writer
import logging
import os
import time
from pathlib import Path
from translatepy import Translate
import ffmpeg
import sys
import re


class SubtitleTranslator:
    def __init__(self, model_size, video_path, target_lang):
        self.sampling_rate = 16000
        self.model_size = model_size
        self.video_path = video_path
        self.target_lang = target_lang
        self.whisper_model = WhisperModel(model_size=model_size)
        self.whisper_model.load_model()

    def transcribe(self):
        audio = load_audio(self.video_path, self.sampling_rate)

        start_time = time.time()
        path = Path(self.video_path)

        # 字幕提取
        if self.target_lang == 'default':
            transcribe_result = self.whisper_model.transcribe(audio, None)
            logging.info(f'Transcribe result for {input} is {transcribe_result}')
            # 输出目录
            output_dir = str(path.absolute().parent)
            # 生成字幕文件
            srt_file = self.writeSrtFile(output_dir, path, transcribe_result, self.target_lang)
            # 添加字幕文件到视频
            completed_video_path = self.add_subtitile_to_video(output_dir, path, srt_file, start_time)
            return completed_video_path
        else:
            # 字幕提取+翻译成英文
            transcribe_result = self.whisper_model.translate(audio, 'en')
            logging.info(f'Transcribe result for {input} is {transcribe_result}')
            # 输出目录
            output_dir = str(path.absolute().parent)
            # 生成字幕文件
            srt_file = self.writeSrtFile(output_dir, path, transcribe_result, 'en')

            # 翻译字幕文件，指定语言
            if not self.target_lang == 'default' and not self.target_lang == 'en':
                self.translate_to_target_lang(transcribe_result)
                # 生成翻译后的字幕文件
                srt_file = self.writeSrtFile(output_dir, path, transcribe_result, self.target_lang)
            # 添加字幕文件到视频
            completed_video_path = self.add_subtitile_to_video(output_dir, path, srt_file, start_time)
            return completed_video_path

    def add_subtitile_to_video(self, output_dir, path, srt_file, start_time):
        srt_full_path = os.path.join(output_dir, srt_file)
        # 添加字幕到视频中
        input_name = path.stem
        suffix = path.suffix
        output = os.path.join(output_dir, input_name + "_subtitle" + suffix)
        self.add_subtitles(path, srt_full_path, output)
        assert os.path.exists(srt_full_path), f"SRT file not generated?"
        logging.info(f"Save srt file [{srt_full_path}] to [{output}],time->[{time.time() - start_time:.1f}]")
        return output

    def writeSrtFile(self, output_dir, path, transcribe_result, lang):

        for segment in transcribe_result["segments"]:
            # 不想用到whsiper的新功能，高亮和字符限制的，只能用到英文上
            if "words" in segment:
                del segment["words"]
            # whisper字幕有点超前,延迟0.5s
            segment["start"] = segment["start"] + 0.5
            segment["end"] = segment["end"] + 0.5

        srt_writer = get_writer("srt", output_dir)
        srt_file = path.stem + f"_{lang}.srt"
        logging.info(f"output_dir->{output_dir},srt->{srt_file}")
        srt_writer(transcribe_result, srt_file, {"max_line_width": 47, "max_line_count": 1, "highlight_words": False})
        return srt_file

    def translate_to_target_lang(self, translate_result):
        logging.info(f"Translate to {self.target_lang} start.")
        translator = Translate()
        # translate
        for i in range(len(translate_result["segments"])):
            segment_text = translate_result["segments"][i]["text"]
            try:
                text_ = segment_text.replace("<u>", "").replace("</u>", "")
                translate_text = translator.translate(text_, self.target_lang).result
            except Exception as e:
                # 处理其他所有类型的异常
                logging.info(f"An exception occurred when translate->{segment_text},error->{str(e)}")
                translate_text = segment_text
            translate_result["segments"][i]["text"] = translate_text

    def escape_windows_path(self, path):
        # 将单个反斜杠替换为双反斜杠
        sub = re.sub(r'\\', r'\\\\', path)
        sub = "\'" + sub + "\'"
        split = sub.split(":")
        if len(split) == 2:
            return split[0] + "\\" + ":" + split[1]

        return sub

    def is_windows(self):
        return sys.platform.startswith('win')

    def add_subtitles(self, video_file, subtitle_file, output_file):
        # 使用 ffmpeg.input() 来指定输入文件和字幕文件
        input_video = ffmpeg.input(Path(video_file))
        input_subtitle = ffmpeg.input(Path(subtitle_file))
        # 区分系统
        if self.is_windows():
            subtitle_file = self.escape_windows_path(subtitle_file)
        logging.info(f'subtitle_file after transfer->{subtitle_file}')
        # 使用 filter() 添加字幕
        output = ffmpeg.output(
            input_video,  # 输入视频文件
            input_subtitle,  # 输入字幕文件
            output_file,
            # vcodec='copy',  # 视频编解码器，此处保持原样
            acodec='copy',  # 音频编解码器，此处保持原样
            scodec='mov_text',  # 字幕编解码器
            f='mp4',  # 输出文件格式
            vf=f'subtitles={subtitle_file}',  # 添加字幕滤镜
            strict='experimental',  # 使用实验性字幕编解码器
            y='-y'
        )

        # 运行 ffmpeg 命令以创建输出文件
        ffmpeg.run(output)

        logging.info(f'字幕已添加到 {output_file}')

    def add_subtitle(self, video_path, subtitle_path):
        path = Path(video_path)
        input_name = path.stem
        suffix = path.suffix
        output_dir = str(path.absolute().parent)

        output = os.path.join(output_dir, input_name + "_subtitle_" + self.target_lang + suffix)
        self.add_subtitles(path, subtitle_path, output)

        return output


if __name__ == "__main__":
    translator = SubtitleTranslator("small",
                                    "/Users/viking/ai/develope/ning_agent/app/agent_openai/tools/TimeAfterTime.mp4",
                                    "zh")
    translator.transcribe()
