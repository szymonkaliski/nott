#!/usr/bin/env bash

if [ $(pgrep python3) ]; then
  kill -2 $(pgrep python3)
fi

python3 ./UI/ui.py
