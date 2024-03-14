from langchain.agents import tool
import requests
from app.agent_openai.agent.agent_config import WEB_SEARCH_MAX_RESULT, RAPID_API_KEY
import logging
from app.common.error import ParameterException


# 默认的web搜索工具，查询用户输入的问题最新的网页解释，给大模型作为参考资料
class GoogleSearch:

    @tool
    def web_search(question: str = ""):
        """Utilize the default web search tool to investigate the user's query, focusing on the most recent web pages that provide explanations.
        The findings should be used as reference material for the large model."""
        query = question.strip()

        if query == "":
            return ""

        if RAPID_API_KEY == "":
            raise ParameterException("RAPID_API_KEY", "请配置你的 RapidAPIKey")
        RapidAPIKey = RAPID_API_KEY

        url = "https://google-web-search1.p.rapidapi.com/"

        querystring = {"query": query, "limit": WEB_SEARCH_MAX_RESULT, "related_keywords": "true"}

        headers = {
            "X-RapidAPI-Key": RapidAPIKey,
            "X-RapidAPI-Host": "google-web-search1.p.rapidapi.com"
        }

        logging.info(f"Google.web_search request->{querystring}")
        response = requests.get(url, headers=headers, params=querystring)
        logging.info(f"Google.web_search response->{response.json()}")

        data_list = response.json()['results']

        if len(data_list) == 0:
            return ""
        else:
            result_arr = []
            for i in range(WEB_SEARCH_MAX_RESULT):
                item = data_list[i]
                title = item["title"]
                description = item["description"]
                item_str = f"{title}: {description}"
                result_arr = result_arr + [item_str]

            result_str = "\n".join(result_arr)
            return result_str
