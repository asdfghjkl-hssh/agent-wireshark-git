import os
import logging
# 导入你自己的路径工具函数
from utils.path_tool import get_file_path

# ===================== 1. 日志路径配置（使用你的工具类） =====================
# 获取项目根目录下的 logs 文件夹路径
LOG_FILE_PATH = get_file_path("logs")
# 自动创建日志目录（目录已存在则不报错）
os.makedirs(LOG_FILE_PATH, exist_ok=True)
# 拼接日志文件完整路径（日志文件名为 app.log）
LOG_FILE = os.path.join(LOG_FILE_PATH, "app.log")

# ===================== 2. 日志格式配置（你定义的标准格式） =====================
# 日志输出格式
LOG_FORMAT = "%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s"
# 日志时间格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ===================== 3. 日志初始化核心代码 =====================
def setup_logger():
    """配置全局日志，避免重复添加处理器"""
    # 获取根日志器
    logger = logging.getLogger()
    # 防止重复配置导致日志打印多次
    if logger.handlers:
        return logger

    # 设置全局日志级别：DEBUG 及以上全部输出
    logger.setLevel(logging.DEBUG)

    # 日志格式器
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # -------------------- 处理器1：输出到日志文件 --------------------
    file_handler = logging.FileHandler(
        LOG_FILE,
        mode="a",        # 追加模式（不会覆盖历史日志）
        encoding="utf-8" # 解决中文乱码问题
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # -------------------- 处理器2：输出到控制台 --------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台只打印重要信息
    console_handler.setFormatter(formatter)

    # 给日志器添加两个处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 初始化全局日志，项目中直接导入使用
logger = setup_logger()

if __name__ == '__main__':
    logger.info("hello world")