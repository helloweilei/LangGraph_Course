from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import os
from langchain_classic.agents import create_react_agent
from langchain_classic.hub import pull
from my_tools import get_datetime, get_weather, web_search
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-pro",
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"}  # 关键：关闭思考模式
    }
)

tools = [web_search, get_weather, get_datetime]
# prompt = pull("hwchase17/react")
prompt = PromptTemplate.from_template('''
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

**Notice**: the final answer MUST be placed behind the **Final Answer: **.

Begin!

Question: {input}
Thought:{agent_scratchpad}
''')

agent_runnable = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)