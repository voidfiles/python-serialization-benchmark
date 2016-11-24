#! /bin/bash

cat README.md > REPORT.md
echo "<pre>" >> REPORT.md
python benchmark.py >> REPORT.md
echo "</pre>" >> REPORT.md
python -m markdown REPORT.md > index.html
