from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
import os
from middlewares.log import LoggingMiddleware
from my_tools import web_search, get_weather, get_datetime


load_dotenv()

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    openai_api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"}  # 关键：关闭思考模式
    }
)

tools = [web_search, get_weather, get_datetime]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一位高效的代码助手。",
    middleware=[LoggingMiddleware()],
)

result = agent.invoke({
    "messages": "西安今天的天气如何？"
})

print(result['messages'][-1].content)