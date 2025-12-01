"""  
LangGraph 状态定义  
使用 TypedDict 定义研究过程的状态结构  
"""
from typing import TypedDict, List, Optional, Annotated, Dict, Any
from operator import add


class SearchRecord(TypedDict):
    """单次搜索记录"""
    query: str
    results: List[Dict[str, Any]]
    timestamp: str


class ParagraphState(TypedDict):
    """段落状态"""
    title: str
    content: str
    search_history: List[SearchRecord]
    latest_summary: str
    completed: bool
    reflection_count: int


class AgentState(TypedDict):
    """研究代理的完整状态"""
    # 输入  
    query: str

    # 热点话题信息  
    hot_topic_info: Optional[Dict[str, Any]]  # 存储完整的HotTopic信息  

    # 报告结构  
    report_title: str
    # paragraphs: Annotated[List[ParagraphState], add]  # 使用 add reducer 合并段落列表
    paragraphs: List[ParagraphState]  

    # 流程控制  
    current_paragraph_index: int
    reflection_count: int
    max_reflections: int

    # 输出  
    final_report: Optional[str]
    completed: bool  