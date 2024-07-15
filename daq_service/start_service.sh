#########################################################################
# File Name: exp.sh
# Author: dys
# Function:
# mail:
# Created Time: 2015年06月02日 星期二 16时47分14秒
#########################################################################
#!/bin/bash
#mydev是自己的设备名称，只有一台设备时/dev/PCH1020-0
#有第二台设备时/dev/PCH1020-1。依次类推...

bash ./install.sh

sudo kill -9 $(sudo lsof -t -i:8080)

mydev="/dev/acts3100-0"
if [ -c "$mydev"* ]; then
	if [ ! -r "$mydev"* ]; then
		sudo chmod 666 "$mydev"*
	fi
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:./lib
	./main
else
	echo "The Device "$mydev"* not exist!"
fi
