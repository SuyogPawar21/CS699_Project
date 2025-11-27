from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime
import calendar
import pandas as pd
from scraping.sqlite_database import insert_paper



def input_string_format(input_string):
    result = "%20".join(input_string.split())
    return result

def input_date_format(year,quarter):
    first_month = (quarter - 1) * 3 + 1
    last_month  = first_month + 2
    start_date = datetime.date(year, first_month, 1)
    last_day = calendar.monthrange(year, last_month)[1]
    end_date = datetime.date(year, last_month, last_day)
    start_date_string = start_date.strftime("%Y%m%d")
    end_date_string = end_date.strftime("%Y%m%d")
    return start_date_string,end_date_string

def scrap_ieee(quarter,year,table_name,input_string):
    search = "Newest%20papers"
    if(input_string):
        search = input_string_format(input_string)
    start_date,end_date = input_date_format(year,quarter)
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:{search})&highlight=true&returnType=SEARCH&matchPubs=true&openAccess=true&sortType=paper-citations&ranges={start_date}_{end_date}_Search%20Latest%20Date&returnFacets=ALL&rowsPerPage=25&pageNumber=1"
    driver.get(url)
    element = WebDriverWait(driver, 15, poll_frequency=0.2).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fw-bold"))
    )
    soup = BeautifulSoup(driver.page_source,"html.parser")
    paper_links = []
    paper_block = soup.find_all("a", class_="fw-bold")
    for link_tag in paper_block:
        full_link = "https://ieeexplore.ieee.org" + link_tag["href"]
        paper_links.append((full_link,link_tag.text.strip()))

    count = 1
    for link, title in paper_links:
        if(count==2):
            driver.quit()
            break
        driver.get(link)
        try:
            WebDriverWait(driver,10,poll_frequency=0.2).until(
                EC.presence_of_element_located((By.CLASS_NAME,"col-24-24"))
            )
        except TimeoutException:
            print("Its Timeout1")
            continue

        Paper_Name = title                                  #<-- title

        inner_soup = BeautifulSoup(driver.page_source,"html.parser")
        authors = []
        all_author_span = inner_soup.select('a[href^="/author/"] span')
        for span in all_author_span:
            name = span.text.strip()
            authors.append(name)
        Paper_Author = authors                              #<--Authors
        metric_div = inner_soup.select_one('div.document-banner-metric-count')
        value = 0
        value = metric_div.text.strip()
        Paper_Citations = value                             #<--Citations
        keywords = []
        keyword_link = link + "keywords"
        driver.get(keyword_link)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,"a.stats-keywords-list-item"))
            )
        except TimeoutException:
            print("\nTimeout 2\n")
            Paper_Keywords.append(keywords)
            continue

        inner_inner_soup = BeautifulSoup(driver.page_source,"html.parser")
        keyword_anchors = inner_inner_soup.select("a.stats-keywords-list-item")

        keywords = [a.get_text(strip=True) for a in keyword_anchors]
        Paper_Keywords = keywords                           #<--keywords
        ###################### Database Insertion #####################
        count = count + 1
        insert_paper(name=Paper_Name,author=Paper_Author,citations=Paper_Citations,keywords_list=Paper_Keywords,table_name=table_name)
        print(f"\nInserted {count} papers into {table_name}\n")
    driver.quit()
