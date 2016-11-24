#! /bin/bash

cat README.md > REPORT.md
echo "<pre>" >> REPORT.md
python benchmark.py >> REPORT.md
echo "</pre>" >> REPORT.md
mkdir -p out
python -m markdown REPORT.md > out/index.html
