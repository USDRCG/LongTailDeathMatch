#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i 'cd /share/LongTailDeathMatch; export DISPLAY=:0.0; echo 1a; /share/LongTailDeathMatch/tron_render.py; echo 1b;' >>output.txt
done

