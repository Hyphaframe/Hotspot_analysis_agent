
"""  
Streamlit Web界面 - 社交媒体热点分析智能体系统  
集成热榜爬取功能和舆情分析功能  
"""  
import os  
import sys  
  
# 将项目根目录加入 sys.path  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))  
  
import streamlit as st  
from src import DeepSearchAgent, Config  
from src.utils.config import load_config  
from src.hot_topics.crawler import HotTopicCrawler  
from src.hot_topics.database import DatabaseManager  
from src.hot_topics.models import HotTopic  
  
  
def main():  
    # -------------------- 页面配置 --------------------  
    st.set_page_config(  
        page_title="社交媒体热点分析智能体系统",  
        page_icon="📱",  
        layout="wide",  
    )  
  
    st.title("📱 社交媒体热点分析智能体系统")  
    st.markdown("基于LangGraph的社交媒体热点AI代理")  
  
    # -------------------- 侧边栏配置 --------------------  
    try:  
        default_config = load_config()  
        has_config_file = True  
        st.sidebar.success("✅ 已检测到配置文件，API Key 已自动填充")  
    except Exception:  
        default_config = None  
        has_config_file = False  
        st.sidebar.warning("⚠️ 未找到配置文件，请手动输入API密钥")  
  
    with st.sidebar:  
        st.header("⚙️ 配置")  
  
        # --- API 密钥 ---  
        st.subheader("API密钥")  
        openai_api_key = st.text_input(  
            "OpenAI/硅基流动 API Key",  
            value=default_config.openai_api_key if has_config_file else "",  
            type="password",  
            help="从配置文件自动读取，或手动输入",  
        )  
        openai_model = st.text_input(  
            "模型名称",  
            value=default_config.openai_model if has_config_file else "deepseek-ai/DeepSeek-V3",  
            help="例如：deepseek-ai/DeepSeek-V3 (硅基流动) 或 gpt-4o-mini (OpenAI)",  
        )  
        tavily_api_key = st.text_input(  
            "Tavily API Key",  
            value=default_config.tavily_api_key if has_config_file else "",  
            type="password",  
            help="从配置文件自动读取，或手动输入",  
        )  
  
        # --- 研究参数 ---  
        st.subheader("研究参数")  
        max_reflections = st.slider(  
            "反思次数",  
            min_value=0,  
            max_value=5,  
            value=default_config.max_reflections if has_config_file else 2,  
            help="每个段落的反思搜索次数",  
        )  
        max_search_results = st.slider(  
            "搜索结果数",  
            min_value=1,  
            max_value=10,  
            value=default_config.max_search_results if has_config_file else 3,  
            help="每次搜索返回的结果数量",  
        )  
        max_content_length = st.number_input(  
            "内容最大长度",  
            min_value=5000,  
            max_value=50000,  
            value=default_config.max_content_length if has_config_file else 20000,  
            step=5000,  
            help="搜索内容的最大字符数",  
        )  
        output_dir = st.text_input(  
            "报告保存目录",  
            value=default_config.output_dir if has_config_file else "reports",  
            help="报告文件的保存位置",  
        )  
  
        # --- 热榜配置 ---  
        st.subheader("热榜配置")  
        enable_hot_topics = st.checkbox(  
            "启用热榜功能",  
            value=True,  
            help="是否显示实时热榜"  
        )  
        max_hot_topics_display = st.slider(  
            "热榜显示数量",  
            min_value=5,  
            max_value=20,  
            value=10,  
            help="每个平台显示的热榜话题数量"  
        )  
  
        st.markdown("---")  
        st.markdown("### 关于")  
        st.markdown(  
            """  
            社交媒体热点分析智能体系统是一个面向舆情分析师和内容创作者的智能辅助系统，  
  
            旨在通过人工智能技术和智能体架构，实现从热点发现到舆情分析的全流程智能化支持。  
  
            """  
        )  
  
    # -------------------- 热榜展示区域 --------------------  
    if enable_hot_topics:  
        st.markdown("---")  
        st.header("🔥 实时热榜")  
          
        # 初始化热榜相关组件  
        if 'hot_topics_initialized' not in st.session_state:  
            st.session_state.crawler = HotTopicCrawler()  
            st.session_state.db = DatabaseManager()  
            st.session_state.hot_topics = []  
            st.session_state.hot_topics_initialized = True  
          
        # 刷新热榜按钮和统计信息  
        col1, col2, col3 = st.columns([1, 2, 1])  
        with col1:  
            if st.button("🔄 刷新热榜", use_container_width=True):  
                with st.spinner("正在获取最新热榜..."):  
                    try:  
                        topics = st.session_state.crawler.crawl_all_platforms()  
                        st.session_state.db.save_topics(topics)  
                        st.session_state.hot_topics = topics  
                        st.success(f"✅ 已获取 {len(topics)} 个热点话题")  
                    except Exception as e:  
                        st.error(f"❌ 热榜获取失败：{str(e)}")  
          
        with col2:  
            if st.session_state.hot_topics:  
                latest_time = st.session_state.db.get_latest_crawl_time()  
                st.info(f"📅 最后更新：{latest_time}")  
          
        with col3:  
            if st.session_state.hot_topics:  
                stats = st.session_state.db.get_platform_stats()  
                total_count = sum(stat['count'] for stat in stats.values())  
                st.metric("总话题数", total_count)  
          
        # 展示热榜  
        if st.session_state.hot_topics:  
            # 平台筛选  
            platforms = list(set(topic.platform for topic in st.session_state.hot_topics))  
            selected_platform = st.selectbox("筛选平台", ["全部"] + platforms)  
              
            # 过滤话题  
            filtered_topics = st.session_state.hot_topics  
            if selected_platform != "全部":  
                filtered_topics = [t for t in filtered_topics if t.platform == selected_platform]  
              
            # 话题列表  
            st.subheader(f"📊 {selected_platform}热榜")  
            for i, topic in enumerate(filtered_topics[:max_hot_topics_display]):  
                with st.container():  
                    col1, col2, col3, col4 = st.columns([1, 6, 2, 1])  
                    with col1:  
                        st.write(f"**#{topic.rank}**")  
                    with col2:  
                        if st.button(f"📱 {topic.title}", key=f"topic_{topic.id}", use_container_width=True):  
                            st.session_state.selected_topic = topic.title  
                            st.session_state.selected_platform = topic.platform  
                            st.rerun()  
                    with col3:  
                        st.write(f"🔥{topic.hot_value:,}")  
                        st.write(f"`{topic.platform}`")  
                    with col4:  
                        st.markdown(f"[🔗]({topic.url})")  
                  
                if i < len(filtered_topics[:max_hot_topics_display]) - 1:  
                    st.divider()  
  
    # -------------------- 舆情分析区域 --------------------  
    st.markdown("---")  
    st.header("📝 舆情分析")  
      
    # 检查是否选择了热点话题  
    if 'selected_topic' in st.session_state:  
        st.info(f"🎯 已选择热点话题：**{st.session_state.selected_topic}** ({st.session_state.get('selected_platform', '')})")  
        query = st.text_area(  
            "分析主题",  
            value=st.session_state.selected_topic,  
            height=100,  
            help="基于选择的热点话题进行舆情分析，您可以修改或补充分析内容"  
        )  
    else:  
        query = st.text_area(  
            "输入分析主题",  
            height=100,  
            placeholder="选择上方热点话题或手动输入您要分析的社交媒体热点话题...",  
            help="输入您要分析的社交媒体热点话题"  
        )  
  
    col1, col2 = st.columns([1, 4])  
    with col1:  
        start_research = st.button("🚀 开始分析", type="primary", use_container_width=True)  
    with col2:  
        save_report = st.checkbox("保存报告到文件", value=True)  
  
    # -------------------- 研究执行 --------------------  
    if start_research:  
        # 简单校验  
        if not tavily_api_key:  
            st.error("❌ 请输入 Tavily API Key")  
            return  
        if not openai_api_key:  
            st.error("❌ 请输入 OpenAI/硅基流动 API Key")  
            return  
        if not query.strip():  
            st.error("❌ 请输入分析主题")  
            return  
  
        try:  
            # 构造配置  
            config = Config(  
                openai_api_key=openai_api_key,  
                tavily_api_key=tavily_api_key,  
                default_llm_provider="openai",  
                openai_model=openai_model,  
                max_reflections=max_reflections,  
                max_search_results=max_search_results,  
                max_content_length=max_content_length,  
                output_dir=output_dir,  
                save_intermediate_states=False,  
            )  
  
            # 初始化 Agent  
            with st.spinner("正在初始化 Agent..."):  
                agent = DeepSearchAgent(config)  
            st.success("✅ Agent 初始化成功")  
  
            # ---- 实时进度展示 ----  
            st.markdown("---")  
            st.header("🔄 分析进度")  
  
            progress_placeholder = st.empty()  
            status_placeholder = st.empty()  
  
            # 节点中文映射  
            node_names = {  
                "structure": "📋 生成报告结构",  
                "search": "🔍 执行搜索",  
                "summary": "📝 生成总结",  
                "reflect": "🤔 反思搜索",  
                "reflect_summary": "✍️ 更新总结",  
                "next_paragraph": "➡️ 移动到下一段落",  
                "format": "📄 格式化最终报告",  
            }  
  
            final_report = None  
            for progress_data in agent.research(query, save_report=save_report):  
                if progress_data["node"] == "completed":  
                    final_report = progress_data["report"]  
                    status_placeholder.success("✅ 分析完成！")  
                    break  
                else:  
                    node = progress_data["node"]  
                    state = progress_data["state"]  
                    node_display = node_names.get(node, node)  
                    status_placeholder.info(f"当前阶段：{node_display}")  
  
                    # 段落进度条  
                    if "current_paragraph_index" in state and "paragraphs" in state:  
                        current_idx = state["current_paragraph_index"]  
                        total = len(state["paragraphs"])  
                        if total > 0:  
                            progress_placeholder.progress(  
                                (current_idx + 1) / total,  
                                text=f"段落进度：{current_idx + 1}/{total}",  
                            )  
  
            # -------------------- 结果展示 --------------------  
            if final_report:  
                st.markdown("---")  
                st.header("📊 分析结果")  
                tab1, tab2 = st.tabs(["📄 最终报告", "💾 下载"])  
                with tab1:  
                    st.subheader("⏱️ 运行统计")    
                    st.metric("运行时间", f"{progress_data['run_time']:.2f} 秒")  
                      
                    # 显示分析主题信息  
                    if 'selected_topic' in st.session_state:  
                        st.info(f"🎯 分析主题：{st.session_state.selected_topic}")  
                        st.info(f"📱 来源平台：{st.session_state.get('selected_platform', '手动输入')}")  
                      
                    st.markdown(final_report)  
                with tab2:  
                    # 生成文件名  
                    topic_name = st.session_state.get('selected_topic', query)[:20]  
                    filename = f"social_media_analysis_{topic_name}.md"  
                    st.download_button(  
                        label="📥 下载 Markdown 报告",  
                        data=final_report,  
                        file_name=filename,  
                        mime="text/markdown",  
                    )  
  
        except Exception as e:  
            st.error(f"❌ 分析过程中发生错误：{str(e)}")  
            st.exception(e)  
  
    # -------------------- 清除选择按钮 --------------------  
    if 'selected_topic' in st.session_state:  
        if st.button("🗑️ 清除选择的热点话题"):  
            del st.session_state.selected_topic  
            if 'selected_platform' in st.session_state:  
                del st.session_state.selected_platform  
            st.rerun()  
  
  
if __name__ == "__main__":  
    main()