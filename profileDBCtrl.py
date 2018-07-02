import sqlite3



"""This is the profile database controller"""



##########Display the profile table(for testing)
def printProfileTable():
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	for row in newCursor.execute("SELECT * FROM profile"):
        	print row
	newConnection.close()



#Create a database for storing all user's p 
#There information it stores are: 
#user, realName, jobTitle, description, physicalLocation, picture, encoding, encryption, decryptionKey
def newProfileDatabase():

	newConnection = sqlite3.connect('vetterData.db')	#Connect to the database
	newCursor = newConnection.cursor()	#New cursor
	
	try:
		#Create table for saving the online user list
		newCursor.execute('''CREATE TABLE profile(user, realName, jobTitle, description, physicalLocation, picture, encoding, encryption, decryptionKey)''')
		newConnection.commit()

	except sqlite3.OperationalError as e:
		return 0;	#do nothing	
			
	newConnection.close()	#Close connection
	


#Add/update users' profile 
def updateUserProfile(user, realName, jobTitle, description, physicalLocation, picture, encoding, encryption, decryptionKey):

	#Connect to the database and make a cursor for controllin
	newConnection = sqlite3.connect('vetterData.db')	
	newCursor = newConnection.cursor()	
	
	#Find if the database already has the current user's profile
	found = False;
	for row in newCursor.execute("SELECT * FROM profile"):
        	if (row[0] == user):
			found = True

	#Go into the database and make cursor
	newConnection = sqlite3.connect('vetterData.db')	
	newCursor = newConnection.cursor()	

	#If the profile is founud, just update the field that has changed, 
	#the field that haven't change(indicate by "-") will be ignored
	if (found):
			
		if (realName != ""): #Update real name
			newCursor.execute("UPDATE profile SET realName = ? WHERE user = ?", (realName, user,))

		if (jobTitle != ""): #Update job title
			newCursor.execute("UPDATE profile SET jobTitle = ? WHERE user = ?", (jobTitle, user,))

		if (description != "" and description != "-"): #Update description
			newCursor.execute("UPDATE profile SET description = ? WHERE user = ?", (description, user,))
			
		if (physicalLocation != ""):	#Update physicalLocation
			newCursor.execute("UPDATE profile SET physicalLocation = ? WHERE user = ?", (physicalLocation, user,))

		if (picture == "-"): #Initially, display a default image
			newCursor.execute("UPDATE profile SET picture = ? WHERE user = ?", ("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT15rBzgsmxrdDIpOoi4IIEYGBhrnabBnHvR9CCaKWwJQ_VEqPZ5Nf4QAI", user,))

		if (picture != "" and picture != "-"):#Update profile picture
			newCursor.execute("UPDATE profile SET picture = ? WHERE user = ?", (picture, user,))

		if (encoding != None): #Update endcoding
			newCursor.execute("UPDATE profile SET encoding = ? WHERE user = ?", (encoding, user,))

		if (encryption != None): #Update encryption
			newCursor.execute("UPDATE profile SET encryption = ? WHERE user = ?", (encryption, user,))

		if (decryptionKey != None): #Update decryptionKey
			newCursor.execute("UPDATE profile SET decryptionKey = ? WHERE user = ?", (decryptionKey, user,))
			
	#Insert the user's new profile if his/her profile is not found in the database
	else:
		newCursor.execute("INSERT INTO profile VALUES(?,?,?,?,?,?,?,?,?)", (user, realName, jobTitle, description, physicalLocation, picture, encoding, encryption, decryptionKey))
	
	#Save and exit
	newConnection.commit() 
	newConnection.close()	
	


#Clear all profile -- free up the memory in the server for doing something	
def clearAllProfile():

	#Connect to the database and make a cursor for controllin
	newConnection = sqlite3.connect('vetterData.db')	
	newCursor = newConnection.cursor()	
	
	#Delete and free space
	newCursor.execute("DELETE FROM profile")
	newCursor.execute("VACUUM")
	
	#Save and exit
	newConnection.commit() 
	newConnection.close()



#Find a specific user's profile from the database, if can't find this user's profile, 
#that mean this user's profile hasn't download to the datavase yet, return "0" in that case
def getProfile(user):

	gotIt = 0

	#Connect to the database and make a cursor for controllin
	newConnection = sqlite3.connect('vetterData.db')	
	newCursor = newConnection.cursor()	
	
	#Search user
	newCursor.execute("SELECT * FROM profile WHERE user = ?", (user,))
	gotIt = (newCursor.fetchone())
	
	#Exit
	newConnection.close()

	return gotIt



#Update all the signed-up users
def updateUsers(signedUpUsers):

	#Connect to the database and make a cursor for controllin
	newConnection = sqlite3.connect('vetterData.db')	
	newCursor = newConnection.cursor()

	for i in range (0, len(signedUpUsers), 1):
		
		#Search the user first
		newCursor.execute("SELECT * FROM profile WHERE user = ?", (signedUpUsers[i],))
		gotIt = (newCursor.fetchone())

		#If can not find the user in the database, that mean the thie user is newly sign up and add him/her to the database
		if(gotIt == None):
			newCursor.execute("INSERT INTO profile VALUES (?,?,?,?,?,?,?,?,?)", (signedUpUsers[i],"-", "-", "-", "-", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT15rBzgsmxrdDIpOoi4IIEYGBhrnabBnHvR9CCaKWwJQ_VEqPZ5Nf4QAI", "", "", ""))
			newConnection.commit() #Save	

	newConnection.close() #Exit



#Return a list of all the current signed up user
def allVeeBuddy():
	
	veeBuddyList =[]
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	for row in newCursor.execute("SELECT * FROM profile"):
        	veeBuddyList.append(row[0])
	newConnection.close()

	return veeBuddyList
	
#Check if the user is authenticated, but check if the data has his/her profile
def checkAuthenticated(user):
	
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	
	#Search user
	newCursor.execute("SELECT * FROM profile WHERE user = ?", (user,))
	gotIt = (newCursor.fetchone())
	newConnection.close()
	
	#If found the profile, that mean the user is authenticated and return a "True" 
	if (gotIt != None):
		return True
	else:
		return False
