#!/bin/bash
for i in `cat tile-hosts.txt` 
do
    ssh -f $i 'cd /share/sandbox-cluster-guide-master/examples/LongtailDeathMatch/Parallel_Tron-master; export DISPLAY=:0.0; sudo ./tron_render.py'
done

