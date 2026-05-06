from langchain.agents.middleware import AgentMiddleware
from typing import Callable, Any


class LoggingMiddleware(AgentMiddleware):
    """日志中间件 - 记录Agent的输入输出"""

    def before_agent(self, input: Any, **kwargs):
        """在Agent执行前调用"""
        print(f"\n🟢 [用户输入] {input}")

    def after_agent(self, output: Any, **kwargs):
        """在Agent执行后调用"""
        print(f"🔴 [Agent输出] {output}")

    def wrap_model_call(self, request, handler: Callable):
        """包装模型调用"""
        print(f"🔵 [模型调用前] 准备调用LLM")
        response = handler(request)
        print(f"🟣 [模型调用后] LLM响应已获取")
        return response

    def wrap_tool_call(self, request, handler: Callable):
        """包装工具调用"""
        print(f"🟡 [工具调用前] 准备调用工具: {request.tool.name}")
        response = handler(request)
        print(f"🟠 [工具调用后] 工具执行完成")
        return response
