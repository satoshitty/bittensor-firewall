
import bittensor
from typing import Optional
import argparse
from time import time
from types import SimpleNamespace
from munch import Munch
import sys

block_time = 12  # seconds
protocol = 4  # Constant
port = 8123  # Constant


def main(config: "bittensor.config") -> 0:
    bittensor.__use_console__ = False
    if config.subtensor.chain_endpoint == "":
        config.subtensor.chain_endpoint = bittensor.__finney_entrypoint__

    sub: "bittensor.Subtensor" = bittensor.subtensor(
        network="finney",
        chain_endpoint=config.subtensor.chain_endpoint,
    )
    wallet = bittensor.wallet(
        name=config.wallet.name,
        hotkey=config.wallet.hotkey,
        path=config.wallet.path,
    )
    wallet.hotkey

    netuid = config.netuid

    ip_addr = bittensor.utils.networking.get_external_ip()

    # Get axon
    print("Getting current axon from chain...")
    axon_info: Optional["SimpleNamespace"]
    last_axon_update: int = 0
    axon_info_result = sub.query_subtensor(
        "Axons", params=[netuid, wallet.hotkey.ss58_address]
    )
    if axon_info_result != None:
        value = Munch(axon_info_result.value)
        axon_info = SimpleNamespace(
            ip=bittensor.utils.networking.int_to_ip(value.ip),
            ip_type=value.ip_type,
            port=value.port,
            protocol=value.protocol,
            version=value.version,
            placeholder1=value.placeholder1,
            placeholder2=value.placeholder2,
        )
        last_axon_update = value.block
    else:
        print("No axon found, assuming no axon yet")

    print("Comparing axon to current ip...")
    if axon_info and axon_info.ip == ip_addr:
        print("Axon is up to date")
        return 0

    print("Axon is out of date, attempting to update...")

    bittensor.__version_as_int__ = (
        axon_info.version if axon_info and hasattr(axon_info, "version") else 533
    )

    # Check if axon rate-limit is fine
    print("Checking axon rate-limit...")
    limit: int = 0
    limit_result = sub.query_subtensor("ServingRateLimit", params=[netuid])
    if limit_result is None:
        print("No rate-limit found, assuming 0")
    else:
        limit = limit_result.value

    curr_block = sub.get_current_block()

    wait_time_blocks = limit - (curr_block - last_axon_update)
    wait_time = wait_time_blocks * block_time
    if wait_time > 0:
        print(
            f"Axon was updated too recently, need to try again in {wait_time} seconds"
        )

        if wait_time > 60:
            print("Waiting for more than a minute, exiting")
            return 0
        else:
            print(f"Waiting for {wait_time} seconds")
            time.sleep(wait_time)
            return main(config)

    print("Updating axon on chain...")
    call_params = {
        "version": bittensor.__version_as_int__,
        "ip": bittensor.utils.networking.ip_to_int(ip_addr),
        "port": port,
        "ip_type": bittensor.utils.networking.ip_version(ip_addr),
        "netuid": netuid,
        "hotkey": wallet.hotkey.ss58_address,
        "coldkey": wallet.coldkeypub.ss58_address,
        "protocol": protocol,
        "placeholder1": axon_info.placeholder1,
        "placeholder2": axon_info.placeholder2,
    }

    success, error_message = sub._do_serve_axon(
        wallet=wallet,
        call_params=call_params,
        wait_for_finalization=True,
        wait_for_inclusion=True,
    )

    if success == True:
        print(
            f"Axon served with: AxonInfo({wallet.hotkey.ss58_address},{ip_addr}:{port}) on {sub.network}:{netuid} "
        )
        return 0
    else:
        print(f"!!! Axon failed to served with error: {error_message} ")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wallet.name",
        "--wallet.coldkey",
        "--name",
        "-w",
        type=str,
        required=True,
        help="Name of the wallet to use.",
    )
    parser.add_argument(
        "--wallet.hotkey",
        "--hotkey",
        "-k",
        type=str,
        required=True,
        help="Name of the hotkey to use.",
    )
    parser.add_argument(
        "--wallet.path",
        "-p",
        type=str,
        required=False,
        help="Path to the wallets directory.",
        default="~/.bittensor/wallets",
    )
    parser.add_argument(
        "--netuid",
        "-n",
        type=int,
        required=False,
        default=11,
    )
    parser.add_argument(
        "--subtensor.chain_endpoint",
        "--endpoint",
        "-e",
        type=str,
        required=False,
        default="",
    )

    config = Munch()
    params = parser.parse_args()
    # Splits params on dot syntax i.e neuron.axon_port
    # The is_set map only sets True if a value is different from the default values.
    for arg_key, arg_val in params.__dict__.items():
        split_keys = arg_key.split(".")
        head = config
        keys = split_keys
        while len(keys) > 1:
            if hasattr(head, keys[0]):
                head = getattr(head, keys[0])
                keys = keys[1:]
            else:
                head[keys[0]] = Munch()
                head = head[keys[0]]
                keys = keys[1:]
        if len(keys) == 1:
            head[keys[0]] = arg_val

    err_code = main(config) 
    sys.exit(err_code)
