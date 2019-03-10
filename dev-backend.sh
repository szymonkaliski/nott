#!/usr/bin/env bash

nodemon --signal SIGKILL -e ck -x 'chuck --adc3 --dac3 ./Backend/backend.ck'
