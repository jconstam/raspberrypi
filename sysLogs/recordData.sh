#!/bin/bash

DATE=$(date +%Y%m%d)
TIME=$(date +%H:%M:%S.%N)
TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
CPU=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}')
OUTPUT_DIR="/home/pi/raspberrypi/sysLogs"
FILE_NAME="$OUTPUT_DIR/SysLog_$DATE.csv"
TEMP_DIR="$OUTPUT_DIR/Temp"
ARCHIVE_FILE="$OUTPUT_DIR/ArchivedSysLogs.tar.gz"
NUM_FILES_TO_KEEP=3

if [ ! -e $FILE_NAME ]
then
	echo "Time, Temperature, CPU Usage" >> $FILE_NAME
fi

echo "$TIME, $TEMP, $CPU" >> $FILE_NAME

FILE_COUNT=$(ls -l $OUTPUT_DIR/SysLog_* | wc -l)
if [ "$FILE_COUNT" -gt "$NUM_FILES_TO_KEEP" ]
then
	ARCHIVE_COUNT=$((FILE_COUNT - NUM_FILES_TO_KEEP))
	ARCHIVE_NEW_FILES=$(ls SysLog_* | head -n $ARCHIVE_COUNT)

	if [ -e "$ARCHIVE_FILE" ]
	then
		mkdir -p $TEMP_DIR
		tar -xzf $ARCHIVE_FILE -C $TEMP_DIR
		for file in $ARCHIVE_NEW_FILES
		do
			mv $file $TEMP_DIR
		done
		rm -rf $ARCHIVE_FILE
		ARCHIVE_NEW_FILES=$(cd $TEMP_DIR && ls SysLog_*)
		cd $TEMP_DIR && tar -czf $ARCHIVE_FILE $ARCHIVE_NEW_FILES
		rm -rf $TEMP_DIR
	else
		tar -czf $ARCHIVE_FILE $ARCHIVE_NEW_FILES
		rm -rf $ARCHIVE_NEW_FILES
	fi
fi
