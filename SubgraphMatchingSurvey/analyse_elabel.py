import os, re, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path

# === CONFIG ===
BASE_DIR = "results/elabel"
LOG_DIR = f"{BASE_DIR}/logs"
TABLE_DIR = f"{BASE_DIR}/tables"
PLOT_DIR = f"{BASE_DIR}/plots"
os.makedirs(TABLE_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

print(f"📂 Analyzing Edge-Labeled logs from: {LOG_DIR}")

patterns = {
    "filter": re.compile(r"Filter Type:\s*(\S+)"),
    "order": re.compile(r"Order Type:\s*(\S+)"),
    "engine": re.compile(r"Engine Type:\s*(\S+)"),
    "embeddings": re.compile(r"#Embeddings:\s*(\d+)"),
    "runtime": re.compile(r"Total time \(seconds\):\s*([\d.]+)"),
    "memory": re.compile(r"Memory cost \(MB\):\s*([\d.]+)"),
    "eps": re.compile(r"EPS:\s*([\d.]+)", re.IGNORECASE),
    "exit": re.compile(r"Exit status:\s*(\d+)")
}

def parse_elabel_log(filepath):
    """Extract metrics from one elabel log file."""
    with open(filepath, "r", errors="ignore") as f:
        text = f.read()
    row = {"File": Path(filepath).name, "Branch": "elabel"}

    # extract query name (e.g. Q10-100.txt)
    q = re.search(r"Q10-\d+", filepath)
    row["Query"] = q.group(0) if q else "Unknown"

    for k, p in patterns.items():
        m = p.search(text)
        if not m:
            row[k] = None
            continue
        val = m.group(1)
        if k in ["runtime", "memory", "eps"]:
            try: val = float(val)
            except: val = None
        elif k in ["embeddings", "exit"]:
            try: val = int(val)
            except: val = None
        row[k] = val

    # skip failed runs
    if row.get("exit",0) != 0:
        return None

    if not row.get("eps") and row.get("runtime",0)>0:
        e,t=row.get("embeddings",0),row.get("runtime",0)
        row["eps"]=e/t if t>0 else None

    row["Algorithm"]=f"{row.get('filter','')}-{row.get('order','')}-{row.get('engine','')}"
    return row

rows=[]
for f in os.listdir(LOG_DIR):
    if f.endswith(".txt"):
        r=parse_elabel_log(os.path.join(LOG_DIR,f))
        if r: rows.append(r)

df=pd.DataFrame(rows)
if df.empty:
    print("⚠️ No valid elabel entries found!")
else:
    df.to_csv(f"{TABLE_DIR}/elabel_results.csv",index=False)
    print(f"[✓] Saved elabel_results.csv with {len(df)} rows")

    avg=df.groupby("Algorithm").agg({"runtime":"mean","eps":"mean"}).reset_index()
    avg.to_csv(f"{TABLE_DIR}/elabel_overall_avg.csv",index=False)
    print("[✓] Saved elabel_overall_avg.csv")

    # --- Plot ---
    plt.figure(figsize=(8,5))
    plt.bar(avg["Algorithm"], avg["eps"], edgecolor="black")
    plt.title("ELabel: Average EPS per Algorithm")
    plt.ylabel("Embeddings per second")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/elabel_avg_eps.png")
    plt.close()

    plt.figure(figsize=(8,5))
    plt.bar(avg["Algorithm"], avg["runtime"], edgecolor="black")
    plt.title("ELabel: Average Runtime per Algorithm")
    plt.ylabel("Runtime (s)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/elabel_avg_runtime.png")
    plt.close()

    print(f"[✓] Plots generated under {PLOT_DIR}")
