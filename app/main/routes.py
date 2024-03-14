import logging
import os.path

from flask import Flask, render_template, request, jsonify, send_file
from app.open_ai import chatgpt_proxy
from app.tts import gtts_proxy, gpt_tts_proxy
from app.models import Audio
from app.open_ai import whisper_proxy
from app.main import bp
import io
import time
from pathlib import Path
from app.agent_openai import agent_facade
from app.common.error import ParameterException
from os import path
from app.open_ai.subtitle_translator import SubtitleTranslator


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/text_chat', methods=['POST'])
def text_chat():  # put application's code here
    print(str(request))
    # 获取参数
    user_message = request.form['user_message']
    user_id = request.form['user_id']
    chat_id = request.form['chat_id']
    if chat_id is None or chat_id == 'undefined' or len(chat_id) == 0:
        chat_id = str(abs(hash(user_message)))
    gpt_version = request.form['gpt_version']

    # chatgpt请求
    # ai_message, chat_history = chatgpt_proxy.text_chat(user_message, user_id, chat_id, gpt_version)
    # 使用agent
    chat_history, _ = chatgpt_proxy.get_chat_history(user_id, chat_id, gpt_version)
    ai_message = agent_facade.dispatch(user_message, chat_history)

    # tts转成语音
    audio_id = gpt_tts_proxy.convert_to_audio(user_id, chat_id, ai_message)

    # 返回信息
    return jsonify({
        'ai_message': ai_message,
        'chat_history': chat_history,
        'audio_id': audio_id,
        'chat_id': chat_id
    })


@bp.route('/get_audio', methods=['POST'])
def receive_audio():
    audio_id = request.form['audio_id']
    audio = Audio.query.get_or_404(audio_id)

    return send_file(
        io.BytesIO(audio.audio_data),
        mimetype="audio/wav"  # 设置适当的MIME类型
    )


@bp.route('/speech_chat', methods=['POST'])
def speech_chat():
    print(str(request))
    user_id = request.form.get('user_id')
    chat_id = request.form.get('chat_id')
    gpt_version = request.form.get('gpt_version')

    audio_file = request.files['audio']
    # Save the audio file (optional)
    audio_path = str(
        Path("app/files/audio/input", user_id + "_" + chat_id + "_" + str(time.time()) + ".wav").absolute())
    audio_file.save(audio_path)

    chat_text = whisper_proxy.transcribe_to_text(audio_path)

    if chat_id is None or chat_id == 'undefined' or len(chat_id) == 0:
        chat_id = str(abs(hash(chat_text)))

    # chatgpt请求
    # ai_message, chat_history = chatgpt_proxy.text_chat(chat_text, user_id, chat_id, gpt_version)
    chat_history, _ = chatgpt_proxy.get_chat_history(user_id, chat_id, gpt_version)
    ai_message = agent_facade.dispatch(chat_text, chat_history)

    # tts转成语音
    audio_id = gpt_tts_proxy.convert_to_audio(user_id, chat_id, ai_message)

    return jsonify({
        'user_message': chat_text,
        'ai_message': ai_message,
        'audio_id': audio_id,
        'chat_id': chat_id})


@bp.route('/clear_history', methods=['POST'])
def clear_history():
    data = request.get_json()
    userid = data.get('userId')
    print(data)
    return jsonify({'message': 'History cleared successfully'})


@bp.route('/get_image_list', methods=['POST'])
def get_image_list():
    data = request.get_json()
    userid = data.get('userId')

    # 示例：替换为实际的目录路径
    directory_path = os.path.join(os.path.dirname(__file__), f"../files/image")

    # 获取目录下的所有文件名称，并按创建时间排序
    iamges = get_files_sorted_by_creation_time(directory_path)

    return jsonify({
        'message': 'History cleared successfully',
        'imageList': iamges
    })


@bp.route('/get_image')
def get_image():
    # 从请求参数中获取文件名
    file_name = request.args.get('fileName')

    # 构造完整的文件路径
    file_path = os.path.join(os.path.dirname(__file__), f"../files/image/{file_name}")

    try:
        # 发送文件作为响应
        return send_file(file_path, mimetype='image/jpeg')  # 根据实际情况设置 mimetype
    except FileNotFoundError:
        # 处理文件不存在的情况
        return 'File not found', 404


@bp.route('/download_video', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('videoUrl')
    video_file_path = data.get('videoFilePath')
    videoQuality = data.get('videoQuality')
    if not video_url:
        raise ParameterException("video_url")
    if not videoQuality:
        raise ParameterException("videoQuality")
    if not video_file_path or not path.exists(video_file_path):
        raise ParameterException("video_path")

    video_file = agent_facade.download_youtube_video(video_url, video_file_path, videoQuality)

    return jsonify({'message': f'Youtube video download onto {video_file} successfully'})


@bp.route('/download_music', methods=['POST'])
def download_music():
    data = request.get_json()
    musicUrl = data.get('musicUrl')
    musicFilePath = data.get('musicFilePath')
    if not musicUrl:
        raise ParameterException("musicUrl")
    if not musicFilePath or not path.exists(musicFilePath):
        raise ParameterException("video_path")

    music_file = agent_facade.download_spotify_music(musicUrl, musicFilePath)

    return jsonify({'message': f'Spotify music download onto {music_file} successfully'})


@bp.route('/subtitle_translate', methods=['POST'])
def subtitle_translate():
    data = request.get_json()
    logging.info(f"subtitle_translate request params->{data}")

    translationVideoFile = data.get('translationVideoFile')
    translationLanguage = data.get('translationLanguage')
    translationSubtitleFile = data.get('translationSubtitleFile')
    translationModel = data.get('translationModel')
    if not translationVideoFile or not path.exists(translationVideoFile):
        raise ParameterException("translationVideoFile")
    if not translationLanguage:
        raise ParameterException("translationLanguage")

    if not translationModel:
        translationModel = "small"

    translator = SubtitleTranslator(translationModel, translationVideoFile, translationLanguage)
    if not translationSubtitleFile:
        completed_video = translator.transcribe()
    else:
        completed_video = translator.add_subtitle(translationVideoFile, translationSubtitleFile)

    return jsonify({'message': f'Subtitle add to {completed_video} successfully'})


def get_files_sorted_by_creation_time(directory):
    try:
        # 获取目录下的所有文件和子目录
        all_files = os.listdir(directory)

        # 过滤出文件，而非子目录，并获取文件的创建时间
        files_with_creation_time = [(file, os.path.getctime(os.path.join(directory, file))) for file in all_files if
                                    os.path.isfile(os.path.join(directory, file))]

        # 根据创建时间排序文件列表
        sorted_files = sorted(files_with_creation_time, key=lambda x: x[1], reverse=True)

        # 仅返回文件名称，不包括创建时间
        sorted_file_names = [file[0] for file in sorted_files]

        return sorted_file_names
    except Exception as e:
        print(f"Error getting files: {e}")
        return None


@bp.errorhandler(Exception)
def handle_parameter_exception(error):
    response = jsonify({'error': error.message})
    response.status_code = 400
    return response
