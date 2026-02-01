import json
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

# 默认配置，万一config.json坏了还能兜底
DEFAULT_CONFIG = {
    "api": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "token": "",
        "model": "deepseek-chat"
    },
    "output": {
        "show_ai_response": True
    },
    "paths": {
        "data_dir": "./data",
        "output_dir": "./output"
    }
}

CONFIG_FILE = "config.json"


def ensure_config_exists():
    """检查config.json是否存在，不存在就创建一个"""
    if not os.path.exists(CONFIG_FILE):
        console.print(f"[yellow]⚠ 配置文件 {CONFIG_FILE} 不存在，正在创建默认配置...[/yellow]")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        console.print(f"[green]✓[/green] 已创建默认配置文件: [dim]{CONFIG_FILE}[/dim]")


def save_token_to_config(token):
    """保存token到config.json"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'api' not in config:
            config['api'] = {}
        config['api']['token'] = token
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        return True
    except Exception as e:
        console.print(f"[red]✗ 保存Token失败: {e}[/red]")
        return False


def load_config():
    """加载配置，如果没config就创建一个"""
    ensure_config_exists()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 简单校验一下关键字段
            if 'api' not in config or 'token' not in config.get('api', {}):
                console.print("[yellow]⚠ 配置文件格式可能有问题，使用默认配置[/yellow]")
                return DEFAULT_CONFIG.copy()
            return config
    except json.JSONDecodeError:
        console.print("[yellow]⚠ config.json 解析失败，使用默认配置[/yellow]")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        console.print(f"[yellow]⚠ 读取配置出错: {e}，使用默认配置[/yellow]")
        return DEFAULT_CONFIG.copy()


def ensure_dirs(config):
    """确保必要的目录都存在"""
    data_dir = config.get('paths', {}).get('data_dir', './data')
    output_dir = config.get('paths', {}).get('output_dir', './output')
    
    for dir_path in [data_dir, output_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            console.print(f"[green]✓[/green] 创建目录: [dim]{dir_path}[/dim]")


def get_api_token(config):
    """获取API Token，优先从环境变量，其次从config.json"""
    # 先看环境变量
    env_token = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if env_token:
        return env_token
    
    # 再看配置文件
    token = config.get('api', {}).get('token', '')
    if token:
        return token
    
    return None


def should_show_ai_response(config):
    """是否显示AI的原始回复"""
    return config.get('output', {}).get('show_ai_response', True)
