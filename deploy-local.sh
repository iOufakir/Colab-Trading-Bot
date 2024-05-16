#!/bin/bash

docker rm -f trading-bot
docker build -t trading-bot:latest .
docker run --env-file .env --name trading-bot -p 5000:5000 trading-bot