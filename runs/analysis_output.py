import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

file_path = "C:/Users/LENOVO/Desktop/plato/"
df = pd.read_excel("C:/Users/LENOVO/Desktop/plato/runs.xlsx", sheet_name="Sheet1")

# For plots of selection

agt1_counts = df.groupby(["SCENARIO", "AGT1choice"]).size().unstack(fill_value=0)
agt2_counts = df.groupby(["SCENARIO", "AGT2choice"]).size().unstack(fill_value=0)

# Percentage
agt1_perc = agt1_counts.div(10).mul(100).add_prefix("AGT1_")
agt2_perc = agt2_counts.div(10).mul(100).add_prefix("AGT2_")

# Merge into one dataframe
result_explicit = pd.concat([agt1_perc, agt2_perc], axis=1).reset_index()


# Ensure missing columns exist (so stacking works even if a Uni never appears)
for col in ["AGT1_Uni3", "AGT1_Uni4", "AGT2_Uni3", "AGT2_Uni4"]:
    if col not in result_explicit.columns:
        result_explicit[col] = 0.0
result_explicit = result_explicit.fillna(0.0)

# Colors
color_map = {"Uni3": "blue", "Uni4": "orange"}

# Generate one PNG per scenario
for _, row in result_explicit.iterrows():
    scenario = row["SCENARIO"]
    fig, ax = plt.subplots(figsize=(6, 5))
    
    x = [0, 1]
    ax.bar(x[0], row["AGT1_Uni3"], color=color_map["Uni3"], label="Uni3")
    ax.bar(x[0], row["AGT1_Uni4"], bottom=row["AGT1_Uni3"], color=color_map["Uni4"], label="Uni4")
    
    ax.bar(x[1], row["AGT2_Uni3"], color=color_map["Uni3"])
    ax.bar(x[1], row["AGT2_Uni4"], bottom=row["AGT2_Uni3"], color=color_map["Uni4"])
    
    ax.set_xticks(x)
    ax.set_xticklabels(["AGT1", "AGT2"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("% Selection")
    ax.set_title(f"Scenario {scenario}")
    
    # Only two legend entries, no duplicates
    handles = [Patch(facecolor=color_map["Uni3"], label="Uni3"),
               Patch(facecolor=color_map["Uni4"], label="Uni4")]
    ax.legend(handles=handles)
    
    # Save PNG
    out_path = f"C:/Users/LENOVO/Desktop/plato/scenario_{scenario}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

print("PNG files created for each scenario.")

# boxplots ####

# Keep only what we need
cols = ["SCENARIO", "Uni1", "Uni2", "Uni3", "Uni4"]
df_sub = df[cols].copy()

# Make an output folder (optional)
out_dir = os.path.join(os.path.dirname(file_path), "boxplots")
os.makedirs(out_dir, exist_ok=True)

# Plot one figure per scenario
for scenario, g in df_sub.groupby("SCENARIO"):
    data = [g["Uni1"].values, g["Uni2"].values, g["Uni3"].values, g["Uni4"].values]

    fig, ax = plt.subplots(figsize=(6, 5))
    bp = ax.boxplot(
        data,
        labels=["Uni1", "Uni2", "Uni3", "Uni4"],
        patch_artist=True,   # allows filled boxes
        showmeans=True,
        meanprops=dict(marker='o', markerfacecolor='green', markeredgecolor='black', markersize=6) # dot for mean
    )

    ax.set_title(f"Scenario {scenario}")
    ax.set_ylabel("Centrality Index")
    ax.set_ylim(0, 1)       # values look like probabilities; set as needed
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.axhline(y=0.25, color="red", linestyle="--", linewidth=1, label="y = 0.25")

    # Save and close
    out_path = os.path.join(out_dir, f"boxplot_scenario_{scenario}.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

print(f"Saved PNGs to: {out_dir}")


















