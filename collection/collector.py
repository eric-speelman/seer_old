import requests
from bs4 import BeautifulSoup
import os.path

cache_path = "../cache/"

def collect(url, ignore_cache = False):
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)
    path = cache_path + url.replace('http://', '').replace('https://', '').replace('/', '_').replace('.', '_')
    html = None
    if not ignore_cache and os.path.exists(path):
        file = open(path, 'r')
        html = file.read()
        file.close()
    if html == None:
        res = requests.get(url = "https://www.basketball-reference.com/")
        html = res.text
    if not ignore_cache:
        file = open(path, 'w')
        file.write(html)
        file.close()
    return BeautifulSoup(html, 'html.parser')