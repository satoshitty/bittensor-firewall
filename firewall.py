import bittensor as bt
import subprocess
import toml
import argparse
import os
import grp
from typing import List, Dict, Set

# Function to run Docker command with or without sudo based on user's permissions
def run_docker_command(command):
    # Check if the user is root or in the docker group
    if os.getuid() == 0 or "docker" in [g.gr_name for g in grp.getgrall() if os.getlogin() in g.gr_mem]:
        docker_command = ["docker"]
    else:
        docker_command = ["sudo", "docker"]
    # Execute the command
    subprocess.run(docker_command + command)

# Function to resynchronize with the Bittensor metagraph
def resync_metagraph(netuids: List[int]) -> Dict[int, List['bt.NeuronInfoLite']]:
    bt.logging.info("resync_metagraph()")
    # Handle single or multiple netuids
    if isinstance(netuids, int): netuids = [netuids]
    new_neurons = {}
    for netuid in netuids:
        new_neurons[netuid] = subtensor.neurons_lite(netuid=netuid)
    bt.logging.info("Metagraph synced!")
    return new_neurons

# Function to get the IPs of any neurons that have vpermit = True
def neurons_to_ips(all_neurons: Dict[int, List['bt.NeuronInfoLite']]) -> Set[str]:
    bt.logging.info("neurons_to_ips()")
    validator_ips = set()
    for _, subnet_neurons in all_neurons.items():
        ips = [neuron.axon_info.ip for neuron in subnet_neurons if neuron.validator_permit]
        validator_ips.update(set(ips))
    return validator_ips

# Function to whitelist IPs in Traefik
def whitelist_ips_in_traefik(ips: List[str]):
    # Transform the IPs to a specific format
    ip_list = [ip.split(".")[0] + "." + ip.split(".")[1] + '.0.0/16' for ip in ips]
    # Update the dynamic configuration file
    config = {
        "http": {
            "middlewares": {
                "myipwhitelist": {
                    "ipWhiteList": {
                        "sourceRange": ip_list
                    }
                }
            }
        }
    }
    with open('dynamic_conf/middlewares.toml', 'w') as file:
        toml.dump(config, file)

# Function to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run firewall")
    parser.add_argument('--netuid', help='Subnet(s) to add firewall to', choices=[1, 11, 21], default=1, type=int, nargs='+')
    parser.add_argument('--subtensor.chain_endpoint', dest='chain_endpoint', help='Subtensor node', type=str, required=False, default=None)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    # Connect to Bittensor network
    subtensor = bt.subtensor(network="finney", chain_endpoint=args.chain_endpoint) if args.chain_endpoint else bt.subtensor(network="finney")
    # Resync the metagraph
    neurons_dict = resync_metagraph(netuids=args.netuid)
    # Get the IPs of any neurons that have vpermit = True
    ips = neurons_to_ips(neurons_dict)
    # Whitelist the IPs in Traefik
    whitelist_ips_in_traefik(ips)
