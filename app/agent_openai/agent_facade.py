from app.agent_openai.agent.agent_core import NingAgent
from app.common.error import ParameterException
from app.agent_openai.tools.youtube_search import YoutubeSearch
from app.agent_openai.tools.spotify_search import SpotifySearch
from os import path

ning_agent = NingAgent()


def dispatch(chat: str = "", chat_history: str = ""):
    if not chat:
        raise ParameterException("chat")
    content = ning_agent.query(chat, chat_history)
    return content


def download_youtube_video(video_url: str, video_path: str, video_quality: str):
    return YoutubeSearch.download_youtube_video_for_web(video_url, video_path, video_quality)


def download_spotify_music(music_url: str, music_path: str):
    if not music_url:
        raise ParameterException("music_url")
    if not music_path or not path.exists(music_path):
        raise ParameterException("music_path")

    return SpotifySearch.download_song_for_web(music_url, music_path)


if __name__ == "__main__":
    dispatch("文明的起源")
