#!/bin/bash

# Check if the user is in the docker group or root
if [ $(id -u) -eq 0 ] || groups $USER | grep -q '\bdocker\b'; then
  DOCKER_COMMAND="docker"
else
  DOCKER_COMMAND="sudo docker"
fi

# Path to the traefik.toml file
TRAEFIK_CONFIG_PATH="traefik.toml"

# Get the gateway IP address of the Docker bridge network
GATEWAY_IP=$($DOCKER_COMMAND network inspect bridge --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}')

# Replace GATEWAY_IP in the traefik.toml file
sed -i "s/GATEWAY_IP/$GATEWAY_IP/g" $TRAEFIK_CONFIG_PATH

# Replace PORT in the traefik.toml file if not specified
PORT=8888 # default
sed -i "s/PORT/$PORT/g" $TRAEFIK_CONFIG_PATH

$DOCKER_COMMAND stop traefik
$DOCKER_COMMAND rm traefik

# Run Traefik using Docker
$DOCKER_COMMAND run -d \
  --name traefik \
  --publish 80:80 \
  --volume $PWD/traefik.toml:/etc/traefik/traefik.toml \
  --volume $PWD/dynamic_conf:/etc/traefik/dynamic_conf \
  traefik:latest

# Start the Python script with PM2
pm2 start firewall.py --name "BittensorFW" --interpreter "$(which python)"

echo "Traefik and Bittensor Firewall are now running!"
