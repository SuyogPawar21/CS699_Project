import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

plt.switch_backend("Agg")

def author_trends_plots(csv_path,out_dir="static/plots"):
    os.makedirs(out_dir,exist_ok=True)
    df = pd.read_csv(csv_path)
    df['author'] = df['author'].apply(json.loads)
    df['keywords'] = df['keywords'].apply(json.loads)
    df["authors_list"] = df["author"].astype(str).apply(lambda x: [a.strip() for a in x.split(",") if a.strip()])
    df["cit_int"] = df["citations"].apply(lambda x: int(str(x).strip().replace(",", "") or 0))
    author_pop = {}
    for _, r in df.iterrows():
        for a in r["authors_list"]:
            author_pop[a] = author_pop.get(a, 0) + r["cit_int"]
    df["author_pop"] = df["authors_list"].apply(lambda lst: sum(author_pop.get(a, 0) for a in lst))

    def norm(s):
        s = s.astype(float)
        if s.max() == s.min():
            return s / (s.max() or 1)
        return (s - s.min()) / (s.max() - s.min())

    df["nc"] = norm(df["cit_int"])
    df["na"] = norm(df["author_pop"])
    df["composite"] = 0.6 * df["nc"] + 0.4 * df["na"]
    df = df.sort_values("composite", ascending=False).reset_index(drop=True)
    out_csv = os.path.join(out_dir,"top_papers_composite.csv")
    df.to_csv(out_csv, index=False)
    saved = []

    def short_label(title,author,max_len=60):
        """Shortens long paper titles for prettier plots."""
        title = title.strip()
        if len(title) > max_len:
            title = title[:max_len - 3] + "..."
        return f"{title} — {author}"

    top = df.head(15)
    fig, ax = plt.subplots(figsize=(14,10)) 
    ax.barh(top.index[::-1], top["composite"][::-1], color="#1976d2")
    ax.set_yticks(top.index[::-1])
    labels = [short_label(row["name"], row["authors_list"][0]) for _, row in top.iloc[::-1].iterrows()]
    ax.set_yticklabels(labels,fontsize=10)
    ax.set_title("Top Papers (Composite Score)",fontsize=16,pad=20)
    ax.set_xlabel("Composite Score",fontsize=12)
    plt.subplots_adjust(left=0.45,right=0.95,top=0.92,bottom=0.05)
    plt.tight_layout()
    p1 = os.path.join(out_dir,"top_papers_by_composite.png")
    plt.savefig(p1,dpi=160)
    plt.close(fig)
    saved.append(os.path.basename(p1))