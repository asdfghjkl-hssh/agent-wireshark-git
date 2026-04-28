import time
import streamlit as st
from agent.react_agent import ReactAgent

# ---------- 左侧栏手动切换提示词 ----------
st.sidebar.title("💡 提问示例")

# 提示词列表（可自行增删）
tips = [
    "你可以向模型提问：测试我的网速",
    "你可以向模型提问：哪个进程占用了8080端口？",
    "你可以向模型提问：列出所有网络接口",
    "你可以向模型提问：抓取5个TCP包",
    "你可以向模型提问：查看本机IP配置"
]

# 初始化当前提示词索引
if "tip_index" not in st.session_state:
    st.session_state.tip_index = 0

# 手动切换按钮
if st.sidebar.button("换一条提示"):
    st.session_state.tip_index = (st.session_state.tip_index + 1) % len(tips)

# 显示当前提示词
current_tip = tips[st.session_state.tip_index]
st.sidebar.info(current_tip)

# ---------- 主界面 ----------
st.title("智网通(教育版)")
st.divider()

# 初始化 Agent 和消息记录
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

# 显示历史消息
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入框
prompt = st.chat_input()

if prompt:
    # 显示用户消息
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    time.sleep(0.01)
                    yield char

        # 流式输出助手回复
        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        # 保存完整回复（取最后一个缓存块，实际应保存整个拼接内容）
        full_response = "".join(response_messages)
        st.session_state["message"].append({"role": "assistant", "content": full_response})
        st.rerun()