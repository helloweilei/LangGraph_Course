from typing import TypedDict
from click import Command
from langgraph.graph import add_messages, END, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

class BaseState(TypedDict):
    txt: str

def node_a(state: BaseState):
    print('Node A')
    return Command(
        goto='node_b',
        update={
            'txt': state['txt'] + 'a -> '
        }
    )

def node_b(state: BaseState):
    print('Node B')
    user_review = interrupt("Do you want to goto C/D?")
    if user_review == 'C':
        return Command(
            goto='node_c',
            update={
                'txt': state['txt'] + 'b -> '
            }
        )
    elif user_review == 'D':
        return Command(
            goto='node_d',
            update={
                'txt': state['txt'] + 'b -> '
            }
        )
    else:
        raise ValueError('Invalid user review')

def node_c(state: BaseState):
    print('Node C')
    return Command(
        goto=END,
        update={
            'txt': state['txt'] + 'c -> END'
        }
    )

def node_d(state: BaseState):
    print('Node D')
    return Command(
        goto=END,
        update={
            'txt': state['txt'] + 'd -> END'
        }
    )
memory = MemorySaver()
config = { "configurable": { "thread_id": '2' } }
graph = StateGraph(BaseState)
graph.add_node('node_a', node_a)
graph.add_node('node_b', node_b)
graph.add_node('node_c', node_c)
graph.add_node('node_d', node_d)
graph.set_entry_point('node_a')

app = graph.compile(checkpointer=memory)
print(app.invoke({"txt": "start -> "}, config=config)["txt"])
print(app.get_state(config=config).next)
print(app.invoke(Command(resume='D'), config=config)["txt"])