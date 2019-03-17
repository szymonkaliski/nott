#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/../backend" || exit 1

~/.bin/chuck --adc3 --dac3 ./backend.ck
