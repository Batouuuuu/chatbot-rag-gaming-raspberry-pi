"""Scrapping the data from the league of legends fan page (vocabulary), 
the lore page, champions abilities,
the patch notes and the  and saving it into many csv"""

from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import requests
import csv
import os
import re
import time

def fetch_page(url: str, headers: Dict[str, str]) -> BeautifulSoup:
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, "html.parser") 
    return soup


### collecting lexic from the league page #######
def parse_lexic(html: BeautifulSoup) -> Dict[str, str]:
    """Extracts a dictionary of terms and their definitions from the parsed HTML."""
    lexic = {} 
    entry_div = html.find('div', class_='article-template__content page-width page-width--narrow rte scroll-trigger animate--slide-in')  
    p_balises = entry_div.find_all("p")
    for balise in p_balises:
        strong_tag = balise.find("strong")
        if strong_tag:
            word = strong_tag.get_text()
            texte_complet = balise.get_text().strip()
        
            cleaned_text = clean_parsing(texte_complet)
            cleaned_text = cleaned_text.replace('\xa0', ' ').strip()

            definition = cleaned_text.replace(f"{word}:", "").strip()
            lexic[word] = definition
    return lexic

def clean_parsing(text_parsed: str) -> str:
    """Clean unbreakable spaces and remove HTML tags"""
    cleaning_spaces = [':\xa0', '\xa0:', '\xa0:\xa0',' :', ': ', '  :', '\n']
    for pattern in cleaning_spaces:
        text_parsed = text_parsed.replace(pattern, ':')
    
    ##clean html tag
    text_parsed = re.sub(r'<.*?>', '', text_parsed)
    text_parsed = text_parsed.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return text_parsed.strip()

    
def save_data(lexic: Dict[str, str], filepath: str) -> None:
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Definition"])
        for word, definition in lexic.items():
            writer.writerow([word, definition])


###### collecting data from the lore page using selenium and Chrome driver (because page is loaded with js) ###################

class Champion:
    """Every league champion got a region, a sum up, a bio and a story"""  
    def __init__(self, name: str, region: str, sum_up: str, biography: str, story: str):
        self.name = name
        self.region = region
        self.sum_up = sum_up
        self.biography = biography
        self.story = story

    def __repr__(self):
        return f"Champion(name='{self.name}', region={self.region}, sum_up={self.sum_up}, biography={self.biography}, story={self.story})"

    @staticmethod
    def save_csv(filepath: os.PathLike, champions: List["Champion"]):
        """"""
        fields = ["Name", "Region", "SumUp", "Biography", "Story"]
        with open(filepath, 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fields)
            for champion in champions:
                writer.writerow([champion.name, champion.region, champion.sum_up, champion.biography, champion.story])


class PatchNote:
    """All the patch note from league page"""
    def __init__(self, number: str, sum_up: str, skins: str, content: str):
        self.number = number
        self.sum_up = sum_up
        self.skins = skins
        self.content = content

    def __repr__(self):
        return f"Patch(name='{self.number}',sum_up={self.sum_up},skins={self.skins},content={self.content}, )"

    @staticmethod
    def save_csv(filepath: os.PathLike, patch_list: List["PatchNote"]):
        fields = ["Number", "Sum_up", "Skins", "Content"]
        with open(filepath, "w", newline='', encoding="utf8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fields)
            for patch in patch_list:
                writer.writerow([patch.number, patch.sum_up, patch.skins, patch.content])

def get_champion_name(driver) -> List[str]:
    scroll_and_get_elements(driver, By.TAG_NAME, "h1") ## when the element appear on the page switch instantly
    champions_names = driver.find_elements(By.TAG_NAME, "h1")
    return [champion.text for champion in champions_names if champion.text != "CHAMPIONS"]  ## not taking the first h1 of the page because it's "CHAMPIONS" 
    

def get_region_name(driver: WebDriver) -> List[str]:
    scroll_and_get_elements(driver, By.TAG_NAME, "h2") 
    region_names = driver.find_elements(By.TAG_NAME, "h2")
    regions = [region.text for region in region_names]
    regions.pop(0) ## suppress the first h2 beacause it's empty
    return regions


def get_href_champions(driver: WebDriver ,url: str) -> List[str]:
    """Stock the hrefs"""
    driver.get(url)
    scroll_and_get_elements(driver, By.XPATH, "//a[contains(@href, '/fr_FR/champion/')]" )
    continue_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/fr_FR/champion/')]")
    hrefs = [el.get_attribute("href") for el in continue_links if el.get_attribute("href")]
    return hrefs
        
def get_sumup_champion(driver: WebDriver, urls_links: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """Opening the hrefs to go to the champion sumup and scrappin it"""
    sum_up_list = []
    list_biography = []
    list_story = []
    for link in tqdm(urls_links, total=len(urls_links), desc="Processing champion parsing"):
        driver.get(link)    
        texts = scroll_and_get_elements(driver, By.CLASS_NAME, "biographyText_3-to")
        joined_text = " ".join(el.text for el in texts) ##convert the selenium object into the element text
        sum_up_list.append(joined_text)
        list_biography.append(get_paragraph(driver))
        list_story.append(get_story(driver))
    # print(list_biography)
    return sum_up_list, list_biography, list_story

def get_paragraph(driver: WebDriver) -> str:
    """Go to the biography page of the champion and scrapping it"""

    try:
        continue_links = driver.find_element(By.XPATH, "//a[contains(@href, '/fr_FR/story/')]")
        jsp = continue_links.get_attribute("href")
        driver.get(jsp)
        time.sleep(10)
        liste = scroll_and_get_elements(driver , By.CLASS_NAME, "p_1_sJ")
        cleaned_paragraph = [clean_parsing(bio.get_attribute('innerHTML')) for bio in liste ] ##using the clean parsing fonction and innerHTML beacause of the js injection text
        return ' '.join(cleaned_paragraph) ## concat all the p mark
    
    except NoSuchElementException:
        print(f"No story found for: {driver.current_url}")
        return '' ## case where a champion doesn't have a history

def get_story(driver: WebDriver) -> str:
    """Navigates to the story page and scrapes it using get_paragraph"""
    return get_paragraph(driver)
    
def scroll_and_get_elements(driver: WebDriver, by, value, first: bool = False) -> None:
    """Optimisation for faster parsing on the page, scrolling down the page to avoid js lazy loading 
    and get the element immediately when it appears"""
    driver.execute_script("window.scrollTo(0, 250);") ## scrolling to avoid js lazyness loading
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((by, value))
        )

        if first:
            return driver.find_element(by, value)
        else:
            return driver.find_elements(by, value)
    except Exception as e:
        print(f"Erreur : {e}")
        return []

def fill_class_champion(driver: WebDriver, list_hrefs: List[str]) -> List[Champion]:
    """Store all the informations into a list of the Champion class"""   
    liste_champions_infos = [] 
    names = get_champion_name(driver)
    region = get_region_name(driver)
    list_sum_up_description, liste_bi, list_story  = get_sumup_champion(driver, list_hrefs)
    print(len(names), len(region), len(list_sum_up_description), len(liste_bi), len(list_story))
    for name, region, sum_up, bio, story in zip(names, region, list_sum_up_description, liste_bi, list_story):
        champion = Champion(name=name, region=region, sum_up=sum_up, biography=bio, story=story)
        liste_champions_infos.append(champion)
        
    #print(liste_champions_infos)
    return liste_champions_infos



######## patch notes ##############

def get_patchnote_urls(driver: WebDriver, url_page: List[str]) -> List[str]:
    """Stock all the url from the differents patchs"""
    driver.get(url_page)
    continue_links = scroll_and_get_elements(driver, By.XPATH, "//a[contains(@href, '/fr-fr/news/game-updates/')]" )
    hrefs = [el.get_attribute("href") for el in continue_links if el.get_attribute("href")]

    return hrefs

def get_name_patch(driver: WebDriver) -> List[str]:
    """"""
    liste_patch = []
    element = driver.find_elements(By.XPATH, "//div[@data-testid='card-title']")
    for el in element:
        patch = re.sub("Notes de patch", "", el.text).strip()
        liste_patch.append(patch)
    
    return liste_patch

def open_links(driver: WebDriver, list_hrefs: List[str]):
    all_patches = []
    all_skins = []
    all_champ_buffs = []
    for url in list_hrefs:
        driver.get(url)
        sum_up_patch = get_sum_up_patch(driver)
        all_patches.extend(sum_up_patch)
        skins = get_skin_update(driver)
        all_skins.extend(skins)
        champ_buffs = get_champion_nerf_and_buff(driver)
        all_champ_buffs.append(champ_buffs)
    
    return all_patches, all_skins, all_champ_buffs

def get_sum_up_patch(driver: WebDriver):
    element = scroll_and_get_elements(driver , By.CSS_SELECTOR, "blockquote.blockquote.context", first=True)
    if element and element.text.strip():  
        return [clean_parsing(element.text)]
    return []

def get_skin_update(driver: WebDriver):
    """"""
    ### generaly the skins update are in the first class white-stone accent-before 
    element = scroll_and_get_elements(driver , By.CSS_SELECTOR, ".white-stone.accent-before p", True)
    if element and element.text.strip():  
        return [clean_parsing(element.text)]
    return []

def get_champion_nerf_and_buff(driver: WebDriver) -> Dict[str, str]:
    """"""
    dict_champion = {}
    champion_elements = scroll_and_get_elements(driver, By.TAG_NAME, "h3")
    champion_names = [el.text for el in champion_elements]

    summary_elements = scroll_and_get_elements(driver, By.CLASS_NAME, "summary")
    summary_texts = [el.text for el in summary_elements]

    for champion, summary in zip(champion_names, summary_texts):
        dict_champion[champion] = summary

    return dict_champion

def fill_class_patch_note(list_patch_name: List[str], list_sum_up: List[str], list_skins: List[str], list_content_patch: List[Dict[str,str]]) -> List[PatchNote]:
    """"""
    list_of_all_patchs = []
    for patch_name, sump_up,skin, content in zip(list_patch_name, list_sum_up, list_skins, list_content_patch):
        list_of_all_patchs.append(PatchNote(number=patch_name,sum_up=sump_up,skins=skin,content=content)) 
    # print(list_of_all_patchs)
    return list_of_all_patchs



#### part for the champion abilities #######
""""""


def main():
    
    ## parsing with beautifulsoup for the dictionnary of definition
    RUN_PARSING_DEF = False
    RUN_PARSING_LORE = False

    if RUN_PARSING_DEF:
        headers = {"Accept-Encoding": "gzip",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
        lexic_url = "https://www.legends-path.com/blogs/legends-blog-league-of-legends/dictionnaire-des-termes-technique-de-league-of-legends-lol?srsltid=AfmBOorNHcOEI8cWRHyOtQUgGROP8n0hg1lxycIpVqigJ_iN9i8QQkzn"
        filepath = "./data/lexic.csv"
        lexic_page = fetch_page(lexic_url, headers)
        lexic = parse_lexic(lexic_page)
        save_data(lexic, filepath)
    
    ### for the lore page
    if RUN_PARSING_LORE:
        try:
            driver = webdriver.Chrome()
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=chrome_options)
            lore_url = "https://universe.leagueoflegends.com/fr_FR/champions/"
            liste_url = get_href_champions(driver, lore_url) 
            champions = fill_class_champion(driver, liste_url)
            Champion.save_csv("./data/lore.csv", champions) ##calling the static method to save into a csv
        finally:    
            driver.close()

    try:
        driver = webdriver.Chrome()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        patch_note_page = "https://www.leagueoflegends.com/fr-fr/news/tags/patch-notes/"
        liste_patch_url = get_patchnote_urls(driver, patch_note_page)
        patch_name_list = get_name_patch(driver)
        sum_up_patch_list, skin_list, content_patch = open_links(driver, liste_patch_url)
        patchs = fill_class_patch_note(patch_name_list, sum_up_patch_list, skin_list, content_patch)
        PatchNote.save_csv("./data/patchs.csv", patchs)
    finally:
        driver.close()
    

if __name__ == "__main__":
    main()