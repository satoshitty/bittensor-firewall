#!/bin/bash

# Check if the user is in the docker group or root
if [ $(id -u) -eq 0 ] || groups $USER | grep -q '\bdocker\b'; then
  DOCKER_COMMAND="docker"
else
  DOCKER_COMMAND="sudo docker"
fi

# Set up the dummy docker image
$DOCKER_COMMAND build -t hello-world-image .
cd .. # back to main repo directory

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

# Wait for the containers to be up and running
sleep 5

# Test the setup using curl
RESULT=$(curl -s localhost)

# Check if the result contains "Hello, World!"
if [[ $RESULT == *"Hello, World!"* ]]; then
  echo "Success! Received 'Hello, World!' from the application. Traefik is working as expected."
else
  echo "Error! Did not receive the expected response from the application."
fi

# Stop and remove the containers
$DOCKER_COMMAND stop myapp traefik
$DOCKER_COMMAND rm myapp traefik