import re

filename = "main.py"

print(f"正在修复 {filename}...")

# 读取整个文件
with open(filename, 'r') as f:
    content = f.read()

# 方法1：使用正则表达式找到并修复有问题的行
# 查找包含"STRM 生成任务"的行
pattern = r'^(\s*)return \{"status": "started", "msg": "STRM 生成任务已在后台启动"\}'

# 检查是否能找到
match = re.search(pattern, content, re.MULTILINE)
if match:
    print(f"找到问题行，当前缩进: {len(match.group(1))} 字符")
    
    # 确定正确的缩进：应该是4的倍数，至少4个空格
    # 查找这个函数开始的def行
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "STRM 生成任务已在后台启动" in line:
            print(f"问题在第 {i+1} 行")
            # 向上找最近的async def或def
            for j in range(i-1, max(-1, i-20), -1):
                if lines[j].strip().startswith(('async def ', 'def ')):
                    print(f"属于函数（第{j+1}行）: {lines[j].strip()}")
                    # 计算函数定义的缩进
                    func_indent = len(lines[j]) - len(lines[j].lstrip())
                    expected_indent = func_indent + 4
                    print(f"函数缩进: {func_indent}, 期望缩进: {expected_indent}")
                    
                    # 修复这一行
                    current_line = lines[i]
                    current_indent = len(current_line) - len(current_line.lstrip())
                    
                    if current_indent != expected_indent:
                        lines[i] = ' ' * expected_indent + current_line.lstrip()
                        print(f"已修复第{i+1}行")
                        print(f"修复前: {repr(current_line)}")
                        print(f"修复后: {repr(lines[i])}")
                    break
            break
    
    # 写回文件
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

# 方法2：如果正则没找到，直接按行修复
else:
    print("正则未匹配，使用行扫描...")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "STRM 生成任务已在后台启动" in line:
            print(f"在第 {i+1} 行找到问题")
            print(f"原内容: {repr(line)}")
            
            # 简单修复：确保有4个空格的缩进
            if not line.startswith('    '):
                lines[i] = '    ' + line.lstrip()
                print(f"修复为: {repr(lines[i])}")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

print("✅ 修复完成")

# 验证
try:
    compile(content, filename, 'exec')
    print("✅ 语法验证通过")
except SyntaxError as e:
    print(f"❌ 语法错误: {e}")
