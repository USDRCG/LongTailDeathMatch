#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i 'cd /share/LongTailDeathMatch; export DISPLAY=:0.0; cat /etc/hostname; /share/LongTailDeathMatch/tron_render.py; echo 1d; python tron_master.py'
# add sudo to tron_render.py command to switch to full screens
done

