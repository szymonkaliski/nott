#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/../ui" || exit 1

nodemon -e py -x ../scripts/dev-ui.sh
