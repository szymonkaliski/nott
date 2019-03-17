#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.." || exit 1

rsync -azP . --exclude .git pi@raspberrypi.local:/home/pi/app/
