import os
import sqlite3
import uuid
import time
from threading import Thread
from datetime import datetime
from flask import Flask,render_template,request,redirect,url_for,flash,jsonify
import pandas as pd
import json
from plots import keyword_summary_plot
from visualization import *
from scraping.sqlite_database import merge_tables
from scraping.acm_scrap import scrap_acm
from scraping.ieee_scrap import scrap_ieee
from scraping.arxiv_scrap import scrap_arxiv
from visualization import keyword_summary, k_means_cluster
from visualization.authors_citations_impact import author_trends_plots
from visualization.cooccurance import compute_keyword_cooccurrence,plot_keyword_cooccurrence_heatmap
from visualization.input_keyword_similarity import compute_keyword_paper_similarity
from threading import Thread
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "vst25m211025m211625m2117"
pipeline_state = {"step1": False,"step2": False,"step3": False,"step4": False,"step5": False,"message": "Idle","error": None}

last_search_keyword = ""
df_k_means = None

def reset_pipeline_state():
    """Reset pipeline flags before running."""
    for key in pipeline_state:
        if key.startswith("step"):
            pipeline_state[key] = False
    pipeline_state["message"] = "Idle"
    pipeline_state["error"] = None


def update_pipeline(step=None,message=None,error=None):
    """General function to update pipeline progress."""
    if step:
        pipeline_state[f"step{step}"] = True
    if message:
        pipeline_state["message"] = message
    if error:
        pipeline_state["error"] = error


def run_scraping_threads(quarter,year,tables,keyword):
    """Start scraping threads for ACM, IEEE, arXiv."""
    jobs = [(scrap_acm,tables["acm"]),(scrap_ieee,tables["ieee"]),(scrap_arxiv,tables["arxiv"])]
    threads = []
    for fn, tb in jobs:
        t = Thread(target=fn,args=(quarter, year, tb, keyword))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

def run_full_pipeline(quarter,year,tables,keyword):
    global last_search_keyword, df_k_means
    last_search_keyword = keyword
    try:
        update_pipeline(step=1,message="Request accepted. Starting pipeline...")


        update_pipeline(message="Fetching data from ACM, IEEE, arXiv...")
        run_scraping_threads(quarter, year, tables, keyword)
        update_pipeline(step=2,message="Scraping finished. Merging tables...")

        merge_tables(tables["final_table"],[tables["acm"], tables["ieee"], tables["arxiv"]])
        update_pipeline(step=3,message="Database prepared. Creating plots...")


        df_summary = keyword_summary.keyword_similarity_summary()
        keyword_summary_plot(df_summary)
        author_trends_plots("files/Final_Data.csv",out_dir="static/plots")
        cooc_df = compute_keyword_cooccurrence("files/Final_Data.csv")
        plot_keyword_cooccurrence_heatmap(cooc_df)
        df_k_means = k_means_cluster.k_means_cluster()
        update_pipeline(step=4,message="Visualizations created.")


        update_pipeline(step=5,message="Pipeline complete. Ready for results.")

    except Exception as e:
        update_pipeline(message="Pipeline failed due to an error.",error=str(e))

@app.route("/")
def index():
    return render_template("index.html",current_year=datetime.now().year)

@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword", "").strip()
    quarter = int(request.form.get("quarter",0))
    year = int(request.form.get("year",0))

    if not keyword:
        flash("Keyword is required","danger")
        return redirect(url_for("index"))

    if quarter not in (1, 2, 3):
        flash("Quarter must be between 1 and 3","danger")
        return redirect(url_for("index"))

    if not (2000 <= year <= 2025):
        flash("Invalid year.", "danger")
        return redirect(url_for("index"))

    tables = {"acm": f"acm_{year}_{quarter}","ieee": f"ieee_{year}_{quarter}","arxiv": f"arxiv_{year}_{quarter}","final_table": f"{year}_{quarter}"}

    reset_pipeline_state()
    update_pipeline(message="Running background tasks...")

    worker = Thread(target=run_full_pipeline,args=(quarter,year,tables,keyword))
    worker.daemon = True
    worker.start()

    return redirect(url_for("index"))

@app.route("/pipeline-status")
def pipeline_status():
    return jsonify(pipeline_state)


@app.route("/results")
def results():
    if df_k_means is None:
        flash("Results not ready yet.","warning")
        return redirect(url_for("index"))

    df_selected = df_k_means[["name","author","cluster"]]
    table_data = df_selected.to_dict(orient="records")

    return render_template("results.html",table_data=table_data,columns=df_selected.columns.tolist())


if __name__ == "__main__":
    app.run(debug=True, port=5010, threaded=True)

csv_path = "files/Final_Data.csv"
if os.path.exists(csv_path):
    os.remove(csv_path)
    print("Old Final_Data.csv removed.")
