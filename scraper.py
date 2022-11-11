from bs4 import BeautifulSoup
import multiprocessing
import requests
import sqlite3
import sys
import time

class Artifact:
    def __init__(self, accession_num, name, date, url, img_urls) -> None:
        self.accession_num = accession_num
        self.name = name
        self.date = date
        self.url = url
        self.img_urls = img_urls

    def tuple(self):
        return self.accession_num, self.name, self.date, self.url, ','.join(self.img_urls)


def process_page(page_num):
    page = requests.get('https://www.agakhanmuseum.org/collection?page=' + str(page_num))
    page.raise_for_status()
    soup = BeautifulSoup(page.text, 'html.parser')
    items = soup.select('#events > div > div')
    return list(items)

def get_artifact_data(artifact):
    url = str('https://www.agakhanmuseum.org' + artifact.select_one('div > a')['href']).strip()
    name = str(artifact.select_one('div > a')['aria-label']).strip()

    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, 'html.parser')

    accession_num = str(soup.find(string='Accession Number:').parent.nextSibling).strip()
    date = str(soup.find(string='Date:').parent.nextSibling).strip()

    img_urls = [str('https://www.agakhanmuseum.org' + u['src']) for u in soup.select('.image-popup > img')]

    return Artifact(accession_num, name, date, url, img_urls)

sys.setrecursionlimit(10000)
if __name__ == '__main__':
    p = multiprocessing.Pool(10)
    start = time.time()
    print('Starting scraper...')
    with multiprocessing.Pool(10) as p:
        pages = p.map(process_page, range(1,41))
        artifacts = p.map(get_artifact_data, [a for p in pages for a in p])
    end = time.time()
    print('Scraping completed. Elapsed time:', end - start)

    ca = [a for a in artifacts if len(a.img_urls) == 1] # less than ideal
    con = sqlite3.connect('akmbot.db')
    cur = con.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS artifacts(accession_num PRIMARY KEY, name, date, url, img_urls)')

    cur.executemany('INSERT OR IGNORE INTO artifacts VALUES(?, ?, ?, ?, ?)', [a.tuple() for a in ca]) 
    con.commit()