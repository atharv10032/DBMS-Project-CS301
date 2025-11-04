import os, re, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path

# === CONFIG ===
BASE_DIR = "results/vlabel"
LOG_DIR = f"{BASE_DIR}/logs"
TABLE_DIR = f"{BASE_DIR}/tables"
PLOT_DIR = f"{BASE_DIR}/plots"
os.makedirs(TABLE_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

print(f"📂 Analyzing Vertex-Labeled logs from: {LOG_DIR}")

patterns = {
    "filter": re.compile(r"Filter Type:\s*(\S+)"),
    "order": re.compile(r"Order Type:\s*(\S+)"),
    "engine": re.compile(r"Engine Type:\s*(\S+)"),
    "embeddings": re.compile(r"#Embeddings:\s*(\d+)"),
    "runtime": re.compile(r"Total time \(seconds\):\s*([\d.]+)"),
    "memory": re.compile(r"Memory cost \(MB\):\s*([\d.]+)"),
    "eps": re.compile(r"EPS:\s*([\d.]+)", re.IGNORECASE),
}

def parse_log(filepath):
    """Extract metrics from one vlabel log file."""
    with open(filepath, "r", errors="ignore") as f:
        text = f.read()
    row = {"File": Path(filepath).name, "Branch": "vlabel"}
    row["Query"] = re.search(r"query_dense_\d+_\d+", filepath).group(0) if re.search(r"query_dense_\d+_\d+", filepath) else "Unknown"

    for k, p in patterns.items():
        m = p.search(text)
        row[k] = float(m.group(1)) if (m and k in ["runtime","memory","eps"]) else int(m.group(1)) if (m and k=="embeddings") else (m.group(1) if m else None)

    # fallback EPS = embeddings/runtime
    if not row.get("eps") and row.get("runtime",0)>0:
        e, t = row.get("embeddings",0), row.get("runtime",0)
        row["eps"] = e/t if t>0 else None

    row["Algorithm"] = f"{row.get('filter','')}-{row.get('order','')}-{row.get('engine','')}"
    return row

rows = [parse_log(os.path.join(LOG_DIR,f)) for f in os.listdir(LOG_DIR) if f.endswith(".txt")]
df = pd.DataFrame(rows)
df = df[df["runtime"].fillna(0)>0]

if df.empty:
    print("⚠️ No valid vlabel entries found!")
else:
    df.to_csv(f"{TABLE_DIR}/vlabel_results.csv", index=False)
    print(f"[✓] Saved vlabel_results.csv with {len(df)} rows")

    avg = df.groupby("Algorithm").agg({"runtime":"mean","eps":"mean"}).reset_index()
    avg.to_csv(f"{TABLE_DIR}/vlabel_overall_avg.csv", index=False)
    print("[✓] Saved vlabel_overall_avg.csv")

    # --- Plot ---
    plt.figure(figsize=(8,5))
    plt.bar(avg["Algorithm"], avg["eps"], edgecolor="black")
    plt.title("VLabel: Average EPS per Algorithm")
    plt.ylabel("Embeddings per second")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/vlabel_avg_eps.png")
    plt.close()

    plt.figure(figsize=(8,5))
    plt.bar(avg["Algorithm"], avg["runtime"], edgecolor="black")
    plt.title("VLabel: Average Runtime per Algorithm")
    plt.ylabel("Runtime (s)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/vlabel_avg_runtime.png")
    plt.close()

    print(f"[✓] Plots generated under {PLOT_DIR}")
