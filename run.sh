#!/bin/bash
if [ ! -d "./instance/database.db" ]; then
    mkdir ./data ./data/waiting ./data/inprogress ./data/done  instance
    python3 -m scripts.init-db

fi

python main.py
