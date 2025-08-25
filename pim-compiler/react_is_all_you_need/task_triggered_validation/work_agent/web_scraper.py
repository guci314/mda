import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


class WebScraper:
    """
    一个简单的Web爬虫工具类
    支持获取网页标题和链接
    """
    
    def __init__(self, delay=1):
        """
        初始化爬虫
        :param delay: 请求间隔时间（秒）
        """
        self.delay = delay
        self.session = requests.Session()
        # 设置User-Agent避免被某些网站屏蔽
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page(self, url):
        """
        获取网页内容
        :param url: 目标网址
        :return: BeautifulSoup对象
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            response.encoding = response.apparent_encoding  # 自动检测编码
            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(self.delay)  # 延时避免请求过快
            return soup
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return None
        except Exception as e:
            print(f"解析错误: {e}")
            return None
    
    def get_title(self, url):
        """
        获取网页标题
        :param url: 目标网址
        :return: 网页标题字符串
        """
        soup = self.get_page(url)
        if soup:
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            else:
                # 尝试获取H1标签作为备选标题
                h1_tag = soup.find('h1')
                if h1_tag:
                    return h1_tag.get_text().strip()
                return "未找到标题"
        return None
    
    def get_links(self, url):
        """
        获取网页中的所有链接
        :param url: 目标网址
        :return: 链接列表
        """
        soup = self.get_page(url)
        if not soup:
            return []
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # 处理相对链接
            absolute_url = urljoin(url, href)
            links.append({
                'text': link.get_text().strip(),
                'url': absolute_url
            })
        return links
    
    def get_internal_links(self, url):
        """
        获取网页中的内部链接（同域名）
        :param url: 目标网址
        :return: 内部链接列表
        """
        links = self.get_links(url)
        base_domain = urlparse(url).netloc
        internal_links = []
        
        for link in links:
            link_domain = urlparse(link['url']).netloc
            if link_domain == base_domain:
                internal_links.append(link)
        
        return internal_links
    
    def get_external_links(self, url):
        """
        获取网页中的外部链接（不同域名）
        :param url: 目标网址
        :return: 外部链接列表
        """
        links = self.get_links(url)
        base_domain = urlparse(url).netloc
        external_links = []
        
        for link in links:
            link_domain = urlparse(link['url']).netloc
            if link_domain and link_domain != base_domain:
                external_links.append(link)
        
        return external_links