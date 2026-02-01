import requests
import json
import os
from .config import load_config, get_api_token, should_show_ai_response


def api_single(value: list[dict[str, str]], stream_callback=None, temp=0.2):
    """
    调用 AI API，支持流式传输
    现在从config.json读取配置，不再硬编码
    """
    config = load_config()
    
    # 获取API Token
    api_key = get_api_token(config)
    if not api_key:
        print("[!] 错误: API Token 未设置")
        print("    请设置以下之一:")
        print("    1. 环境变量 DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
        print("    2. 在 config.json 中填写 api.token")
        return None

    # 从配置读取API地址和模型
    api_config = config.get('api', {})
    url = api_config.get('url', 'https://api.deepseek.com/v1/chat/completions')
    model = api_config.get('model', 'deepseek-chat')
    show_response = should_show_ai_response(config)

    # 构造请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构造请求体
    data = {
        "model": model,
        "messages": [item for item in value],
        "temperature": temp,
        "stream": True,
        'type': 'json_object'
    }

    try:
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
                                # 根据配置决定是否实时打印
                                if show_response:
                                    print(content, end='', flush=True)
                                # 如果有回调函数，也调用一下
                                if stream_callback:
                                    stream_callback(content)
                        except json.JSONDecodeError:
                            continue
            
            if show_response:
                print()  # 最后换行
                print("=" * 50)
            
            return full_message.strip()
        else:
            print(f"[!] 请求失败，状态码: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"[!] 错误详情: {error_detail}")
            except:
                print(f"[!] 响应内容: {response.text[:200]}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[!] 网络或请求错误: {e}")
        return None
    except Exception as e:
        print(f"[!] 未知错误: {e}")
        return None
