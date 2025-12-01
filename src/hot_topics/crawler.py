import requests  
from bs4 import BeautifulSoup  
from datetime import datetime  
from typing import List  
from .models import HotTopic  
  
class HotTopicCrawler:  
    def __init__(self):  
        self.headers = {  
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'  
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