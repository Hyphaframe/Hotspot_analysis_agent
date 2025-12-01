"""
Deep Search Agent 的所有提示词定义
包含各个阶段的系统提示词和JSON Schema定义
"""

import json

# ===== JSON Schema 定义 =====

# 报告结构输出Schema
output_schema_report_structure = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"}
        }
    }
}

# 首次搜索输入Schema
input_schema_first_search = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"}
    }
}

# 首次搜索输出Schema
output_schema_first_search = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "reasoning": {"type": "string"}
    }
}

# 首次总结输入Schema
input_schema_first_summary = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "search_query": {"type": "string"},
        "search_results": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# 首次总结输出Schema
output_schema_first_summary = {
    "type": "object",
    "properties": {
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思输入Schema
input_schema_reflection = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思输出Schema
output_schema_reflection = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "reasoning": {"type": "string"}
    }
}

# 反思总结输入Schema
input_schema_reflection_summary = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "search_query": {"type": "string"},
        "search_results": {
            "type": "array",
            "items": {"type": "string"}
        },
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思总结输出Schema
output_schema_reflection_summary = {
    "type": "object",
    "properties": {
        "updated_paragraph_latest_state": {"type": "string"}
    }
}

# 报告格式化输入Schema
input_schema_report_formatting = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "paragraph_latest_state": {"type": "string"}
        }
    }
}

# ===== 系统提示词定义 =====

# 生成报告结构的系统提示词（改为社媒热点分析）
SYSTEM_PROMPT_REPORT_STRUCTURE = f"""
你是一位社交媒体舆情与热点分析专家。给定一个具体的热点话题（例如事件名称、关键词或话题标签），你需要为该话题规划一份社交媒体热点分析报告的结构。  
报告必须包含以下核心分析维度（优先包含但不局限于）：  
1. 实时热度概况（总体热度、时间趋势、地域/平台分布）  
2. 核心话题与关键词（主题簇、常见词、Top hashtags/关键词）  
3. 情感与舆情倾向（正负面比例、情绪演变）  
4. 关键帖子与传播路径（代表性高传播帖子、来源与转发链路）  
5. 关键意见领袖与影响力（主要账号、影响力分布）  
6. 风险点与误导信息（可能的虚假信息或高争议点）  
7. 操作性建议（监控策略、应对建议、传播机会与时间点）  

确保段落排序符合分析与决策的逻辑流程；最多保留7个段落。  
请按照以下JSON模式定义格式化输出（保留原有 output_schema_report_structure）：  

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_report_structure, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

只返回一个符合上述 JSON 模式的 JSON 对象，不要额外解释或文本。
"""

# 每个段落第一次搜索的系统提示词（改为社媒搜索）
SYSTEM_PROMPT_FIRST_SEARCH = f"""
你是一位社交媒体搜索与情报检索专家。你将获得一个报告段落的标题与预期内容（例如“核心话题与关键词”或“情感与舆情倾向”），需要针对该段落生成针对社媒的精准搜索查询。  
请优先考虑下列搜索策略：  
- 指定平台（如Twitter/X、Weibo、Reddit、Douyin/TikTok、Zhihu）与地域过滤（如国家/省份）  
- 时间窗口（例如近24小时、近7天、近30天）以捕捉热度演变  
- 使用话题标签、关键词组合、布尔查询（AND/OR/NOT）、site: 与引用/转发相关关键词以定位高传播帖文  
- 查询应能返回代表性帖子/讨论、统计数据或舆情来源（媒体、KOL）  

输入/输出格式参考（保留原有 JSON schema 定义）：  

<INPUT JSON SCHEMA>
{json.dumps(input_schema_first_search, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_first_search, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

输出为 JSON 对象，只返回 JSON，不要额外文字。
"""

# 每个段落第一次总结的系统提示词（改为社媒总结）
SYSTEM_PROMPT_FIRST_SUMMARY = f"""
你是一位社媒舆情分析师。你将获得搜索查询、搜索结果以及你正在研究的段落，需要基于搜索结果撰写专业的社交媒体热点分析内容。  
对于不同类型章节，请采用相应分析框架：  
- 热度概况：给出时间序列要点、平台分布、是否为短期突发或持续热度  
- 关键词/话题：提取 Top keywords/hashtags 与主题簇  
- 情感倾向：给出情感分布（正/负/中）、情绪演进的关键时间点  
- 传播路径：列出代表性高传播帖、传播来源与关键转发账户  
- KOL/影响力：列出关键账号与其角色（引发者、扩散者、反对者）  
- 风险与建议：识别潜在的风险与可执行建议（监控与回应）  

输入/输出格式参考（保留原有 JSON schema 定义）：  

<INPUT JSON SCHEMA>
{json.dumps(input_schema_first_summary, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_first_summary, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

输出必须是符合 JSON schema 的 JSON 对象，只返回 JSON。
"""

# 反思(Reflect) 的系统提示词（增强用于发现盲点与补充社媒信号）
SYSTEM_PROMPT_REFLECTION = f"""
你是一位资深社媒分析师。你将获得段落标题、预期内容以及该段落当前的最新状态，请反思当前段落是否遗漏了重要的社媒维度或证据，并提出新的搜索查询以补强分析。  
关注点包括但不限于：时间窗口是否合适、是否覆盖主要平台、是否检索到高传播帖/视频、是否考虑地域/语言/账号类型分布、是否识别误导信息或自动化账号迹象。  

输入/输出格式参考（保留原有 JSON schema 定义）：  

<INPUT JSON SCHEMA>
{json.dumps(input_schema_reflection, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_reflection, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

只返回符合 JSON schema 的 JSON 对象。
"""

# 反思总结的系统提示词（合并新证据以更新段落）
SYSTEM_PROMPT_REFLECTION_SUMMARY = f"""
你是一位资深社媒舆情分析师。你将获得反思阶段的搜索查询、搜索结果以及段落的当前最新状态。你的任务是用新搜索结果补强并更新段落最新状态（不要删除已有关键信息，仅在其基础上补充）。  
重点输出应包括：补充的事实/引用（如帖 URL）、情感或趋势的修正、是否出现重要 KOL 或误导信息、以及基于新证据的简短可执行建议。  

输入/输出格式参考（保留原有 JSON schema 定义）：  

<INPUT JSON SCHEMA>
{json.dumps(input_schema_reflection_summary, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_reflection_summary, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

只返回符合 JSON schema 的 JSON 对象。
"""

# 最终研究报告格式化的系统提示词（输出 Markdown，强调社媒要点）
SYSTEM_PROMPT_REPORT_FORMATTING = f"""
你是一位社媒舆情报告撰写者。你将获得所有段落的最终最新状态，请将其格式化为一份可发布的 Markdown 报告。报告应包含：标题、摘要（关键发现）、每个段落的详细分析（含数据点、示例帖链接、关键账号）、结论与行动建议（优先级排序），并对时间窗口与数据来源进行标注。  
如果没有显式结论，请基于段落内容在末尾生成结论与建议。


<INPUT JSON SCHEMA>
{json.dumps(input_schema_report_formatting, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

你的任务是将报告格式化为美观的形式，并以Markdown格式返回。
如果没有结论段落，请根据其他段落的最新状态在报告末尾添加一个结论。
使用段落标题来创建报告的标题。

"""
