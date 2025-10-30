#!/bin/bash 
ip=10.5.200.60
port=11000
echo "Synching dev to fabric studio LXC at ip=$ip port=$port"
rsync -av --exclude='settings.py' --rsh="ssh -p $port" /home/cgustave/github/python/packages/netcontrol/netcontrol root@$ip:/fabric/venv/lib/python3.9/site-packages


