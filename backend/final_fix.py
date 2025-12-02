import re

with open("main.py", "r") as f:
    lines = f.readlines()

print("=== 分析第318行问题 ===")
print(f"第318行内容: {repr(lines[317].rstrip())}")

# 查找第318行所在的函数
function_start = -1
for i in range(317, -1, -1):
    if lines[i].strip().startswith(('async def ', 'def ')):
        function_start = i
        break

if function_start != -1:
    print(f"\n第318行位于函数中，函数从第{function_start+1}行开始:")
    print(f"函数定义: {lines[function_start].strip()}")
    
    # 计算函数的缩进
    func_line = lines[function_start]
    func_indent = len(func_line) - len(func_line.lstrip())
    print(f"函数定义缩进: {func_indent} 空格")
    
    # 函数内的代码应该比函数定义多4个空格
    expected_indent = func_indent + 4
    print(f"第318行期望缩进: {expected_indent} 空格")
    
    # 检查当前缩进
    current_line = lines[317]
    current_indent = len(current_line) - len(current_line.lstrip())
    print(f"第318行当前缩进: {current_indent} 空格")
    
    if current_indent != expected_indent:
        print(f"⚠️  缩进错误！修复中...")
        # 修复缩进
        lines[317] = ' ' * expected_indent + lines[317].lstrip()
        print(f"修复后: {repr(lines[317].rstrip())}")

# 再检查第312行
print(f"\n=== 检查第312行 ===")
print(f"第312行内容: {repr(lines[311].rstrip())}")

# 写回文件
with open("main.py", "w") as f:
    f.writelines(lines)

print("\n✅ 修复完成")
