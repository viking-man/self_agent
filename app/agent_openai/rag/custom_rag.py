from typing import Any, List, Dict, Mapping, Optional
import os
from langchain_community.document_loaders import TextLoader, UnstructuredFileLoader
from langchain.vectorstores import FAISS
import datetime
import torch
from tqdm import tqdm
from app.agent_openai.agent.agent_config import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
import logging


def load_txt_file(filepath):
    loader = TextLoader(filepath, encoding="utf8")
    textsplitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                                  chunk_overlap=CHUNK_OVERLAP,
                                                  length_function=len)
    docs = loader.load_and_split(text_splitter=textsplitter)
    return docs


def torch_gc():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    elif torch.backends.mps.is_available():
        try:
            from torch.mps import empty_cache
            empty_cache()
        except Exception as e:
            logging.error(f"清除缓存时出错，错误信息->{e}")
            logging.info(
                "如果您使用的是 macOS 建议将 pytorch 版本升级至 2.0.0 或更高版本，以支持及时清理 torch 产生的内存占用。")


def load_file(filepath):
    if filepath.lower().endswith(".md"):
        loader = UnstructuredFileLoader(filepath, mode="elements")
        docs = loader.load()
    elif filepath.lower().endswith(".pdf"):

        loader = PyPDFLoader(filepath)
        textsplitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                                      chunk_overlap=CHUNK_OVERLAP,
                                                      length_function=len)
        docs = textsplitter.split_documents(loader.load())
    else:
        docs = load_txt_file(filepath)
    return docs


def load_dir(dir_path):
    docs = []
    failed_files = []
    loaded_files = []
    try:
        for path in tqdm(os.listdir(dir_path), "加载文件"):
            full_filepath = os.path.join(dir_path, path)
            if os.path.isdir(full_filepath):
                sub_docs, sub_failed_files, sub_loaded_files = load_dir(full_filepath)
                docs += sub_docs
                failed_files += sub_failed_files
                loaded_files += sub_loaded_files
            elif os.path.isfile(full_filepath):
                docs += load_file(full_filepath)
                loaded_files += full_filepath
    except Exception as e:
        logging.error(f"An error occuren when load file from {dir_path},error->{e}")
        failed_files.append(dir_path)
    return docs, failed_files, loaded_files


def get_related_content(related_docs):
    related_content = []
    for doc in related_docs:
        related_content.append(doc.page_content)
    return "\n".join(related_content)


def get_docs_with_score(docs_with_score):
    docs = []
    for doc, score in docs_with_score:
        doc.metadata["score"] = score
        docs.append(doc)
    return docs


# filepath 可以是目录，也可以是文件
def init_knowledge_vector_store(filepath: str or List[str],
                                vs_path: str or os.PathLike = None,
                                embeddings: object = None):
    loaded_files = []
    failed_files = []
    docs = []
    # 单个文件
    if isinstance(filepath, str):
        if not os.path.exists(filepath):
            logging.info(f"{filepath} 路径不存在")
            return None
        elif os.path.isfile(filepath):
            file = os.path.split(filepath)[-1]
            try:
                docs = load_file(filepath)
                logging.info(f"{file} 已成功加载")
                loaded_files.append(filepath)
            except Exception as e:
                logging.error(e)
                logging.info(f"{file} 未能成功加载")
                return None
        elif os.path.isdir(filepath):
            sub_docs, sub_failed_files, sub_loaded_files = load_dir(filepath)
            docs += sub_docs
            failed_files += failed_files
            loaded_files += sub_loaded_files
    #  文件列表
    else:
        docs = []
        for file in filepath:
            try:
                docs += load_file(file)
                logging.info(f"{file} 已成功加载")
                loaded_files.append(file)
            except Exception as e:
                logging.error(e)
                logging.info(f"{file} 未能成功加载")

    if len(failed_files) > 0:
        logging.info(f"以下文件未能成功加载：{failed_files}")

    if len(docs) > 0:
        logging.info("文件加载完毕，正在生成向量库")
        if vs_path and os.path.isdir(vs_path):
            vector_store = FAISS.load_local(vs_path, embeddings)
            vector_store.add_documents(docs)
            torch_gc()
        else:
            if not vs_path:
                vs_path = os.path.join(vs_path,
                                       f"""FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}""")
            vector_store = FAISS.from_documents(docs, embeddings)
            torch_gc()

        vector_store.save_local(vs_path)
        logging.info("向量生成成功")
        return vs_path, loaded_files
    else:
        logging.info("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
        return None, loaded_files


class LocalDocQA:
    filepath: str
    vs_path: str
    load_files: List[str] = []
    top_k: int
    embedding: object
    llm: object
    conversation_with_summary: object
    init: bool = True

    def __init__(self, filepath: str, vs_path: str, embeddings: object,
                 init: bool = True):
        if init and (vs_path and (not os.path.exists(vs_path))):
            vs_path, loaded_files = init_knowledge_vector_store(filepath=filepath,
                                                                vs_path=vs_path,
                                                                embeddings=embeddings)
        else:
            vs_path = VS_PATH
            loaded_files = []

        self.load_files = loaded_files
        self.vs_path = vs_path
        self.filepath = filepath
        self.embeddings = embeddings
        self.top_k = VECTOR_SEARCH_TOP_K
        # self.llm = ChatOpenAI(temperature=0, model=ChatGPTModel.GPT3.value, openai_api_key=OPENAI_API_KEY)
        # self.conversation_with_summary = ConversationChain(llm=self.llm,
        #                                                    memory=ConversationSummaryBufferMemory(llm=self.llm,
        #                                                                                           max_token_limit=256),
        #                                                    verbose=True)

    def query_knowledge(self, query: str):
        vector_store = FAISS.load_local(self.vs_path, self.embeddings)
        vector_store.chunk_size = CHUNK_SIZE
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        related_docs = get_docs_with_score(related_docs_with_score)
        related_content = get_related_content(related_docs)
        return related_content

    # def get_knowledge_based_answer(self, query: str):
    #     related_content = self.query_knowledge(query)
    #     prompt = PromptTemplate(
    #         input_variables=["context", "question"],
    #         template=PROMPT_TEMPLATE,
    #     )
    #     pmt = prompt.format(context=related_content,
    #                         question=query)
    #
    #     # answer=self.conversation_with_summary.predict(input=pmt)
    #     answer = self.llm(pmt)
    #     return answer


if __name__ == '__main__':
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings

    EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    embeddings = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese",
                                       model_kwargs={'device': EMBEDDING_DEVICE})
    qa_doc = LocalDocQA(filepath=LOCAL_CONTENT,
                        vs_path=VS_PATH,
                        embeddings=embeddings,
                        init=False)

    result = qa_doc.query_knowledge("中国最早朝代")
    print(result)
