from app.agent_openai.rag.custom_rag_chroma import ChromaVectorStore
import torch.cuda
import torch.backends
from app.agent_openai.agent.agent_config import *
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.agents import tool
from app.agent_openai.tools.web_search import GoogleSearch
import logging

EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese",
                                   model_kwargs={'device': EMBEDDING_DEVICE})

vector_store = ChromaVectorStore(filepath=LOCAL_CONTENT,
                                 vs_path=CHROMA_VS_PATH,
                                 embeddings=embeddings,
                                 init=True)

googleSearch = GoogleSearch()


class ChromaRagSearch:

    @tool
    def rag_search(query: str = ""):
        """This method involves researching historical information related to the user's question,
        providing relevant information to the AI assistant for reference during processing."""
        related_content = vector_store.query_knowledge(query=query)
        formed_related_content = "\n" + related_content

        logging.info(f"RagSearch.rag_search request->{query}")
        current_content = googleSearch.web_search(query)
        logging.info(f"RagSearch.rag_search response->{current_content}")

        return [formed_related_content, current_content]
