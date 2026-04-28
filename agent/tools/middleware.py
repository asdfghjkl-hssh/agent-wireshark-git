from langchain.agents.middleware import wrap_tool_call, before_model
from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState
from utils.logger_handler import logger

# 低费率模型
basic_model = ChatTongyi(
    model="qwen-max",
)

# 高费率模型
advanced_model = ChatTongyi(
    model="qwen3-max",
)
@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])

    if message_count > 5:
        # Use a basic model for longer conversations
        model = basic_model
    else:
        model = advanced_model


    print(f"message_count: {message_count}")
    print(f"model_name: {model.model_name}")

    return handler(request.override(model=model))

agent = create_agent(
    model=advanced_model,  # Default model
    middleware=[dynamic_model_selection]
)
@wrap_tool_call
def monitor_tool(request,handler):# 工具执行的监控
    logger.info(f"[工具执行]工具名称：{request.tool_call['name']}")
    logger.info(f"[工具执行]工具参数：{request.tool_call['args']}")
    try:
        result=handler(request)
        logger.info(f"[工具执行]成功，结果：{result}")
        return result
    except Exception as e:
        logger.error(f"[工具执行]工具执行失败：{e}")
        raise e
@before_model
def log_before_model(state,runtime):  # 在模型执行前输出日志
    logger.info(f"[模型执行]模型名称：{len(state['messages'])}条消息")
    return None
if __name__ == '__main__':
    state: MessagesState = {"messages": []}
    items = ['汽车', '飞机', '摩托车', '自行车']
    for idx, i in enumerate(items):
        print(f"\n=== Round {idx + 1} ===")
        state["messages"] += [HumanMessage(content=f"{i}有几个轮子，请简单回答")]
        result = agent.invoke(state)
        state["messages"] = result["messages"]
        print(f'content: {result["messages"][-1].content}')