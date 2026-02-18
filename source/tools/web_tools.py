# tools/web_tools.py
import requests

def search_web(query: str, num_results: int = 5) -> str:
    """简单的网页搜索（需要接入搜索 API）"""
    # 示例：使用 DuckDuckGo 或 SerpAPI
    # 这里仅作占位，实际需接入真实 API
    return f"搜索 '{query}' 的结果（需配置搜索 API）"

def fetch_url(url: str) -> str:
    """获取网页内容"""
    try:
        response = requests.get(url, timeout=10)
        return response.text[:2000]  # 限制长度
    except Exception as e:
        return f"获取失败: {e}"