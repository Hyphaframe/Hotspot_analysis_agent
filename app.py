"""  
Streamlit Web界面 - LangGraph版本  
自动读取配置文件中的API密钥,提供友好的Web界面进行深度搜索  
"""  
  
import streamlit as st  
import sys  
import os  
  
# 添加项目根目录到路径  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))  
  
from src import DeepSearchAgent, Config  
from src.utils.config import load_config  
  
  
def main():  
    st.set_page_config(  
        page_title="Deep Search Agent (LangGraph版本)",  
        page_icon="🔍",  
        layout="wide"  
    )  
      
    st.title("🔍 Deep Search Agent (LangGraph版本)")  
    st.markdown("基于LangGraph的深度搜索AI代理 - 自动读取配置文件中的API密钥")  
      
    # 尝试加载配置文件  
    try:  
        default_config = load_config()  
        has_config_file = True  
        st.sidebar.success("✅ 已检测到配置文件,API Key已自动填充")  
    except:  
        default_config = None  
        has_config_file = False  
        st.sidebar.warning("⚠️ 未找到配置文件,请手动输入API密钥")  
      
    # 侧边栏配置  
    with st.sidebar:  
        st.header("⚙️ 配置")  
          
        # API密钥配置  
        st.subheader("API密钥")  
          
        # OpenAI/硅基流动 API Key (自动填充)  
        openai_api_key = st.text_input(  
            "OpenAI/硅基流动 API Key",  
            value=default_config.openai_api_key if has_config_file else "",  
            type="password",  
            help="从配置文件自动读取,或手动输入"  
        )  
          
        # OpenAI 模型配置  
        openai_model = st.text_input(  
            "模型名称",  
            value=default_config.openai_model if has_config_file else "deepseek-ai/DeepSeek-V3",  
            help="例如: deepseek-ai/DeepSeek-V3 (硅基流动) 或 gpt-4o-mini (OpenAI)"  
        )  
          
        # Tavily API Key (自动填充)  
        tavily_api_key = st.text_input(  
            "Tavily API Key",  
            value=default_config.tavily_api_key if has_config_file else "",  
            type="password",  
            help="从配置文件自动读取,或手动输入"  
        )  
          
        # 研究参数配置  
        st.subheader("研究参数")  
          
        max_reflections = st.slider(  
            "反思次数",  
            min_value=1,  
            max_value=5,  
            value=default_config.max_reflections if has_config_file else 2,  
            help="每个段落的反思搜索次数"  
        )  
          
        max_search_results = st.slider(  
            "搜索结果数",  
            min_value=1,  
            max_value=10,  
            value=default_config.max_search_results if has_config_file else 3,  
            help="每次搜索返回的结果数量"  
        )  
          
        max_content_length = st.number_input(  
            "内容最大长度",  
            min_value=5000,  
            max_value=50000,  
            value=default_config.max_content_length if has_config_file else 20000,  
            step=5000,  
            help="搜索内容的最大字符数"  
        )  
          
        # 输出目录配置  
        output_dir = st.text_input(  
            "报告保存目录",  
            value=default_config.output_dir if has_config_file else "reports",  
            help="报告文件的保存位置"  
        )  
          
        st.markdown("---")  
        st.markdown("### 关于")  
        st.markdown("""  
        这是Deep Search Agent的LangGraph版本,使用声明式图结构实现研究工作流。  
 
        """)  
      
    # 主界面  
    st.header("📝 研究查询")  
      
    query = st.text_area(  
        "输入您的研究问题",  
        height=100,  
        placeholder="例如: 2025年人工智能发展趋势",  
        help="输入您想要深度研究的问题"  
    )  
      
    col1, col2 = st.columns([1, 4])  
      
    with col1:  
        start_research = st.button("🚀 开始研究", type="primary", use_container_width=True)  
      
    with col2:  
        save_report = st.checkbox("保存报告到文件", value=True)  
      
    # 执行研究  
    if start_research:  
        # 验证API密钥  
        if not tavily_api_key:  
            st.error("❌ 请输入Tavily API Key")  
            return  
          
        if not openai_api_key:  
            st.error("❌ 请输入OpenAI/硅基流动 API Key")  
            return  
          
        if not query.strip():  
            st.error("❌ 请输入研究问题")  
            return  
          
        try:  
            # 创建配置  
            config = Config(  
                openai_api_key=openai_api_key,  
                tavily_api_key=tavily_api_key,  
                default_llm_provider="openai",  # 使用OpenAI兼容接口  
                openai_model=openai_model,  
                max_reflections=max_reflections,  
                max_search_results=max_search_results,  
                max_content_length=max_content_length,  
                output_dir=output_dir,  
                save_intermediate_states=False  # LangGraph版本使用内置检查点  
                
            )  
              
            # 创建Agent  
            with st.spinner("正在初始化Deep Search Agent (LangGraph版本)..."):  
                agent = DeepSearchAgent(config)  
              
            st.success("✅ Agent初始化成功")  
              
            # 执行研究  
            st.markdown("---")  
            st.header("🔄 研究进度")  
              
            progress_placeholder = st.empty()  
            result_placeholder = st.empty()  
              
            with st.spinner("正在执行深度研究..."):  
                # 显示进度信息  
                progress_placeholder.info("📊 LangGraph正在执行工作流,请稍候...")  
                  
                # 执行研究  
                final_report = agent.research(query, save_report=save_report)  
                  
                progress_placeholder.success("✅ 研究完成!")  
              
            # 显示结果  
            st.markdown("---")  
            st.header("📄 研究报告")  
              
            # 使用markdown显示报告  
            result_placeholder.markdown(final_report)  
              
            # 提供下载按钮  
            st.download_button(  
                label="📥 下载报告",  
                data=final_report,  
                file_name=f"deep_search_report_{query[:20]}.md",  
                mime="text/markdown"  
            )  
              
        except Exception as e:  
            st.error(f"❌ 研究过程中发生错误: {str(e)}")  
            st.exception(e)  
  
  
if __name__ == "__main__":  
    main()