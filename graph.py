from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langgraph.store.memory import InMemoryStore

from .state import OverallState
from .tools import priority_clients_search, priority_websites_search
from .llms import llm

# 将用户输入的数据存入store中, 或者说从中读取
user_preferences_store = InMemoryStore()
# Nodes
def user_config(state):
    """
    用户配置节点：
    
    管理和存储用户的定制化配置，包括:
    1. priority_websites: 优先搜索的网站列表。
    2. priority_clients: 优先搜索的客户端及其配置（例如，X.com 的推主列表）。
    
    Input: 用户配置数据。
    Output: 更新后的用户配置状态。
    
    用户主动进行配置操作时触发。
    """
    pass


def request_analysis(state):
    """
    需求分析节点：
    
    接收用户提出的研究请求，并将其分解为初步的研究子目标或步骤。
    
    Input: 用户的自然语言研究请求（例如：“本周以色列伊朗冲突的最新进展”）。
    Output: 
        1. 初步研究方案（例如你示例中的 1.3.1, 1.3.2 等）。
        2.  一个布尔标志，指示是否需要用户评估 needs_user_review = True
        
    利用 LLM 对请求进行语义理解和任务拆解。
    """
    return {
        "messages": "识别伊朗和以色列或其代理人之间最近的直接和间接军事交战或重大事件, 收集伊朗、以色列政府以及主要国际机构或国家对这些最新进展的官方声明和反应...",
        "needs_user_review": True
    }


def user_review(state, config):
    """
    用户评估节点：
    
    暂停流程，等待用户评估并确认或修改研究方案。
    
    Input: RequestAnalysisNode 提供的初步研究方案。
    Output: 
        1. 用户确认或修改后的最终研究方案。
        2. 一个布尔标志，指示是否通过评估 is_approved = True/False
    
    RequestAnalysisNode 输出 needs_user_review = True 时，可以用condition edge实现，参考Human in the loop
    """
    if state.get("needs_user_review", True):
        # resp = llm.invoke({"messages": "需要进行XXXX调整"}, config=config)
        return {
            "messages": "改成XXX样子"
        }
    else:
        return {
            "is_approved": True  # 用户确认
        }


def information_gathering(state, config):
    """
    信息收集节点
    
    根据当前研究步骤，执行信息检索。
    
    Input: 单个研究步骤（例如：“识别伊朗和以色列或其代理人之间最近的直接和间接军事交战或重大事件”）。
    Output: 
        1. 检索到的原始信息片段。
        2. 检索来源列表（URL、客户端名称、推文链接等）。
        3. 一个布尔标志，指示是否需要进一步深入研究 needs_deep_dive = True/False

    - **优先检索逻辑：** 首先查询 `priority_websites` 和 `priority_clients`。
    - **通用搜索：** 若优先源不足，则进行通用网络搜索。
    - **客户端 API 调用：** 对于 X.com 等，调用相应的 API 检索指定推主的推文。这部分需要开发者进行扩展，可以抽象出一个 `ClientAPIAdapter` 接口。
    """
    # tool_calling ...
    # llm = create_react_chat("deepseek")
    tools = [priority_websites_search, priority_clients_search]
    messages = {
        "messages": "使用priority_websites_search和priority_clients_search 搜索关键词",
        "addtional_arge": "",
        "tools": ""
    }
    # resp = llm.invoke(messages, config=config, tool=tools)
    resp = {
        "have_contents": False
    }
    if not resp.get("have_contents", False):  # 如果情报不够, 使用搜索引擎搜索
        tools = ["ganai", "jinai"]
        messages = {
            "contents": "搜索各国政府官网、联合国新闻稿等"
        }
        # resp = llm.invoke(messages, config=config, tool=tools)
    return {
        "contents": "XXXX信息情报",
        "needs_deep_dive": True
    }


def synthesis_and_analysis(state):
    """
    综合分析节点
    
    对收集到的信息进行整合、去重、提炼和初步分析，形成结构化的报告内容。
    
    Input: `InformationGatheringNode` 提供的原始信息片段。
    Output: 
        - 结构化、去重和总结后的研究内容。
        - 潜在的后续研究方向或未解决的问题。
    
    利用 LLM 进行信息归纳、关键信息提取和初步洞察生成。
    """
    # llm_with_struct_respon = llm.with_struct_respon(Analysis)
    # resp = llm.invoke("将信息进行整合、去重、提炼、初步分析，形成结构化报告内容")
    resp = {"将信息进行整合、去重、提炼、初步分析，形成结构化报告内容"}
    return {
        "contents": resp
    }


def deep_dive_decision(state):
    """
    深度探索决策节点
    
    根据当前研究的深度和广度，判断是否需要进一步探索或调整研究方案。
    
    Input: `SynthesisAndAnalysisNode` 的输出（总结内容、未解决问题）以及 `InformationGatheringNode` 的 `needs_deep_dive` 标志。
    Output: 
        - 新的或调整后的研究步骤列表。
        - 一个布尔标志，指示是否完成研究 is_research_complete = True/False
    
    再次利用 LLM 判断当前信息是否满足用户请求，或是否需要针对特定方面进行更深入的挖掘。
    """
    needs_deep_dive = state.get("needs_deep_dive", True)
    if needs_deep_dive:
        # resp = llm.invoke("新的或调整后的研究步骤列表。")
        return {
            "contents": "",
            "is_research_complete": False
        }
    return {
        "content": "",
        "is_research_complete": True
    }


def report_generation(state, config):
    """
    报告生成节点
    
    整理所有收集和分析的信息，生成最终的深度研究报告。
    
    Input: 整个研究过程中积累的结构化内容和来源列表。
    Output: 格式化的研究报告（Markdown 或可导出格式）。
    
    结合 LLM 的文本生成能力和预设的报告模板。
    """
    # prompt = "通过{收集的信息}, 生成最终的深度研究报告"
    # resp = llm.invoke(prmpt, config)
    return {
        "contents": "最终生成的研究报告",
        "sites": [...],
        "clients": [...]
    }
    


def human_approved(state):
    """
    用户决策是否批准研究，批准就进行下一步，未批准就提供反馈意见重新分析需求
    """
    if state.get("is_approved", True):
        return [
            Send(
                "information_gathering",
                {
                    
                }
            )
        ]
    return [
        Send(
            "request_analysis",
            {
                
            }
        )
    ]

def research_complete(state):
    """
    判断是否需要深入研究
    """
    if not state.get("is_research_complete", False):
        return [
            Send(
                "information_gathering",
                {
                    "新的或调整后的研究步骤列表"
                }
            )
        ]
    return [
        Send(
            "report_generation",
            {
                
            }
        )
    ]

workflow = StateGraph(OverallState)
# 流程就是：
#   1. plan节点列出计划，让用户确认，如果需要修改就返回plan节点修改计划
#   2. 执行节点开始执行调查任务
#   3. 反思节点反思是否要继续获取信息，如果需要就返回执行节点继续执行调查，直到没必要调查为止
#   4. 报告节点，根据当前数据形成报告，将所需的url、页面翻译、摘要也反馈给用户

workflow.add_node("request_analysis", request_analysis)
workflow.add_node("user_review", user_review)
workflow.add_node("information_gathering", information_gathering)
workflow.add_node("synthesis_and_analysis", synthesis_and_analysis)
workflow.add_node("deep_dive_decision", deep_dive_decision)
workflow.add_node("report_generation", report_generation)


workflow.add_edge(START, "request_analysis")
workflow.add_edge("request_analysis", "user_review")
workflow.add_conditional_edges(
    "user_review",
    human_approved,
    ["information_gathering", "request_analysis"]
)

workflow.add_edge("information_gathering", "synthesis_and_analysis")
workflow.add_edge("synthesis_and_analysis", "deep_dive_decision")
workflow.add_conditional_edges(
    "deep_dive_decision",
    research_complete,
    ["information_gathering", "report_generation"]
)
workflow.add_edge("report_generation", END)

workflow_with_store = workflow.compile(store=store)

workflow_with_store.invoke