import re

with open("backend/main.py", "r") as f:
    content = f.read()

# 方法：重新统一缩进
# 先将所有连续空格缩进转换为4的倍数
lines = content.split('\n')
new_lines = []

for i, line in enumerate(lines):
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    
    if indent > 0:
        # 转换为4空格倍数
        new_indent = (indent // 4) * 4
        if new_indent == 0 and stripped:
            new_indent = 4  # 至少4个空格
        
        # 特殊情况：第312行强制修复
        if i == 311:  # 0-based索引
            print(f"强制修复第312行（索引{i+1}）")
            # 查找上一行的缩进
            if i > 0:
                prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                new_indent = prev_indent
                if lines[i-1].strip().endswith(':'):  # 如果是冒号，应该缩进更多
                    new_indent += 4
        
        new_line = ' ' * new_indent + stripped
    else:
        new_line = line
    
    new_lines.append(new_line)

# 写回文件
with open("backend/main.py", "w") as f:
    f.write('\n'.join(new_lines))

print("✅ 已完成强制修复")
