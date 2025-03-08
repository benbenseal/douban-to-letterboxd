# douban-to-letterboxd

douban_to_letterboxd.py 代码和此Readme.md 均由 Claude 3.7 Sonnet 生成。本人调试测试通过后，在此分享给有需求的人。

# 豆瓣观影数据导出工具

将豆瓣电影收藏数据导出为Letterboxd可导入的CSV格式。

## 功能介绍

这个Python工具可以帮助你：

- 从豆瓣电影"看过"页面获取你的观影记录
- 提取每部影片的豆瓣评分、观影日期和短评
- 自动获取对应的IMDb ID
- 将数据导出为Letterboxd支持的CSV格式
- 考虑了防爬虫机制，加入随机延迟

## 前提条件

- Python 3.6+
- 以下Python库:
  - requests
  - beautifulsoup4
  - re (正则表达式，标准库)
  - csv (标准库)
  - datetime (标准库)
  - time (标准库)
  - random (标准库)

## 安装

1. 克隆仓库或下载代码
2. 安装依赖:

```bash
pip install requests beautifulsoup4
```

## 使用方法

1. 运行脚本:

```bash
python douban_to_letterboxd.py
```

2. 按提示输入:
   - 豆瓣用户ID (即个人主页URL中的ID，例如: `https://www.douban.com/people/你的ID/`)
   - 豆瓣Cookie (登录状态下从浏览器获取。自行网上搜索找到Cookie)

3. 程序将开始爬取数据并显示进度
4. 完成后，输入CSV文件名（默认为`letterboxd_import.csv`）

## 获取Cookie方法

1. 使用Chrome或Firefox浏览器登录豆瓣
2. 打开开发者工具 (F12 或右键 -> 检查)
3. 切换到"网络"(Network)选项卡
4. 刷新页面
5. 点击任意一个请求
6. 在"标头"(Headers)中找到"Cookie"字段
7. 复制整个Cookie值

## 导入Letterboxd

1. 登录Letterboxd账户
2. 进入Settings -> Import & Export
3. 选择"Import your data"
4. 上传生成的CSV文件
5. 按照Letterboxd的指导完成导入

## 注意事项

- 尊重豆瓣网站规则，不要频繁使用或短时间内爬取大量数据
- 程序已加入随机延迟以避免被检测为机器人
- 某些电影可能无法获取IMDb ID，这些电影将在Letterboxd导入时被跳过。另外，TV剧集也无法在Letterboxd上标记。
- 豆瓣的5星制对应为Letterboxd的5分制
- 默认可读取1500条以内的观影记录。如果你的标记数量超过1500条，请找到 def process_all_collections(self, max_pages=100): 这一行。这里 max_pages 的值默认是100，表示可以读取100*15=1500条数据，假如你有2700条数据，2700/15=则修改为 max_pages = 180

## 导出数据格式

程序生成的CSV文件包含以下字段:

- `imdbID`: 电影的IMDb ID (例如: tt0111161)
- `Rating`: 你给电影的评分 (1-5)
- `WatchedDate`: 观看日期 (YYYY-MM-DD格式)
- `Review`: 你写的短评

## 许可证

MIT

## 贡献

欢迎提交问题和改进建议!
