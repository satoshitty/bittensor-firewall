import time
import bittensor as bt
import subprocess
import toml
import argparse
from typing import List, Dict, Set

# Function to resynchronize with the Bittensor metagraph
def resync_metagraph(netuids: List[int]) -> Dict[int, List['bt.NeuronInfoLite']]:
    bt.logging.info("resync_metagraph()")

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
    ips = ['"' + ip.split(".")[0] + "." + ip.split(".")[1] + '.0.0/16"' for ip in ips]
    ip_list = ', '.join(ips)

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
    with open('dynamic_conf/ip_whitelist.toml', 'w') as file:
        toml.dump(config, file)

    # Notify Traefik to reload its configuration
    subprocess.run(["docker", "stop", "traefik"])
    subprocess.run(["docker", "start", "traefik"])

# Function to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run firewall")
    parser.add_argument('--netuid', help='Subnet(s) to add firewall to', choices=[1, 11, 21], default=1, type=int, nargs='+')
    parser.add_argument('--subtensor.chain_endpoint', dest='chain_endpoint', help='Subtensor node', type=str, required=False, default=None)
    parser.add_argument('--sleep-blocks', dest='sleep_blocks', help='Number of blocks to sleep between updates', type=int, required=False, default=100)
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
        
        # Whitelist the IPs in Traefik
        whitelist_ips_in_traefik(ips)
        
        # Wait for N blocks (default approximately 1200 seconds or 20 minutes)
        bt.logging.info(f"Waiting for {args.sleep_blocks} blocks, sleeping")
        time.sleep(int(args.sleep_blocks*12))
