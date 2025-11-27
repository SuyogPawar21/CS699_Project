import pandas as pd
from itertools import combinations
from collections import Counter
import networkx as nx
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json

def clean_keywords(x):
    if isinstance(x, str):
        x = x.replace("[", "").replace("]", "").replace('"', "")
        parts = [p.strip() for p in x.replace(";", ",").split(",")]
        return [p for p in parts if p]
    return []

def compute_keyword_cooccurrence(csv_path):
    """Compute keyword co-occurrence pairs """
    df = pd.read_csv(csv_path)
    # df['author'] = df['author'].apply(json.loads)
    # df['keywords'] = df['keywords'].apply(json.loads)
    df["clean_keywords"] = df["keywords"].apply(clean_keywords)
    pair_counter = Counter()

    for keyword_list in df["clean_keywords"]:
        pairs = combinations(sorted(set(keyword_list)), 2)
        pair_counter.update(pairs)

    print("Total co-occurring keyword pairs:",len(pair_counter))
    co_ocurrence_df = pd.DataFrame(
        [(kw1,kw2,count) for (kw1,kw2), count in pair_counter.items()],
        columns=["Keyword1","Keyword2","Cooccurrence"]
    )
    co_ocurrence_df = co_ocurrence_df.sort_values("Cooccurrence",ascending=False)
    return co_ocurrence_df

def plot_keyword_cooccurrence_heatmap(co_ocurrence_df,top_n=10,figsize=(16, 12),save_path="static/plots/keyword_heatmap.png"):
    """Plot and save an aesthetically improved heatmap of keyword co-occurrence."""
    freq = (co_ocurrence_df.groupby("Keyword1")["Cooccurrence"].sum() + co_ocurrence_df.groupby("Keyword2")["Cooccurrence"].sum())
    
    top_keywords = freq.sort_values(ascending=False).head(top_n).index.tolist()
    print(f"Using Top {top_n} Keywords:", top_keywords)
    matrix = pd.DataFrame(0, index=top_keywords, columns=top_keywords)

    for _, row in co_ocurrence_df.iterrows():
        k1, k2, count = row["Keyword1"],row["Keyword2"],row["Cooccurrence"]
        if k1 in top_keywords and k2 in top_keywords:
            matrix.loc[k1, k2] = count
            matrix.loc[k2, k1] = count
    sns.set_theme(style="white")

    plt.figure(figsize=figsize)
    cmap = sns.color_palette("crest",as_cmap=True)

    ax = sns.heatmap(
        matrix,
        annot=False,                 
        cmap=cmap,
        linewidths=0.3,
        linecolor="white",
        square=True,
        cbar_kws={
            "label": "Co-occurrence Frequency",
            "shrink": 0.8,
            "orientation": "vertical",
        }
    )
    plt.title(
        f"Top {top_n} Keyword Co-Occurrence Heatmap",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    plt.xticks(
        rotation=45,
        ha='right',
        fontsize=11
    )
    plt.yticks(fontsize=11)
    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Heatmap saved successfully {save_path}")

