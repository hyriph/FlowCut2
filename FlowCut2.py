import json

import requests
from bs4 import BeautifulSoup
from fastapi import Request
from typing import List, Optional

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,  # Allow including cookies
    expose_headers=["Content-Disposition"],  # Expose specific headers if needed
)

dpu = open('download_post_url.txt', 'r', encoding='utf-8').read()

@app.post("/download")
async def download(input: str):
    url = dpu
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "input": input
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

    return response.json()


@app.get('/nyaa/search', tags=["Extractor"])
def nyaa(query: str, trusted: Optional[bool] = False):
    return sukebei_nyaa_search(site='nyaa', query=query, trusted=trusted)


@app.get('/sukebei/search', tags=["Extractor"])
def sukebei(query: str, trusted: Optional[bool] = False):
    return sukebei_nyaa_search(site='sukebei', query=query, trusted=trusted)


def sukebei_nyaa_search(site, query, trusted):
    query = query.replace(' ', '+')
    if site == 'nyaa':
        url = f'https://nyaa.si/?f=2&q={query}' if trusted else f'https://nyaa.si/?f=0&q={query}'
    elif site == 'sukebei':
        url = f'https://sukebei.nyaa.si/?f=2&q={query}' if trusted else f'https://sukebei.nyaa.si/?f=0&q={query}'

    res = requests.get(url)
    soup = BeautifulSoup(res.content, "lxml")

    tablediv = soup.find('div', class_='table-responsive')
    table = tablediv.find('table', class_='table')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')

    results = []

    for tr in trs:
        tds = tr.find_all('td')

        result = {
            'Category': tds[0].find('a')['title'],
            'Name': tds[1].find_all('a')[-1]['title'],
            'Link': tds[2].find_all('a')[-1]['href'],
            'Size': tds[3].get_text(),
            'Date': tds[4].get_text(),
            'Seeders': tds[5].get_text(),
            'Leachers': tds[6].get_text(),
            'Completed_downloads': tds[7].get_text()
        }

        results.append(result)

    return results

@app.get('/fc2/preview', tags=["Extractor"])
def get_preview(input: str):
    base_url = f'https://javstore.net/search/{input}.html'
    base_res = requests.get(base_url)
    base_soup = BeautifulSoup(base_res.content, "lxml")

    news_pageurl = base_soup.find('div', attrs={'id': 'content_news'})
    news_anchor = news_pageurl.find('a')
    news_href = news_anchor['href']
    news_res = requests.get(news_href)
    news_soup = BeautifulSoup(news_res.content, "lxml")

    page_news = news_soup.find('div', class_='news')
    if page_news.find('div', class_='first_des'):
        page_news.find('div', class_='first_des').decompose()
    if page_news.find('div', class_='fisrst_sc'):
        page_news.find('div', class_='fisrst_sc').decompose()
    if page_news.find('div', class_='Recipepod'):
        page_news.find('div', class_='Recipepod').decompose()
    if page_news.find('div', class_='highslide-gallery'):
        page_news.find('div', class_='highslide-gallery').decompose()


    page_anchor = page_news.find('a')


    page_href = page_anchor['href']
    print(page_href[-3:])
    if (page_href[-3:] == 'jpg'):
        return page_href
    page_res = requests.get(page_href)
    page_soup = BeautifulSoup(page_res.content, "lxml")

    cheveleto_div = page_soup.find('div', attrs={'id': 'image-viewer'})
    cheveleto_img = cheveleto_div.find('img')
    cheveleto_src = cheveleto_img['src']
    return cheveleto_src.replace('.md', '')


if __name__ == "__main__":
    uvicorn.run("FlowCut2:app", host="192.168.0.2", port=8000)