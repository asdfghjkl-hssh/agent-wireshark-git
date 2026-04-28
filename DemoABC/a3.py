import os
import time
import operator

from dotenv import load_dotenv
from typing import Annotated
from datetime import datetime
from pydantic import BaseModel
from typing_extensions import TypedDict
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Send

# 加载模型配置
load_dotenv()

# 加载模型
llm = ChatTongyi(
    model="qwen3-max",
    temperature=0.7,
)
# 创建并行节点a
def node_a(state: MessagesState):
    start_time = datetime.now()
    print(f"[node_a] 进入函数时间: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    # 使用 sleep 模拟占用时间
    time.sleep(2)

    end_time = datetime.now()
    print(f"[node_a] 退出函数时间: {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    return {'messages': [HumanMessage(
        content=f'节点a运行了{round((end_time - start_time).total_seconds(), 3)}秒'
    )]}

# 创建并行节点b
def node_b(state: MessagesState):
    start_time = datetime.now()
    print(f"[node_b] 进入函数时间: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    # 使用 sleep 模拟占用时间
    time.sleep(4)

    end_time = datetime.now()
    print(f"[node_b] 退出函数时间: {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    return {'messages': [HumanMessage(
        content=f'节点b运行了{round((end_time - start_time).total_seconds(), 3)}秒'
    )]}

# 创建图
builder = StateGraph(MessagesState)

# 添加节点
builder.add_node('node_a', node_a)
builder.add_node('node_b', node_b)

# 添加边
builder.add_edge(START, 'node_a')
builder.add_edge(START, 'node_b')
builder.add_edge('node_a', END)
builder.add_edge('node_b', END)

# 编译图
my_graph = builder.compile(name='my-graph')
# 调用图
response = my_graph.invoke({
    'messages': [HumanMessage(content='执行 node_a 和 node_b')]
})

for message in response['messages']:
    message.pretty_print()