import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langgraph_supervisor import create_supervisor
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()
llm = ChatTongyi(model="qwen3-max", temperature=0.1)


@tool
def add(a: float, b: float) -> float:
    """加法工具"""
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """乘法工具"""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """除法工具"""
    return a / b


agent_add = create_agent(model=llm, tools=[add], name="加法专员")
agent_mul = create_agent(model=llm, tools=[multiply], name="乘法专员")
agent_div = create_agent(model=llm, tools=[divide], name="除法专员")

supervisor = create_supervisor(
    agents=[agent_add, agent_mul, agent_div],
    model=llm,
    prompt="""
    你是计算监管者，必须分配任务：
    - 加法 → 加法专员
    - 乘法 → 乘法专员
    - 除法 → 除法专员
    禁止自己计算！
    """,
)

app = supervisor.compile()
query = "计算：100 + 50 × 2 ÷ 5"

# ========== 修改处：用 stream 替代 invoke ==========
print("=" * 60)
print("开始执行，逐步输出消息：")
print("=" * 60)

# stream_mode="values" 每次状态更新都会返回当前完整的 messages 列表
for event in app.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values"
):
    # 每次事件都可能包含新的消息，我们只打印最后一条消息的内容
    if "messages" in event and event["messages"]:
        last_msg = event["messages"][-1]
        # 根据消息类型打印角色
        msg_type = getattr(last_msg, "type", "unknown")
        role = {
            "human": "👤 用户",
            "ai": "🤖 AI",
            "tool": "🔧 工具",
            "system": "⚙️ 系统",
        }.get(msg_type, f"[{msg_type}]")

        # 获取内容（可能是字符串，也可能是其他结构）
        content = getattr(last_msg, "content", str(last_msg))
        print(f"{role}: {content}")
        print("-" * 60)