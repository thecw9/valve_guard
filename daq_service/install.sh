#!/bin/sh
if [ $(getconf WORD_BIT) = '32' ] && [ $(getconf LONG_BIT) = '64' ] ; then
    sudo insmod drv64/acts3100.ko
	cp drv64/libacts3100.so ../app/lib/libacts3100.so
	echo "install 64bit lib success"
else    
    sudo insmod drv32/acts3100.ko
	cp drv32/libacts3100.so ../app/lib/libacts3100.so
	echo "install 32bit lib success"
fi
