#!/bin/bash

# Path to the traefik.toml file
TRAEFIK_CONFIG_PATH="traefik.toml"

# Get the gateway IP address of the Docker bridge network
GATEWAY_IP=$(docker network inspect bridge --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}')

# Replace GATEWAY_IP in the traefik.toml file
sed -i "s/GATEWAY_IP/$GATEWAY_IP/g" $TRAEFIK_CONFIG_PATH

# Replace PORT in the traefik.toml file if not specified
PORT=8091 # default
sed -i "s/PORT/$PORT/g" $TRAEFIK_CONFIG_PATH

# Run Traefik using Docker
sudo docker run -d \
  --name traefik \
  --publish 80:80 \
  --volume $TRAEFIK_CONFIG_PATH:/etc/traefik/traefik.toml \
  traefik:latest

# Start the Python script with PM2
pm2 start firewall.py --name "BittensorFW" --interpreter "$(which python)"

echo "Traefik and Bittensor Firewall are now running!"
