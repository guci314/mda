#!/usr/bin/env python3
"""
搜索工具 - 使用Serper API进行网络搜索
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional, List

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_base import Function


class SearchTool(Function):
    """搜索工具 - 使用Serper API搜索互联网"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="搜索互联网获取最新信息",
            parameters={
                "query": {
                    "type": "string",
                    "description": "搜索查询词"
                },
                "num_results": {
                    "type": "integer",
                    "description": "返回结果数量",
                    "default": 5
                }
            }
        )
        
        # 获取API密钥
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY环境变量未设置")
        
        self.base_url = "https://google.serper.dev/search"
    
    def execute(self, **kwargs) -> str:
        """
        执行搜索
        
        Args:
            query: 搜索查询词
            num_results: 返回结果数量（默认5）
            
        Returns:
            搜索结果的格式化字符串
        """
        query = kwargs.get('query')
        if not query:
            return "错误：需要提供搜索查询词"
        
        num_results = kwargs.get('num_results', 5)
        
        try:
            # 构建请求
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results
            }
            
            # 发送请求
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                return f"搜索失败：HTTP {response.status_code} - {response.text}"
            
            data = response.json()
            
            # 格式化结果
            results = []
            
            # 添加答案框（如果有）
            if 'answerBox' in data:
                answer = data['answerBox']
                if 'answer' in answer:
                    results.append(f"📌 直接答案：{answer['answer']}\n")
                elif 'snippet' in answer:
                    results.append(f"📌 摘要：{answer['snippet']}\n")
            
            # 添加知识图谱（如果有）
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                if 'description' in kg:
                    results.append(f"📚 知识图谱：{kg.get('title', '')} - {kg['description']}\n")
            
            # 添加搜索结果
            if 'organic' in data:
                results.append("🔍 搜索结果：")
                for i, result in enumerate(data['organic'][:num_results], 1):
                    title = result.get('title', '无标题')
                    link = result.get('link', '')
                    snippet = result.get('snippet', '无摘要')
                    results.append(f"\n{i}. {title}")
                    results.append(f"   链接：{link}")
                    results.append(f"   摘要：{snippet}")
            
            # 添加相关搜索（如果有）
            if 'relatedSearches' in data and data['relatedSearches']:
                results.append("\n💡 相关搜索：")
                for related in data['relatedSearches'][:3]:
                    results.append(f"   - {related.get('query', '')}")
            
            return "\n".join(results) if results else "未找到相关结果"
            
        except requests.exceptions.Timeout:
            return "搜索超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            return f"搜索请求失败：{str(e)}"
        except json.JSONDecodeError:
            return "搜索结果解析失败"
        except Exception as e:
            return f"搜索失败：{str(e)}"


class NewsSearchTool(Function):
    """新闻搜索工具 - 搜索最新新闻"""
    
    def __init__(self):
        super().__init__(
            name="search_news",
            description="搜索最新新闻和时事",
            parameters={
                "query": {
                    "type": "string",
                    "description": "新闻搜索查询词"
                },
                "time_range": {
                    "type": "string",
                    "description": "时间范围：day, week, month, year",
                    "default": "week"
                }
            }
        )
        
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY环境变量未设置")
        
        self.base_url = "https://google.serper.dev/news"
    
    def execute(self, **kwargs) -> str:
        """
        执行新闻搜索
        
        Args:
            query: 搜索查询词
            time_range: 时间范围
            
        Returns:
            新闻搜索结果
        """
        query = kwargs.get('query')
        if not query:
            return "错误：需要提供新闻搜索查询词"
        
        time_range = kwargs.get('time_range', 'week')
        
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'tbs': f'qdr:{time_range[0]}',  # day->d, week->w, month->m, year->y
                'num': 5
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                return f"新闻搜索失败：HTTP {response.status_code}"
            
            data = response.json()
            
            # 格式化新闻结果
            results = [f"📰 关于 '{query}' 的最新新闻：\n"]
            
            if 'news' in data:
                for i, news in enumerate(data['news'][:5], 1):
                    title = news.get('title', '无标题')
                    source = news.get('source', '未知来源')
                    date = news.get('date', '未知时间')
                    snippet = news.get('snippet', '无摘要')
                    link = news.get('link', '')
                    
                    results.append(f"{i}. {title}")
                    results.append(f"   来源：{source} | 时间：{date}")
                    results.append(f"   摘要：{snippet}")
                    results.append(f"   链接：{link}\n")
            
            return "\n".join(results) if len(results) > 1 else "未找到相关新闻"
            
        except Exception as e:
            return f"新闻搜索失败：{str(e)}"