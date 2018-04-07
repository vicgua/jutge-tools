#!/bin/sed -f
s|''||g     # Delete empty lines
s|\n|\n./|g # Prepend ./ to each line
s|^|./|     # Apply to the first line too
 
