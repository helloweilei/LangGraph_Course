from typing import List, Optional, Annotated, TypedDict
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import add_messages, END, StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langgraph.checkpoint.memory import MemorySaver
from uuid import uuid4
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.tools import tool
from ddgs import DDGS

@tool
def web_search(query: str) -> str:
    """
    通过DuckDuckGo进行网络搜索。可获取最新新闻、资讯等。
    输入应为简洁的关键词。
    """
    try:
        with DDGS() as ddgs:
            # 使用 .text() 方法获取文本搜索结果
            # 限制返回5条结果
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
        # 常见异常包括版本过旧或触发限流
        if "RatelimitException" in str(e) or "202" in str(e):
             return f"搜索服务暂时繁忙 (请求过快)。请稍后再试。错误详情: {e}"
        # 检查版本提示
        if "subsection" in str(e).lower():
             return f"搜索服务解析失败，请尝试升级库: `pip install -U duckduckgo-search`。错误详情: {e}"
        return f"搜索过程中发生错误: {e}"


load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
model = ChatOpenAI(
    model_name="deepseek-v4-pro",
    openai_api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
    extra_body={
        "thinking": {"type": "disabled"}  # 关键：关闭思考模式
    }
)

tools = [web_search]
llm_with_tools = model.bind_tools(tools=tools)
checkpointer = MemorySaver()

class ChatbotState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

async def chat_model_node(state: ChatbotState):
    messages = state['messages']
    result = await llm_with_tools.ainvoke(messages)
    return {'messages': [result]}

def find_tool_by_name(name):
    return next((tool for tool in tools if tool.name == name), None)

def should_call_tool(state: ChatbotState):
    last_message = state['messages'][-1]
    return hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0

async def tool_node(state: ChatbotState):
    last_message = state['messages'][-1]
    tool_messages = []
    if should_call_tool(state):
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call['id']
            tool = find_tool_by_name(tool_name)
            if tool is not None:
                tool_result = tool.invoke(tool_args)
                tool_messages.append(ToolMessage(content=tool_result, tool_call_id=tool_id))
    return {'messages': tool_messages}

def call_tool_router(state: ChatbotState):
    if should_call_tool(state):
        return 'tool'
    return END

graph = StateGraph(ChatbotState)
graph.add_node("chat_model", chat_model_node)
graph.add_node("tool", tool_node)
graph.set_entry_point("chat_model")
graph.add_edge("tool", "chat_model")
graph.add_conditional_edges("chat_model", call_tool_router)

config = {
    "configurable": {
        "thread_id": 1
    }
}
app = graph.compile(checkpointer=checkpointer)

async def ask(question: str):
    events = app.astream_events({
        "messages": [HumanMessage(content=question)]
    }, config=config)
    async for event in events:
        if event['event'] == 'on_chat_model_stream':
            print(event)
            #msg_chunk = event['data']['chunk'].content
            #print(msg_chunk, sep='', end='')

server = FastAPI()
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

# 开发模式（热重载）
# uvicorn app:server --reload

@server.get("/chat/{message}")
async def chat(message: str, thread_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_events_response(message, thread_id),
        media_type="text/event-stream"
    )

async def generate_events_response(message: str, thread_id: Optional[str]):
    if thread_id is None:
        thread_id = str(uuid4())
        yield f"data: {json.dumps({'type': 'thread_id', 'thread_id': thread_id})}\n\n"
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    events = app.astream_events({
        "messages": [HumanMessage(content=message)]
    }, config=config)
    async for event in events:
        if event['event'] == 'on_chat_model_stream':
            msg_chunk = event['data']['chunk'].content
            yield f"data: {json.dumps({'type': 'message', 'message': msg_chunk})}\n\n"
        elif event['event'] == 'on_chat_model_end':
            output: AIMessage = event['data']['output']
            if (hasattr(output, 'tool_calls')
                and len(output.tool_calls) > 0
                and output.tool_calls[0]['name'] == 'web_search'
            ):
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': 'web_search'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
        elif event['event'] == 'on_tool_end':
            tool_result = event['data']['output']
            yield f"data: {json.dumps({'type': 'tool_result', 'content': tool_result})}\n\n"
        # elif event['event'] == 'on_chain_end':
        #     # 整个流程结束
        #     yield f"data: {json.dumps({'type': 'done'})}\n\n"
