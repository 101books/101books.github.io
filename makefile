MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --jobs=8
SHELL = /bin/bash
GSFLAGS := -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH
.ONESHELL:
.RECIPEPREFIX=-
.SECONDEXPANSION:
.PHONY: FORCE
.PRECIOUS: %.gnos

# overview of what makes what:
# ./download.sh:  101weiqi.com -> problems/*.json     (to be run manually)
# ./extract.py:   problems/*.json -> problems/*.gnos  (%.gnos: %.json rule below)
# pdflatex+gs:    *.tex + problems/*.gnos -> *.pdf    (%.pdf: %.tex rule below)

# dependencies:
# https://github.com/otrego/go-type1
# https://packages.debian.org/stable/texlive
# https://packages.debian.org/stable/ghostscript

books = $(shell find . -name "*.tex" -not -name header.tex)
all: $(books:.tex=.pdf)

%.gnos: %.json extract.py
- ./extract.py "$<"

%.pdf: %.tex header.tex $$(shell find problems/$$(*F)/ -name "*.json" | sed -e "s/.json/.gnos/")
- pdflatex -output-directory=.latex.out -interaction=nonstopmode "$<"
- gs $(GSFLAGS) -sOutputFile="$@" .latex.out/"$@" && echo "minimized: $@"

clean: FORCE
- rm -rf -- .latex.out/* *.pdf

watch: FORCE
- git ls-files | entr make

# print corner problems first, half goban second:
# find problems/heavenly-dragons -name "*.sgf" \
#   | xargs -P8 -i bash -c 'grep -q "\[[mnopqrs]" {} && echo 1{} || echo 0{}' \
#   | sort -V | cut -d/ -f3-4 | sed s/.sgf// \
#   | xargs -i echo '\p{{}}%'

# print difficulty ratings:
# find problems/heavenly-dragons -name "*.json" \
#   | sort -V | xargs -i jq --raw-output '"{}: \(.levelname)"' {}
