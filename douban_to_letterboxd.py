import requests
import re
import time
import json
import random
import csv
from bs4 import BeautifulSoup
from datetime import datetime


class DoubanToLetterboxd:
    def __init__(self, user_id, cookies):
        self.user_id = user_id
        self.cookies = self._parse_cookies(cookies)
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': f'https://movie.douban.com/people/{user_id}/collect'
        })
        self.results = []
        
    def _parse_cookies(self, cookie_str):
        cookies = {}
        for item in cookie_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies[name] = value
        return cookies
    
    def _random_sleep(self):
        """随机延迟，避免被识别为机器人"""
        time.sleep(random.uniform(1, 3))
    
    def get_movie_collections(self, start=0, count=15):
        """获取用户的电影收藏"""
        url = f'https://movie.douban.com/people/{self.user_id}/collect?start={start}&sort=time&rating=all&filter=all&mode=grid'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error fetching collections: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching collections: {e}")
            return None
    
    def get_movie_rating(self, douban_id):
        """获取电影评分"""
        url = f'https://movie.douban.com/subject/{douban_id}/'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rating_input = soup.find('input', {'id': 'n_rating'})
                if rating_input:
                    return rating_input.get('value')
            return "0"  # 如果无法获取评分，返回0
        except Exception as e:
            print(f"Error fetching rating for {douban_id}: {e}")
            return "0"
    
    def get_imdb_id(self, douban_id):
        """通过豆瓣ID获取IMDB ID - 改进版"""
        url = f'https://movie.douban.com/subject/{douban_id}/'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 方法1：从页面内容直接提取IMDb ID信息
                info = soup.select_one('div#info')
                if info:
                    # 先尝试从文本中提取
                    imdb_text = info.text
                    imdb_match = re.search(r'IMDb:\s*(tt\d+)', imdb_text)
                    if imdb_match:
                        return imdb_match.group(1)
                    
                    # 然后尝试从链接中提取
                    imdb_link = info.find('a', href=lambda href: href and 'imdb.com/title/' in href)
                    if imdb_link:
                        href = imdb_link.get('href')
                        match = re.search(r'imdb\.com/title/(tt\d+)', href)
                        if match:
                            return match.group(1)
                
                # 方法2：直接搜索页面中所有可能包含IMDb ID的文本
                page_text = response.text
                imdb_patterns = [
                    r'IMDb:\s*(tt\d+)',
                    r'imdb\.com/title/(tt\d+)',
                    r'IMDb</span>: <a[^>]*>(tt\d+)</a>',
                    r'IMDb</span>: <a[^>]*href="[^"]*?(tt\d+)[^"]*"',
                ]
                
                for pattern in imdb_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        return match.group(1)
                        
                # 输出调试信息
                print(f"无法找到电影 {douban_id} 的IMDb ID")
                # 如果有必要，可以保存页面内容以进一步调试
                # with open(f"debug_{douban_id}.html", "w", encoding="utf-8") as f:
                #     f.write(page_text)
                return ""
                
            else:
                print(f"获取电影 {douban_id} 详情失败: HTTP {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"获取电影 {douban_id} 的IMDb ID时出错: {e}")
            return ""
    
    def parse_collections(self, html_content):
        """解析HTML内容，提取电影信息"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = soup.select('.item')
        
        movies = []
        for item in items:
            try:
                # 获取豆瓣ID
                href = item.select_one('.pic a')['href']
                douban_id = re.search(r'/subject/(\d+)/', href).group(1)
                
                # 获取标题
                title_elem = item.select_one('.title a')
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                # 获取观看日期
                date_elem = item.select_one('.date')
                watched_date = date_elem.text.strip() if date_elem else ""
                # 转换日期格式为Letterboxd格式 (YYYY-MM-DD)
                if watched_date:
                    try:
                        dt = datetime.strptime(watched_date, "%Y-%m-%d")
                        watched_date = dt.strftime("%Y-%m-%d")
                    except:
                        pass
                
                # 获取评论
                comment_elem = item.select_one('.comment')
                review = comment_elem.text.strip() if comment_elem else ""
                
                # 获取IMDB ID (改进版)
                self._random_sleep()  # 随机延迟
                print(f"正在获取 [{title}] 的IMDB ID...")
                imdb_id = self.get_imdb_id(douban_id)
                
                # 获取用户评分
                self._random_sleep()  # 随机延迟
                print(f"正在获取 [{title}] 的评分...")
                rating = self.get_movie_rating(douban_id)
                
                
                movie = {
                    'imdbID': imdb_id,
                    'Rating': rating,
                    'WatchedDate': watched_date,
                    'Review': review,
                    'Title': title,  # 额外添加标题用于显示
                    'DoubanID': douban_id  # 额外添加豆瓣ID用于调试
                }
                movies.append(movie)
                
                # 输出当前电影信息
                print(f"处理: {title}")
                print(f"imdbID: {imdb_id}, Rating: {rating}, WatchedDate: {watched_date}")
                print(f"Review: {review[:50]}..." if len(review) > 50 else f"Review: {review}")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error parsing movie item: {e}")
        
        return movies
    
    def process_all_collections(self, max_pages=100):
        """处理所有收藏页面"""
        total_movies = []
        for page in range(max_pages):
            start = page * 15
            print(f"正在处理第 {page+1} 页...")
            html_content = self.get_movie_collections(start)
            if not html_content:
                break
                
            movies = self.parse_collections(html_content)
            if not movies:
                break
                
            total_movies.extend(movies)
            self._random_sleep()  # 随机延迟
            
            # 检查是否为最后一页
            if "后页" not in html_content:
                break
        
        self.results = total_movies
        return total_movies
    
    def export_to_csv(self, filename="letterboxd_import.csv"):
        """导出为Letterboxd可导入的CSV格式"""
        if not self.results:
            print("没有数据可导出")
            return
            
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['imdbID', 'Rating', 'WatchedDate', 'Review']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for movie in self.results:
                writer.writerow({
                    'imdbID': movie['imdbID'],
                    'Rating': movie['Rating'],
                    'WatchedDate': movie['WatchedDate'],
                    'Review': movie['Review']
                })
                
        print(f"已导出 {len(self.results)} 条数据到 {filename}")


def main():
    print("豆瓣观影数据导出工具 - Letterboxd导入")
    print("-" * 60)
    
    user_id = input("请输入你的豆瓣用户ID: ")
    cookies = input("请输入你的豆瓣Cookie: ")
    
    exporter = DoubanToLetterboxd(user_id, cookies)
    print("开始获取数据，这可能需要一些时间...")
    exporter.process_all_collections()
    
    export_filename = input("请输入导出文件名(默认为letterboxd_import.csv): ") or "letterboxd_import.csv"
    exporter.export_to_csv(export_filename)
    print("处理完成!")


if __name__ == "__main__":
    main()