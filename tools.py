# 工具节点
from langchain_core.tools import tool

@tool
def xiaohongshu(state):
    """ 把小红书封装成tool calling """
    pass


@tool
def priority_websites_search():
    pass

@tool
def priority_clients_search():
    pass