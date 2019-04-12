#!/usr/bin/env bash


DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/../dist" || exit 1

/Applications/Slic3r.app/Contents/MacOS/Slic3r ./case-top.stl --export-svg -o case-top.svg
/Applications/Slic3r.app/Contents/MacOS/Slic3r ./case-bottom.stl --export-svg -o case-bottom.svg

