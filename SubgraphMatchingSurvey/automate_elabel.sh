#!/bin/bash
# =========================================
# Automated experiment runner — EDGE-LABELED BRANCH
# =========================================

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
ELBL_DIR="$ROOT_DIR/elabel"
BUILD_DIR="$ELBL_DIR/build/matching"
DATA_GRAPH="$ELBL_DIR/elabel_test/HPRD_elabeled.txt"
QUERY_DIR="$ELBL_DIR/elabel_test/elabel"

OUT_BASE="$ROOT_DIR/results/elabel"
OUT_LOGS="$OUT_BASE/logs"
mkdir -p "$OUT_LOGS"

algos=(
  "GQL RI LFTJ"
  "DPiso DPiso DPiso"
  "VEQ RI VEQ"
  "CaLiG RI KSS"
)

queries=(
  "Q10-3.txt"
  "Q10-50.txt"
  "Q10-100.txt"
  "Q10-150.txt"
  "Q10-180.txt"
)

if [ ! -x "$BUILD_DIR/SubgraphMatching.out" ]; then
  echo "❌ Error: SubgraphMatching.out not found in $BUILD_DIR"
  echo "   Please build using: cd $ELBL_DIR && mkdir -p build && cd build && cmake .. && make -j"
  exit 1
fi

echo "========================================="
echo "Running Edge-Labeled Experiments"
echo "========================================="

cd "$BUILD_DIR" || exit 1

for query in "${queries[@]}"; do
  for combo in "${algos[@]}"; do
    set -- $combo
    filter=$1; order=$2; engine=$3
    base=$(basename "$query" .txt)
    out="$OUT_LOGS/run_${filter}_${order}_${engine}_${base}.txt"
    echo "-----------------------------------------"
    echo "[elabel] Query: $query | Algo: $filter-$order-$engine"
    echo "-----------------------------------------"
    /usr/bin/time -v ./SubgraphMatching.out \
      -d "$DATA_GRAPH" \
      -q "$QUERY_DIR/$query" \
      -filter "$filter" -order "$order" -engine "$engine" \
      -num MAX > "$out" 2>&1
  done
done

echo "✅ Edge-labeled runs complete."
echo "   Logs saved under: $OUT_LOGS"
