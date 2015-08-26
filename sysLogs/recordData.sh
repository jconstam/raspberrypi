#!/bin/bash

DATE=$(date +%Y%m%d)
TIME=$(date +%H:%M:%S.%N)
TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
CPU=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}')
FILE_NAME="/home/pi/raspberrypi/sysLogs/SysLog_$DATE.csv"

if [ ! -e $FILE_NAME ]
then
	echo "Time, Temperature, CPU Usage" >> $FILE_NAME
fi

echo "$TIME, $TEMP, $CPU" >> $FILE_NAME
