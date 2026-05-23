from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from my_tools import get_weather, get_datetime, web_search
from langchain.agents import create_agent


load_dotenv()
api_key = os.environ["DEEPSEEK_API_KEY"]

llm = ChatOpenAI(
    model_name="deepseek-v4-pro",
    openai_api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

agent = create_agent(
    model=llm,
    tools=[get_weather, get_datetime, web_search]
)


# structured output
# class CityInfo(BaseModel):
#     """城市信息"""
#     name: str = Field(..., description="城市名称")
#     desc: str = Field(..., description="城市描述")
#     travel_advice: str = Field(..., description="旅行建议")

city_json_schema = {
    "name": "城市信息",
    "description": "城市信息",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "城市名称"
        },
        "desc": {
            "type": "string",
            "description": "城市描述"
        },
        "travel_advice": {
            "type": "string",
            "description": "旅行建议"
        }
    }
}


def get_city_info(city = '西安'):
    # deepseek model not support json_schema
    model = llm.with_structured_output(city_json_schema, method="json_schema")
    city = model.invoke(f"简单介绍一下城市‘{city}’， 不超过100个字 ")
    print(city)

# if __name__ == '__main__':
#     get_city_info()