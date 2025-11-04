#!/bin/bash
# =========================================
# Automated experiment runner for vlabel
# =========================================

# Algorithm combinations to test
algos=(
  "GQL RI LFTJ"
  "DPiso DPiso DPiso"
  "VEQ RI VEQ"
  "CaLiG RI KSS"
)

# Paths
DATA_GRAPH="../../test/data_graph/HPRD.graph"
QUERY_DIR="../../test/query_graph"
OUT_DIR="../../../results/logs/vlabel_data"
mkdir -p "$OUT_DIR"

# Representative queries (you can add more)
queries=(
  "query_dense_16_3.graph"
  "query_dense_16_50.graph"
  "query_dense_16_100.graph"
  "query_dense_16_150.graph"
  "query_dense_16_180.graph"
)

# =========================================
# Run experiments
# =========================================
for query in "${queries[@]}"; do
  for combo in "${algos[@]}"; do
    set -- $combo
    filter=$1; order=$2; engine=$3

    # Construct output filename
    base=$(basename "$query" .graph)
    out="${OUT_DIR}/run_${filter}_${order}_${engine}_${base}.txt"

    echo "========================================="
    echo "Running: $filter-$order-$engine | Query: $query"
    echo "Output -> $out"
    echo "========================================="

    /usr/bin/time -v ./SubgraphMatching.out \
      -d "$DATA_GRAPH" \
      -q "$QUERY_DIR/$query" \
      -filter "$filter" -order "$order" -engine "$engine" \
      -num MAX > "$out" 2>&1
  done
done

echo "All runs complete. Logs stored in $OUT_DIR"

