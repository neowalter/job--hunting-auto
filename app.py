
import streamlit as st
import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv

load_dotenv()
# 从.env文件中获取api_key的值
api_key = os.getenv("API_KEY")     
def get_stream(prompt):
    client = ZhipuAI(api_key=api_key)
    stream = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "system",
              "content": """你是一个资深的求职顾问，
              非常善于针对不同的求职者设计不同且具有求职竞争力的简历
              请向求职者提问以获得求职者的过往经验，
              提问的同时给予合适的样例，
              在收集到足够的简历信息后，
              以合适的格式产出用户的全文简历。
              """
            },
            {"role": "user",
              "content": prompt
            },],
        top_p=0.7,
        temperature=0.8,
        max_tokens=7095,
        tools=[{"type":"web_search","web_search":{"search_result":True}}],
        stream=True
    )
    return stream

def stream_api_response(response):
    for trunk in response:
        content = trunk.choices[0].delta.content
        if content:
            yield content

def main():
    st.set_page_config(page_title="简历小帮手", layout="wide")
    st.markdown('<h1 class="title">简历小帮手</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content":"""
             就让我来帮你整理简历和求职方向吧！首先请简单的介绍一下自己。例如 ：
            ______
              **我是李明，来自北京大学计算机科学专业的大三学生。我对人工智能和机器学习特别感兴趣，\
             并且已经在这些领域参与了几个研究项目。我曾作为团队的一员，在一项国际比赛中获得了第三名的成绩。\
             此外，我还担任过学生会的技术部负责人，这让我有机会提升我的组织能力和团队协作技巧。\
             在未来，我希望能在一家领先的科技公司从事研发工作，继续探索前沿技术。**
            ______
              **我是王华，目前在ABC科技有限公司担任产品经理。我在软件行业已经有五年的工作经验，\
             主要专注于移动应用开发和用户体验设计。在过去的工作中，我成功地带领团队完成了多个项目的迭代升级，\
             并且在市场上取得了不错的反馈。我对市场趋势有着敏锐的洞察力，擅长利用数据分析来驱动产品决策。\
             除了日常工作，我也积极参与行业研讨会和技术论坛，不断学习最新的技术和管理理念。**
             """}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Handle new user input
    if prompt := st.chat_input('聊聊你自己吧！'):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            for response in stream_api_response(get_stream(prompt)):
                full_response += response
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()