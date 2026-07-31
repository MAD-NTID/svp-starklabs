docker stop dashboard 2>$null; docker rm dashboard 2>$null

docker build -t escape-room-dashboard .

docker run -d -p 8000:8000 `
  -v dashboard-data:/app/data `
  -v "$(pwd)/cards/tasks.yaml:/app/cards/tasks.yaml" `
  --name dashboard `
  escape-room-dashboard
