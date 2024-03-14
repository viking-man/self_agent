import logging

import requests
from bs4 import BeautifulSoup
import subprocess
import os
import webbrowser
from app.common.error import ParameterException
from langchain.tools import tool


class BilibiliSearch:
    video_path = "/Users/viking/video/ningning/"

    def search_bilibili_video(keyword: str = ""):
        """
        搜索Bilibili视频
        :param keyword: 搜索关键词
        :return: 视频页面URL列表
        """
        search_url = f"https://search.bilibili.com/all?keyword={keyword}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        video_urls = []
        for item in soup.select('.img-anchor'):
            video_urls.append("https:" + item['href'])
            if len(video_urls) > 10:
                break
            # if a_tag and a_tag.has_attr('href'):
            #     video_url = "https:" + a_tag['href']
            #     video_urls.append(video_url)
        return video_urls

    @tool
    def search_play_bilibili_video(video_name):
        """用于搜索bilibili视频并在线播放"""
        video_urls = BilibiliSearch.search_bilibili_video(video_name)
        if video_urls and len(video_urls) > 0:
            webbrowser.open(video_urls[0])
        else:
            raise ParameterException(f"Cannot find the corresponding video->{video_name}")

    # def search_download_play_video(video_name):
    #     video_urls = search_bilibili_video(video_name)
    #     if video_urls:
    #         logging.info(f"Find video_urls->：{video_urls}")
    #         download_url = video_urls[0]  # 下载第一个搜索结果
    #         download_bilibili_video(download_url, video_path)
    #         # 由于you-get会自动给下载的视频文件命名，我们需要找到下载的视频文件
    #         # 这里假设下载的是MP4格式的视频，并且是下载目录中的第一个MP4文件
    #         video_files = [f for f in os.listdir(video_path) if f.endswith('.mp4')]
    #         if video_files:
    #             play_video(os.path.join(video_path, video_files[0]))
    #         else:
    #             raise ParameterException(f"Cannot find the corresponding video in local path.->{video_name}")
    #     else:
    #         raise ParameterException(f"Cannot find the corresponding video->{video_name}")

    # def download_bilibili_video(url, save_path):
    #     """
    #     使用you-get下载Bilibili视频
    #     :param url: Bilibili视频页面URL
    #     :param save_path: 视频保存路径
    #     """
    #     command = f"you-get -o {save_path} {url}"
    #     subprocess.run(command, shell=True)
    #
    # def play_video(video_path):
    #     """
    #     使用系统默认播放器播放视频
    #     :param video_path: 视频路径
    #     """
    #     if os.path.exists(video_path):
    #         if os.name == "nt":  # Windows系统
    #             os.startfile(video_path)
    #         else:  # macOS或Linux系统
    #             opener = "open" if os.name == "posix" else "xdg-open"
    #             subprocess.call([opener, video_path])
    #     else:
    #         print("视频文件不存在")


if __name__ == "__main__":
    BilibiliSearch.search_play_bilibili_video("NingNing")
