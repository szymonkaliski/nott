#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.." || exit 1

rsync -azP . --exclude .git --exclude node_modules --exclude __pycache__ pi@raspberrypi.local:/home/pi/app/
