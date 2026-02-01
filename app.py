#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诗词默写生成器 - 主程序
功能：通过AI生成诗词理解性默写题目，并输出为可打印的HTML试卷
"""

import os
import sys

# 把lib目录加入路径，方便导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.config import load_config, ensure_dirs, get_api_token, save_token_to_config
from lib.generator import generate_questions, save_generated_data
from lib.printer import generate_test_papers

# rich 相关导入
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

console = Console()


def check_setup():
    """检查并初始化环境"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]诗词默写题目生成器[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    # 加载配置（会自动创建config.json如果不存在）
    config = load_config()
    
    # 确保目录存在
    ensure_dirs(config)
    
    # 检查API Token
    token = get_api_token(config)
    
    # 创建状态表格
    table = Table(show_header=False, box=box.ROUNDED, border_style="dim")
    table.add_column("项目", style="cyan")
    table.add_column("状态")
    
    if not token:
        table.add_row("API Token", "[yellow]⚠ 未设置[/yellow]")
        console.print(table)
        console.print()
        console.print(Panel(
            "[yellow]未检测到 API Key[/yellow]\n\n"
            "[dim]可通过以下方式设置:[/dim]\n"
            "  1. 环境变量: [green]DEEPSEEK_API_KEY[/green] 或 [green]OPENAI_API_KEY[/green]\n"
            "  2. 直接输入（将保存到 config.json）",
            border_style="yellow"
        ))
        console.print()
        
        # 提示用户输入 API Key
        token = Prompt.ask("[cyan]请输入 DeepSeek API Key[/cyan]", password=True)
        
        if not token or len(token.strip()) < 10:
            console.print("[red]✗ API Key 无效，程序退出[/red]")
            sys.exit(1)
        
        token = token.strip()
        
        # 保存到 config.json
        if save_token_to_config(token):
            masked_token = token[:8] + "..." if len(token) > 8 else "***"
            console.print(f"[green]✓[/green] API Key 已保存 [dim]({masked_token})[/dim]")
        else:
            console.print("[yellow]⚠ 保存配置失败，但当前会话仍可使用[/yellow]")
        
        # 更新 config 对象
        config['api']['token'] = token
    else:
        # 只显示token的前8位，安全考虑
        masked_token = token[:8] + "..." if len(token) > 8 else "***"
        table.add_row("API Token", f"[green]✓ 已设置[/green] [dim]{masked_token}[/dim]")
        console.print(table)
    
    console.print()
    return config


def interactive_mode(config):
    """交互模式：询问用户输入并生成题目"""
    console.print(Panel(
        "[bold]开始生成题目[/bold]",
        border_style="green"
    ))
    console.print()
    
    # 获取用户输入
    poet = Prompt.ask("[cyan]请输入诗人[/cyan]").strip()
    if not poet:
        console.print("[red]✗ 诗人不能为空[/red]")
        return
    
    poem = Prompt.ask("[cyan]请输入诗名[/cyan]").strip()
    if not poem:
        console.print("[red]✗ 诗名不能为空[/red]")
        return
    
    num_str = Prompt.ask("[cyan]请输入题目数量[/cyan]", default="5").strip()
    try:
        num = int(num_str) if num_str else 5
    except ValueError:
        console.print("[yellow]⚠ 数量输入无效，使用默认值 5[/yellow]")
        num = 5
    
    difficulty = Prompt.ask("[cyan]请输入难度 0-1[/cyan]", default="0.9").strip()
    if not difficulty:
        difficulty = "0.9"
    
    console.print()
    
    # 用进度条展示生成过程
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"[cyan]正在生成 [bold]{poet}《{poem}》[/bold] 的 {num} 道题目...[/cyan]",
            total=None
        )
        
        # 生成题目
        result = generate_questions(poet, poem, num, difficulty)
    
    if result is None:
        console.print()
        console.print(Panel(
            "[red]生成失败[/red]\n"
            "[dim]请检查API配置和网络连接[/dim]",
            border_style="red"
        ))
        return
    
    console.print()
    console.print(f"[green]✓[/green] 成功生成 [bold]{len(result)}[/bold] 道题目")
    console.print()
    
    # 保存数据
    if save_generated_data(result, config):
        console.print("[dim]正在生成试卷和答案...[/dim]")
        test_file, answer_file = generate_test_papers()
        
        if test_file and answer_file:
            console.print()
            console.print(Panel(
                f"[bold green]全部完成！[/bold green]\n\n"
                f"[dim]试卷文件：[/dim]{test_file}\n"
                f"[dim]答案文件：[/dim]{answer_file}",
                border_style="green"
            ))
            console.print()
            # 自动打开生成的文件（Windows）
            if sys.platform == 'win32':
                os.system(f'start "" "{test_file}"')
                os.system(f'start "" "{answer_file}"')


def main():
    """主函数"""
    try:
        config = check_setup()
        interactive_mode(config)
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]⚠ 操作已取消[/yellow]")
    except Exception as e:
        console.print()
        console.print(Panel(
            f"[red]发生错误[/red]\n\n[dim]{e}[/dim]",
            border_style="red"
        ))
        import traceback
        console.print("[dim]详细错误信息：[/dim]")
        console.print(traceback.format_exc())
    
    console.print()
    Prompt.ask("[dim]按回车键退出[/dim]", default="")


if __name__ == "__main__":
    main()
