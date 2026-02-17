MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --jobs=8
SHELL = /bin/bash
.ONESHELL:
.RECIPEPREFIX=-
.SECONDEXPANSION:
.PHONY: FORCE
.PRECIOUS: %.gnos

# overview of what makes what:
# ./download.sh:  101weiqi.com -> problems/*.json
# ./extract.py:   problems/*.json -> problems/*.gnos
# pdflatex:       books/*.tex + problems/*.gnos -> pdfs/*.pdf

# dependencies:
# https://github.com/otrego/go-type1
# https://packages.debian.org/stable/texlive
# https://packages.debian.org/stable/ghostscript
# https://packages.debian.org/stable/linkchecker

pdfs = $(shell ls books | grep -v header.tex | xargs -i echo pdfs/{} | sed s/.tex/.pdf/g)
all: $(pdfs) index.html
logs: high-problems.log wide-problems.log duplicates.log problem-count.log page-count.log

%.gnos: %.json
- ./extract.py "$<"

pdfs/%.pdf: books/%.tex books/header.tex $$(shell find problems/$$(*F)/ -name "*.json" | sed -e "s/.json/.gnos/")
- mkdir .latex.out
- pdflatex -output-directory=.latex.out -interaction=nonstopmode "$<"
- cp .latex.out/"$(@F)" "$@"

index.html: index.py problem-count.log
- ./index.py

problem-count.log: $(pdfs)
- expr $$(find pdfs -name "*.pdf" | xargs -n1 -P8 pdfgrep -Poh "Problems: \K[0-9]+" | xargs -i -P8 bash -c "printf '{} + '")0 | tee $@

page-count.log: $(pdfs) index.html
- lynx -dump -listonly $(shell pwd)/index.html | grep file | cut -d/ -f8-9 | xargs -i bash -c 'printf "{}:\t" && pdfinfo "{}" | grep Pages | awk "{print \$$2}"' | expand -t 10,40 | tee $@

clean: FORCE
- rm -rf -- .latex.out/* pdfs/*.pdf

watch: FORCE
- git ls-files | entr make

# grep $book duplicates.log | cut -d/ -f4 | cut -d. -f1 | xargs -IX sed -i 's/^[^%].*{X}/%&%duplicate/g' books/$book.tex
duplicates.log: FORCE
- find problems -name "*.gnos" -exec md5sum {} + | sort | uniq -w32 -dD > $@

high-problems.log: FORCE
- find problems -name "*.sgf" -exec grep "[abcdefghi]\]" -l {} + \
  | grep -v problems/korean-endgame/1173/169874.sgf \
  | grep -v problems/heavenly-dragons/39/28612.sgf \
  | grep -v problems/leechangho-endgame/0/116789.sgf \
  | sort -V > $@

wide-problems.log: FORCE
- find problems -name "*.sgf" -exec grep "\[[lmnopqrs]" -l {} + | sort -V > $@

# (
#   echo "\def\problems{%"
#   find problems/$book -name *.sgf \
#     | grep -v --file high-problems.log \
#     | grep -v --file wide-problems.log \
#     | sort -V \
#     | cut -d/ -f3-4 | sed s/.sgf// | sed "s|/|}{|"  \
#     | xargs -i echo "\p{{}}%"
#   echo "\halfgoban%"
#   find problems/$book -name *.sgf \
#     | grep -v --file high-problems.log \
#     | grep --file wide-problems.log \
#     | sort -V \
#     | cut -d/ -f3-4 | sed s/.sgf// | sed "s|/|}{|"  \
#     | xargs -i echo "\p{{}}%"
#   find problems/$book -name *.sgf \
#     | grep --file high-problems.log \
#     | sort -V \
#     | cut -d/ -f3-4 | sed s/.sgf// | sed "s|/|}{|"  \
#     | xargs -i echo "%\p{{}}%full-goban"
#   echo "}"
#   echo "\input{books/header}"
# ) >> books/$book.tex

# real_lvl=$(
#     git ls-files | grep -P $(grep -Po '^\\p{\K\d+}{\d+' "books/$book.tex" | sed s@}{@/@g | xargs | sed 's/ /|/g') | grep .json |  sort -V \
#         | xargs -P8 -i jq --raw-output '.levelname' {} \
#         | sed -e s/20K/1/g -e s/19K/2/g -e s/18K/3/g -e s/17K/4/g -e s/16K/5/g -e s/15K/6/g -e s/14K/7/g \
#                 -e s/13K/8/g -e s/12K/9/g -e s/11K/10/g -e s/10K/11/g -e s/9K/12/g -e s/8K/13/g -e s/7K/14/g \
#                 -e s/6K/15/g -e s/5K/16/g -e s/4K/17/g -e s/3K/18/g -e s/2K/19/g -e s/1K/20/g -e s/1D/21/g \
#                 -e s/2D/22/g -e s/3D/23/g -e s/4D/24/g -e s/5D/25/g -e s/6D/26/g -e s/7D/27/g -e s/8D/28/g \
#                 -e s/9D/29/g -e s/+//g \
#         | awk '{for (i=1;i<=NF;++i) {sum+=$i; ++n}} END {printf "x%.0fx\n", sum/n}' \
#         | sed -e s/x1x/20' ky\\=u'/g -e s/x2x/19' ky\\=u'/g -e s/x3x/18' ky\\=u'/g -e s/x4x/17' ky\\=u'/g -e s/x5x/16' ky\\=u'/g -e s/x6x/15' ky\\=u'/g \
#                 -e s/x7x/14' ky\\=u'/g -e s/x8x/13' ky\\=u'/g -e s/x9x/12' ky\\=u'/g -e s/x10x/11' ky\\=u'/g -e s/x11x/10' ky\\=u'/g -e s/x12x/9' ky\\=u'/g \
#                 -e s/x13x/8' ky\\=u'/g -e s/x14x/7' ky\\=u'/g -e s/x15x/6' ky\\=u'/g -e s/x16x/5' ky\\=u'/g -e s/x17x/4' ky\\=u'/g -e s/x18x/3' ky\\=u'/g \
#                 -e s/x19x/2' ky\\=u'/g -e s/x20x/1' ky\\=u'/g -e s/x21x/1' dan'/g -e s/x22x/2' dan'/g -e s/x23x/3' dan'/g -e s/x24x/4' dan'/g \
#                 -e s/x25x/5' dan'/g -e s/x26x/6' dan'/g -e s/x27x/7' dan'/g -e s/x28x/8' dan'/g -e s/x29x/9' dan'/g;
# )
# book_lvl=$(grep -Po '\\def\\level{\K[^}]+' "books/$book.tex")
# test "$real_lvl" == "$book_lvl" || sed -i "s/level{$(echo $book_lvl | sed 's/\\/\\\\/g')/level{$(echo $real_lvl | sed 's/\\/\\\\/g')/" "books/$book.tex"
