import os
import hashlib
from utils.logger_handler import logger
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from typing import List

def get_file_md5_hex(filepath: str):      # 获取文件的md5的十六进制字符串
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return None

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return None

    md5_obj = hashlib.md5()

    chunk_size = 4096      # 4KB分片，避免文件过大爆内存
    try:
        with open(filepath, "rb") as f:      # 必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            me5_hex = md5_obj.hexdigest()
            return me5_hex
    except Exception as e:
        logger.error(f"[md5计算]文件{filepath}计算失败：{e}")
        return None



def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)




def load_text(filepath: str) -> List[Document]:
    return TextLoader(filepath,encoding="utf-8").load()