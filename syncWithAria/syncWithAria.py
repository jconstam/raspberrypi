import os
import time
import xmlrpclib

class DownloadFile:
	def __init__( self, filePath, sourceRootFolder, destRootFolder,
			localTempRootFolder, remoteTempRootFolder,
			HTTPSbase, serverURL ):
		self.set_filePath( filePath )
		self.set_sourceRootFolder( sourceRootFolder )
		self.set_destRootFolder( destRootFolder )
		self.set_localTempRootFolder( localTempRootFolder )
		self.set_remoteTempRootFolder( remoteTempRootFolder )
		self.set_HTTPSbase( HTTPSbase )
		self.set_serverURL( serverURL )

	def get_filePath( self ):
		return self.__filePath
	def set_filePath( self, newFilePath ):
		self.__filePath = newFilePath

	def get_sourceRootFolder( self ):
		return self.__sourceRootFolder
	def set_sourceRootFolder( self, newSourceRootFolder ):
		self.__sourceRootFolder = newSourceRootFolder

	def get_destRootFolder( self ):
		return self.__destRootFolder
	def set_destRootFolder( self, newDestRootFolder ):
		self.__destRootFolder = newDestRootFolder

	def get_localTempRootFolder( self ):
		return self.__localTempRootFolder
	def set_localTempRootFolder( self, newLocalTempRootFolder ):
		self.__localTempRootFolder = newLocalTempRootFolder

	def get_remoteTempRootFolder( self ):
		return self.__remoteTempRootFolder
	def set_remoteTempRootFolder( self, newRemoteTempRootFolder ):
		self.__remoteTempRootFolder = newRemoteTempRootFolder

	def get_HTTPSbase( self ):
		return self.__HTTPSbase
	def set_HTTPSbase( self, newHTTPSbase ):
		self.__HTTPSbase = newHTTPSbase

	def get_serverURL( self ):
		return self.__serverURL
	def set_serverURL( self, newServerURL ):
		self.__serverURL = newServerURL
		self.__server = xmlrpclib.ServerProxy( self.__serverURL ) 

	def get_GID( self ):
		return self.__gid
	def set_GID( self, newGID ):
		self.__gid = newGID

	def get_status( self ):
		return self.__status
	def set_status( self, newStatus ):
		self.__status = newStatus

	@property
	def relPath( self ):
		return self.__filePath[ len( self.__sourceRootFolder ) : ]
	@property
	def sourcePath( self ):
		return self.__sourceRootFolder + self.relPath
	@property
	def sourceFolder( self ):
		return self.sourcePath[ : self.sourcePath.rfind( '/' ) ]
	@property
	def destPath( self ):
		return self.__destRootFolder + self.relPath
	@property
	def destFolder( self ):
		return self.destPath[ : self.destPath.rfind( '/' ) ]
	@property
	def localTempPath( self ):
		return self.__localTempRootFolder + self.relPath
	@property
	def localTempFolder( self ):
		return self.localTempPath[ : self.localTempPath.rfind( '/' ) ]
	@property
	def remoteTempPath( self ):
		return self.__remoteTempRootFolder + self.relPath
	@property
	def remoteTempFolder( self ):
		return self.remoteTempPath[ : self.remoteTempPath.rfind( '/' ) ]
	@property
	def HTTPSURI( self ):
		return self.__HTTPSbase + self.relPath

	def StartDownload( self ):
		self.set_GID( self.__server.aria2.addUri( [ self.HTTPSURI ], 
			dict( dir=self.remoteTempFolder ) ) )

	def UpdateStatus( self ):
		self.set_status( self.__server.aria2.tellStatus( 
					self.__gid, [ 'status' ] )[ 'status' ] )
		return self.get_status( )

	def MoveFromTemp( self ):
		if not self.__status == 'complete':
			os.remove( self.localTempPath )	
		else:
			os.remove( self.sourcePath )
			if not os.path.isdir( self.destFolder ):
				os.mkdir( self.destFolder )
			os.rename( self.localTempPath, self.destPath )

	def __str__( self ):
		return self.remoteTempFolder

def main( ):
	ariaRPCURL = 'http://192.168.1.11:6800/rpc'
	HTTPSbase = 'https://dorado.whatbox.ca/private/Completed/'
	sourceFolder = '/media/Whatbox/Completed/'
	destFolder = '/media/Temporary/Completed/'
	localTempFolder = '/media/Temporary/Temporary/'
	remoteTempFolder = '/mnt/DroboFS/Shares/Temporary/Temporary/'

	sourceFilePathList = findFilesAtSource( sourceFolder )
	fileList = setupFileList( sourceFilePathList, sourceFolder, destFolder, 
					localTempFolder, remoteTempFolder,
					HTTPSbase, ariaRPCURL )
	addFilesToAria( fileList )
	monitorDownloads( fileList )
	cleanup( fileList )

def printList( fileList ):
	print [ str( x ) for x in fileList ]

def findFilesAtSource( sourceFolder ):
	files = []
	for root, dirnames, fileNames in os.walk( sourceFolder ):
		for currFile in fileNames:
			files.append( os.path.join( root, currFile ) )
	return files

def setupFileList( sourceFilePathList, sourceFolder, destFolder,
			localTempFolder, remoteTempFolder, HTTPSbase, serverURL ):
	return [ DownloadFile( currFile, sourceFolder, destFolder,
			localTempFolder, remoteTempFolder, HTTPSbase, serverURL )
		for currFile in sourceFilePathList ]

def addFilesToAria( fileList ):
	map( lambda currFile: currFile.StartDownload( ), fileList )

def monitorDownloads( fileList ):
	downloadInProgress = True
	while downloadInProgress:
		statuses = { 
			'active' : 0,	'waiting' : 0,	'paused' : 0,	
			'error' : 0,	'complete' : 0,	'removed' : 0
			}

		downloadInProgress = False
		for currFile in fileList:
			currStatus = currFile.UpdateStatus( )
	
			statuses[ currStatus ] = statuses[ currStatus ] + 1

			if currStatus == 'complete' or currStatus == 'error':
				downloadInProgress = downloadInProgress | False
			else:
				downloadInProgress = downloadInProgress | True

		os.system( 'clear' )
		print time.strftime( '%Y-%m-%d %H:%M:%S', time.gmtime( ) )
		print statuses
		time.sleep( 1 )

def cleanup( fileList ):
	map( lambda currFile: currFile.MoveFromTemp( ), fileList )

main( )
