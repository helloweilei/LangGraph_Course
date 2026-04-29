from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv
from typing import Literal
from langchain_core.messages import HumanMessage


load_dotenv()
api_key = os.environ["DEEPSEEK_API_KEY"]

@tool
def search(query: str) -> str:
    """Search the web for information and return a summary"""
    if query.lower == 'xian' or '西安' in query.lower():
        return "西安今天天气晴转多云, 最低气温8度。"
    return "今天天气晴朗，适合出行。"

tool_node = ToolNode([search])

model = ChatOpenAI(
    model_name="deepseek-chat",
    openai_api_key=api_key,
    base_url="https://api.deepseek.com/v1"
).bind_tools([search])

def should_continue(state: MessagesState) -> Literal['tools', '__end__']:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return 'tools'
    return END

def call_model(state: MessagesState) -> str:
    messages = state['messages']
    response = model.invoke(messages)
    return {
        'messages': [response],
    }

graph = StateGraph(MessagesState)
graph.add_node('tools', tool_node)
graph.add_node('model', call_model)

graph.set_entry_point('model')
graph.add_conditional_edges(
    'model', should_continue
)

graph.add_edge('tools', 'model')

app = graph.compile(checkpointer=MemorySaver())
result = app.invoke(
    input={
        'messages': [HumanMessage(content="西安天气如何？")]
    },
    config ={
        'configurable': {
            'thread_id': 43
        }
    }
)['messages'][-1].content

print(result)

graph_png = app.get_graph().draw_mermaid_png()
if not os.path.exists('graph.png'):
    with open('graph.png', 'wb') as f:
        f.write(graph_png)
