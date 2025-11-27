import pandas as pd
from io import StringIO
import ast
import numpy as np
import itertools
from collections import defaultdict
import json
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity


def keyword_embedding(keywords,model):
    embeddings = model.model.embed(keywords)
    return embeddings

def cosine_similarity_matrix(A,B):
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
    return np.dot(A_norm, B_norm.T)

def keyword_similarity_summary():
    df = pd.read_csv("files/Final_Data.csv")
    df['author'] = df['author'].apply(json.loads)
    df['keywords'] = df['keywords'].apply(json.loads)

    model = KeyBERT(model='all-MiniLM-L6-v2')
    TOP_N = 5                                                  
    final_results = []
    for (_,row1), (_,row2) in itertools.combinations(df.iterrows(),2):
        keyword1 = row1["keywords"]      
        keyword2 = row2["keywords"]      
        emb1 = keyword_embedding(keyword1,model)
        emb2 = keyword_embedding(keyword2,model)
        sim_matrix = cosine_similarity_matrix(emb1, emb2)
        pairs = []
        for id_x1, k1 in enumerate(keyword1):
            for id_x2, key2 in enumerate(keyword2):
                sim = float(sim_matrix[id_x1][id_x2])
                pairs.append((k1, key2, sim))

        top_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)[:TOP_N]
        for key1, key2, sim in top_pairs:
            final_results.append({"paper1_id": row1["id"],"paper2_id": row2["id"],"paper1_name": row1["name"],"paper2_name": row2["name"],"keyword1": key1,"keyword2": key2,"similarity": sim})
    
    paper_groups = defaultdict(list)
    for values in final_results:
        paper_groups[values["paper1_id"]].append(values)

    paper_summary = []
    for paper_id, values in paper_groups.items():
        partner_groups = defaultdict(list)
        for it in values:
            partner_groups[it["paper2_id"]].append(it)
        unique_keywords = []
        mean_sim_values = []
        for partner_id, pairs in partner_groups.items():
            sims = [p["similarity"] for p in pairs]
            mean_sim = float(np.mean(sims))   
            mean_sim_values.append(mean_sim)
            chosed_keyword = pairs[0]["keyword1"]
            unique_keywords.append(chosed_keyword)

        unique_keywords = list(dict.fromkeys(unique_keywords))
        final_mean = float(np.mean(mean_sim_values)) if mean_sim_values else 0.0
        paper_summary.append({"paper_id": paper_id,"keywords": unique_keywords,"mean_similarity": final_mean})
    print(paper_summary)
    df_summary = pd.DataFrame(paper_summary)
    df_summary['name'] = df_summary['paper_id'].map(df.set_index('id')['name'])
    df_summary["keywords"] = df_summary["keywords"].apply(lambda x: ", ".join(x))
    df_summary = df_summary.sort_values(by="mean_similarity",ascending=False)

    mean_vals = df_summary["mean_similarity"].values
    exp_vals = np.exp(mean_vals - np.max(mean_vals))   
    softmax_vals = exp_vals / np.sum(exp_vals)
    df_summary["similarity_percent"] = softmax_vals * 100

    df_summary.to_csv("files/paper_keyword_summary.csv",index=False)
    return df_summary



