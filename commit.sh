cd /Users/quebec/Playground/others_indexed/TextRank4ZH
mkdir hw6
cp -r src hw6/
cp -r data hw6/
cp 报告.pdf hw6/
cp README.md hw6/ 
rm -f hw6/__py*
tar czf hw6.tgz hw6
rm -r hw6
mv hw6.tgz ~/Downloads