from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.environ["DEEPSEEK_API_KEY"]

llm = ChatOpenAI(
    model_name="deepseek-v4-pro",
    openai_api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)