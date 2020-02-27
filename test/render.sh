#!/bin/bash

# On ubuntu, you need to install the package 'libsaxonb-java'.
# And for 'state-machine-cat', install nodejs and npm.
# Then:
#   npm i -g state-machine-cat

cd semantics

for SCCDFILE in $(find . -type f -name '*.xml'); do
  saxonb-xslt -xsl:../sccd_to_smcat.xsl -s:$SCCDFILE -o:${SCCDFILE%.xml}.smcat
  state-machine-cat ${SCCDFILE%.xml}.smcat -o ${SCCDFILE%.xml}.svg
  #rm ${SCCDFILE%.xml}.smcat
done
