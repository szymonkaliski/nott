#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd /lib/systemd/system || exit 1

sudo cp -f "$DIR/../systemd/ui.service" nott-ui.service
sudo cp -f "$DIR/../systemd/backend.service" nott-backend.service

