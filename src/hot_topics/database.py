"""  
数据库管理类 - 热点话题数据持久化  
负责管理SQLite数据库，存储和检索热点话题数据  
"""  
  
import sqlite3  
from typing import List, Dict  
from datetime import datetime  
from .models import HotTopic  
  
  
class DatabaseManager:  
    """数据库管理类"""  
      
    def __init__(self, db_path="hot_topics.db"):  
        """  
        初始化数据库管理器  
          
        Args:  
            db_path: 数据库文件路径  
        """  
        self.db_path = db_path  
        self.init_db()  
      
    def init_db(self):  
        """初始化数据库表结构"""  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
          
        # 创建热点话题表  
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS hot_topics (  
                id TEXT PRIMARY KEY,  
                title TEXT NOT NULL,  
                platform TEXT NOT NULL,  
                hot_value INTEGER,  
                url TEXT,  
                timestamp TEXT,  
                rank INTEGER  
            )  
        ''')  
          
        # 创建爬取历史表  
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS crawl_history (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                platform TEXT,  
                crawl_time TEXT,  
                topic_count INTEGER  
            )  
        ''')  
          
        conn.commit()  
        conn.close()  
      
    def save_topics(self, topics: List[HotTopic]):  
        """  
        保存话题到数据库  
          
        Args:  
            topics: 热点话题列表  
        """  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
          
        # 清空当前数据  
        cursor.execute("DELETE FROM hot_topics")  
          
        # 插入新数据  
        for topic in topics:  
            cursor.execute('''  
                INSERT OR REPLACE INTO hot_topics   
                (id, title, platform, hot_value, url, timestamp, rank)  
                VALUES (?, ?, ?, ?, ?, ?, ?)  
            ''', (topic.id, topic.title, topic.platform,   
                  topic.hot_value, topic.url, topic.timestamp, topic.rank))  
          
        # 记录爬取历史  
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        platforms = list(set(topic.platform for topic in topics))  
        for platform in platforms:  
            platform_count = len([t for t in topics if t.platform == platform])  
            cursor.execute('''  
                INSERT INTO crawl_history (platform, crawl_time, topic_count)  
                VALUES (?, ?, ?)  
            ''', (platform, crawl_time, platform_count))  
          
        conn.commit()  
        conn.close()  
      
    def get_all_topics(self) -> List[HotTopic]:  
        """  
        获取所有话题，按热度值降序排列  
          
        Returns:  
            热点话题列表  
        """  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
        cursor.execute('''  
            SELECT * FROM hot_topics   
            ORDER BY hot_value DESC  
        ''')  
        rows = cursor.fetchall()  
        conn.close()  
          
        topics = []  
        for row in rows:  
            topics.append(HotTopic(  
                id=row[0],  
                title=row[1],  
                platform=row[2],  
                hot_value=row[3],  
                url=row[4],  
                timestamp=row[5],  
                rank=row[6]  
            ))  
        return topics  
      
    def get_platform_stats(self) -> Dict:  
        """  
        获取各平台统计信息  
          
        Returns:  
            平台统计信息字典  
        """  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
        cursor.execute('''  
            SELECT platform, COUNT(*) as count, AVG(hot_value) as avg_hot  
            FROM hot_topics  
            GROUP BY platform  
        ''')  
        rows = cursor.fetchall()  
        conn.close()  
          
        stats = {}  
        for row in rows:  
            stats[row[0]] = {  
                'count': row[1],  
                'avg_hot': round(row[2] or 0)  
            }  
        return stats  
      
    def get_topics_by_platform(self, platform: str) -> List[HotTopic]:  
        """  
        根据平台获取话题  
          
        Args:  
            platform: 平台名称  
              
        Returns:  
            指定平台的热点话题列表  
        """  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
        cursor.execute('''  
            SELECT * FROM hot_topics   
            WHERE platform = ?  
            ORDER BY hot_value DESC  
        ''', (platform,))  
        rows = cursor.fetchall()  
        conn.close()  
          
        topics = []  
        for row in rows:  
            topics.append(HotTopic(  
                id=row[0],  
                title=row[1],  
                platform=row[2],  
                hot_value=row[3],  
                url=row[4],  
                timestamp=row[5],  
                rank=row[6]  
            ))  
        return topics  
      
    def get_latest_crawl_time(self) -> str:  
        """  
        获取最近一次爬取时间  
          
        Returns:  
            最近爬取时间字符串  
        """  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
        cursor.execute('''  
            SELECT MAX(crawl_time) FROM crawl_history  
        ''')  
        result = cursor.fetchone()  
        conn.close()  
          
        return result[0] if result and result[0] else "暂无数据"  
      
    def clear_old_data(self, days: int = 7):  
        """  
        清除指定天数前的历史数据  
          
        Args:  
            days: 保留天数  
        """  
        conn = sqlite3.connect(self.db_path)  
        cursor = conn.cursor()  
          
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)  
        cutoff_str = datetime.fromtimestamp(cutoff_date).strftime("%Y-%m-%d %H:%M:%S")  
          
        cursor.execute('''  
            DELETE FROM crawl_history   
            WHERE crawl_time < ?  
        ''', (cutoff_str,))  
          
        conn.commit()  
        conn.close()