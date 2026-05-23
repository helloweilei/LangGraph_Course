import json
from langchain.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from chains import execute_tools, responder_node, revisor_node
from typing import Literal

graph = StateGraph(MessagesState)
graph.add_node('draft', responder_node)
graph.add_node('revisor', revisor_node)
graph.add_node('execute_tools', execute_tools)

graph.set_entry_point('draft')
graph.add_edge('draft', 'execute_tools')
graph.add_edge('execute_tools', 'revisor')

def should_continue(state: MessagesState) -> Literal['execute_tools', '__end__']:
    messages = state['messages']
    last_message = messages[-1]
    tool_messages_count = sum(1 for message in messages if isinstance(message, ToolMessage))
    if tool_messages_count >= 2 or not getattr(last_message, 'tool_calls', None):
        return END
    return 'execute_tools'

graph.add_conditional_edges('revisor', should_continue)

app = graph.compile(checkpointer=MemorySaver())
last_message = app.invoke(
    input={
        'messages': [HumanMessage(content="Write a blog post on how small business leverage AI to grow.")]
    },
    config ={
        'configurable': {
            'thread_id': 43
        }
    }
)['messages'][-1]
if last_message.tool_calls:
    result = last_message.tool_calls[0]['args']['answer']
elif last_message.content:
    try:
        result = json.loads(last_message.content)['answer']
    except (json.JSONDecodeError, KeyError, TypeError):
        result = last_message.content
else:
    result = last_message.content

print(result)
