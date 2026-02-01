#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加原始诗词数据到参考库
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.api import api_single
from lib.config import load_config, ensure_dirs


def main():
    config = load_config()
    ensure_dirs(config)
    
    data_dir = config.get('paths', {}).get('data_dir', './data')
    
    # 加载参考数据
    ref_file = os.path.join(data_dir, 'reference-original.json')
    try:
        with open(ref_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        raw = []
        print(f"[!] 参考数据文件不存在，将创建新文件: {ref_file}")
    except json.JSONDecodeError:
        raw = []
        print("[!] 参考数据文件格式错误，将重新创建")
    
    # 加载格式化提示词
    prompt_file = os.path.join(data_dir, 'format_prompt.md')
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
    except FileNotFoundError:
        print(f"[!] 提示词文件不存在: {prompt_file}")
        return
    
    # 从input.txt读取输入
    input_file = 'input.txt'
    if not os.path.exists(input_file):
        print(f"[!] 输入文件不存在: {input_file}")
        print("    请创建input.txt并写入要处理的诗词内容")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        print("[!] 输入文件为空")
        return
    
    print("[*] 正在处理诗词数据...")
    result_str = api_single([
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': content}
    ])
    
    if result_str is None:
        print("[!] API调用失败")
        return
    
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError as e:
        print(f"[!] JSON解析失败: {e}")
        print("[!] 尝试修复...")
        # 尝试修复markdown代码块
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0].strip()
        result = json.loads(result_str)
    
    # 追加到参考数据
    raw.append(result)
    
    # 保存
    with open(ref_file, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    
    print(f"[+] 数据已添加到: {ref_file}")


if __name__ == "__main__":
    main()
