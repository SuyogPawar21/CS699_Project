This week for project progress we have done Web scraping of conference website acm. we face some issues like when we try to scrap acm website using requests and beautifulsoup it dosent give us 200 response so,
I am using Selenium and undetected chromedriver instead of BeautifulSoup because:
    ⏩The ACM search page loads content dynamically using JavaScript.
    ⏩requests.get() or BeautifulSoup alone can only fetch static HTML.
    The list of newest papers is populated after the page loads via JavaScript (AJAX).
    ⏩Cloudflare bot protection can detect and block automated browsers; Selenium alone is often detected and does not reliably bypass Cloudflare, so I use undetected_chromedriver to run a Chrome instance that is harder for Cloudflare to flag.



```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd

Paper_Name = []
Paper_Author = []
Paper_Citations = []
Paper_Keywords = []

quarter = int(input("Enter Quarter of Year--> "))
year = int(input("Enter Year--> "))

if(quarter == 1):
    start_date = 1
    end_date = 4
elif(quarter == 2):
    start_date = 5
    end_date = 8
else:
    start_date = 9
    end_date = 12

url = f"https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl&field1=AllField&text1=newest+papers&AfterMonth={start_date}&AfterYear={year}&BeforeMonth={end_date}&BeforeYear={year}&sortBy=cited"

driver = uc.Chrome()
driver.get(url)

# Wait until at least one paper title is loaded
try:
    element = WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hlFld-Title"))
    )
    print("Element found:", element.text)

except TimeoutException:
    print("Element with class hlFld-Title not found → skipping this iteration")

html = driver.page_source
soup = BeautifulSoup(html, features="html.parser")

#Collect all paper links and titles
paper_links = []
paper_spans = soup.find_all("span", class_="hlFld-Title")

for span in paper_spans:
    a_tag = span.find("a")
    if a_tag and a_tag.get("href"):
        full_link = "https://dl.acm.org" + a_tag["href"]
        paper_links.append((full_link, a_tag.text.strip()))

# Visit each link to extract authors
for link, title in paper_links:
    driver.get(link)

    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dropBlock"))
        )

    except TimeoutException:
        continue

    Paper_Name.append(title)
    inner_soup = BeautifulSoup(driver.page_source, "html.parser")

    authors = []
    drop_blocks = inner_soup.find_all("span", class_="dropBlock")
    for block in drop_blocks:
        a_tag = block.find("a")  # get the <a> inside span
        if a_tag and a_tag.get("title"):
            authors.append(a_tag["title"])  # get the title attribute

    Paper_Author.append(authors)

    #########################
    citation_value = None
    contributors_link = link + "#tab-contributors"
    driver.get(contributors_link)

    metric_link = link + "#tab-metrics-inner"
    driver.get(metric_link)

    metric_soup = BeautifulSoup(driver.page_source,features="html.parser")
    metric_div = metric_soup.find("div",class_="metric-value")
    citation_value = metric_div.text.strip()
    driver.back()
    driver.back()

    Paper_Citations.append(citation_value)

driver.quit()

# Create DataFrame
df = pd.DataFrame({"Paper Name": Paper_Name, "Paper Author": Paper_Author,"Paper Citations":Paper_Citations})
print(df)
```


