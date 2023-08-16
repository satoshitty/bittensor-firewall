# Bittensor Firewall
***Traefik IP Whitelisting with Docker***

This tutorial guides you through setting up [Traefik](https://traefik.io/) in a Docker container to proxy and apply IP whitelisting to an application running on the host machine. This setup is suitable for Linux users, but also works for Mac and includes a Python script to dynamically update the whitelisted IPs pulled from the [Bittensor](https://github.com/opentensor/bittensor) metagraph.

## Support keeping Bittensor information free and open
This work is done at-will, is fully open source, and is not affiliated with the Opentensor Foundation. Please consider donating to help maintain the ecosystem.

TAO Address: 5GeYLB44QY9wcqJmFZvJW8D3EYPDaJGSgGfkbJVxUbkVcU7C
ETH Address: 0x638e97d12D478daEF38919acd8286020aB567D0B


## Prerequisites

- Docker installed on your Linux system.
- Python 3.x
- PM2 (Process Manager 2)
- A bittensor application running on a specific port on your host machine (e.g., 8091).
- Bittensor

## Step 0: Install requirements
```bash
python -m pip install -r requirements.txt
```

## Step 1: Set the application port(s) manually

Identify the port number on which your application is running on the host machine. Open the `traefik.toml` file provided in the repository and replace `PORT` with the actual port number you are using (defaults to `8091` if none provided). 

```bash
[http.services]
  [http.services.btfirewall.loadBalancer]
    [[http.services.btfirewall.loadBalancer.servers]]
      url = "http://GATEWAY_IP:PORT" # Replace PORT with your application's port
...
      url = "http://GATEWAY_IP:8091 # 8091 is replaced in start.sh if none provided
```

If you have multiple applications running on different ports:

```bash
[http.services]
  [http.services.btfirewall.loadBalancer]
    [[http.services.btfirewall.loadBalancer.servers]]
      url = "http://GATEWAY_IP:PORT1" # Replace PORT1 manually
    [[http.services.btfirewall.loadBalancer.servers]]
      url = "http://GATEWAY_IP:PORT2" # Replace PORT2 manually
    # Add more URLs as needed
```

> `GATEWAY_IP` will be replaced automatically by the `start.sh` script or you can specifcy manually if known.

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

The script will determine the gateway IP address of the Docker bridge network, update the `traefik.toml` file, start the Traefik Docker container, and run the PM2 instance of the `firewall.py` script. 

> NOTE: If no port is specificed, (e.g. PORT is left unchanged in the traefik.toml file) port defaults to 8091.

#### What this script does:

1. Determine the Host's Gateway IP Address:

    Finds the gateway IP address of the Docker bridge network using the following command:

    ```bash
    docker network inspect bridge --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}'
    ```

2. Replaces `GATEWAY_IP` in the `traefik.toml` file with the IP address obtained from the above command.
    ```bash
    sed -i "s/GATEWAY_IP/$GATEWAY_IP/g" $TRAEFIK_CONFIG_PATH
    ```
    It looks like this:
    ```bash
    [http.services]
      [http.services.myapp.loadBalancer]
        [[http.services.myapp.loadBalancer.servers]]
          url = "http://GATEWAY_IP:PORT" # Replaces GATEWAY_IP automatically
        ...
          url = "http://192.168.99.1:PORT" # Replaced GATEWAY_IP with 192.168.99.1

> NOTE: If you are not on a docker group, you'll need to add `sudo` before any docker command in the `firewall.py` script and the `start.sh` script.
firewall.py:
> `subprocess.run(["sudo", "docker", "kill", "-s", "HUP", "traefik"])`
> start.sh:
> `GATEWAY_IP=$(sudo docker network inspect bridge --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}')`

## Conclusion

Once you set ports appropriately and run the `start.sh` script, Traefik is now running in a Docker container, handling all incoming HTTP traffic on port 80, and applying IP whitelisting to the traffic. It proxies requests to the application running on the specified port(s) on the host machine. The Python firewall script runs continuously, updates the whitelisted IPs from the bittensor metagraph and reloads Traefik every interval (default is 1200 sec or 20 minutes).

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
