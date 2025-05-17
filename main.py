import streamlit as st
from langchain_core.messages.chat import ChatMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import load_prompt
from langchain import hub


# API KEY 정보로드
load_dotenv()

st.title("나의 챗봇")
# 대화 기록을 저장할 용도
if "messages" not in st.session_state:
    # 대화 기록을 저장할 리스트를 초기화합니다.
    # 처음 한번만 실행할 코드
    st.session_state["messages"] = []

# 사이드바
with st.sidebar:
    # 초기화 버튼
    clear_btn = st.button("대화내용 초기화")
    selected_prompt = st.selectbox(
        "프롬프트를 선택해주세요", ("기본모드", "SNS 게시글", "요약"), index=0
    )


def add_message(role, message):
    # 대화 기록을 추가하는 함수
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


def print_messages():
    for chat_message in st.session_state["messages"]:
        # 대화 기록을 출력하는 함수
        st.chat_message(chat_message.role).write(chat_message.content)


# 체인 생성
def create_chain(prompt_type):
    if prompt_type == "기본모드":
        # prompt | llm | output_parser
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "당신은 친절한 AI 어시스턴트입니다"),
                ("user", "#Question:\n{question}"),
            ]
        )
    elif prompt_type == "SNS 게시글":
        prompt = load_prompt("sns.yaml", encoding="utf-8")

    elif prompt_type == "요약":
        prompt = hub.pull("eunbi/chain-of-density-korean")

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    return chain


if clear_btn:
    st.session_state["messages"] = []
# 이전 대화 기록
print_messages()

# 사용자의 입력
user_input = st.chat_input("궁금한 내용을 물어보세요")


# 만약에 사용자 입력이 들어오면...

if user_input:
    # st.write(f"사용자 입력 :{user_input}")
    st.chat_message("user").write(user_input)
    # chain 을 생성
    chain = create_chain(selected_prompt)
    response = chain.stream({"question": user_input})
    with st.chat_message("assistant"):
        # 빈 공간 (컨테이너) 생성한 후, 여기에 토큰을 스트리밍 한다
        container = st.empty()

        answer = ""

        for token in response:
            answer += token
            container.markdown(answer)

    # 대화 기록 저장
    add_message("user", user_input)
    add_message("assistant", answer)
