import os

LOCAL_CONTENT = os.path.join(os.path.dirname(__file__), "../../resources/docs")
VS_PATH = os.path.join(os.path.dirname(__file__), "vector_store\FAISS")
CHROMA_VS_PATH = os.path.join(os.path.dirname(__file__), "vector_store\chroma_db")
CHUNK_SIZE = 768
CHUNK_OVERLAP = 64
VECTOR_SEARCH_TOP_K = 2
# os.environ["SERPAPI_API_KEY"] = "Your SerpAPI Key"

# WEB_SEARCH_MAX_RESULT = 2
IMAGE_STORE_PATH = ""

PROMPT_TEMPLATE = """已知信息：
{context}

根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请给出你认为最合理的回答。答案请使用中文。 问题是：{question}"""

PROMPT_TEMPLATE_EN = """
Given the information:
{context}
Based on the above information, concisely and professionally answer the user's question. If an answer cannot be derived from the given context, provide the most reasonable response you can think of. Please respond in Chinese. The question is: {question}
"""
