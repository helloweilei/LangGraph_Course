from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from typing import List, Annotated, TypedDict
from langgraph.graph import add_messages, END, StateGraph
from langchain_core.messages import BaseMessage, HumanMessage
from my_tools import get_datetime, get_weather, web_search
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"}  # 关键：关闭思考模式
    }
)
tools = [get_datetime, get_weather, web_search]
llm_with_tools = llm.bind_tools(tools=tools)

class ChatbotState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def chatbot(state: ChatbotState):
    response = llm_with_tools.invoke(state['messages'])
    return {'messages': [response]}

graph = StateGraph(ChatbotState)
graph.add_node('chatbot', chatbot)
graph.set_entry_point('chatbot')

toolNode = ToolNode(tools=tools)
graph.add_node('toolNode', toolNode)

def tool_router(state: ChatbotState):
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return 'toolNode'
    else:
        return END
graph.add_conditional_edges('chatbot', tool_router)
graph.add_edge('toolNode', 'chatbot')

checkpointer = MemorySaver()
app = graph.compile(interrupt_before=['toolNode'], checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": '1'
    }
}
def ask(query: str) -> str:
    result = app.invoke(input={'messages': [HumanMessage(content=query)]}, config=config)
    print(result['messages'][-1].content)

def interrupt_ask(query: str):
    events = app.stream(input={'messages': [HumanMessage(content=query)]}, config=config, stream_mode='values')
    for event in events:
        print(event['messages'][-1].pretty_print())
        print('Next node: ', app.get_state(config=config).next)
        print('Continuing...')
        events = app.stream(None, config=config, stream_mode='values')

        for event in events:
            print(event['messages'][-1].pretty_print())

