## Self_Agent 宁宁小助理
#### 程序主体思路使用类似剧本的定制逻辑，主体框架使用flask作为前后端链接，Agent内部使用Langchain作为处理框架，梳理用户请求、分发对应处理工具、定制执行逻辑，语音处理使用whisper、GPT_SOVITS，画图使用StableDiffusion等。

## 整体架构图
![Agent助理](https://github.com/viking-man/self_agent/assets/22117154/94c9d99f-25bf-4330-8a79-a2afc0ec7c8f)

## 整体思路
![剧本流](https://github.com/viking-man/self_agent/assets/22117154/e262679f-66bd-4f3d-8c36-4d2f04aaaf88)

## 基本流程
->前端读取音频信息  
->flask服务端  
->whsiper转化成文本  
->agent梳理用户请求并分发  
->agent-tool定制化处理逻辑   
->agent总结并输出最终结果  
->GPT_SOVITS文本转为音频信息  
->前端直接播放音频文件  

## 使用说明
Agent使用的文本转语音tts模型和语音转文本whisper模型的推理比较耗计算资源和内存，不推荐无GPU电脑使用。如果不想使用tts模型，可以自行在routes类中修改。

## 使用流程  
python版本需要为3.10  

1. 下载程序
```
git clone git@github.com:viking-man/self_agent.git
```
2. 下载必备程序
   
   1. ffmpeg
3. 配置本地文件：app/agent_openai/custom_config.py
| 配置项   | 配置解释 | 示例    | 网址    |
|--------|------|---------|---------|
| RAPID_API_KEY   | Google搜索用到的rapid-api-key   | "3b5dd7d5f5mshd78f146dc498a60p143d49jsn07023d199"    | https://rapidapi.com/UnlimitedAPI/api/google-web-search1  |
| STABLE_DIFFUSION_MODEL_PATH  | 本地下载的stable-diffusion模型文件路径   |  "G:\data\stablediffusion\models\dream\ghostmix_v20Bakedvae.safetensors"  | https://civitai.com/models    |
| MUSIC_DIRECTORY   | Spotify音乐存储路径   | "E:\music\spotify\songs"    |     |
| SPOTIFY_CLIENT_ID   | Spotify-APP的client_id   | "55ed24ee34534fe48d1"   | https://developer.spotify.com/dashboard    |
| SPOTIFY_CLIENT_SECRET   | Spotify-APP的client_secret   | "55ed24ee34534fe48d1"   | https://developer.spotify.com/dashboard    |
| ENABLE_SOVITS   | 是否使用GPT_SOVITS的TTS工具，具体使用情况查询后面的github地址   | True   | https://github.com/RVC-Boss/GPT-SoVITS   |
   
   
4. 初始化项目虚拟环境  
```
  python -m venv venv
  . venv/bin/activate
```

windows用户在使用`python -m venv venv`创建虚拟环境后，通过命令`cd venv/Scripts/`到Scripts目录，直接使用activate命令激活创建的虚拟环境

5. 安装对应python包
   `pip install \external\package\GPT_SoVITS-1.0.tar.gz` 安装GPT_SOVITS引用包
   `pip install -r requirements.txt`
6. 初始化对应数据库
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```
7. 配置本地参数
8. 运行启动
   
   `flask run`

9. 网页打开环境运行地址
   

   `127.0.0.1:5000`

## 注意事项
1. .flaskenv中的OPENAI_API_KEY需要换成你自己的openai_api_key，这个可能不好用，建议直接export OPENAI_API_KEY=your_api_key
2. chatgpt_proxy中需要填写你自己的openai_api_key
3. whsiper第一次使用会默认下载medium的模型，大概1.3G，需要等待；如果觉得转换效果不好，可以到WhisperModel.py文件中将small换成medium或者large


