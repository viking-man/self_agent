from dotenv import load_dotenv
import os

# 加载环境变量，todo 无效需要更改
load_dotenv('../../.flaskenv', override=True)
# 获取环境变量
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

if __name__ == "__main__":
    print(OPENAI_API_KEY)
    print(TAVILY_API_KEY)
