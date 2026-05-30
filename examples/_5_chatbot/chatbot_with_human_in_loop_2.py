from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from typing import TypedDict
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"}  # 关键：关闭思考模式
    }
)

class ChatbotState(TypedDict, total=False):
    generated_post: str
    human_feedback: str
    post_topic: str

def chatbot(state: ChatbotState):
    prompt = f'''
    1. 生成或基于用户反馈修改一个关于 {state['post_topic']} 的帖子。
    2. 已经生成的帖子： {state['generated_post'] if state['generated_post'] is not None else ''}
    3. 用户反馈： {state['human_feedback'] if state['human_feedback'] is not None else ''}
    '''
    response = llm.invoke(input=[
        SystemMessage(content="你是一个优秀的AI助手。"),
        HumanMessage(content=prompt)
    ])
    return {"generated_post": response.content}

def human_feedback_node(state: ChatbotState):
    print(f"AI助手生成的帖子：\n{state['generated_post']}\n\n")
    feedback = interrupt("请输入你的反馈(done结束)：")
    if feedback == "done":
        return Command(goto=END)
    prior = state.get("human_feedback") or ""
    return Command(
        goto="chatbot",
        update={"human_feedback": prior + feedback},
    )

checkpointer = MemorySaver()
graph = StateGraph(ChatbotState)
graph.add_node('chatbot', chatbot)
graph.add_node('human_feedback', human_feedback_node)
graph.add_edge('chatbot', 'human_feedback')
graph.set_entry_point('chatbot')

app = graph.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": '1'
    }
}

post_topic = input("请输入帖子的主题：")
initial_state = {
    "post_topic": post_topic,
    "human_feedback": None,
    "generated_post": None,
}

result = app.invoke(initial_state, config=config)

while True:
    snapshot = app.get_state(config)
    if not snapshot.next:
        print(snapshot.values.get("generated_post", snapshot.values))
        break

    interrupt_value = snapshot.tasks[0].interrupts[0].value
    feedback = input(interrupt_value)
    result = app.invoke(Command(resume=feedback), config=config)


