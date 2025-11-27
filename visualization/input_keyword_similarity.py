import pandas as pd
import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util

def compute_keyword_paper_similarity(df_summary,input_keyword,top_n_expand=5):
    """returns df of similarity between papers"""

    embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    model = KeyBERT(embed_model)
    df = df_summary  
    df["keywords"] = df["keywords"].apply(lambda x: [k.strip() for k in x.split(",")])

    def expand_keyword(input_text,top_n=5):
        kws = model.extract_keywords(input_text, top_n=top_n)
        return [kw for kw, score in kws]

    def similarity_to_papers(input_keyword,df,top_n_expand=5):
        expanded_keywords = expand_keyword(input_keyword, top_n_expand)
        expanded_embs = embed_model.encode(expanded_keywords, convert_to_tensor=True)
        results = []

        for _, row in df.iterrows():
            paper_id = row["paper_id"]
            paper_keywords = row["keywords"]
            paper_embs = embed_model.encode(paper_keywords, convert_to_tensor=True)
            sim_matrix = util.cos_sim(expanded_embs, paper_embs)
            max_sim = float(np.max(sim_matrix.cpu().numpy()))

            results.append({"paper_id": paper_id,"expanded_keywords": expanded_keywords,"paper_keywords": paper_keywords,"max_similarity": max_sim})
        return results

    results = similarity_to_papers(input_keyword,df,top_n_expand)
    out_df = pd.DataFrame(results)
    out_df = out_df.sort_values(by="max_similarity",ascending=False)
    return out_df