#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i 'echo 1a; cd /share/LongTailDeathMatch; echo 1b; export DISPLAY=:0.0; echo 1c; /share/LongTailDeathMatch/tron_render.py; echo 1d;'
done

