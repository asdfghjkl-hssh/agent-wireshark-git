import yaml
from utils.path_tool import get_file_path
def config_rag(config_path:str=get_file_path("config/rag.yml"),encoding="utf-8"):
    with open(config_path,encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)


def config_chroma(config_path:str=get_file_path("config/chroma.yml"),encoding="utf-8"):
    with open(config_path,encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)


def config_prompt(config_path:str=get_file_path("config/prompt.yml"),encoding="utf-8"):
    with open(config_path,encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)


def config_agent(config_path:str=get_file_path("config/agent.yml"),encoding="utf-8"):
    with open(config_path,encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)

rag_config=config_rag()
chroma_config=config_chroma()
prompt_config=config_prompt()
agent_config=config_agent()

if __name__ == '__main__':
    print(agent_config["chat-model-name"])