import time
import bittensor as bt
import subprocess
import toml
import argparse
from typing import List, Dict, Set

def resync_metagraph(netuids: List[int]) -> Dict[int, List['bt.NeuronInfoLite']]:
    """
    Resynchronizes with the Bittensor metagraph and retrieves the neurons corresponding to the given netuids.

    :param netuids: List of netuids to synchronize with.
    :return: Dictionary with netuids as keys and corresponding neuron information as values.
    """
    bt.logging.info("resync_metagraph()")

    if isinstance(netuids, int): netuids = [netuids]

    new_neurons = {}
    for netuid in netuids:
        new_neurons[netuid] = subtensor.neurons_lite(netuid=netuid)
    
    bt.logging.info("Metagraph synced!")

    return new_neurons

def neurons_to_ips(all_neurons: Dict[int, List['bt.NeuronInfoLite']]) -> Set[str]:
    """
    Extracts the IPs of neurons that have validator permission (vpermit = True).

    :param all_neurons: Dictionary containing neuron information.
    :return: Set of IPs with validator permission.
    """
    bt.logging.info("neurons_to_ips()")

    validator_ips = set()
    for _, subnet_neurons in all_neurons.items():
        ips = [neuron.axon_info.ip for neuron in subnet_neurons if neuron.validator_permit]
        validator_ips.update(set(ips))
    
    return validator_ips

def whitelist_ips_in_ufw(ips):
    """
    Whitelists the provided IPs using Uncomplicated Firewall (UFW).

    :param ips: IPs to whitelist.
    """
    stop_cmd = "sudo ufw disable"
    reset_cmd = "echo y | sudo ufw reset"

    subprocess.run(stop_cmd, shell=True)
    subprocess.run(reset_cmd, shell=True)

    ssh_cmd = "sudo ufw allow ssh"
    subprocess.run(ssh_cmd, shell=True)
    for ip in ips:
        cmd = f"sudo ufw allow proto tcp from {ip}/16"
        subprocess.run(cmd, shell=True)
        bt.logging.info(f"Whitelisted IP {ip} for bittensor")

    start_cmd = "echo y | sudo ufw enable"
    subprocess.run(start_cmd, shell=True)

def whitelist_ips_in_iptables(ips: set):
    """
    Updates the iptables rules to whitelist the provided IPs for incoming traffic.
    :param ips: A set of IPs to whitelist.
    """
    # First, remove all existing rules related to Bittensor whitelist
    # (this step assumes a specific comment is used to identify these rules)
    subprocess.run("sudo iptables -D INPUT -m comment --comment 'bittensor-whitelist' -j ACCEPT", shell=True, stderr=subprocess.DEVNULL)

    # Now add rules for each IP in the set
    for ip in ips:
        cmd = f"sudo iptables -A INPUT -s {ip}/16 -m comment --comment 'bittensor-whitelist' -j ACCEPT"
        subprocess.run(cmd, shell=True)
        bt.logging.info(f"Whitelisted IP {ip} for bittensor")

def parse_arguments():
    """
    Parses command-line arguments.

    :return: Parsed arguments object.
    """
    parser = argparse.ArgumentParser(description="Run firewall")
    parser.add_argument('--netuid', help='Machine to connect to', choices=[1, 11, 21], default=[1, 11])
    parser.add_argument('--subtensor.chain_endpoint', dest='chain_endpoint', help='Subtensor node', type=str, required=False, default=None)
    parser.add_argument('--use_iptables', dest='use_iptables', help='Use iptables instead of UFW', action='store_true', default=False)
    parser.add_argument('--sleep_blocks', dest='sleep_blocks', help='Number of blocks to sleep between updates', type=int, default=100)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    # Connect to Bittensor network
    subtensor: 'bt.subtensor'
    if args.chain_endpoint:
        subtensor = bt.subtensor(network="finney", chain_endpoint=args.chain_endpoint)
    else:
        subtensor = bt.subtensor(network="finney")

    # Infinite loop to keep the metagraph synced and firewall updated
    while True:
        # Resync the metagraph
        neurons_dict = resync_metagraph(netuids = args.netuid)

        # Get the IPs of any neurons that have vpermit = True
        ips = neurons_to_ips(neurons_dict)
        
        # Whitelist the IPs in iptables or ufw (default ufw)
        if args.use_iptables:
            whitelist_ips_in_iptables(ips)
        else:
            whitelist_ips_in_ufw(ips)
        
        # Wait for N blocks (default approximately 1200 seconds or 20 minutes)
        bt.logging.info(f"Waiting for {args.sleep_blocks} blocks, sleeping")
        time.sleep(int(12*args.sleep_blocks))
