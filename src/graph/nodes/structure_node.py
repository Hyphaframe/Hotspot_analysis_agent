"""
结构生成节点
对应原 ReportStructureNode,负责生成报告大纲和段落结构
"""
from typing import Dict, Any
from ..state import AgentState, ParagraphState
from langgraph.types import RunnableConfig

def generate_structure(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    生成报告结构

    对应原 DeepSearchAgent._generate_report_structure() 的功能

    Args:
        state: 当前状态,包含用户查询
        config: 配置字典,通过 configurable 传递 llm_client

    Returns:
        包含 report_title 和 paragraphs 的状态更新字典
    """
    llm_client = config["configurable"]["llm_client"]
    query = state["query"]

    # 导入提示词(需要从原项目复用)
    from ...prompts.prompts import SYSTEM_PROMPT_REPORT_STRUCTURE
    user_content = (
        f"\n\n查询主题: {query}"
        + SYSTEM_PROMPT_REPORT_STRUCTURE)
    
    # 构建提示词
    messages = [
        {"role": "system", "content": "你是一个专业的研究助手,擅长规划研究报告结构。"},
        {"role": "user", "content": user_content}
    ]

    # 定义 JSON Schema(与原项目保持一致)
    json_schema = {
        "type": "object",
        "properties": {
            "report_title": {"type": "string"},
            "paragraphs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["title", "content"]
                }
            }
        },
        "required": ["report_title", "paragraphs"]
    }

    # 调用 LLM(使用原项目的 BaseLLM.chat 接口)
    result = llm_client.chat(messages, json_schema=json_schema)

    # 构建段落状态列表
    paragraphs = [
        ParagraphState(
            title=p["title"],
            content=p["content"],
            search_history=[],
            latest_summary="",
            completed=False,
            reflection_count=0
        )
        for p in result["paragraphs"]
    ]

    return {
        "report_title": result["report_title"],
        "paragraphs": paragraphs,
        "current_paragraph_index": 0,
        "reflection_count": 0,
        "max_reflections": config["configurable"].get("max_reflections", 2)
    }