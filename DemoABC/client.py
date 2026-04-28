from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
# ✅ 修复：使用新的 create_agent（去掉警告）
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
import asyncio
model = ChatTongyi(model='qwen3-max')

server_params = StdioServerParameters(
    command="python",
    args=["math_server.py"],
)


async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            # ✅ 使用新函数
            agent = create_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            return agent_response


if __name__ == "__main__":
    result = asyncio.run(run_agent())
    # 只打印最终答案，更清爽
    print(result['messages'][-1].content)