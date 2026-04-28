import os

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document

from utils.logger_handler import logger
from utils.file_handler import load_text, listdir_with_allowed_type, get_file_md5_hex
from utils.config_handler import chroma_config
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_file_path

class VectorStore:
    def __init__(self):
        self.embeddings=DashScopeEmbeddings(model="text-embedding-v4")
        self.vector_store=Chroma(
            collection_name=chroma_config["collection_name"],
            persist_directory=chroma_config["persist_directory"],
            embedding_function=self.embeddings,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            # 分块大小
            chunk_size=chroma_config["chunk_size"],
            # 分块重叠长度
            chunk_overlap=chroma_config["chunk_overlap"],
            # 分割符（优先按分段、换行、标点分割，适配中文）
            separators=chroma_config["separators"],
            # 按字符分割（中文/英文通用）
            length_function=len
        )
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k":chroma_config["k"]})
    def load_documents(self):
        def check_md5_hex(md5_for_check:str):
            if not os.path.exists(get_file_path(chroma_config["md5_hex_store"])):
                open(get_file_path(chroma_config["md5_hex_store"]),"w",encoding="utf-8").close()
                return False
            with open(get_file_path(chroma_config["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() == md5_for_check:
                        return True

                return False
        #保存md5
        def save_md5_hex(md5_for_check:str):
            with open(get_file_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check+"\n")
        def get_file_documents(read_path):
            if read_path.endswith("txt"):
                return load_text(read_path)
            return []
        allowed_files_path=listdir_with_allowed_type(get_file_path(chroma_config["data_path"]),
                                                allowed_types=tuple(chroma_config["allow_knowledge_file_type"]))
        for file_path in allowed_files_path:
            md5_hex=get_file_md5_hex(file_path)
            if not md5_hex:
                continue
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]:{file_path}内容已存在，跳过")
                continue
            try:
                documents:list[Document]=get_file_documents(file_path)
                if not documents:
                    logger.error(f"[加载知识库]:{file_path}为空，跳过")
                    continue
                spliter_documents=self.splitter.split_documents(documents)
                if not spliter_documents:
                    logger.error(f"[加载知识库]:{file_path}分块为空，跳过")
                    continue
                #向量存储
                self.vector_store.add_documents(spliter_documents)
                save_md5_hex(md5_hex)
                logger.info(f"[加载知识库]:{file_path}加载成功")
            except Exception as e:
                logger.error(f"[加载知识库]:{file_path}加载失败：{e}",exc_info=True)
                continue


if __name__ == '__main__':
    vs=VectorStore()
    vs.load_documents()
    retriever=vs.get_retriever()
    res=retriever.invoke("网络")
    for i in res:
        print(i.page_content)
