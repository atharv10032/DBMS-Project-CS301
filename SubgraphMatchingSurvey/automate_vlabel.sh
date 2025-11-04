#!/bin/bash
# =========================================
# Automated experiment runner — VERTEX-LABELED BRANCH
# =========================================

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VLBL_DIR="$ROOT_DIR/vlabel"
BUILD_DIR="$VLBL_DIR/build/matching"
DATA_GRAPH="$VLBL_DIR/test/data_graph/HPRD.graph"
QUERY_DIR="$VLBL_DIR/test/query_graph"

OUT_BASE="$ROOT_DIR/results/vlabel"
OUT_LOGS="$OUT_BASE/logs"
mkdir -p "$OUT_LOGS"

algos=(
  "GQL RI LFTJ"
  "DPiso DPiso DPiso"
  "VEQ RI VEQ"
  "CaLiG RI KSS"
)

queries=(
  "query_dense_16_3.graph"
  "query_dense_16_50.graph"
  "query_dense_16_100.graph"
  "query_dense_16_150.graph"
  "query_dense_16_180.graph"
)

if [ ! -x "$BUILD_DIR/SubgraphMatching.out" ]; then
  echo "❌ Error: SubgraphMatching.out not found in $BUILD_DIR"
  echo "   Please build using: cd $VLBL_DIR && mkdir -p build && cd build && cmake .. && make -j"
  exit 1
fi

echo "========================================="
echo "Running Vertex-Labeled Experiments"
echo "========================================="

cd "$BUILD_DIR" || exit 1

for query in "${queries[@]}"; do
  for combo in "${algos[@]}"; do
    set -- $combo
    filter=$1; order=$2; engine=$3
    base=$(basename "$query" .graph)
    out="$OUT_LOGS/run_${filter}_${order}_${engine}_${base}.txt"
    echo "-----------------------------------------"
    echo "[vlabel] Query: $query | Algo: $filter-$order-$engine"
    echo "-----------------------------------------"
    /usr/bin/time -v ./SubgraphMatching.out \
      -d "$DATA_GRAPH" \
      -q "$QUERY_DIR/$query" \
      -filter "$filter" -order "$order" -engine "$engine" \
      -num MAX > "$out" 2>&1
  done
done

echo "✅ Vertex-labeled runs complete."
echo "   Logs saved under: $OUT_LOGS"
