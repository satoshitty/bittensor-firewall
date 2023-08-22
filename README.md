# Bittensor Firewall

> TL;DR 
This tutorial guides you through setting up [Traefik](https://traefik.io/) in a Docker container to proxy and apply IP whitelisting to Bittensor applications running on the host machine. This setup is mostly suitable for Linux users, but *should* also work for Mac. It includes a Python script to dynamically update the whitelisted IPs pulled from the [Bittensor](https://github.com/opentensor/bittensor) metagraph as well as a watcher script to publish local IP to chain, both of which are managed by a pm2 process.


***Traefik IP Whitelisting with Docker***

> NOTE: There is a "lightweight" firewall option to just use ufw if you don't use docker containers for your applications. See the [ufw](ufw/firewall.py) script and [README](ufw/README.md).

The Bittensor Firewall utilizes Traefik and Docker to create a secure and efficient gateway for Bittensor applications. Traefik, running inside a Docker container, acts as a reverse proxy, fielding incoming HTTP requests and directing them to the appropriate Bittensor applications running on the host machine. This configuration allows Traefik to control and monitor the traffic, applying IP whitelisting to ensure that only authorized IP addresses can access the applications. By employing Traefik's dynamic configuration capabilities, the setup can regularly update the whitelist, reflecting changes in the Bittensor metagraph. This ensures continuous alignment with the current network state, thereby enhancing security.

In addition to acting as a firewall, this combination of Traefik and Docker also brings load balancing and automated routing benefits. With Docker hosting both the Traefik container and the application containers, they are part of a unified ecosystem that simplifies configuration, deployment, and scaling. By strategically managing the routing of requests, Traefik ensures efficient utilization of resources and provides a seamless integration point between the Bittensor applications and the external world. 


## Support keeping Bittensor information free and open
This work is done at-will, is fully open source, and is not affiliated with the Opentensor Foundation. Please consider donating to help maintain the ecosystem.

TAO Address: 5GeYLB44QY9wcqJmFZvJW8D3EYPDaJGSgGfkbJVxUbkVcU7C

ETH Address: 0x638e97d12D478daEF38919acd8286020aB567D0B

## Prerequisites

- Docker installed on your Linux system.
- Python 3.x
- Bittensor
- PM2 (Process Manager 2)
- Bittensor application running inside a docker container.

## Step 1: Install requirements
```bash
python -m pip install -r requirements.txt
```

> NOTE: `GATEWAY_IP` will be replaced automatically by the `start.sh` script based on your docker network gateway, or you can specify it manually if known.

### Step 1.1: Update `start.sh` to use your docker image and specify port(s) desired.
```bash
$DOCKER_COMMAND run -d \
    -p 8081:8080 \                                                   # Only modify the number left of the colon (:), refers to external port
    --name myapp \                                                   # Name of your docker container, irrelevant
    -l "traefik.enable=true" \                                       # Tell docker to use traefik
    -l 'traefik.http.routers.myapp.rule=PathPrefix(`/`)' \           # This refers to all routes that begin with `/`, do not modify
    -l "traefik.http.services.myapp.loadbalancer.server.port=8080" \ # This specifies internal port, do not modify
    -l "traefik.http.routers.myapp.middlewares=myipwhitelist@file" \ # This specifies name for our whitelist middleware
    <YOUR-DOCKER-IMAGE>                                              # This is your docker image name housing your application

```

## Step 2: Run automated shell script

You can use the provided `start.sh` script to automate the rest of the process:

```bash
./start.sh
```

#### What this script does:

1. **Stops existing containers**: Stops and removes any existing container named `myapp`. You should update this 

2. **Starts new containers**: Starts new Docker containers for your Bittensor applications, configuring them with Traefik for load balancing and traffic routing. (You should modify this specifically for your own application and docker image)

3. **Determines the Host's Gateway IP Address**: Finds the gateway IP address of the Docker bridge network.

4. **Replaces `GATEWAY_IP` in `traefik.toml`**: Updates the `traefik.toml` file with the IP address obtained from the above command.

5. **Starts the Traefik container**: Starts the Traefik Docker container and configures it according to the `traefik.toml` file.

6. **Runs the PM2 instances**: Starts the PM2 instance of the `firewall.py` script, which continuously updates the whitelisted IPs from the Bittensor metagraph and reloads Traefik every interval (default is 1200 seconds or 20 minutes). Runs `watcher.py` which is relevant for continually publishing your IP to the chain (5 minute interval).

> NOTE: If you are not in a Docker group, you may need to add `sudo` before any Docker command in the `firewall.py` script and the `start.sh` script.

## Conclusion

Once you configure your docker image for your Bittensor application appropriately and run the `start.sh` script, Traefik should now running in a Docker container, handling all incoming HTTP traffic on port 80, and applying IP whitelisting to the traffic. It proxies requests to the Bittensor applications running on the specified port(s) inside their respective docker containers.

For more information on Traefik and its configuration options, refer to the [official Traefik documentation](https://doc.traefik.io/traefik/).

### Troubleshooting: Container Name Conflict

If you encounter an error like the following when running the `start.sh` script:

```
docker: Error response from daemon: Conflict. The container name "/traefik" is already in use by container "4664...". You have to remove (or rename) that container to be able to reuse that name.
See 'docker run --help'.
```

This means that a container with the name "traefik" already exists on your system. You'll need to stop and remove that container before you can create a new one with the same name. Follow these steps to resolve the issue:

1. **Stop the existing container** with the name "traefik":

   ```bash
   docker stop traefik
   ```

2. **Remove the existing container** with the name "traefik":

   ```bash
   docker rm traefik
   ```

3. **Run the `start.sh` script again** to start the new container.

By stopping and removing the existing container, you'll free up the name "traefik" so that you can use it for the new container.
