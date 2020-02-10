#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i /share/sandbox-cluster-guide-master/examples/LongtailDeathMatch/Parallel_Tron-master/kill-tron.sh
done
