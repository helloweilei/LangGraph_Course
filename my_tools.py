from langchain_core.tools import tool
from ddgs import DDGS
import requests
from langchain_core.tools.retriever import create_retriever_tool
# from rags.retriever import retriever

# retriever_tool = create_retriever_tool(
#     retriever=retriever,
#     name="search_from_rag",
#     description="""
#     获取小说《红楼梦》相关的信息.
#     """
# )


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


@tool
def get_weather(longitude, latitude):
    '''获取天气
      Args:
          longitude: 经度
          latitude: 纬度
    '''
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    data = requests.get(url).json()["current_weather"]
    del data["time"]
    return data

@tool
def get_datetime(format: str = "%Y-%m-%D %H:%M:%S"):
    """
    获取当前日期时间。
    """
    from datetime import datetime
    return datetime.now().strftime(format)
