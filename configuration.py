# 配置
from pydantic import BaseModel, Field

class Configuration(BaseModel):
    """ Agent 的配置 """
    model: str = Field("deepseek", description="给plan节点用的大语言模型名称")