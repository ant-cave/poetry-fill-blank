import json
import app

with open("./data/reference-original.json", "r", encoding="utf-8") as f:
    raw = json.loads(f.read())

with open('data/format_prompt.md', 'r', encoding='utf-8') as f:
    prompt = f.read()
texts=[]
'''while 1:
    text = input("请输入要填写的诗词: ")
    if text=="":
        break
    texts.append(text)

result=json.loads(app.api_single([{'role': 'system', 'content': prompt},{'role': 'user', 'content': "\n".join(texts)}]))
'''
with open('input.txt', 'r', encoding='utf-8') as f:
    result=json.loads(app.api_single([{'role': 'system', 'content': prompt},{'role': 'user', 'content': f.read()}]))
# 以读写模式打开文件，若文件为空则初始化为空列表，否则读取原有数据
with open("./data/reference-original.json", "r+", encoding="utf-8") as f:
    content = f.read().strip()
    raw_text = json.loads(content) if content else []
    raw_text.append(result)
    # 将文件指针移到开头，清空原内容后写入更新后的数据
    f.seek(0)
    f.truncate()
    f.write(json.dumps(raw_text, ensure_ascii=False, indent=2))
