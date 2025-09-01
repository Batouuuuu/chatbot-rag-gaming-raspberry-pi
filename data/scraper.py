"""Extracting data from the league of legends fan page and the lore page, and saving it into csv"""

from typing import Dict
from bs4 import BeautifulSoup
import requests
import csv

def fetch_page(url: str, headers: Dict[str, str]) -> BeautifulSoup:
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser") 
    return soup



def parse_lexic(html: BeautifulSoup) -> Dict[str, str]:
    """Extracts a dictionary of terms and their definitions from the parsed HTML."""
    lexic = {} 
    entry_div = html.find('div', class_='article-template__content page-width page-width--narrow rte scroll-trigger animate--slide-in')  
    p_balises = entry_div.find_all("p")
    # print((p_balises))
    for balise in p_balises:
        strong_tag = balise.find("strong")
        if strong_tag:
            word = strong_tag.get_text()
            texte_complet = balise.get_text().strip()
            definition = texte_complet.replace(f"{word} :", "")
            definition = definition.replace('\xa0', ' ').strip()
            lexic[word] = definition
    return lexic

def save_data(lexic: Dict[str, str], filepath: str) -> None:
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Definition"])
        for word, definition in lexic.items():
            writer.writerow([word, definition])


def main():
    
    headers = {"Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    url = "https://www.legends-path.com/blogs/legends-blog-league-of-legends/dictionnaire-des-termes-technique-de-league-of-legends-lol?srsltid=AfmBOorNHcOEI8cWRHyOtQUgGROP8n0hg1lxycIpVqigJ_iN9i8QQkzn"
    filepath = "./data/words.csv"
    html = fetch_page(url, headers)
    lexic = parse_lexic(html)
    print(lexic)
    save_data(lexic, filepath)


if __name__ == "__main__":
    main()