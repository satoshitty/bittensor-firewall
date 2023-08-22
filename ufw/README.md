Certainly! Here's the refactored README that incorporates the `start.sh` script to run the firewall script as a PM2 instance:

# Bittensor Lightweight Firewall with IP Whitelisting

Bittensor Lightweight Firewall is a nimble solution designed to synchronize with the Bittensor metagraph and whitelist IPs of specific neurons that have validator permission. This script leverages either Uncomplicated Firewall (UFW) or iptables to manage the whitelisting process, providing a straightforward approach for Linux-based systems.

## Prerequisites

- Python 3.x
- Bittensor
- Either UFW or iptables installed on the system
- PM2 (Process Manager 2)

## Features

- **Quick Setup**: Simple and efficient setup process.
- **Flexibility**: Choice between UFW or iptables for whitelisting, depending on user preference.
- **Dynamic Sync**: Continuous synchronization with the Bittensor metagraph.
- **Lightweight**: Minimal dependencies and low resource consumption.
- **Managed Execution**: Controlled execution using PM2, with scheduled restarts.

## Usage

1. **Install Dependencies:**
    ```bash
    pip install bittensor
    npm install pm2 -g
    ```

2. **Run the Start Script:**
    ```bash
    chmod +x start.sh
    ./start.sh
    ```

### Configuration

You can modify the `start.sh` script to customize the firewall behavior:

- `--netuid`: NetUID(s) to connect to (default: [1, 11]).
- `--subtensor.chain_endpoint`: Subtensor node endpoint (optional).
- `--use_iptables`: Use iptables instead of UFW for IP whitelisting (optional).
- `--sleep_blocks`: Number of blocks to sleep between updates (default: 100).

### `start.sh` Content

Modify the parameters according to your needs.

```bash
pm2 start firewall.py --name "BittensorUFW" \
    --interpreter "$(which python)" \
    -- \
    --netuid 1 \
    --subtensor.chain_endpoint <endpoint> \
    --sleep_blocks 100
```

## Conclusion

Bittensor Lightweight Firewall offers a streamlined approach to secure Bittensor network interactions through IP whitelisting. By integrating with PM2, it provides controlled execution, including scheduled restarts, making it an attractive choice for lightweight deployments. It offers a simple and low-overhead alternative to more complex solutions, suitable for users prioritizing efficiency and ease of use.
