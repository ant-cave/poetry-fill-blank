import json
import os
from collections import defaultdict
from .config import load_config
from rich.console import Console

console = Console()


def generate_test_papers(json_file=None):
    """
    生成试卷和答案HTML
    """
    config = load_config()
    
    # 如果没传文件路径，就用默认的
    if json_file is None:
        data_dir = config.get('paths', {}).get('data_dir', './data')
        json_file = os.path.join(data_dir, 'generated.json')
    
    # 检查文件是否存在
    if not os.path.exists(json_file):
        console.print(f"[red]✗ 错误：文件 {json_file} 不存在！[/red]")
        console.print("[yellow]⚠ 请先生成题目数据[/yellow]")
        return None, None

    # 读取JSON文件
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ JSON解析错误: {e}[/red]")
        return None, None
    except Exception as e:
        console.print(f"[red]✗ 读取文件错误: {e}[/red]")
        return None, None

    # 按诗人和诗名分组
    poem_dict = defaultdict(list)
    for item in data:
        key = (item.get('poet', '未知'), item.get('title', '未知'))
        poem_dict[key].append(item)

    # 生成试卷HTML（只有题目，没有答案）
    test_paper = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>诗词默写试卷</title>
    <style>
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #000;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .info {
            font-size: 14px;
            margin-bottom: 5px;
        }
        .section {
            margin-bottom: 30px;
        }
        .poem-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #000;
        }
        .question {
            margin-bottom: 20px;
            page-break-inside: avoid;
        }
        .question-number {
            font-weight: bold;
            margin-right: 5px;
        }
        .question-text {
            margin-bottom: 10px;
        }
        .blank {
            display: inline-block;
            width: 200px;
            border-bottom: 1px solid #000;
            margin: 0 5px;
            height: 20px;
            vertical-align: middle;
        }
        .two-blank {
            display: inline-block;
        }
        .blank-line {
            height: 20px;
            margin-top: 5px;
        }
        @media print {
            .page-break {
                page-break-before: always;
            }
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 12px;
            color: #666;
        }
    </style>
    <script>
        setTimeout(function() {
            window.print();
        }, 1000);
    </script>
</head>
<body>
    <div class="header">
        <div class="title">高中语文诗词默写测试卷</div>
        <div class="info">姓名：___________ 班级：___________ 学号：___________</div>
        <div class="info">得分：___________</div>
    </div>
'''

    # 生成答案HTML
    answer_sheet = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>诗词默写答案</title>
    <style>
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #000;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .section {
            margin-bottom: 30px;
        }
        .poem-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #000;
        }
        .question {
            margin-bottom: 20px;
        }
        .question-number {
            font-weight: bold;
            margin-right: 5px;
            display: inline;
        }
        .question-text {
            display: inline;
            margin-right: 10px;
        }
        .answer {
            color: #c00;
            font-weight: bold;
            display: inline;
        }
        .answer-line {
            display: inline;
            margin-right: 10px;
        }
        .full-question {
            margin-bottom: 15px;
            line-height: 1.8;
        }
    </style>
    <script>
        setTimeout(function() {
            window.print();
        }, 1000);
    </script>
</head>
<body>
    <div class="header">
        <div class="title">诗词默写测试卷参考答案</div>
    </div>
'''

    question_count = 0

    # 为每首诗生成题目
    for (poet, title), sentences in poem_dict.items():
        # 去重
        unique_sentences = []
        seen_values = set()
        for sentence in sentences:
            if sentence.get('value') not in seen_values:
                seen_values.add(sentence.get('value'))
                unique_sentences.append(sentence)

        # 添加到试卷
        test_paper += f'''
    <div class="section">
        <div class="poem-title">{title}（{poet}）</div>
'''

        # 添加到答案
        answer_sheet += f'''
    <div class="section">
        <div class="poem-title">{title}（{poet}）</div>
'''

        # 生成每道题
        for i, sentence in enumerate(unique_sentences):
            question_count += 1

            # 处理题目文本，将占位符替换为下划线
            value_text = sentence.get('value', '')
            answers = sentence.get('answer', [])
            
            for _ in answers:
                value_text = value_text.replace("{{answer}}", "_______________", 1)
            
            value_text = value_text.replace('{{answer}}', "_______________")
            
            # 试卷：添加题目
            test_paper += f'''
        <div class="question">
            <div class="question-text"><span class="question-number">{question_count}.</span>
            {value_text}</div>
        </div>
'''

            # 答案：创建完整的题目文本，将占位符替换为答案
            original_text = sentence.get('value', '')
            answer_text = original_text

            # 将{{answer}}替换为实际答案
            for answer_line in answers:
                if "{{answer}}" in answer_text:
                    answer_text = answer_text.replace("{{answer}}", f"<span class='answer'>{answer_line}</span>", 1)

            # 答案：添加题目和答案（不换行）
            answer_sheet += f'''
        <div class="full-question">
            <span class="question-number">{question_count}.</span>
            <span class="question-text">{answer_text}</span>
        </div>
'''

        test_paper += '''    </div>
'''
        answer_sheet += '''    </div>
'''

    # 添加页脚
    test_paper += f'''
    <div class="footer">
        共 {question_count} 题，每题 5 分，总分 {question_count * 5} 分
    </div>
</body>
</html>'''

    answer_sheet += '''</body>
</html>'''

    # 保存试卷和答案
    output_dir = config.get('paths', {}).get('output_dir', './output')
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        console.print(f"[green]✓[/green] 创建输出目录: [dim]{output_dir}[/dim]")

    test_file = os.path.join(output_dir, "诗词默写试卷.html")
    answer_file = os.path.join(output_dir, "诗词默写答案.html")

    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_paper)

        with open(answer_file, 'w', encoding='utf-8') as f:
            f.write(answer_sheet)

        console.print(f"[green]✓[/green] 生成完成！")
        console.print(f"  [dim]试卷文件：[/dim]{test_file}")
        console.print(f"  [dim]答案文件：[/dim]{answer_file}")
        console.print(f"  [dim]题目总数：[/dim][bold]{question_count}[/bold] 题")

        return test_file, answer_file
    except Exception as e:
        console.print(f"[red]✗ 保存HTML文件失败: {e}[/red]")
        return None, None
