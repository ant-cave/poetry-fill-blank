#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从生成的JSON数据创建可打印的试卷和答案
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.printer import generate_test_papers


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='生成诗词默写试卷和答案')
    parser.add_argument('input_file', nargs='?', help='输入的JSON文件路径（默认使用data/generated.json）')
    args = parser.parse_args()
    
    test_file, answer_file = generate_test_papers(args.input_file)
    
    if test_file and answer_file and sys.platform == 'win32':
        os.system(f'start "" "{test_file}"')
        os.system(f'start "" "{answer_file}"')


if __name__ == "__main__":
    main()
