Certainly! Based on the provided original README and the logic in `start.sh`, here's the updated README file:

# Bittensor Firewall
***Traefik IP Whitelisting with Docker***

This tutorial guides you through setting up [Traefik](https://traefik.io/) in a Docker container to proxy and apply IP whitelisting to Bittensor applications running on the host machine. This setup is suitable for Linux users, but also works for Mac, and includes a Python script to dynamically update the whitelisted IPs pulled from the [Bittensor](https://github.com/opentensor/bittensor) metagraph.

## Support keeping Bittensor information free and open
This work is done at-will, is fully open source, and is not affiliated with the Opentensor Foundation. Please consider donating to help maintain the ecosystem.

TAO Address: 5GeYLB44QY9wcqJmFZvJW8D3EYPDaJGSgGfkbJVxUbkVcU7C

ETH Address: 0x638e97d12D478daEF38919acd8286020aB567D0B

## Prerequisites

- Docker installed on your Linux system.
- Python 3.x
- PM2 (Process Manager 2)
- Bittensor applications running on specific ports on your host machine (e.g., 8091).
- Bittensor

## Step 0: Install requirements
```bash
python -m pip install -r requirements.txt
```

## Step 1: Set the application port(s) manually

Identify the port number(s) on which your Bittensor applications are running on the host machine. Open the `traefik.toml` file provided in the repository and replace `PORT` with the actual port number(s) you are using (defaults to `8091` if none provided). 

> `GATEWAY_IP` will be replaced automatically by the `start.sh` script or you can specify it manually if known.

Follow the instructions in the original README for multiple applications on different ports.

## Step 2: Run automated shell script

You can use the provided `start.sh` script to automate the rest of the setup process:

1. Make the script executable:
   ```bash
   chmod +x start.sh
   ```

2. Run the script:
   ```bash
   ./start.sh
   ```

#### What this script does:

1. **Stops existing containers**: Stops and removes any existing containers named `myapp1` and `myapp2`.

2. **Starts new containers**: Starts new Docker containers for your Bittensor applications, configuring them with Traefik for load balancing and traffic routing.

3. **Determines the Host's Gateway IP Address**: Finds the gateway IP address of the Docker bridge network.

4. **Replaces `GATEWAY_IP` in `traefik.toml`**: Updates the `traefik.toml` file with the IP address obtained from the above command.

5. **Starts the Traefik container**: Starts the Traefik Docker container and configures it according to the `traefik.toml` file.

6. **Runs the PM2 instance**: Starts the PM2 instance of the `firewall.py` script, which continuously updates the whitelisted IPs from the Bittensor metagraph and reloads Traefik every interval (default is 1200 seconds or 20 minutes).

> NOTE: If you are not in a Docker group, you may need to add `sudo` before any Docker command in the `firewall.py` script and the `start.sh` script.

## Conclusion

Once you set the ports appropriately and run the `start.sh` script, Traefik is now running in a Docker container, handling all incoming HTTP traffic on port 80, and applying IP whitelisting to the traffic. It proxies requests to the Bittensor applications running on the specified port(s) on the host machine.

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
