#!/usr/bin/env bash

version="v2.2.2"
file="overmind-${version}-linux-arm"
url="https://github.com/DarthSim/overmind/releases/download/${version}/${file}.gz"

# cleanup
rm "${file}"
rm "${file}.gz"

curl -L "$url" -O

gunzip "${file}.gz"

chmod +x "$file"
mv "$file" /usr/local/bin/
