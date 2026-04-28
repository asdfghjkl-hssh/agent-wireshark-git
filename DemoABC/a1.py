# ===================== 1. 导入需要的库 =====================
import os
from dotenv import load_dotenv
# 通义千问大模型（你之前用的，无缝衔接）
from langchain_community.chat_models import ChatTongyi
# LangGraph 监管者核心函数
from langgraph_supervisor import create_supervisor
# 工具函数（子代理专用工具）
from langchain_core.tools import tool

# ===================== 2. 加载配置 =====================
load_dotenv()  # 加载.env文件里的API_KEY

# 初始化大模型（监管者 + 子代理都用它）
llm = ChatTongyi(
    model="qwen3-max",  # 用轻量版，速度快，适合学习
    temperature=0.1,     # 低温度，更听话，不瞎编
)

# ===================== 3. 定义工具（子代理的技能） =====================
@tool
def add(a: float, b: float) -> float:
    """加法工具：只做两个数相加"""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """乘法工具：只做两个数相乘"""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """除法工具：只做两个数相除"""
    return a / b

# ===================== 4. 创建【子代理】（专业员工） =====================
# 子代理1：只会加法
agent_add = create_supervisor(
    tools=[add],
    model=llm,
    name="加法专员",
)

# 子代理2：只会乘法
agent_mul = create_supervisor(
    tools=[multiply],
    model=llm,
    name="乘法专员",
)

# 子代理3：只会除法
agent_div = create_supervisor(
    tools=[divide],
    model=llm,
    name="除法专员",
)

# ===================== 5. 创建【监管者】（总指挥） =====================
supervisor = create_supervisor(
    # 把3个员工交给监管者管理
    agents=[agent_add, agent_mul, agent_div],
    model=llm,
    prompt="""
    你的身份是【计算监管者】，必须严格遵守规则：
    1. 看到加法 → 分配给【加法专员】
    2. 看到乘法 → 分配给【乘法专员】
    3. 看到除法 → 分配给【除法专员】
    4. 禁止自己计算，必须分配任务！
    """,
)

# ===================== 6. 编译并运行 =====================
# 编译监管者工作流
app = supervisor.compile()

# 测试提问（包含加减乘除，监管者会自动分配）
query = "计算：100 + 50 × 2 ÷ 5"

# 执行
result = app.invoke({
    "messages": [{"role": "user", "content": query}]
})

# 打印结果
print("="*50)
print("最终结果：")
print(result["messages"][-1].content)