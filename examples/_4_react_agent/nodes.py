from .agent_state import AgentState
from .reason_runnable import agent_runnable
from .reason_runnable import tools

def reason_node(state: AgentState) -> AgentState:
    agent_outcome = agent_runnable.invoke(state)
    return {
        "agent_outcome": agent_outcome,
    }

def execute_tool(agent_action):
    tool_name = agent_action.tool
    tool_input = agent_action.tool_input
    try:
        tool_input = eval(tool_input)
    except Exception as e:
        pass
    if (tool_name == "get_weather") and isinstance(tool_input, str) and 'longitude' not in tool_input:
        tool_input = list(map(lambda x: float(x.strip()), tool_input.split(",")))

    tool_function = None
    for tool in tools:
        if tool.name == tool_name:
            tool_function = tool.func
            break

    print(type(tool_input), tool_input)
    if tool_function is not None:
        if isinstance(tool_input, dict):
            tool_result = tool_function(**tool_input)
        elif isinstance(tool_input, (list, tuple)):
            tool_result = tool_function(*tool_input)
        else:
            tool_result = tool_function(tool_input)
        return tool_result
    else:
        return f"Tool `{tool_name}` No tool found"

def act_node(state: AgentState) -> AgentState:
    agent_action = state['agent_outcome']
    # 这里可以直接使用ToolExecutor
    action_result = execute_tool(agent_action)
    return {
        "intermediate_steps": [(agent_action, action_result)]
    }
