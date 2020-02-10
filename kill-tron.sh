#!/bin/bash
ps aux | grep "python ./tron*" | grep -v grep | awk '{print $2}' | xargs sudo kill
