# Start lightweight ufw firewall for entire machine. Runs every 20 min
pm2 start firewall.py --name "BittensorUFW" --interpreter "$(which python)"
