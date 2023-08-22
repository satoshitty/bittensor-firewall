# Test docker image

This will help you quickly test if traefik is configured properly by setting up a hello world docker image, running it, setting up traefik, running it, and attempting to query the application from localhost through the traefik whitelist middleware.  Initially is set to allow all IPs but after running `firewall.py` will be updated to Bittensor metagraph axon IPs.

## Usage

Simply run the `test.sh` script from the the `test` directory.
```
cd test
bash test.sh
```