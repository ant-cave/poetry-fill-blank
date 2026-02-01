import requests as req


import os
import requests
import json

def api_single(value:list[dict[str, str]], stream_callback=None,temp=0.2):
    """
    调用 DeepSeek API，支持流式传输
    stream_callback: 回调函数，每收到一块数据就调用一次，参数是 chunk_text
    """
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
        "model": "deepseek-chat",
        "messages": [
            item for item in value
        ],
        "temperature": temp,
        "stream": True,  # 开启流式传输,response_format={
        'type': 'json_object'
    }

    try:
        # 4. 发送 POST 请求（流式）
        response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)
        
        if response.status_code == 200:
            full_message = ""
            # 逐行读取流式响应
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    # SSE 格式以 "data: " 开头
                    if line_text.startswith('data: '):
                        json_str = line_text[6:]  # 去掉 "data: " 前缀
                        if json_str == '[DONE]':
                            break
                        try:
                            chunk = json.loads(json_str)
                            # 提取 delta 中的 content
                            delta = chunk.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_message += content
                                # 实时打印
                                print(content, end='', flush=True)
                                # 如果有回调函数，也调用一下
                                if stream_callback:
                                    stream_callback(content)
                        except json.JSONDecodeError:
                            continue
            print()  # 最后换行
            print("="*50)
            return full_message.strip()
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络或请求错误: {e}")
    except KeyError as e:
        print(f"❌ 响应格式异常，缺少字段: {e}")
        return None

if __name__ == "__main__":
    api_single([{'role': 'system', 'content': '你是一个专业的诗词填写助手。'},{'role': 'user', 'content': '介绍你的使命'}])
