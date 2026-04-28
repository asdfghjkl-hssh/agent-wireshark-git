from typing import List, Optional
from langchain_core.tools import tool
from utils.logger_handler import logger

# 尝试导入 Scapy，若未安装则给出友好提示
try:
    from scapy.all import sniff, get_if_list, conf, IP, TCP, UDP

    # 关闭 Scapy 的冗余输出
    conf.verb = 0
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logger.warning("Scapy 未安装，请先运行: pip install scapy")

# 全局缓存，用于存储最近抓到的包（简单演示用）
recent_packets = []


def _format_packet_summary(pkt) -> str:
    """内部辅助函数：格式化单个数据包为可读字符串"""
    summary = f"[{pkt.time}] "
    if IP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        if TCP in pkt:
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            flags = pkt[TCP].flags
            summary += f"TCP {src_ip}:{sport} -> {dst_ip}:{dport} Flags:{flags}"
        elif UDP in pkt:
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            summary += f"UDP {src_ip}:{sport} -> {dst_ip}:{dport} Len:{len(pkt[UDP])}"
        else:
            summary += f"IP {src_ip} -> {dst_ip}"
    else:
        summary += "Non-IP Packet"
    return summary


@tool(description="列出本机所有可用的网络接口（网卡）。用于在抓包前确认需要监听的接口名称。")
def list_network_interfaces() -> str:
    if not SCAPY_AVAILABLE:
        return "错误: Scapy 库未安装，无法使用此功能。"

    ifaces = get_if_list()
    if not ifaces:
        return "未找到任何网络接口。"

    result = "可用网络接口列表:\n"
    # 在 Windows 上尝试获取更友好的名称，Linux 直接显示
    for i, iface in enumerate(ifaces):
        result += f"{i + 1}. {iface}\n"
    return result
@tool(description="查看本机端口状态")
def get_local_port_status() -> str:
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, encoding='gbk')
    return result.stdout

@tool(return_direct=False)
def capture_tcp_packets(interface: str, count: int = 10, timeout: int = 10) -> str:
    """
    抓取指定网络接口上的 TCP 数据包。
    类似于 Wireshark 的过滤规则 'tcp'。

    Args:
        interface: 网卡名称 (从 list_network_interfaces 获取)
        count: 抓取数据包的数量 (默认 10 个)
        timeout: 超时时间，单位秒 (默认 10 秒)
    """
    if not SCAPY_AVAILABLE:
        return "错误: Scapy 库未安装。"

    try:
        logger.info(f"开始在 {interface} 上抓取 TCP 包...")
        # 使用 Scapy 的 sniff 函数
        packets = sniff(
            iface=interface,
            filter="tcp",
            count=count,
            timeout=timeout
        )

        if not packets:
            return "未捕获到 TCP 数据包。"

        # 格式化输出
        result = f"成功捕获 {len(packets)} 个 TCP 包:\n"
        for pkt in packets:
            result += f"- {_format_packet_summary(pkt)}\n"

        return result
    except Exception as e:
        return f"抓包出错 (权限不足或接口名错误?): {str(e)}"

# 导入必需依赖
from langchain.tools import tool
import subprocess

# 核心Agent工具：打开CMD执行ipconfig
# 修复中文乱码版 ipconfig 工具
@tool(description="自动打开Windows CMD命令行，执行ipconfig命令，查看本机网卡IP、子网掩码、网关、MAC地址等基础网络配置信息")
def run_windows_ipconfig():
    """
    工具功能：执行ipconfig命令并返回网络配置信息（不弹出窗口，直接返回结果）
    使用gbk编码解码Windows中文输出，确保无乱码。
    """
    result = subprocess.run(
        ["ipconfig"],
        capture_output=True,
        text=True,
        encoding='gbk',      # Windows 中文系统默认编码
        shell=True
    )
    return result.stdout
from langchain_core.tools import tool
import time
import sys

# 尝试导入 requests，若未安装则使用 urllib 降级方案
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    import urllib.request

# 默认测试文件大小 (字节) - 这里使用 10 MB
TEST_SIZE = 10 * 1024 * 1024   # 10 MB
# 测速 URL（返回指定字节数的纯数据）
SPEED_TEST_URL = f"https://httpbin.org/bytes/{TEST_SIZE}"

# 备用 URL（如果 httpbin 不可用）
BACKUP_URL = f"https://speed.cloudflare.com/__down?bytes={TEST_SIZE}"


def _download_with_requests(url: str, timeout: float = 30) -> float:
    """使用 requests 下载，返回耗时（秒）"""
    start = time.perf_counter()
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    # 读取全部数据以确保完成下载
    for _ in resp.iter_content(chunk_size=8192):
        pass
    end = time.perf_counter()
    return end - start


def _download_with_urllib(url: str, timeout: float = 30) -> float:
    """降级方案：使用 urllib 下载，返回耗时（秒）"""
    start = time.perf_counter()
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        while resp.read(8192):
            pass
    end = time.perf_counter()
    return end - start


from langchain_core.tools import tool
import time

# 尝试导入 requests，若未安装则使用 urllib 降级方案
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    import urllib.request

# 默认测试文件大小 (字节) - 这里使用 100 MB
TEST_SIZE = 100 * 1024 * 1024   # 100 MB
# 主测速 URL（Cloudflare 支持大文件，推荐）
SPEED_TEST_URL = f"https://speed.cloudflare.com/__down?bytes={TEST_SIZE}"
# 备用 URL（httpbin 可能不支持 100MB，作为降级）
BACKUP_URL = f"https://httpbin.org/bytes/{TEST_SIZE}"

# 下载超时时间（秒），100MB 慢速网络可能需要更长时间
DOWNLOAD_TIMEOUT = 120


def _download_with_requests(url: str, timeout: float = DOWNLOAD_TIMEOUT) -> float:
    """使用 requests 下载，返回耗时（秒）"""
    start = time.perf_counter()
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    # 读取全部数据以确保完成下载
    for _ in resp.iter_content(chunk_size=8192):
        pass
    end = time.perf_counter()
    return end - start


def _download_with_urllib(url: str, timeout: float = DOWNLOAD_TIMEOUT) -> float:
    """降级方案：使用 urllib 下载，返回耗时（秒）"""
    start = time.perf_counter()
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        while resp.read(8192):
            pass
    end = time.perf_counter()
    return end - start


@tool(description="测试当前网络的下载速度")
def download_speed() -> str:
    """
    测试当前网络的下载速度，返回以 MB/s（兆字节/秒）为单位的结果。
    适用场景：诊断网络带宽、评估下载大文件的可行性。
    测试文件大小：100 MB
    """
    # 选择下载函数
    if REQUESTS_AVAILABLE:
        download_func = _download_with_requests
    else:
        download_func = _download_with_urllib

    # 尝试主 URL，失败则用备用 URL
    urls_to_try = [SPEED_TEST_URL, BACKUP_URL]
    last_error = None

    for url in urls_to_try:
        try:
            elapsed = download_func(url)
            break  # 成功则跳出循环
        except Exception as e:
            last_error = e
            continue
    else:
        # 所有 URL 都失败
        return f"测速失败：无法连接到测速服务器。请检查网络。\n详细错误：{last_error}"

    # 计算速度 (MB/s)
    speed_mbps = (TEST_SIZE / 1024 / 1024) / elapsed  # MB/s
    speed_mbps_round = round(speed_mbps, 2)
    speed_mb_ps = round(speed_mbps * 8, 2)  # 转换为 Mbps

    return (f"📡 下载速度测试完成（测试文件大小：{TEST_SIZE // (1024 * 1024)} MB）\n"
            f"⏱️ 耗时：{elapsed:.2f} 秒\n"
            f"🚀 速度：{speed_mbps_round} MB/s （≈ {speed_mb_ps} Mbps）")



@tool(description="抓取指定网络接口上的 UDP 数据包。")
def capture_udp_packets(interface: str, count: int = 10, timeout: int = 10) -> str:
    """
    抓取指定网络接口上的 UDP 数据包。

    Args:
        interface: 网卡名称
        count: 抓取数量
        timeout: 超时时间
    """
    if not SCAPY_AVAILABLE:
        return "错误: Scapy 库未安装。"

    try:
        logger.info(f"开始在 {interface} 上抓取 UDP 包...")
        packets = sniff(
            iface=interface,
            filter="udp",
            count=count,
            timeout=timeout
        )

        if not packets:
            return "未捕获到 UDP 数据包。"

        result = f"成功捕获 {len(packets)} 个 UDP 包:\n"
        for pkt in packets:
            result += f"- {_format_packet_summary(pkt)}\n"

        return result
    except Exception as e:
        return f"抓包出错: {str(e)}"
if __name__ == '__main__':
    print(download_speed.invoke({}))