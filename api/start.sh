#!/bin/bash

# MoleSearch API startup script

# Check if worker mode is requested
if [ "$1" = "worker" ]; then
    echo "Starting MoleSearch async worker..."
    python workers/start_worker.py
else
    echo "Starting MoleSearch API server..."
    gunicorn -c gunicorn.conf.py main:app
fi