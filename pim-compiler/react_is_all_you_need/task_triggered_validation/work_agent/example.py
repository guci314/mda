"""
WebScraper使用示例
展示如何使用WebScraper类获取网页信息
"""

from web_scraper import WebScraper


def main():
    # 创建爬虫实例
    scraper = WebScraper(delay=1)  # 设置1秒延时
    
    # 示例1: 获取网页标题
    print("=== 获取网页标题 ===")
    url = "https://httpbin.org/html"
    title = scraper.get_title(url)
    if title:
        print(f"网页标题: {title}")
    else:
        print("获取标题失败")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 获取网页链接
    print("=== 获取网页链接 ===")
    links = scraper.get_links(url)
    print(f"找到 {len(links)} 个链接:")
    for i, link in enumerate(links[:5]):  # 只显示前5个链接
        print(f"{i+1}. {link['text'][:50]}... -> {link['url'][:40]}...")
    
    print("\n" + "="*50 + "\n")
    
    # 示例3: 获取内部链接和外部链接
    print("=== 获取内部和外部链接 ===")
    # 使用一个更复杂的网站作为示例
    test_url = "https://httpbin.org/"
    internal_links = scraper.get_internal_links(test_url)
    external_links = scraper.get_external_links(test_url)
    
    print(f"内部链接数量: {len(internal_links)}")
    for i, link in enumerate(internal_links[:3]):  # 只显示前3个
        print(f"  {i+1}. {link['text'][:30]}... -> {link['url'][:40]}...")
    
    print(f"外部链接数量: {len(external_links)}")
    for i, link in enumerate(external_links[:3]):  # 只显示前3个
        print(f"  {i+1}. {link['text'][:30]}... -> {link['url'][:40]}...")


if __name__ == "__main__":
    main()