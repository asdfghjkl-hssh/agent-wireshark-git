from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from rag.vector_store import VectorStore
from utils.prompt_loader import load_rag_prompt
from utils.config_handler import agent_config
from utils.logger_handler import logger

def print_prompt(prompt):
    print("="*10)
    print(prompt.to_string())
    print("="*10)
    return prompt
class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStore()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = ChatTongyi(model="qwen-max")
        self.chain = self.__init__chain()
    def __init__chain(self):
        chain=self.prompt_template|print_prompt|self.model|StrOutputParser()
        return chain
    def retriever_docs(self,query):

        return self.retriever.invoke(query)
    def rag_summarize(self,query):
        docs = self.retriever_docs(query)
        context=""
        counter=0
        for doc in docs:
            counter+=1
            context+=f"{counter}. {doc.page_content}\n"
        return self.chain.invoke({"input": query,"context":context})


if __name__ == '__main__':
    # 测试RAG服务
    service = RagSummarizeService()
    result = service.rag_summarize("网络")
    print(result)
