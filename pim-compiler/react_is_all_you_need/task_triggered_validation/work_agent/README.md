# 简单Web爬虫工具

一个基于Python的简单Web爬虫工具，支持获取网页标题和链接。

## 功能特性

- 获取网页标题
- 获取网页中的所有链接
- 区分内部链接和外部链接
- 自动处理相对链接
- 可配置请求延时避免被屏蔽

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 使用方法

### 基本使用

```python
from web_scraper import WebScraper

# 创建爬虫实例
scraper = WebScraper(delay=1)  # 设置1秒延时

# 获取网页标题
title = scraper.get_title("https://example.com")
print(f"网页标题: {title}")

# 获取网页链接
links = scraper.get_links("https://example.com")
for link in links:
    print(f"{link['text']} -> {link['url']}")
```

### 获取内部和外部链接

```python
# 获取内部链接（同域名）
internal_links = scraper.get_internal_links("https://example.com")

# 获取外部链接（不同域名）
external_links = scraper.get_external_links("https://example.com")
```

## 运行示例

```bash
python example.py
```

## 运行测试

```bash
python test_scraper.py
```

## 类说明

### WebScraper

#### 构造函数
```python
WebScraper(delay=1)
```
- `delay`: 请求间隔时间（秒），默认为1秒

#### 方法

- `get_title(url)`: 获取网页标题
- `get_links(url)`: 获取网页中的所有链接
- `get_internal_links(url)`: 获取网页中的内部链接
- `get_external_links(url)`: 获取网页中的外部链接

## 注意事项

1. 请遵守网站的robots.txt规则
2. 合理设置请求延时，避免对目标网站造成压力
3. 仅用于学习和合法用途