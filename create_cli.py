#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行版本 - 直接运行生成（兼容旧版用法）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.config import load_config, ensure_dirs
from lib.generator import generate_questions, save_generated_data
from lib.printer import generate_test_papers


def main():
    config = load_config()
    ensure_dirs(config)
    
    poet = input("请输入诗人：")
    poem = input("请输入诗名：")
    num_str = input("请输入题目数量：")
    
    try:
        num = int(num_str)
    except ValueError:
        print("[!] 数量必须是数字")
        return
    
    difficulty = '0.9'
    
    print(f"[*] 正在生成 {poet}《{poem}》的题目...")
    
    result = generate_questions(poet, poem, num, difficulty)
    
    if result is None:
        print("[!] 生成失败")
        return
    
    # 保存数据
    if save_generated_data(result, config):
        print("[*] 正在生成试卷...")
        test_file, answer_file = generate_test_papers()
        
        if test_file and answer_file and sys.platform == 'win32':
            os.system(f'start "" "{test_file}"')
            os.system(f'start "" "{answer_file}"')


if __name__ == "__main__":
    main()
