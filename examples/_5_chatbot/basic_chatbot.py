from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from typing import List, Annotated, TypedDict
from langgraph.graph import add_messages, END, StateGraph
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"}  # 关键：关闭思考模式
    }
)

class ChatbotState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def chatbot(state: ChatbotState):
    response = llm.invoke(state['messages'])
    return {'messages': [response]}

graph = StateGraph(ChatbotState)
graph.add_node('chatbot', chatbot)
graph.add_edge('chatbot', END)
graph.set_entry_point('chatbot')

# checkpointer = MemorySaver()
sqlite_conn = sqlite3.connect('checkpoint.db', check_same_thread=False)
checkpointer = SqliteSaver(sqlite_conn)
app = graph.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": '1'
    }
}
while True:
    user_input = input("用户：")
    if (user_input in ['exit', 'quit', 'bye']):
        break
    messages = app.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)['messages']
    print(messages[-1].content)