# Self_Agent 宁宁小助理
#### 程序主体框架使用flask作为前后端链接，Agent内部使用Langchain作为处理框架，梳理用户请求、分发对应处理工具、定制执行逻辑，语音处理使用whisper、GPT_SOVITS，画图使用StableDiffusion等。

# 整体架构图
![Agent助理](https://github.com/viking-man/self_agent/assets/22117154/b71e73a5-746d-4d2e-9e83-7ae0488205bf)

## 基本流程
->前端读取音频信息  
->flask服务端  
->whsiper转化成文本  
->agent梳理用户请求并分发
->agent-tool定制化处理逻辑 
->agent总结并输出最终结果
->GPT_SOVITS文本转为音频信息
->前端直接播放音频文件

## 使用流程  
python版本需要为3.10  

1. 下载程序
```
git clone https://github.com/viking-man/IntroventsEnglishCorner.git
cd IntroventsEnglishCorner
```
2. 初始化项目虚拟环境  
```
  python -m venv venv
  . venv/bin/activate
```

windows用户在使用`python -m venv venv`创建虚拟环境后，通过命令`cd venv/Scripts/`到Scripts目录，直接使用activate命令激活创建的虚拟环境

3. 安装对应python包

   `pip install -r requirements.txt`
4. 初始化对应数据库
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```
5. 配置本地参数
6. 运行启动
   
   `flask run`

7. 网页打开环境运行地址
   

   `127.0.0.1:5000`

## 注意事项
1. .flaskenv中的OPENAI_API_KEY需要换成你自己的openai_api_key
2. chatgpt_proxy中需要填写你自己的openai_api_key
3. whsiper第一次使用会默认下载small的模型，大概500M，需要等待；如果觉得转换效果不好，可以到WhisperModel.py文件中将small换成medium或者large


