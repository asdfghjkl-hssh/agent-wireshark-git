from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from agent.tools.agent_tools import (list_network_interfaces,capture_tcp_packets,capture_udp_packets,
                                     get_local_port_status,run_windows_ipconfig,download_speed)
from utils.prompt_loader import load_system_prompt
from agent.tools.middleware import monitor_tool,log_before_model



class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=ChatTongyi(model="qwen3-max"),
            tools=[list_network_interfaces,capture_tcp_packets,capture_udp_packets,
                   get_local_port_status,run_windows_ipconfig,download_speed],
            system_prompt=load_system_prompt(),
            middleware=[monitor_tool,log_before_model],
        )


    def execute_stream(self,query:str):
        input_dict={
            "messages":[{
                "role":"user",
                "content":query

            }]
        }
        for chunk in self.agent.stream(input_dict,stream_mode="values",context={"report":False}):
            lass_message=chunk["messages"][-1]
            if lass_message.content:
                yield lass_message.content.strip()+"\n"
if __name__ == '__main__':
    agent=ReactAgent()
    for chunk in agent.execute_stream("测试一下我的网速"):
        print(chunk,end="",flush=True)
