# Deep Search Agent 配置文件
# 请在这里填入您的API密钥
from dotenv import load_dotenv
import os

load_dotenv() 
# DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API Key (可选)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Tavily搜索API Key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# 配置参数
DEFAULT_LLM_PROVIDER = "openai"  # 可选值: "deepseek" 或 "openai"
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-V3"
OPENAI_MODEL = "deepseek-ai/DeepSeek-V3"

MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
# SAVE_INTERMEDIATE_STATES = True
