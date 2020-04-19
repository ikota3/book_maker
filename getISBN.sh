#!/bin/bash

# Number of pages to check in PDF
PAGE_COUNT=1
# File path
FILE_PATH="$1"

# If the file extension is not pdf
shopt -s nocasematch
if [[ ! $1 =~ .+(\.pdf)$ ]]; then
  exit 1
fi
shopt -u nocasematch

# Delete all .image* generated by pdfimages
rm -f .image*

# Get total count of PDF pages
pages=$(pdfinfo "$FILE_PATH" | grep -E "^Pages" | sed -E "s/^Pages: +//") &&
# Generate JPEG from PDF
pdfimages -j -l "$PAGE_COUNT" "$FILE_PATH" .image_h &&
pdfimages -j -f $((pages - PAGE_COUNT)) "$FILE_PATH" .image_t &&
# Grep ISBN
isbnTitle="$(zbarimg -q .image* | sort | uniq | grep -E '^EAN-13:978' | sed -E 's/^EAN-13://')" &&
# If the ISBN was found, echo the ISBN
[ "$isbnTitle" != "" ] &&
echo "$isbnTitle" && rm -f .image* && exit 0 ||
# Else, exit with error code
rm -f .image* && exit 1
