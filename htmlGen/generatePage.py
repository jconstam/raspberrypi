import os
import time
import csv
from datetime import date, timedelta

def main( ):
	pageTemplate = fileToStr( "/home/pi/raspberrypi/htmlGen/mainPageTemplate.htm" )

	time = getTime( )
	date = getDate( )
	sysinfo = getSysInfo( )

	data = getTemperatureData( )
	
	contents = pageTemplate.format( **locals( ) )
	strToFile( contents, "/var/www/index.html" )

def strToFile( text, filename ):
	output = open( filename, "w" )
	output.write( text )
	output.close( )

def fileToStr( filename ):
	fileHandle = open( filename, "r" )
	fileData = fileHandle.read( )
	fileHandle.close( )
	return fileData

def getTemperatureData( ):
	data = ""

	currdate = date.today( )

	while True:
		fileName = "/home/pi/raspberrypi/sysLogs/SysLog_" + currdate.strftime( "%Y%m%d" ) + ".csv"
		if not os.path.isfile( fileName ):
			break

		with open( fileName, 'rb' ) as csvfile:
			fileReader = csv.reader( csvfile, delimiter=',' )
			fileReader.next()
			for row in fileReader:
				data += "\t\t[ new Date( {0}, {1}, {2}, {3}, {4}, {5} ), {6}, {7} ],\n".format(
					currdate.strftime( "%Y" ),
					int( currdate.strftime( "%m" ) ) - 1,
					currdate.strftime( "%d" ),
					row[ 0 ][ 0:2 ],
					row[ 0 ][ 3:5 ],
					row[ 0 ][ 6:8 ],
					float( row[ 1 ] ) / 1000,
					float( row[ 2 ] ) )
	
		currdate = currdate - timedelta( days = 1 )

	return data

def getSysInfo( ):
	stream = os.popen( "uname -a" )
	returnData = stream.read( )
	stream.close( )

	return returnData

def getTime( ):
	return time.strftime( "%H:%M:%S" )

def getDate( ):
	return time.strftime( "%A %B %d" )

main( )
