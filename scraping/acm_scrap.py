from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import requests
import time
from scraping.sqlite_database import insert_paper
from scraping.keywords_gen import get_keywords
import json
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd


def input_string_format(input_string):
    result = "+".join(input_string.strip().split())
    return result

def scrap_acm(quarter,year,table_name,input_string):
    search = "newest+papers"
    if(input_string):
        print("Search Input Given\n")
        search = input_string_format(input_string)
    if(quarter == 1):
        start_date = 1
        end_date = 4
    elif(quarter == 2):
        start_date = 5
        end_date = 8
    else:
        start_date = 9
        end_date = 12

    count = 1
    for index in range(0,16):
        print("\n################  Current paper number in acm --> ",count,"  ##################\n")
        # url = f"https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl&field1=AllField&text1={search}&AfterMonth={start_date}&AfterYear={year}&BeforeMonth={end_date}&BeforeYear={year}&sortBy=cited&startPage={index}&pageSize=10"
        url = f"https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl&field1=AllField&text1={search}&AfterMonth={start_date}&AfterYear={year}&BeforeMonth={end_date}&BeforeYear={year}&startPage=0&ContentItemType=research-article&sortBy=cited&pageSize=20"       
        driver = uc.Chrome()
        driver.get(url)
        try:
            input_element = WebDriverWait(driver, 15,poll_frequency=0.2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hlFld-Title"))
            )
            print("Element found:", input_element.text)

        except TimeoutException:
            print("Element with class hlFld-Title not found so skipping this iteration")

        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")

        paper_links = []
        paper_spans = soup.find_all("span", class_="hlFld-Title")

        for span in paper_spans:
            a_link = span.find("a")
            if a_link and a_link.get("href"):
                full_link = "https://dl.acm.org" + a_link["href"]
                paper_links.append((full_link, a_link.text.strip()))

        for link, title in paper_links:
            if(count == 1):
                driver.quit()
            count = count +1
            driver.get(link)
            try:
                WebDriverWait(driver,5,poll_frequency=0.2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dropBlock"))
                )
            except TimeoutException:
                continue

            Paper_Name = title                                                           #<-- Title
            ###################
            inner_soup = BeautifulSoup(driver.page_source, "html.parser")
            authors = []
            drop_blocks = inner_soup.find_all("span", class_="dropBlock")
            for block in drop_blocks:
                a_block = block.find("a")  
                if a_block and a_block.get("title"):
                    authors.append(a_block["title"])

            Paper_Author = authors                                                      # <-- Authors
            ####################
            value_block = inner_soup.find("div",class_="article-metric citation")
            if(value_block):
                span_block = value_block.find("span")
                if(span_block):
                    citation_value = span_block.text.strip()
                else:
                    citation_value = 0

            Paper_Citations = citation_value                                           #<-- Citation value
            #####################
            headers = {
                "User-Agent": driver.execute_script("return navigator.userAgent;"),
                "Referer": pdf_link,
                "Accept": "application/pdf",
            }
            pdf_link = inner_soup.find("a", class_="btn btn--eReader blue")["href"]
            pdf_link = "https://dl.acm.org" + pdf_link
            print(f"\n acm paper {count} -> {pdf_link}\n")        
            driver.get(pdf_link)
            time.sleep(1.2)
            selenium_cookies = driver.get_cookies()
            session = requests.Session()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            conn = session.get(pdf_link, headers=headers)                   #<-- download pdf
            print("Status:", conn.status_code)
            if conn.status_code == 200:
                with open("scraping/downloaded_paper.pdf", "wb") as pdf:
                    pdf.write(conn.content)
                print("\n########### PDF Downloaded Successfully! ################\n")
            else:
                print("\n########### Download Failed ################\n")
            driver.back()

            keywords = get_keywords("scraping/downloaded_paper.pdf")                    #<-- Keywords
            ######################### DataBase Insertion ##################################
            insert_paper(name=Paper_Name, author=Paper_Author, citations=Paper_Citations, keywords_list=keywords,table_name=table_name)
            print(f"\nInserted {count} papers into {table_name}\n")
        driver.quit()

