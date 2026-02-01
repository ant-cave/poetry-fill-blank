import requests as req

from rich import print

import os
import requests
import json

def api_single(value:list[dict[str, str]]):
    # 1. 从环境变量获取 API Key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 环境变量 DEEPSEEK_API_KEY 未设置")
        return

    # 2. DeepSeek 兼容 OpenAI 的 API 地址
    url = "https://api.deepseek.com/v1/chat/completions"

    # 3. 构造 OpenAI 格式的请求体
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",  # 或 deepseek-coder 等，根据你拥有的权限选择
        "messages": [
            item for item in value
        ],
        "max_tokens": 100,
        "temperature": 1
    }

    try:
        # 4. 发送 POST 请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(message)
            print("="*50)
            return message.strip()
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络或请求错误: {e}")
    except KeyError as e:
        print(f"❌ 响应格式异常，缺少字段: {e}")
        return None

if __name__ == "__main__":
    api_single([{'role': 'system', 'content': '你是一个专业的诗词填写助手。'},{'role': 'user', 'content': '介绍你的使命'}])
