"""Scrapping the data from the league of legends fan page (vocabulary), 
the lore page, champions abilities,
the patch notes and the  and saving it into many csv"""

from typing import Dict, List
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import csv
import time

def fetch_page(url: str, headers: Dict[str, str]) -> BeautifulSoup:
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser") 
    return soup


### collecting lexic from the league page 
def parse_lexic(html: BeautifulSoup) -> Dict[str, str]:
    """Extracts a dictionary of terms and their definitions from the parsed HTML."""
    lexic = {} 
    entry_div = html.find('div', class_='article-template__content page-width page-width--narrow rte scroll-trigger animate--slide-in')  
    p_balises = entry_div.find_all("p")
    
    for balise in p_balises:
        strong_tag = balise.find("strong")
        print(strong_tag)
        if strong_tag:
            word = strong_tag.get_text()
            texte_complet = balise.get_text().strip()
            
            cleaned_text = clean_parsing(texte_complet)
            cleaned_text = cleaned_text.replace('\xa0', ' ').strip()

            definition = cleaned_text.replace(f"{word}:", "").strip()
            lexic[word] = definition
    return lexic

def clean_parsing(text_parsed: str) -> str:
    """Clean all the unbreakable spaces"""
    cleaning_spaces = [':\xa0', '\xa0:', '\xa0:\xa0',' :', ': ', '  :']
    for pattern in cleaning_spaces:
        text_parsed = text_parsed.replace(pattern, ':')
    return text_parsed.strip()

    
def save_data(lexic: Dict[str, str], filepath: str) -> None:
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Definition"])
        for word, definition in lexic.items():
            writer.writerow([word, definition])


#### collecting data from the lore page using selenium and Chrome driver (because page is loaded with js)
def get_href_champions(driver ,url: str) -> Dict[str, str]:


    champions_infos = {"name": " ",
                       "region": " ",
                       "sumup": " ",
                       "bio": " ",
                       "story": " "}
    
    """Stock the hrefs (urls) of the champions and their name into a dict"""
    driver.get(url)
    time.sleep(5) ## wainting to load entirely the page
    continue_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/fr_FR/champion/')]")
    hrefs = [el.get_attribute("href") for el in continue_links if el.get_attribute("href")]
    # print(f"{len(continue_links)} liens trouvés :")
    # for link in continue_links:
    #     href = link.get_attribute('href')
    #     print(href)
    get_sumup_champion(driver, hrefs)

    # champions_names = driver.find_elements(By.TAG_NAME, "h1")
    # print(f"{len(champions_names)} champions trouvés")
    # champions_names.pop(0) ## deleting the first h1  

    # for (name, link) in enumerate (zip(champions_names, continue_links)):
    #     champions_infos["name"] = name.text
    #     champions_infos["region"] = link.get_attribute('href')

    # print(champions_infos)

    
    
def get_sumup_champion(driver, urls_links: List[str]):
     
    for link in urls_links:
        driver.get(link)
    
        sum_up = driver.find_element(By.CLASS_NAME, "biographyText_3-to")
      
        try:
            ## we need to wait the element to be loaded
            sum_up_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "biographyText_3-to"))
            )

            print(sum_up_element.text)

        except Exception as e:
            print(f"Erreur sur {link} : {e}")
        
   
def get_biography():
    """
    
    
    
    """
#### champion abilities 




#### patch notes 



def main():
    
    headers = {"Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    lexic_url = "https://www.legends-path.com/blogs/legends-blog-league-of-legends/dictionnaire-des-termes-technique-de-league-of-legends-lol?srsltid=AfmBOorNHcOEI8cWRHyOtQUgGROP8n0hg1lxycIpVqigJ_iN9i8QQkzn"
    # filepath = "./data/lexic.csv"
    # lexic_page = fetch_page(lexic_url, headers)
    # lexic = parse_lexic(lexic_page)
    # print(lexic)
    # save_data(lexic, filepath)
    

    # lore_page = fetch_page(tt, headers)
    # print(lore_page)
    driver = webdriver.Chrome()
    # chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    # driver = webdriver.Chrome(options=chrome_options)
    
    lore_url = "https://universe.leagueoflegends.com/fr_FR/champions/"
    get_href_champions(driver, lore_url) 
    driver.close()
    

if __name__ == "__main__":
    main()