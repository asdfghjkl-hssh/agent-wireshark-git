
import os
import uuid
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


# ===================== 1. 加载环境变量 =====================
# 加载.env文件中的API Key
load_dotenv()

# ===================== 2. 配置大模型（通义千问） =====================
llm = ChatTongyi(
    model="qwen3-max"
)


# ===================== 3. 定义3个工具函数 =====================
@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@tool
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters."""
    if height_m <= 0 or weight_kg <= 0:
        raise ValueError("height_m and weight_kg must be greater than 0.")
    return weight_kg / (height_m ** 2)


# ===================== 4. 创建带人工审批的Agent =====================
tool_agent = create_agent(
    model=llm,
    tools=[get_weather, add_numbers, calculate_bmi],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # 无需审批，直接执行
                "get_weather": False,
                # 需要审批：同意/编辑/拒绝
                "add_numbers": True,
                # 需要审批：仅同意/拒绝，禁止修改参数
                "calculate_bmi": {"allowed_decisions": ["approve", "reject"]},
            },
            description_prefix="Tool execution pending approval",
        ),
    ],
    # 必须加：内存状态保存（中断后不丢失数据）
    checkpointer=InMemorySaver(),
    system_prompt="You are a helpful assistant",
)

# ===================== 5. 运行Agent（核心测试） =====================
if __name__ == "__main__":
    # 生成唯一会话ID
    config = {'configurable': {'thread_id': str(uuid.uuid4())}}

    print("=" * 50)
    print("用户提问：我身高180cm，体重180斤，我的BMI是多少")
    print("=" * 50)

    # 1. 第一次调用：触发工具 → 人工中断
    result = tool_agent.invoke(
        {"messages": [{
            "role": "user",
            "content": "我身高180cm，体重140斤，我的BMI是多少"
        }]},
        config=config,
    )

    # 2. 检查是否触发人工中断
    interrupt = result.get('__interrupt__')
    if interrupt:
        print("\n✅ 已触发人工审批中断！等待确认执行工具...")
        print(f"中断信息：{interrupt[0].value}")

    # 3. 人工批准：恢复执行工具
    print("\n🔧 执行人工批准（approve）...")
    result = tool_agent.invoke(
        Command(
            resume={"decisions": [{"type": "approve"}]}
        ),
        config=config
    )

    # 4. 打印最终结果
    print("\n" + "=" * 50)
    print("📊 AI 最终回答：")
    print(result['messages'][-1].content)
    print("=" * 50)