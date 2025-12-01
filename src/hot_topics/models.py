from dataclasses import dataclass  
from typing import List  
  
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