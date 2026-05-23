from langchain.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from schema import AnswerQuestion, RevisorAnswer
from datetime import datetime
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from ddgs import DDGS
from typing import List
from langchain_core.messages import BaseMessage, ToolMessage
import json
from langchain_core.runnables import RunnableLambda
from langgraph.graph import MessagesState

pydantic_parser = PydanticOutputParser(pydantic_object=AnswerQuestion)
pydantic_parser_revisor = PydanticOutputParser(pydantic_object=RevisorAnswer)

actor_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are expert AI researcher.
     Current time: {time}

     1. {fist_instruction}
     2. Reflection and critique your answer. Be severe to maximize improvements.
     3. After the reflection, **list 1-3 search queries separately** for researching
     improvements. Do not include them inside fhe reflection.
     """),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Answer the user's question above using the required format.")
]).partial(time = lambda: datetime.now().isoformat())

responder_prompt_template = actor_prompt_template.partial(
    fist_instruction = "Provide detailed ~250 words answer."
)

load_dotenv()
api_key = os.environ["DEEPSEEK_API_KEY"]

llm = ChatOpenAI(
    model_name="deepseek-v4-pro",
    openai_api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"},  # 关闭思考模式，避免多轮 tool call 需回传 reasoning_content
    },
)

first_responder_chain = responder_prompt_template | llm.bind_tools(tools=[AnswerQuestion]) # | RunnableLambda(lambda x: pydantic_parser._parse_obj(x.tool_calls[0]['args']))
# llm.bind_tools(tools=[AnswerQuestion], tool_choice='AnswerQuestion'), 'tool_choice' not supported in deepseek


# result = first_responder_chain.invoke({"messages": ["Write a blog post on how small business leverage AI to grow."]})
# print(result)

def responder_node(state: MessagesState) -> MessagesState:
    """Respond to user's question"""
    result = first_responder_chain.invoke(state)
    result.content = json.dumps(result.tool_calls[0]['args'])
    return {
        "messages": [result]
    }

revisor_prompt_template = actor_prompt_template.partial(
    fist_instruction = """Revise your previous answer using the new information.
        - Your should use the previous critique to add important information to your answer.
            - You MUST include numerical citations in your revised answer to ensure it can be verified.
            - Add a "References" section to the bottom of your answer(which does not count towards the word limit). in form of:
                - [1] https://example.com
                - [2] https://example.com
        - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
    """
)

revisor_chain = revisor_prompt_template | llm.bind_tools(tools=[RevisorAnswer])

def revisor_node(state: MessagesState) -> MessagesState:
    """Revise the answer"""
    result = revisor_chain.invoke(state)
    if result.tool_calls and (not result.content):
        result.content = json.dumps(result.tool_calls[0]['args'])
    return {
        "messages": [result]
    }

def web_search(query: str) -> str:
    """
    通过DuckDuckGo进行网络搜索。可获取最新新闻、资讯等。
    输入应为简洁的关键词。
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return f"未找到关于 '{query}' 的相关信息。"

        # 格式化输出并控制总长度
        final_output = f"## 搜索结果: {query}\n\n"
        for idx, res in enumerate(results, 1):
             # 摘要截断到500字符防止单条过长
            snippet = res.get('body', '')[:500]
            final_output += f"{idx}. **{res.get('title', '无标题')}**\n"
            final_output += f"   链接: {res.get('href', '#')}\n"
            final_output += f"   摘要: {snippet}\n\n"
            if len(final_output) > 3000:
                final_output += "...(内容过长，已截断)"
                break
        return final_output.strip()
    except Exception as e:
        return f"搜索过程中发生错误: {e}"

def execute_tools(state: MessagesState) -> ToolMessage:
    """Execute tools"""
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            call_id = tool_call["id"]
            search_queries = tool_call['args'].get("search_query", [])
            search_result = {}
            for query in search_queries:
                search_result[query] = web_search(query)
            return {
                "messages": [ToolMessage(content=json.dumps(search_result), tool_call_id=call_id)]
            }
    return {"messages": []}
