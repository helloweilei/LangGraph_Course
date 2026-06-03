# from examples._4_react_agent.react_graph import ask
# from examples._5_chatbot.chatbot_with_tools import ask, interrupt_ask
import asyncio

from perlexity.server.app import ask


if __name__ == "__main__":
    #ask("红楼梦中，花谢花飞花满天，出自那首诗?")
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(ask("Deepseek v4是什么时候发布的?"))