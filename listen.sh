#!/bin/bash

./hooker.py &
sudo tcpdump -W 1 -C 1 -w sniff_logs.txt -i eth0 udp
