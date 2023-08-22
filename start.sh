#!/bin/bash

# Check if the user is in the docker group or root
if [ $(id -u) -eq 0 ] || groups $USER | grep -q '\bdocker\b'; then
  DOCKER_COMMAND="docker"
else
  DOCKER_COMMAND="sudo docker"
fi

# Stop the container if it exists
$DOCKER_COMMAND stop myapp
$DOCKER_COMMAND rm myapp

# Start your own docker application container
$DOCKER_COMMAND run -d \
    -p 8081:8080 \
    --name myapp \
    -l "traefik.enable=true" \
    -l 'traefik.http.routers.myapp.rule=PathPrefix(`/`)' \
    -l "traefik.http.services.myapp.loadbalancer.server.port=8080" \
    -l "traefik.http.routers.myapp.middlewares=myipwhitelist@file" \
    hello-world-image # docker image name

# Stop the container if it exists
$DOCKER_COMMAND stop traefik
$DOCKER_COMMAND rm traefik

# Run Traefik using Docker
$DOCKER_COMMAND run -d \
  --name traefik \
  --publish 80:80 \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume $PWD/traefik.toml:/etc/traefik/traefik.toml \
  --volume $PWD/dynamic_conf:/etc/traefik/dynamic_conf \
  traefik:latest

# Start the Python script with PM2
pm2 start watcher.py --name "BittensorIPWatcher" \
    --interpreter "$(which python)" \
    --cron-restart="*/5 * * * *" \
    --no-autorestart \
    -- \
    --wallet.name churchofrao \
    --wallet.hotkey raovali \
    --netuid 1

pm2 start firewall.py --name "BittensorFW" \
    --interpreter "$(which python)" \
    --cron-restart="*/20 * * * *" \
    --no-autorestart \
    -- \

echo "Traefik and Bittensor Firewall are now running!"
