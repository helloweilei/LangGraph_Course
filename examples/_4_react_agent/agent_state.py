from langchain_core.agents import AgentFinish, AgentAction
from typing import TypedDict, List, Union, Annotated
import operator

class AgentState(TypedDict, total=False):
    input: str
    agent_outcome: Union[AgentFinish, AgentAction, None]
    intermediate_steps: Annotated[List[tuple[AgentAction, str]], operator.add]