#Note--> """ TO RUN THE PROJECT JUST USE COMMAND python app.py """

This project is a web application that analyzes research paper trends across major academic sources — ACM, IEEE Xplore, and arXiv.
Users can input:

Quarter (1, 2, or 3)
Year
Keyword

The system then scrapes research papers, stores them in a database, extracts meaningful insights, and generates interactive visualizations.

web scraping:
    Automatically scrapes papers from:

    ACM Digital Library
    IEEE Xplore
    arXiv

    Extracted fields include:
    Title
    Authors
    Citations
    Keywords
    PDF URL

database:
    All scraped papers are stored in a local SQLite database (Papers_data.db).
    Scripts handle table creation, insertion, and updating.

keyword extraction:
    Using NLP, the system:
    Extracts keywords from paper PDFs (first page only)
    Generates combined keyword summaries
    Computes keyword similarity scores

Research Trend Visualizations
    Keyword co-occurrence heatmaps
    Author influence / citations impact
    Keyword similarity graphs
    K-means paper clustering based on keywords
    Pie charts & trend summaries

project structure:

    Project_Final/
    │
    ├── scraping/
    │   ├── acm_scrap.py              # ACM scraping script
    │   ├── arxiv_scrap.py            # arXiv scraping script
    │   ├── ieee_scrap.py             # IEEE scraping script
    │   ├── keywords_gen.py           # Keyword extraction from PDFs
    │   ├── sqlite_database.py        # SQLite DB creation & insertion
    │   ├── downloaded_paper.pdf      # Temporary downloaded PDF
    │
    ├── visualization/
    │   ├── authors_citations_impact.py   # Plot: author influence
    │   ├── cooccurance.py                # Plot: keyword co-occurrence
    │   ├── input_keyword_similarity.py   # Plot: keyword similarity
    │   ├── k_means_cluster.py            # Paper topic clustering
    │   ├── keyword_summary.py            # Keyword summaries
    │
    ├── static/
    │   ├── css/                          # Stylesheets
    │   ├── plots/                        # Generated visualizations
    │   ├── globe_icon.png
    │   ├── Papers_data.db                # SQLite database
    │
    ├── templates/                         # Flask HTML templates
    │
    ├── app.py                             # Main Flask web application
    ├── plots.py                           # Utilities for generating plots
    ├── db_utils.py                        # Helper functions for DB operations
    ├── paper_clusters.csv                 # Output of K-means clustering
    ├── paper_keyword_summary.csv          # Output of keyword processing
    │
    ├── requirement.txt                    # Python dependencies
    └── README.md                          # This file
