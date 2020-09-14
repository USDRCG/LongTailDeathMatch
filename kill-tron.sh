 #!/bin/bash
#ps aux | grep "tron" | grep -v grep | awk '{print $2}' | xargs sudo kill -9
ps aux | grep "python ./tron*" | grep -v grep | awk '{print $2}' | xargs sudo kill
