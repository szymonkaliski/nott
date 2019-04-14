#!/usr/bin/env bash

sudo systemctl enable nott-ui.service
sudo systemctl enable nott-backend.service

sudo systemctl start nott-ui.service
sudo systemctl start nott-backend.service
