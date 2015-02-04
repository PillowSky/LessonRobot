#!/bin/bash
# compile
coffee --compile js/*.coffee
lessc -x css/style.less css/style.css
jade *.jade

# compress
uglifyjs js/script.js --mangle --compress --screw-ie8 -o js/script.js

echo "The files are ready to deploy."
