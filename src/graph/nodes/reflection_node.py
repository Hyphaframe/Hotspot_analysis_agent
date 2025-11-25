"""
反思节点
对应原 ReflectionNode 和 ReflectionSummaryNode,负责反思搜索和更新总结
"""
from typing import Dict, Any
from datetime import datetime
from ..state import AgentState, SearchRecord
from langgraph.types import RunnableConfig

def reflection_search(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    执行反思搜索

    对应原 DeepSearchAgent._reflection_loop() 中的搜索部分

    Args:
        state: 当前状态
        config: 配置字典,包含 llm_client 和 tavily_api_key

    Returns:
        更新后的状态字典,包含新的搜索记录
    """
    llm_client = config["configurable"]["llm_client"]

    from ...tools.search import tavily_search
    from ...prompts.prompts import SYSTEM_PROMPT_REFLECTION

    current_idx = state["current_paragraph_index"]
    current_paragraph = state["paragraphs"][current_idx]

    user_content1 = (
        f"\n\n查询主题: {state['query']}\n"
        f"段落标题: {current_paragraph['title']}\n"
        f"段落内容: {current_paragraph['content']}\n"
        f"当前总结: {current_paragraph['latest_summary']}\n"
        + SYSTEM_PROMPT_REFLECTION)
    # 生成反思查询
    messages = [
        {"role": "system", "content": "你是一个批判性思维专家,擅长发现知识盲点。"},
        {"role": "user", "content": user_content1}
    ]

    json_schema = {
        "type": "object",
        "properties": {
            "search_query": {"type": "string"},
            "reasoning": {"type": "string"}
        },
        "required": ["search_query", "reasoning"]
    }

    response = llm_client.chat(messages, json_schema=json_schema)
    search_query = response["search_query"]

    # 执行搜索
    search_results = tavily_search(
        search_query,
        max_results=config["configurable"].get("max_search_results", 3),
        timeout=config["configurable"].get("search_timeout", 30),
        api_key=config["configurable"]["tavily_api_key"]
    )

    # 记录搜索
    search_record = SearchRecord(
        query=search_query,
        results=search_results or [],
        timestamp=datetime.now().isoformat()
    )

    # 更新状态
    updated_paragraphs = state["paragraphs"].copy()
    updated_paragraphs[current_idx]["search_history"].append(search_record)
    updated_paragraphs[current_idx]["reflection_count"] += 1

    # return {
    #     "paragraphs": updated_paragraphs
    # }
    return state

def reflection_summary(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    更新反思后的总结

    对应原 DeepSearchAgent._reflection_loop() 中的总结更新部分

    Args:
        state: 当前状态
        config: 配置字典,包含 llm_client

    Returns:
        更新后的状态字典,包含更新后的段落内容
    """
    llm_client = config["configurable"]["llm_client"]

    from ...utils.text_processing import format_search_results_for_prompt
    from ...prompts.prompts import SYSTEM_PROMPT_REFLECTION_SUMMARY

    current_idx = state["current_paragraph_index"]
    current_paragraph = state["paragraphs"][current_idx]

    # 获取最新搜索结果
    if not current_paragraph["search_history"]:
        return {}

    latest_search = current_paragraph["search_history"][-1]

    # 格式化搜索结果
    formatted_results = format_search_results_for_prompt(
        latest_search["results"],
        max_length=config["configurable"].get("max_content_length", 20000)
    )

    # 生成更新后的总结
    user_content2 = (
        f"\n\n查询主题: {state['query']}\n"
        f"段落标题: {current_paragraph['title']}\n"
        f"段落内容: {current_paragraph['content']}\n"
        f"搜索查询: {latest_search['query']}\n"
        f"搜索结果: {formatted_results}\n"
        f"当前总结: {current_paragraph['latest_summary']}"
        + SYSTEM_PROMPT_REFLECTION_SUMMARY)

    messages = [
        {"role": "system", "content": "你是一个专业的内容总结专家。"},
        {"role": "user", "content": user_content2}
    ]


    json_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"}
        },
        "required": ["summary"]
    }

    response = llm_client.chat(messages, json_schema=json_schema)
    updated_summary = response["summary"]

    # 更新段落
    updated_paragraphs = state["paragraphs"].copy()
    updated_paragraphs[current_idx]["content"] = updated_summary
    updated_paragraphs[current_idx]["latest_summary"] = updated_summary

    # return {
    #     "paragraphs": updated_paragraphs
    # }
    return state