import re
import json
import aiohttp
import asyncio
import traceback
import requests
from datetime import datetime, timezone, timedelta

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81'}

def json_load(path):
    with requests.Session() as session:
        with session.get(path, headers=headers) as response:
            # Return list of json content
            return response.json()

# 发请求获取html文本
async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        return await response.text()

# 发请求获取html文本
async def fetch_post(session, url, data):
    async with session.post(url, data=data, headers=headers) as response:
        return await response.text()

# 解析html获取每组的列表页链接
async def parser(html, regex, match_index):
    regex_list = regex
    regex_list = re.compile(regex_list, re.S)
    res = re.findall(regex_list, html)
    for item in res:
        yield  {match_index[i] : item[i] for i in range(len(item))}


async def download(url):
    async with aiohttp.ClientSession() as session:
        try:
            html_text = await fetch(session, url['url'])
            print("\033[1;36m", '-'*30, url['url'], '-'*30, "\033[0m")
            arr = []
            async for item in parser(html_text, url['match'], url['match_index']):
                print("\033[1;36m", str(item), "\033[0m")
                arr.append(item)
            if url['post'] and len(arr):
                url['json'] = json.dumps(arr, ensure_ascii=False)
                html_text = await fetch_post(session, url['post'],url)
                print(f"\033[1;31m {html_text} \033[0m")
        except Exception as e:
            traceback.print_exc()


if __name__ == '__main__':
    start = datetime.now()
    arr = json_load('https://glds1024.serv00.net/urls.json')
    for url in arr:
        urls = json_load(url)
        if urls:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [asyncio.ensure_future(download(url), loop=loop) for url in urls]
            tasks = asyncio.gather(*tasks)
            loop.run_until_complete(tasks)
            loop.close()

    end = datetime.now()
    print("\033[1;32m", "Totally Time is %s" % (end - start), "\033[0m")
