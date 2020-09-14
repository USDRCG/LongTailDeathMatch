#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i 'cd /share/LongTailDeathMatch; export DISPLAY=:0.0; sudo ./tron_render.py; echo $i;'
done

