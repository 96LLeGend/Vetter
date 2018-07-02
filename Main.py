import string
import hashlib
import cherrypy
import urllib
import urllib2
import sys
import socket
import json
import base64
import os
import mimetypes



import userDBCtrl
import profileDBCtrl
import messageDBCtrl
import helper
import webDesign
import blacklistDBCtrl



#To get the external IP Address
from urllib2 import urlopen
externalIPAddress = urlopen('http://ip.42.pl/raw').read()

#Find the local ip address
internalIPAddress = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

listen_port = 10006
listen_ip = "0.0.0.0"



#Cherrypy
class MainApp(object):

	#CherryPy Configuration
    	_cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : 'True',
                 }       	
	

		
	#List all API
	@cherrypy.expose
	def listAPI(self):
		listAPI = "/listAPI "
		default = "/default "
		index = "/index "
		firstTimeLogin = "/firstTImeLogin [username] [psw] [location] "
		userHome = "/userHome [username] [psw] "
		searchMessage = "/searchMessage [username] [psw] [userToShow] "
		logoff = "/logoff "
		displayProfile = "/displayProfile [username] [psw] [userToDisplay] "
		cahngeProfile = "/changeProfile [realName(opt)] [jobTitle(opt)] [description(opt)] [physicalLocation(opt)] [picture(opt)] [encoding(opt)] [encryption(opt)] [decryptionKey(opt)] "
		ping = "/ping [sender] "
		receiveMessage = "/receiveMessage [sender] [destination] [message] [stamp] [markdown(opt)] [encoding(opt)] [encryption(opt)] [hashing(opt)] [hash(opt)] [decryptionKey(opt)] "
		sendMessage = "/sendMessage [message] [destination] "
		getProfile = "/getProfile [profile_username] [sender] "
		receiveFile = "/receiveFile [sender] [destination] [file] [filename] [content_type] [stamp] [encryption(opt)] [hashing(opt)] [hash(opt)] [ecryptionKey(opt)] "
		sendFile = "/sendFile [destination] [fileToSend] "
		displayBlacklist = "/displayBlacklist [username] [psw] "
		addUserToBlacklist = "/addUserToBlacklist [username] [psw] [userToAdd] "
		removeUserFromBlacklist = "/removeUserFromBlacklist [username] [psw] [userToRemove] "

		return (listAPI + default + index + firstTimeLogin + userHome + searchMessage + logoff + displayProfile + cahngeProfile + ping + receiveMessage + sendMessage + getProfile + receiveFile + sendFile + displayBlacklist + addUserToBlacklist + removeUserFromBlacklist)		



	# If they try somewhere we don't know, catch it here and send them to the right place.
	@cherrypy.expose
	def default(self, *args, **kwargs):
        	"""The default page, given when we don't recognise where the request is for."""
        	cherrypy.response.status = 404

		#The page
        	return webDesign.defaultPage()

	

	#The login page
	@cherrypy.expose
	def index(self):
		
		#make databases for storing users' information and their Vee(messages) and files
		userDBCtrl.newUserDatabase()	#For all users' login status 
		profileDBCtrl.newProfileDatabase()	#For storing all users' profile
		messageDBCtrl.newMessageDatabase()	#For all the Vee(messages) and files
		blacklistDBCtrl.newBlacklistDatabase()	#For saving all the blacklist
		
		#Create a folder for downloading file		
		if not os.path.exists("myDownload"):
    			os.makedirs("myDownload")
	
		#The page
        	return webDesign.indexPage()

	

	#Get all the online user and their public key
	def getOnlineUser(self):
		
		#Get data from the data base
		userInformation = userDBCtrl.getCurrentUser()

		#All parameter /Report has
		postdata = {"username": userInformation[2], "password": userInformation[1], "enc": "0", "json": "0"}

		#Address
		dest = "http://cs302.pythonanywhere.com/getList"
	
		#Send
		fptr = urllib2.urlopen(dest, urllib.urlencode(postdata))

		#Read what that API return
		receiveData = fptr.read()
        	fptr.close()

		#Save the list(which from the login server's API) to the database for use later
		#Only Save the information if the we get the list successfully(first character = 0)
		if (receiveData[0] == "0"):
			userDBCtrl.updateOnlineUser(helper.decode(receiveData))
			return 1
		else:
			return 0
	


	#For the user to log on, required username, password and location from the user
	@cherrypy.expose
    	def firstTimeLogin(self, username, psw, location):

		#In the case of the user enter nothing but still hit "login", it go to error page directly
		#Only call the login API when the user enter something
		if (username != "" and psw != ""):		

			#Hash the password 
			hash_object = hashlib.sha256(psw + "COMPSYS302-2017")
			hex_dig = hash_object.hexdigest()

			#Determind which IP address should return. (location = 0 means office(UG Lab) destop,
			#1 means office(Uni) wifi, 2 means external network
			ipAdd = "0.0.0.0"
			if (location == "0" or location == "1"):
				ipAdd = internalIPAddress
			else:	
				ipAdd = externalIPAddress
			
			print(internalIPAddress)
			#Tell login server to login			
			postdata = {"username": username, "password": hex_dig, "location": location, "ip": ipAdd, "port": listen_port}#Json encode
			dest = "http://cs302.pythonanywhere.com/report"	#Address
			fptr = urllib2.urlopen(dest, urllib.urlencode(postdata)) #Send
			receiveData = fptr.read() #Read what that API return
        		fptr.close()	
			
			#Save current user and check online users only when log in successfully and check who is online
			#If the database doesn't have the current user's profile, set up a profile for him/her
			if (receiveData[0] == "0"):
				userDBCtrl.updateCurrentUser(username, hex_dig, location, ipAdd, listen_port)
				raise cherrypy.HTTPRedirect("/userHome?username="+username+"&psw="+hex_dig)
	
			#If login is not success, return error code
			else:
				#Display what the API return to the screen
				Page = receiveData
				Page += webDesign.assetErrorPage()
				return Page

		#If the user enter nothing when login
		else:
			return webDesign.assetErrorPage()			
	
	
	
	#Report to login server, for every 45 seconds(Threading)
	def login(self):

		#Get username and password
		currentUser = userDBCtrl.getCurrentUser()

		#Json encode
		postdata = {"username": currentUser[2], "password": currentUser[1], "location": currentUser[3], "ip": currentUser[4], "port": currentUser[5]}
		dest = "http://cs302.pythonanywhere.com/report"	#Address
		fptr = urllib2.urlopen(dest, urllib.urlencode(postdata)) #Send
		receiveData = fptr.read() #Read what that API return
        	fptr.close()	
	
	

	#The user's home page, which required a correct username and password to loaded
	@cherrypy.expose
	def userHome(self, username = None, psw = None):
		
		#Check if the page being loaded via long rather than loaded by tyre API directly
		#If the page loaded properly, display all the information, otherwise display a error message
		currentUser = userDBCtrl.getCurrentUser()
		
		#Page loaded via a proper way
		if (currentUser[1] == psw and currentUser[2] == username):	
			
			#Communicate with the login server
			self.login()
			
			#Update all signed up user
			self.getAllSigeUpUser()
			
			#Update online users
			self.getOnlineUser()
			onlineUsers = userDBCtrl.displayOnlineUser()
		
			#Check if there is new message(Vee)
			listOfVee = messageDBCtrl.getMessagesHistory()


			Page = webDesign.userHome(onlineUsers, currentUser, listOfVee)
		
		#The page loaded in a wrong way
		else:
			Page = webDesign.assetErrorPage()
			
		return Page
	

	
	#When the user search for message, this function will return all the message relate to that user
	@cherrypy.expose
	def searchMessage(self, username = None, psw = None, userToShow = None):
		
		#Check if the page being loaded via long rather than loaded by tyre API directly
		#If the page loaded properly, display all the information, otherwise display a error message
		currentUser = userDBCtrl.getCurrentUser()

		#Communicate with the login server
		self.login()
		
		#Page loaded via a proper way
		if (currentUser[1] == psw and currentUser[2] == username):	
		
			#get all vee first
			allVee = messageDBCtrl.getMessagesHistory()

			if(userToShow == None):
				return webDesign.messageHistory(currentUser, allVee)	#If the user enter nothing, show all message

			else:
				#Select those relate to the user's search to return
				filtedVee = []
				for i in range(0, len(allVee), 1):
					if (allVee[i][0] == userToShow or allVee[i][1] == userToShow):
						filtedVee.append(allVee[i])
				
				return  webDesign.messageHistory(currentUser, filtedVee)

		else:
			return webDesign.assetErrorPage()



        #For the user to log off
	@cherrypy.expose
	def logoff(self):		
		
		#Get data from the data base
		currentUser = userDBCtrl.getCurrentUser()	

		#All parameter /Report has
		postdata = {"username": currentUser[2], "password": currentUser[1], "enc": "0"}
		#Address
		dest = "http://cs302.pythonanywhere.com/logoff"	
		#Send
		fptr = urllib2.urlopen(dest, urllib.urlencode(postdata))

		#Read what that API return
		receiveData = fptr.read()
        	fptr.close()

		#If log off successfully, go to main menu, otherwise display the error code.
		#It should also reset all users' status to Offline and delete the current user's password from database
		if (receiveData[0] == "0"):
			userDBCtrl.resetCurrentUser()
			raise cherrypy.HTTPRedirect("/index")
		else:
			Page = receiveData
			Page += "</br>"		
			Page += "<a href='index'>return to main menu</a>"
        	return Page


	
	#The page for set up the user's personal profile, same as user homepage, can only be 
	#loaded after the user login successfully 
	@cherrypy.expose
	def displayProfile(self, username = None, psw = None, userToDisplay = None):
		
		#Get data from the data base
		currentUser = userDBCtrl.getCurrentUser()	

		#Communicate with the login server
		self.login()

		#Page loaded via a proper way
		if (currentUser[1] == psw and currentUser[2] == username):
			
			#The profile the user want to view is belong to himeself/herself, 
			#than just get the profile from data base		
			if(userToDisplay == currentUser[2]):
				profile = profileDBCtrl.getProfile(userToDisplay) #Get profile from database
				Page = webDesign.displayProfile(currentUser, profile, True)

			#If the user want to view other people's profile, go and ask for the profile first(for updating),
			#Then display it
			else:
				self.askForProfile(userToDisplay) #Ask for profile
				profile = profileDBCtrl.getProfile(userToDisplay) #Get profile from database
				Page = webDesign.displayProfile(currentUser, profile, False)
		
		#The page loaded in a wrong way
		else:
			Page = webDesign.assetErrorPage()
			
		return Page



	#This function can change the current user's profile
	@cherrypy.expose
	def changeProfile(self, realName = "-", jobTitle = "-", description = "-", physicalLocation = "-", picture = "-", encoding = "-", encryption = "-", decryptionKey = "-"):
		
		#Get data from the data base
		currentUser = userDBCtrl.getCurrentUser()
		
		#Update
		profileDBCtrl.updateUserProfile(currentUser[2], realName, jobTitle, description, physicalLocation, picture, encoding, encryption, decryptionKey)		

		#Back to profile page
		raise cherrypy.HTTPRedirect("/displayProfile?username="+currentUser[2]+"&psw="+currentUser[1]+"&userToDisplay="+currentUser[2])




	#This function will ask the login server for all the sign up user
	def getAllSigeUpUser(self):
		dest = "http://cs302.pythonanywhere.com/listUsers"	#Address
		fptr = urllib2.urlopen(dest) #Send
		receiveData = fptr.read() #Read what that API return
        	fptr.close()	
		
		#Make the string to a list
		listOfUsers = helper.decodeOneUser(receiveData)
		
		#Add to profile table and status table(initialize data)
		profileDBCtrl.updateUsers(listOfUsers)



	#For other user check if this user still online
	@cherrypy.expose
	def ping(self, sender):
		return "0"



	#For check if the destination node is currently online, if online, return a 1, otherwise 0
	def sendPing(self, destination):
		
		#Get data from the data base
		currentUser = userDBCtrl.getCurrentUser()	

		#If the data base don't have this user, that mean the user is not exist or the user haven't login yet
		destinationInfo = userDBCtrl.getUser(destination)
		
		if (destinationInfo == None or destinationInfo[3] != currentUser[3]):
			return "1" #Not online

		#If in different location
		elif (destinationInfo[3] != currentUser[3]):
			return "2"
		
		else:
			try:
				postdata = {"sender": currentUser[2]} #Parameter
				address = "http://" + destinationInfo[4] + ":" + destinationInfo[5] + "/ping" #IP address and port
			
				#Send
				fptr = urllib2.urlopen(address, urllib.urlencode(postdata))
			
				#Read what that API return
				receiveData = fptr.read()
				fptr.close()
				return receiveData
				
			except:
				return "3"
			
			

	#Other user can call this API to send messages to the current user
	@cherrypy.expose	
	@cherrypy.tools.json_in()
	def receiveMessage(self):
		
		#Decode 
		inputData = cherrypy.request.json	
		
		#Get current user from the data base
		currentUser = userDBCtrl.getCurrentUser()
			
		#Determined what error code to return
 		if (inputData.get('sender') == None or inputData.get('destination') == None or inputData.get('message') == None or inputData.get('stamp') == None):
			return "1: Missing Compulsory Field"
		
		#The message is not for the current user
		elif (inputData.get('destination') != currentUser[2]):
			return "6: Insufficient Permissions"

		#The user is not authenticated
		elif (userDBCtrl.getUser(inputData.get('sender')) == None or not profileDBCtrl.getProfile(inputData.get('sender'))):
			return "2: Unauthenticated User"

		#Check if the sender is in blacklist or not, if he/she is in the blacklist, don't save and display the message, 
		elif (blacklistDBCtrl.isBlacklisted(currentUser[2], inputData.get('sender'))):
			return "11: Blacklisted or Rate Limited"

		else:
			#Save the message
			messageDBCtrl.addMessage(inputData.get('sender'), inputData.get('destination'), inputData.get('message'), inputData.get('stamp'), inputData.get('markdown'), inputData.get('encoding'), inputData.get('encryption'), inputData.get('hashing'), inputData.get('hash'), inputData.get('decryptionKey'))
	
			return "0: <Action was successful>"
		
		

	#This function is used for sending Vee(Message) to other user, the file upload only occur when the destination 
	#file is not empty, the user database has the the destination node's ip data and the destination node 
	#is response to the ping
	@cherrypy.expose
	def sendMessage(self, message, destination):
		if (destination != None):
			
			#Get data from the data base
			currentUser = userDBCtrl.getCurrentUser()
			#Get the destination user's IP address and port number
			destinationInfo = userDBCtrl.getUser(destination)
			
			#If the data base don't have this user, that mean the user is not exist or the user
			#haven't login for at least one time yet
			if (destinationInfo == None):
				#return 0 #Not online
				print("===>>IP address is not found")
			
			#If in different location
			elif (destinationInfo[3] != currentUser[3]):
				print("===>>Location error")
			
			else:
				#Ping the target user to make sure he/she is on this IP address
				if (self.sendPing(destination) == "0"):

					try:
						#Parameter in Json object
						postdata = json.dumps({"sender" : currentUser[2], "destination" : destination, "message" : message, "stamp" : helper.getCurrentEpochTime()}) 
						#IP address and port
						address = "http://" + destinationInfo[4] + ":" + destinationInfo[5] + "/receiveMessage" 

						#Send
						fptr = urllib2.urlopen(urllib2.Request(address, postdata, {'Content-Type':'application/json'}))					
	
						#Read what that API return
						receiveData = fptr.read()
						fptr.close()

						#Read the read the return code, if "0", then mean the sending is successful,
						#otherwise the sending is fail
						if (receiveData[0] == "0"):
							#If the sending is successful, save it on locat storage as history.
							messageDBCtrl.addMessage(currentUser[2], destination, message, helper.getCurrentEpochTime())
							#return 1
							print("===>>Success")
						else:
							#return 0
							print(receiveData)
					except:
						print("===>>Network error")

				else:
					#The destination user is not online(Pind return nothing)
					print("===>>Ping has no response")

		#Return to home page		
		raise cherrypy.HTTPRedirect("/userHome?username="+currentUser[2]+"&psw="+currentUser[1])
					


	#Other user call this API to get this user's personal profile
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def getProfile(self):

		#Decode
		inputData = cherrypy.request.json			

		#Only return the profile if the sender is a currently online user, don't return when 
		#someone else asking(who know who is that person?), instead, return a warning
		if(userDBCtrl.getUser(inputData.get('sender')) != None):
			
			#Search profile from the database
			profileReturn = profileDBCtrl.getProfile(inputData.get('profile_username'))
			
			response = {"fullname" : profileReturn[1], "position" : profileReturn[2], "description" : profileReturn[3], "location" : profileReturn[4], "picture" : profileReturn[5], "encoding" : profileReturn[6], "encryption" : profileReturn[7], "decryptionKey" : profileReturn[8]}

			return json.dumps(response) #Json encode
		else:
			return json.dumps({"fullname" : "invalid sender"}) 



	#This function is used for asking other online user for their profile, it will return the error code to indicate if 
	#the the profile is downloaded successfully or not. Some feedback will display on the command window.
	def askForProfile(self, profile_username):
		
		#Get the destination user's IP address and port number
		destinationInfo = userDBCtrl.getUser(profile_username)
		#Get data from the data base
		currentUser = userDBCtrl.getCurrentUser()
			
		#If the online user data base don't have this user's ip address, that mean the user 
		#is not exist or the user haven't login yet, so it won't be possible to ask for profile
		if (destinationInfo == None):
			print("===>>IP address is not found")

		#If in different location
		elif (destinationInfo[3] != currentUser[3]):
			print("===>>The user is in different location")
		
		else:
			#inputData = cherrypy.request.json			

		#Only return the profile if the sender is a currently online user(ping has response)
			if (self.sendPing(profile_username) == "0"):
						
				try:
					postdata = json.dumps({"profile_username" : profile_username, "sender" : currentUser[1]}) #Json encode
					address = "http://" + destinationInfo[4] + ":" + destinationInfo[5] + "/getProfile" #IP address and port
										
					#Send
					fptr = urllib2.urlopen(urllib2.Request(address, postdata, {'Content-Type':'application/json'}))
				
					#Read what that API return
					receiveJson = fptr.read()
					fptr.close()				

					#Insert the data to database
					receiveData = json.loads(receiveJson)
					profileDBCtrl.updateUserProfile(profile_username, receiveData.get('fullname'), receiveData.get('position'), receiveData.get('description'), receiveData.get('location'), receiveData.get('picture'), receiveData.get('encoding'), receiveData.get('encryption'), receiveData.get('decryptionKey'))

					print("===>>Success")
				except:
					print("===>>Network error")
			else:		
				print("===>>Ping has no response")
			


	#Other user can call this API to send messages to the current user
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def receiveFile(self):

		#Decode
		inputData = cherrypy.request.json

		#Get data from the data base
		currentUser = userDBCtrl.getCurrentUser()

		#Determined what error code to return
 		if (inputData.get('sender') == None or inputData.get('destination') == None or inputData.get('file') == None or inputData.get('filename') == None or inputData.get('content_type') == None or inputData.get('stamp') == None):
			return "1: Missing Compulsory Field"
		
		#The file is not for the current user
		elif (inputData.get('destination') != currentUser[2]):
			return "6: Insufficient Permissions"

		#The user is not authenticated
		elif (userDBCtrl.getUser(inputData.get('sender')) == None or not profileDBCtrl.getProfile(inputData.get('sender'))):
			return "2: Unauthenticated User"

		#Check if the sender is in blacklist or not, if he/she is in the blacklist, don't save and display the message, 
		elif (blacklistDBCtrl.isBlacklisted(currentUser[2], inputData.get('sender'))):
			return "11: Blacklisted or Rate Limited"
		else:
			#Check the size of the file, according to how base64 encoding work, not 100% accurate but close enough
			size = len(inputData.get('file')) * 6 / 8

			#Decode the file from base 64
			downloadedFile = base64.b64decode(inputData.get('file'))

			#Save the file on local
			localFile = open("myDownload/"+str(inputData.get('filename')),"w+")
			localFile.write(downloadedFile)
			localFile.close() 
			
			#Add the record to the database
			messageDBCtrl.addMessage(inputData.get('sender'), inputData.get('destination'), "File : "+str(inputData.get('filename')), inputData.get('stamp'), inputData.get('encryption'), inputData.get('hashing'), inputData.get('Hash'), inputData.get('decryptionKey'))
			return "0: <Action was successful>"



	#This function is used for sending file to other user, the file upload only occur when the destination 
	#file is not empty, the user database has the the destination node's ip data and the destination node 
	#is response to the ping
	@cherrypy.expose
	def sendFile(self, destination, fileToSend):
		if (destination != None):

			#Get currentUser's data from the data base
			currentUser = userDBCtrl.getCurrentUser()
			#Get the destination user's IP address and port number
			destinationInfo = userDBCtrl.getUser(destination)
			
			#If the data base don't have this user, that mean the user is not exist or the user haven't login yet
			if (destinationInfo == None):
				print("===>>IP address is not found")

			#If in different location
			elif (destinationInfo[3] != currentUser[3]):
				print("===>>The user is in different location")
			
			else:
				#Ping the target user to make sure he/she is on this IP address
				if (self.sendPing(destination) == "0"):
				#if(True):
					
					#Read and encode the file
					rawData = fileToSend.file.read()
					codedData = base64.b64encode(rawData)
					
					try:
						#Json encode	
						postdata = json.dumps({"sender" : currentUser[2], "destination" : destination, "file" : codedData, "filename" : str(fileToSend.filename), "content_type" : str(fileToSend.content_type), "stamp" : helper.getCurrentEpochTime()}) 			
			
						#IP address and port
						address = "http://" + destinationInfo[4] + ":" + destinationInfo[5] + "/receiveFile" 

						#Send
						fptr = urllib2.urlopen(urllib2.Request(address, postdata, {'Content-Type':'application/json'}))
						#Read what that API return
						receiveData = fptr.read()
						fptr.close()
					
						#Read the read the return code, if "0", then mean the sending is successful,
						#otherwise the sending is fail
						if (receiveData[0] == "0"):
							#If the sending is successful, save it on locat storage as history.
							messageDBCtrl.addMessage(currentUser[2], destination, "File: "+str(fileToSend.filename), helper.getCurrentEpochTime())
							print("===>>Success")	
						else:
							print(receiveData)
					except:
						print("===>>Network error")

				else:
					#The destination user is not online(Pind return nothing)
					print("===>>Ping has no response")
		
		#Return to home page		
		raise cherrypy.HTTPRedirect("/userHome?username="+currentUser[2]+"&psw="+currentUser[1])



	#Show the current user's blacklist, with option to add and remove as well
	@cherrypy.expose
	def displayBlacklist(self, username = None, psw = None):
		#Get currentUser's data from the data base
		currentUser = userDBCtrl.getCurrentUser()

		#Communicate with the login server
		self.login()
	
		#Required correct user name and pasword to load the page
		if (currentUser[1] == psw and currentUser[2] == username):	
			
			#Get the blacklist of this user	
			blacklist = blacklistDBCtrl.getBlacklist(currentUser[2])
			return webDesign.blacklistPage(currentUser, blacklist)

		else:
			return webDesign.assetErrorPage()


	#Add the user to current user's blacklist
	@cherrypy.expose
	def addUserToBlacklist(self, username = None, psw = None, userToAdd = None):
		#Get currentUser's data from the data base
		currentUser = userDBCtrl.getCurrentUser()
	
		#Required correct user name and pasword to load the page
		if (currentUser[1] == psw and currentUser[2] == username):
			#Add to blacklist
			blacklistDBCtrl.addToBlacklist(currentUser[2], userToAdd)
			#return to the page
			raise cherrypy.HTTPRedirect("/displayBlacklist?username="+currentUser[2]+"&psw="+currentUser[1])
	
		else:
			return webDesign.assetErrorPage()



	#Remove user from current user's blacklist
	@cherrypy.expose
	def removeUserFromBlacklist(self, username = None, psw = None, userToRemove = None):
		#Get currentUser's data from the data base
		currentUser = userDBCtrl.getCurrentUser()
	
		#Required correct user name and pasword to load the page
		if (currentUser[1] == psw and currentUser[2] == username):	
			#Remove from blacklist
			blacklistDBCtrl.removeFromBlacklist(currentUser[2], userToRemove)
			#return to the page
			raise cherrypy.HTTPRedirect("/displayBlacklist?username="+currentUser[2]+"&psw="+currentUser[1])

		else:
			return webDesign.assetErrorPage()

	

def runMainApp():

	# Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
	cherrypy.tree.mount(MainApp(), "/")

	# Tell Cherrypy to listen for connections on the configured address and port.
	cherrypy.config.update({'server.socket_host': listen_ip,
		                'server.socket_port': listen_port,
		                'engine.autoreload.on': True,		
		                  })
	print "========================="
	print "Vetter start"
	print "========================="                       
	    
	# Start the web server
	cherrypy.engine.start()

	# And stop doing anything else. Let the web server take over.
	cherrypy.engine.block()



#Run the function to start everything
runMainApp()




