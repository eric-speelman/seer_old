import requests
from bs4 import BeautifulSoup
import os.path

cache_path = "../cache/"

def collect(url, ignore_cache = False, retry = 3):
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)
    path = cache_path + url.replace('http://', '').replace('https://', '').replace('/', '_').replace('.', '_')
    html = None
    cache_hit = False
    if not ignore_cache and os.path.exists(path):
        cache_hit = True
        with open(path, 'r', encoding='utf-8') as file:
            html = file.read()
    if html == None:
        try:
            res = requests.get(url)
        except:
            if retry > 0:
                collect(url, ignore_cache, retry - 1)
            else:
                raise Exception(f'An error occured while trying to retrieve {url}')
        if res.status_code < 200 or res.status_code >= 300:
            return None
        html = res.text
        html.replace('<!--', '').replace('-->', '')
    if not ignore_cache and not cache_hit:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(html)
    if html == '':
        return None
    return BeautifulSoup(html, 'html.parser')