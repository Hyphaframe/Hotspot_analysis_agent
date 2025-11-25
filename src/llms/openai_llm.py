     


"""  
OpenAI LLM 客户端实现  
支持标准的 chat 接口和 JSON Schema 结构化输出  
"""  
from typing import Optional, Dict, Any, List  
from openai import OpenAI  
import json  
  
  
class OpenAILLM:  
    """OpenAI LLM 客户端"""  
      
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", base_url: Optional[str] = None):  
        """  
        初始化 OpenAI 客户端  
          
        Args:  
            api_key: OpenAI API 密钥  
            model_name: 模型名称,默认 gpt-4o-mini  
            base_url: 自定义 API 端点(可选,用于兼容 OpenAI 格式的其他服务)  
        """  
        self.api_key = api_key  
        self.model_name = model_name  
          
        # 初始化 OpenAI 客户端  
        if base_url:  
            self.client = OpenAI(api_key=api_key, base_url=base_url)  
        else:  
            self.client = OpenAI(api_key=api_key,base_url="https://api.siliconflow.cn/v1")  
      
    def chat(self, messages: List[Dict[str, str]], json_schema: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:  
        """  
        使用消息列表调用 LLM,支持 JSON Schema 结构化输出  
          
        Args:  
            messages: 消息列表,格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]  
            json_schema: JSON Schema 定义,用于结构化输出  
            **kwargs: 其他参数(temperature, max_tokens 等)  
              
        Returns:  
            解析后的 JSON 对象(如果提供了 json_schema)或字符串响应  
        """  
        try:  
            # 构建请求参数  
            params = {  
                "model": self.model_name,  
                "messages": messages,  
                "temperature": kwargs.get("temperature", 0.7),  
                "max_tokens": kwargs.get("max_tokens", 4000)  
            }  
              
            # 如果提供了 JSON Schema,使用 response_format  
            if json_schema:  
                params["response_format"] = {  
                    "type": "json_schema",  
                    "json_schema": {  
                        "name": "response",  
                        "strict": True,  
                        "schema": json_schema  
                    }  
                }  
              
            # 调用 OpenAI API  
            response = self.client.chat.completions.create(**params)  
              
            # 提取响应内容  
            if response.choices and response.choices[0].message:  
                content = response.choices[0].message.content  
                  
                # 如果使用了 JSON Schema,解析 JSON  
                if json_schema:  
                    return json.loads(content)  
                else:  
                    return content  
            else:  
                raise Exception("OpenAI API 返回空响应")  
                  
        except Exception as e:  
            print(f"OpenAI API 调用错误: {str(e)}")  
            raise e  
      
    def get_model_info(self) -> str:  
        """返回模型信息"""  
        return f"OpenAI ({self.model_name})"