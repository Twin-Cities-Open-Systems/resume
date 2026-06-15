#!/bin/sh
# Spencer Butler <spencer@tcos.us>
# Convert SpencerButler.md to SpencerButler.{html,pdf,txt}
# Requires: pandoc, wkhtmltopdf, texlive-latex-recommended

resume="${resume:-SpencerButler}"

pandoc -s ${resume}.md -t html5 -o ${resume}.html
pandoc -s ${resume}.md -t latex  -o ${resume}.pdf

sed -e 's/^#*[[:space:]]//g' ${resume}.md > ${resume}.txt

cp ${resume}.md README.md
