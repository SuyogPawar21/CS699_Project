from scraping.keywords_gen import get_keywords
from scraping.sqlite_database import insert_paper
import arxiv
from datetime import date
from calendar import monthrange
import fitz
from keybert import KeyBERT
import os
import requests

def get_papers(quarter:int,year:int,keyword:str = None) -> list[dict]:
    """fetches papers from arXiv and returns a list of dict which contain the paper details"""
    quarter = str(quarter)
    if quarter not in ['1','2','3']:
        raise ValueError("Quarter must be '1', '2', '3'")
    
    if len(str(year)) != 4 or not str(year).isdigit():
        raise ValueError("Year must be a four-digit string, e.g., '2021'")

    if quarter == '1':
        start_month, end_month = 1,4
    elif quarter == '2':
        start_month, end_month = 5,8
    else:  #'3'
        start_month, end_month = 9, 12
    
    start_str = f"{str(year)}{start_month:02d}01"
    end_day = monthrange(year, end_month)[1]
    end_str = f"{str(year)}{end_month:02d}{end_day:02d}"
    date_query = f"submittedDate:[{start_str} TO {end_str}]"
    if keyword:
        query = f"{keyword} AND {date_query}"
    else:
        query = date_query
    
    papers = []
    try:
        search = arxiv.Search(query=query,max_results=3,sort_by=arxiv.SortCriterion.Relevance,sort_order=arxiv.SortOrder.Descending)
        for result in search.results():
            papers.append({'title': result.title,'authors': [author.name for author in result.authors],'summary': result.summary,'pdf_url': result.pdf_url,'published': result.published.isoformat() if result.published else None})
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return []
    return papers

def scrap_arxiv(quarter:int,year:int,table_name:str,input_string=None):
    """main function: puts paper details into database"""
    papers = get_papers(quarter,year,keyword=input_string)
    quarter = str(quarter)
    temporary_df = "temp_paper.pdf"
    count = 1
    for paper in papers:
        try:
            response = requests.get(paper['pdf_url'])
            response.raise_for_status()
            
            with open(temporary_df, 'wb') as f:
                f.write(response.content)
            keywords = get_keywords(temporary_df)
            insert_paper(name=paper['title'],author=paper['authors'],citations=0,keywords_list=keywords,table_name=table_name)
            print(f"\nInserted {count} papers into {table_name}\n")
            count = count + 1
            os.remove(temporary_df)
        except Exception as e:
            print(f"Error processing paper '{paper['title']}': {e}")
            if os.path.exists(temporary_df):
                os.remove(temporary_df)