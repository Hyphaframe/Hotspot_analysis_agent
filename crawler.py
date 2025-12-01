"""
今日热榜应用 - 实时显示各大平台热点话题
设计思路：
1. 数据采集：通过API或网页抓取获取各平台热榜数据
2. 数据处理：清洗、去重、排序、存储
3. Web界面：使用Flask提供Web界面展示
4. 定时更新：使用定时任务定期更新数据
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string
import sqlite3
from dataclasses import dataclass
from typing import List, Dict
import re

@dataclass
class HotTopic:
    """热点话题数据类"""
    id: str
    title: str
    platform: str
    hot_value: int
    url: str
    timestamp: str
    rank: int

class HotTopicCrawler:
    """热榜数据爬虫类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.platforms = {
            'baidu': self.crawl_baidu,
            'bilibili': self.crawl_bilibili
        }
    


    
    def crawl_baidu(self) -> List[HotTopic]:
        """爬取百度热榜"""
        try:
            url = "http://top.baidu.com/buzz?b=1&c=513&fr=topbuzz_b1_c513"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                topics = []
                items = soup.select('.c-single-text-ellipsis')
                for i, item in enumerate(items[:20]):
                    title = item.get_text().strip()
                    topic = HotTopic(
                        id=f"baidu_{i}",
                        title=title,
                        platform="百度",
                        hot_value=10000 - i*100,  # 模拟热度值
                        url=f"https://www.baidu.com/s?wd={title}",
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        rank=i+1
                    )
                    topics.append(topic)
                return topics
        except Exception as e:
            print(f"百度热榜爬取失败: {e}")
        return []
    

    
    def crawl_bilibili(self) -> List[HotTopic]:
        """爬取B站热榜"""
        try:
            url = "https://api.bilibili.com/x/web-interface/ranking/v2"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                topics = []
                for i, item in enumerate(data['data']['list'][:20]):
                    topic = HotTopic(
                        id=f"bilibili_{i}",
                        title=item['title'],
                        platform="B站",
                        hot_value=int(item.get('stat', {}).get('view', 0)),
                        url=f"https://www.bilibili.com/video/{item['bvid']}",
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        rank=i+1
                    )
                    topics.append(topic)
                return topics
        except Exception as e:
            print(f"B站热榜爬取失败: {e}")
        return []

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path="hot_topics.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
        """保存话题到数据库"""
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
        
        conn.commit()
        conn.close()
    
    def get_all_topics(self) -> List[Dict]:
        """获取所有话题"""
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
            topics.append({
                'id': row[0],
                'title': row[1],
                'platform': row[2],
                'hot_value': row[3],
                'url': row[4],
                'timestamp': row[5],
                'rank': row[6]
            })
        return topics
    
    def get_platform_stats(self) -> Dict:
        """获取各平台统计信息"""
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

class HotTopicApp:
    """主应用类"""
    
    def __init__(self):
        self.crawler = HotTopicCrawler()
        self.db = DatabaseManager()
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        @self.app.route('/')
        def index():
            topics = self.db.get_all_topics()
            stats = self.db.get_platform_stats()
            return render_template_string(HTML_TEMPLATE, topics=topics, stats=stats)
        
        @self.app.route('/api/topics')
        def api_topics():
            topics = self.db.get_all_topics()
            return {'topics': topics}
        
        @self.app.route('/api/stats')
        def api_stats():
            stats = self.db.get_platform_stats()
            return {'stats': stats}
    
    def crawl_all_platforms(self):
        """爬取所有平台数据"""
        all_topics = []
        for platform, crawler_func in self.crawler.platforms.items():
            print(f"正在爬取{platform}...")
            try:
                topics = crawler_func()
                all_topics.extend(topics)
                print(f"{platform}爬取完成，获取{len(topics)}个话题")
            except Exception as e:
                print(f"{platform}爬取失败: {e}")
        
        # 保存到数据库
        self.db.save_topics(all_topics)
        print(f"总共获取{len(all_topics)}个话题，已保存到数据库")
        
        return all_topics
    
    def start_crawling_task(self, interval=300):
        """启动定时爬取任务"""
        def crawl_worker():
            while True:
                try:
                    self.crawl_all_platforms()
                    time.sleep(interval)
                except Exception as e:
                    print(f"定时任务出错: {e}")
                    time.sleep(60)  # 出错后等待1分钟再重试
        
        thread = threading.Thread(target=crawl_worker, daemon=True)
        thread.start()
        print(f"定时爬取任务已启动，间隔{interval}秒")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行应用"""
        # 立即执行一次爬取
        print("正在初始化数据...")
        self.crawl_all_platforms()
        
        # 启动定时任务
        self.start_crawling_task()
        
        # 运行Web服务
        print(f"应用启动中... 访问 http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>今日热榜 - 实时热点话题聚合</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            margin: 0;
            opacity: 0.9;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        .content {
            padding: 20px;
        }
        .platform-filter {
            margin-bottom: 20px;
            text-align: center;
        }
        .platform-btn {
            background: #e9ecef;
            border: none;
            padding: 8px 16px;
            margin: 0 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .platform-btn.active {
            background: #667eea;
            color: white;
        }
        .topic-list {
            display: grid;
            gap: 15px;
        }
        .topic-item {
            display: flex;
            align-items: center;
            padding: 15px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
            background: white;
        }
        .topic-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .rank {
            font-size: 1.2em;
            font-weight: bold;
            width: 30px;
            text-align: center;
            margin-right: 15px;
            color: #667eea;
        }
        .topic-content {
            flex: 1;
        }
        .topic-title {
            font-size: 1.1em;
            margin: 0 0 5px 0;
            color: #333;
        }
        .topic-meta {
            display: flex;
            justify-content: space-between;
            color: #6c757d;
            font-size: 0.9em;
        }
        .platform-tag {
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
        }
        .hot-value {
            color: #ff6b6b;
            font-weight: bold;
        }
        .topic-link {
            color: #667eea;
            text-decoration: none;
            margin-left: 10px;
        }
        .topic-link:hover {
            text-decoration: underline;
        }
        .last-update {
            text-align: center;
            color: #6c757d;
            padding: 20px;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .stats {
                flex-direction: column;
                gap: 15px;
            }
            .topic-item {
                flex-direction: column;
                align-items: flex-start;
            }
            .rank {
                margin-bottom: 10px;
            }
            .topic-meta {
                width: 100%;
                justify-content: space-between;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 今日热榜</h1>
            <p>实时聚合各大平台热点话题</p>
        </div>
        
        <div class="stats">
            {% for platform, stat in stats.items() %}
            <div class="stat-item">
                <div class="stat-number">{{ stat.count }}</div>
                <div class="stat-label">{{ platform }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="content">
            <div class="platform-filter">
                <button class="platform-btn active" onclick="filterPlatform('all')">全部</button>
                {% for platform in stats.keys() %}
                <button class="platform-btn" onclick="filterPlatform('{{ platform }}')">{{ platform }}</button>
                {% endfor %}
            </div>
            
            <div class="topic-list" id="topicList">
                {% for topic in topics %}
                <div class="topic-item" data-platform="{{ topic.platform }}">
                    <div class="rank">#{{ topic.rank }}</div>
                    <div class="topic-content">
                        <h3 class="topic-title">{{ topic.title }}</h3>
                        <div class="topic-meta">
                            <span class="platform-tag">{{ topic.platform }}</span>
                            <span class="hot-value">🔥{{ topic.hot_value }}</span>
                            <a href="{{ topic.url }}" target="_blank" class="topic-link">查看详情</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="last-update">
            数据最后更新: {{ topics[0].timestamp if topics else '暂无数据' }}
        </div>
    </div>
    
    <script>
        function filterPlatform(platform) {
            // 更新按钮状态
            document.querySelectorAll('.platform-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // 过滤话题
            const items = document.querySelectorAll('.topic-item');
            items.forEach(item => {
                if (platform === 'all' || item.dataset.platform === platform) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        // 定时刷新数据
        setInterval(function() {
            fetch('/api/topics')
                .then(response => response.json())
                .then(data => {
                    // 这里可以实现动态更新，简化起见不实现
                })
                .catch(error => console.error('刷新数据失败:', error));
        }, 300000); // 每5分钟刷新一次
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app = HotTopicApp()
    app.run(host='0.0.0.0', port=5000, debug=False)