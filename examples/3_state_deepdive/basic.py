from typing import TypedDict, Literal, List, Annotated
from langgraph.graph import StateGraph, END
import operator

class SimpleState(TypedDict):
    count: int
    sum: Annotated[int, operator.add]
    history: Annotated[List[int], operator.concat]

def should_continue(state: SimpleState) -> Literal['continue', 'stop']:
    if state['count'] < 10:
        return 'continue'
    return 'stop'

def increment(state: SimpleState) -> SimpleState:
    next_count = state['count'] + 1
    # return SimpleState(
    #     count=next_count,
    #     sum=state['sum'] + next_count,
    #     history=state['history'] + [next_count]
    # )
    return SimpleState(
        count=next_count,
        sum=next_count,
        history=[next_count]
    )


graph = StateGraph(SimpleState)
graph.add_node('increment', increment)
graph.set_entry_point('increment')
graph.add_conditional_edges('increment', should_continue, {
    "continue": "increment",
    "stop": END
})

app = graph.compile()
state = app.invoke(SimpleState(count=0, sum=0, history=[]))
print(state)
