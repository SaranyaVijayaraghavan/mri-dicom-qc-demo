#!/usr/bin/env bash
set -e

python qc_check.py
git add -A
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    git commit -m "Refresh QC results $(date +%Y-%m-%d)"
fi
git push
