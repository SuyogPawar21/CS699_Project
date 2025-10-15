as part of our project we have scrap three websites and in this part i have scrap ieee website using selenium and beautifulsoup as webpages are client side executing i have used selenium WebDriverWait() method to wait till time we get html parse page of that javascript page then once we get html parse page then we can simply scrap it using beautifulsoup also pages were too complicated so what i did is first i took the links and names of conference papers then once i have link in one array (instead of getting driver everytime inside that link then doing driver.back() which will take more time) then i visit that page get all metadata that i need then i direclty cutt down the connection as i dont need it anymore.similaryly i visit all pages and get all metadata that i need.

'''python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import pandas as pd

Paper_Name = []
Paper_Author = []
Paper_Citations = []
Paper_Keywords = []


chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)


driver.get("https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:newest%20papers)&highlight=true&returnType=SEARCH&matchPubs=true&sortType=paper-citations&ranges=20250101_20250430_Search%20Latest%20Date&returnFacets=ALL&refinements=ContentType:Conferences")

url = "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=(%22All%20Metadata%22:newest%20papers)&ranges=20250101_20251006_Search%20Latest%20Date&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&rowsPerPage=25&openAccess=true"

# wait until at least one paper title loads
element = WebDriverWait(driver, 15, poll_frequency=0.2).until(
    EC.presence_of_element_located((By.CLASS_NAME, "fw-bold"))
)


soup = BeautifulSoup(driver.page_source, "html.parser")

paper_links = []
paper_tags = soup.find_all("a", class_="fw-bold")
for a in paper_tags:
    full_link = "https://ieeexplore.ieee.org" + a["href"] #https://ieeexplore.ieee.org/document/10951154
    paper_links.append((full_link, a.text.strip()))

# print(paper_links,"\n")
count = 1
for link, title in paper_links:
    if(count == 10):
        break
    driver.get(link)
    # Wait until at least one dropBlock element is present
    try:
        element = WebDriverWait(driver, 10,poll_frequency=0.2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "col-24-24"))
        )
    except TimeoutException:
        print("Its Timeout1")
        continue

    Paper_Name.append(title)

    inner_soup = BeautifulSoup(driver.page_source, "html.parser")

    #Extracting authors
    authors = []
    all_author_span = inner_soup.select('a[href^="/author/"] span')
    for span in all_author_span:
        name = span.text.strip()
        authors.append(name)
    
    
    Paper_Author.append(authors)

    #Extracting Citations value
    metric_div = inner_soup.select_one('div.document-banner-metric-count')
    value = 0
   
    value = metric_div.text.strip()
    Paper_Citations.append(value)

    #Extraction of Keywords
    keywords = []
    keyword_link = link + "keywords"
    driver.get(keyword_link)

    # Wait for keyword elements to appear
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.stats-keywords-list-item"))
        )
    except TimeoutException:
        print("\nTimeout 2\n")
        Paper_Keywords.append(keywords)
        continue

    inner_inner_soup = BeautifulSoup(driver.page_source, "html.parser")
    keyword_anchors = inner_inner_soup.select("a.stats-keywords-list-item")

    keywords = [a.get_text(strip=True) for a in keyword_anchors]
    
    Paper_Keywords.append(keywords)

    print("count--> ",count,"\n")
    count = count + 1

driver.quit()

df = pd.DataFrame({"Paper Name": Paper_Name, "Paper Author": Paper_Author,"Paper Citations":Paper_Citations,"Paper Keywords":Paper_Keywords})
df.to_csv("metadata.csv", index=False)
'''