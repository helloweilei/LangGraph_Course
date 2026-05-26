from langgraph.graph import StateGraph, END
from .nodes import act_node, reason_node
from .agent_state import AgentState
from typing import Literal, Union
from langchain_core.agents import AgentFinish

REASON_NODE = 'reason_node'
ACT_NODE = 'act_node'

graph = StateGraph(AgentState)
graph.add_node(REASON_NODE, reason_node)
graph.add_node(ACT_NODE, act_node)

def should_continue(state: AgentState) -> Literal['act_node', '__end__']:
    agent_outcome = state['agent_outcome']
    if isinstance(agent_outcome, AgentFinish):
        return '__end__'
    return ACT_NODE

graph.add_conditional_edges(REASON_NODE, should_continue)
graph.add_edge(ACT_NODE, REASON_NODE)
graph.set_entry_point(REASON_NODE)

app = graph.compile()

def ask(query: str):
    result = app.invoke(AgentState(
        input=query
    ))
    print(result['agent_outcome'].return_values['output'])