import os
import uuid
import sqlite3

from typing import Callable
from dotenv import load_dotenv
from dataclasses import dataclass
from langchain_community.chat_models import ChatTongyi
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, wrap_model_call, ModelRequest, ModelResponse, SummarizationMiddleware
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore


# 加载模型配置
load_dotenv()

# 加载模型
llm = ChatTongyi(
    model="qwen3-max"
)
@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)

    base = "You are a helpful assistant."

    if message_count > 8:
        base += "\nThis is a long conversation - be extra concise."

    # 临时打印base看效果
    print(base)

    return base

agent = create_agent(
    model=llm,
    middleware=[state_aware_prompt]
)

result = agent.invoke(
    {"messages": [
        {"role": "user", "content": "广州今天的天气怎么样？"},
        {"role": "assistant", "content": "广州天气很好"},
        {"role": "user", "content": "吃点什么好呢"},
        {"role": "assistant", "content": "要不要吃香茅鳗鱼煲"},
        {"role": "user", "content": "香茅是什么"},
        {"role": "assistant", "content": "香茅又名柠檬草，常见于泰式冬阴功汤、越南烤肉"},
        {"role": "user", "content": "auv 那还等什么，咱吃去吧"},
    ]},
)

for message in result['messages']:
    message.pretty_print()