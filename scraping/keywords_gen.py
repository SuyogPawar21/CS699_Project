import fitz
import pdfplumber
from io import BytesIO
from keybert import KeyBERT
from keybert import KeyBERT
import requests

def extract_first_page(pdf_path):
    document = fitz.open(pdf_path)
    return document[0].get_text()

def get_keywords(pdf_path):
    text_of_pdf = extract_first_page(pdf_path)
    model = KeyBERT("all-MiniLM-L6-v2")
    keywords = model.extract_keywords(text_of_pdf,top_n=10,keyphrase_ngram_range=(1,3))
    keywords_list = [x[0] for x in keywords]
    # print(keywords_list)
    return keywords_list
