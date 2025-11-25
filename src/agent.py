"""
Deep Search Agent主类 - LangGraph版本
整合LangGraph图结构,实现完整的深度搜索流程
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from .llms import DeepSeekLLM, OpenAILLM, BaseLLM
from .graph import create_research_graph, AgentState
from .utils import Config, load_config


class DeepSearchAgent:
    """Deep Search Agent主类 - 使用LangGraph实现"""

    def __init__(self, config: Optional[Config] = None):
        """
        初始化Deep Search Agent

        Args:
            config: 配置对象,如果不提供则自动加载
        """
        # 加载配置
        self.config = config or load_config()

        # 初始化LLM客户端
        self.llm_client = self._initialize_llm()

        # 创建LangGraph图
        self.graph = create_research_graph()

        # 确保输出目录存在
        os.makedirs(self.config.output_dir, exist_ok=True)

        print(f"Deep Search Agent 已初始化 (LangGraph版本)")
        print(f"使用LLM: {self.llm_client.get_model_info()}")

    def _initialize_llm(self) -> BaseLLM:
        """初始化LLM客户端"""
        
        from .llms.openai_llm import OpenAILLM  
      
        # 使用 OpenAILLM 客户端,设置 base_url 指向硅基流动  
        return OpenAILLM(  
            api_key=self.config.openai_api_key,  # 使用您的硅基流动 API Key  
            model_name=self.config.openai_model,  # 使用硅基流动支持的模型名称  
            base_url="https://api.siliconflow.cn/v1"  # 硅基流动的 API 端点  
        )

    def research(self, query: str, save_report: bool = True) -> str:
        """
        执行深度研究

        Args:
            query: 研究查询
            save_report: 是否保存报告到文件

        Returns:
            最终报告内容
        """
        print(f"\n{'=' * 60}")
        print(f"开始深度研究: {query}")
        print(f"{'=' * 60}")

        try:
            # 准备初始状态
            initial_state: AgentState = {
                "query": query,
                "report_title": "",
                "paragraphs": [],
                "current_paragraph_index": 0,
                "reflection_count": 0,
                "max_reflections": self.config.max_reflections,
                "final_report": None,
                "completed": False
            }

            # 准备配置
            config = {
                "configurable": {
                    "llm_client": self.llm_client,
                    "tavily_api_key": self.config.tavily_api_key,
                    "max_search_results": self.config.max_search_results,
                    "search_timeout": self.config.search_timeout,
                    "max_content_length": self.config.max_content_length,
                    "max_reflections": self.config.max_reflections},
                    "recursion_limit": 100
            }

            # 执行图
            print("\n执行研究工作流...")
            final_state = self.graph.invoke(initial_state, config)

            # 获取最终报告
            final_report = final_state["final_report"]

            # 保存报告
            if save_report:
                self._save_report(final_report, query)

            print(f"\n{'=' * 60}")
            print("深度研究完成！")
            print(f"{'=' * 60}")

            return final_report

        except Exception as e:
            print(f"研究过程中发生错误: {str(e)}")
            raise e

    def _save_report(self, report_content: str, query: str):
        """保存报告到文件"""
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        query_safe = query_safe.replace(' ', '_')[:30]

        filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        filepath = os.path.join(self.config.output_dir, filename)

        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"报告已保存到: {filepath}")

    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要 - LangGraph版本暂不支持"""
        return {
            "message": "LangGraph版本使用内置检查点机制,请使用LangGraph的状态查询API"
        }


def create_agent(config_file: Optional[str] = None) -> DeepSearchAgent:
    """
    创建Deep Search Agent实例的便捷函数

    Args:
        config_file: 配置文件路径

    Returns:
        DeepSearchAgent实例
    """
    config = load_config(config_file)
    return DeepSearchAgent(config)