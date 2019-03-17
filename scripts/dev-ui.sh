#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/../ui" || exit 1

if [ $(pgrep python3) ]; then
  kill -2 $(pgrep python3)
fi

python3 ./ui.py
