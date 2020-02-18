#!/bin/bash

cd tests
mkdir -p transformed

for FILE in `find . -type f -name '*.txml'`
do

  xsltproc -o transformed/$FILE ../txml_to_sccd.xsl $FILE 
done