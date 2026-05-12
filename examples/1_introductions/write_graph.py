from langgraph.graph import StateGraph, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from basic import llm
import os

graph = StateGraph(MessagesState)

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, 'prompts', 'short_novel.txt'), 'r', encoding='utf-8') as f:
    prompt_txt = f.read()

write_prompt = ChatPromptTemplate.from_messages(
    messages=[
        ("system", 'you are a helpful AI assistant.'),
        ("human", "{input}"),
    ]
)

write_model= write_prompt | llm

def write_node(state: MessagesState) -> MessagesState:
    messages = state['messages']
    response = write_model.invoke({
        'input': messages[-1].content,
    })
    return {
        'messages': [response],
    }

graph.add_node('write', write_node)
graph.add_edge('write', END)
graph.set_entry_point('write')

app = graph.compile(checkpointer=MemorySaver())
result = app.invoke(
    input={
        'messages': [HumanMessage(content='''
    你好
''')]
    },
    config ={
        'configurable': {
            'thread_id': 43
        }
    }
)['messages'][-1].content

print(result)