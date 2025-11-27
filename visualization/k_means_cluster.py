import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np
import json

def k_means_cluster():
    """main function, saves results in csv file and returns the cluster df."""
    df = pd.read_csv("files/Final_Data.csv")
    print("Total papers:",len(df))
    df["clean_keywords"] = df["keywords"].apply(json.loads)
    def embed_keywords(keyword_list,model):
        if len(keyword_list) == 0:
            return model.encode([""], show_progress_bar=False)[0]

        emb = model.encode(keyword_list,show_progress_bar=False)
        return emb.mean(axis=0)

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    embeddings = df["clean_keywords"].apply(lambda keyword: embed_keywords(keyword,model))
    X = np.vstack(embeddings.values)
    print("Embedding shape:", X.shape)

    k = 3 
    kmeans = KMeans(n_clusters=k,random_state=42)
    df["cluster"] = kmeans.fit_predict(X)
    print("Clusters assigned successfully!")
    score = silhouette_score(X,df["cluster"])
    print("Silhouette Score:", score)
    df.to_csv("files/paper_clusters.csv",index=False)
    print("Saved output to paper_clusters.csv")
    return df
