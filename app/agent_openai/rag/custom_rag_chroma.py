# import
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma
from typing import List
from os import path
import datetime
import logging
from app.agent_openai.agent.agent_config import *
from app.common.error import ParameterException, BizException
from app.agent_openai.rag.custom_rag import load_file, load_dir, torch_gc, get_related_content, get_docs_with_score


class ChromaVectorStore:
    filepath: str
    vs_path: str
    top_k: int
    embedding: object
    llm: object
    conversation_with_summary: object
    init: bool = True

    def __init__(self, filepath: str, vs_path: str, embeddings: object, init: bool = True):
        if init and (vs_path and (not os.path.exists(vs_path))):
            vs_path, loaded_files = self.init_knowledge_vector_store(filepath, vs_path, embeddings)
        else:
            vs_path = CHROMA_VS_PATH
            loaded_files = []

        self.load_files = loaded_files
        self.vs_path = vs_path
        self.filepath = filepath
        self.embeddings = embeddings
        self.top_k = VECTOR_SEARCH_TOP_K

    def init_knowledge_vector_store(self, filepath: str,
                                    vs_path: str or os.PathLike = None,
                                    embeddings: object = None):
        loaded_files = []
        failed_files = []
        docs = []
        if not path.exists(filepath):
            logging.info(f"{filepath} 路径不存在")
            raise ParameterException("filepath", f"{filepath}路径不存在")
        elif path.isfile(filepath):
            file_name = path.split(filepath)[-1]
            try:
                docs = load_file(filepath)
                logging.info(f"{file_name} 已成功加载")
                loaded_files.append(filepath)
            except Exception as e:
                logging.error(e)
                logging.info(f"{file_name} 未能成功加载")
                raise BizException(f"{file_name} 未能成功加载")
        elif os.path.isdir(filepath):
            sub_docs, sub_failed_files, sub_loaded_files = load_dir(filepath)
            docs += sub_docs
            failed_files += sub_failed_files
            loaded_files += sub_loaded_files

        if len(docs) > 0:
            logging.info("文件加载完毕，正在生成向量库")
            if vs_path and os.path.isdir(vs_path):
                vector_store = Chroma.from_documents(docs, embeddings, persist_directory=vs_path)
                torch_gc()
            else:
                if not vs_path:
                    vs_path = os.path.join(vs_path,
                                           f"""chroma_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}""")
                vector_store = Chroma.from_documents(docs, embeddings, persist_directory=vs_path)
                torch_gc()

            vector_store.persist()
            logging.info("向量生成成功")
            return vs_path, loaded_files
        else:
            logging.info("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
            raise BizException("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")

    def query_knowledge(self, query: str):

        vector_store = Chroma(persist_directory=self.vs_path, embedding_function=self.embeddings)
        vector_store.chunk_size = CHUNK_SIZE
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        related_docs = get_docs_with_score(related_docs_with_score)
        related_content = get_related_content(related_docs)
        return related_content


if __name__ == '__main__':
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
    import torch

    EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    embeddings = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese",
                                       model_kwargs={'device': EMBEDDING_DEVICE})

    # embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    qa_doc = ChromaVectorStore(filepath=LOCAL_CONTENT,
                               vs_path=CHROMA_VS_PATH,
                               embeddings=embeddings,
                               init=True)

    result = qa_doc.query_knowledge("中国最早朝代")
    print(result)
