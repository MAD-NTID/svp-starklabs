#!/bin/bash

docker stop dashboard 2>/dev/null; docker rm dashboard 2>/dev/null

docker build -t escape-room-dashboard .

docker run -d -p 8000:8000 \
  -v dashboard-data:/app/data \
  -v "$(pwd)/cards/tasks.yaml:/app/cards/tasks.yaml" \
  --network host \
  --name dashboard \
  escape-room-dashboard
