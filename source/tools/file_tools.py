# tools/file_tools.py
import os

def read_file(path: str) -> str:
    """读取文件内容"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"读取失败: {e}"

def write_file(path: str, content: str) -> str:
    """写入文件"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入 {path}"
    except Exception as e:
        return f"写入失败: {e}"

def list_directory(path: str = ".") -> str:
    """列出目录内容"""
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"列出目录失败: {e}"