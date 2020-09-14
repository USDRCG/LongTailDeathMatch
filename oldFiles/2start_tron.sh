#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i 'echo 1a; cd /share2/LongTailDeathMatch; echo 1b; export DISPLAY=:0.0; echo 1c; cp -r /share2/LongTailDeathMatch /tmp; sudo /tmp/LongTailDeathMatch/tron_render.py >>/share2/LongTailDeathMatch/startOutput.txt; echo 1d;'
done

