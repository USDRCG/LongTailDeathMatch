#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i /share/LongTailDeathMatch/kill-tron.sh
done
#bash /share/LongTailDeathMatch/kill-tron.sh
