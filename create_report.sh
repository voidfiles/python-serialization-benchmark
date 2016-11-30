#! /bin/bash

cat README.md > REPORT.md
echo "\`\`\`" >> REPORT.md
python benchmark.py >> REPORT.md
echo "\`\`\`" >> REPORT.md
cat disscussion.md >> REPORT.md
mkdir -p out
echo '<html>' > out/index.html
echo '<head>' >> out/index.html
echo '<link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">' >> out/index.html
echo '</head>' >> out/index.html
echo '<body>' >> out/index.html
echo '<div class="container">' >> out/index.html
python -m markdown -x markdown.extensions.fenced_code REPORT.md >> out/index.html
echo '</div>' >> out/index.html
echo '</body>' >> out/index.html
echo '</html>' >> out/index.html
