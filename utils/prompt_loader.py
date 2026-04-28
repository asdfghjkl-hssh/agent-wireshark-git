from utils.config_handler import prompt_config
from utils.path_tool import get_file_path
from utils.logger_handler import logger

def load_system_prompt():
    try:
        system_prompt_path = get_file_path(prompt_config["main_prompt_path"])
    except Exception as e:
        logger.error(f"加载系统提示语失败：{e}")
        raise e
    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"加载系统提示语失败：{e}")
        raise e

def load_rag_prompt():
    try:
        rag_prompt_path = get_file_path(prompt_config["rag_summarize_prompt_path"])
    except Exception as e:
        logger.error(f"加载系统提示语失败：{e}")
        raise e
    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"加载系统提示语失败：{e}")
        raise e

def load_report_prompt():
    try:
        report_prompt_path = get_file_path(prompt_config["report_prompt_path"])
    except Exception as e:
        logger.error(f"加载系统提示语失败：{e}")
        raise e
    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"加载系统提示语失败：{e}")
        raise e

if __name__ == '__main__':
    print(load_report_prompt())
