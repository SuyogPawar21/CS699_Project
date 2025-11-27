import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def keyword_summary_plot(df_summary):
    sizes = df_summary["similarity_percent"].values
    labels = df_summary["keywords"].values
    fig = plt.figure(figsize=(12, 10))

    ax_pie = fig.add_subplot(2, 1, 1) 
    wedges, texts, autotexts = ax_pie.pie(sizes,autopct='%1.1f%%')
    ax_pie.set_title("Similarity Percentage Distribution Across Papers")
    patches = [Patch(facecolor=w.get_facecolor(), label=l) for w, l in zip(wedges, labels)]
    ax_legend = fig.add_subplot(2, 1, 2) 
    ax_legend.axis('off')
    ax_legend.legend(handles=patches,title="Keywords",loc="upper left",fontsize=12,title_fontsize=14)
    plt.tight_layout()
    plt.savefig("static/plots/similarity_pie_with_legend.png", dpi=300, bbox_inches='tight')
    plt.close()