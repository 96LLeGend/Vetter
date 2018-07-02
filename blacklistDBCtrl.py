import sqlite3



"""This is the blacklist database controller"""



##########Display the blacklist table(for testing)
def printBlacklistTable():
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	for row in newCursor.execute("SELECT * FROM blacklist"):
        	print row
	newConnection.close()


	
#Create a database for the blacklist, it has two columes, for the username and the user who black him/her
#So different user can login in this server and has their own blacklist
def newBlacklistDatabase():

	newConnection = sqlite3.connect('vetterData.db')	#Connect to the database
	newCursor = newConnection.cursor()	#New cursor
	
	try:
		#Create table for saving the users status list
		newCursor.execute("CREATE TABLE blacklist(user, blacklistUser)")
		newConnection.commit()

	except sqlite3.OperationalError as e:
		return 0;	#do nothing
			
	newConnection.close()	#Close connection



#Add user to blacklist
def addToBlacklist(user, blacklistUser):
	
	newConnection = sqlite3.connect('vetterData.db')	#New table
	newCursor = newConnection.cursor()	#New cursor

	#Check if the user already added, if so, do nothing
	newCursor.execute("SELECT * FROM blacklist WHERE user = ? AND blacklistUser = ?", (user, blacklistUser,))
	gotIt = (newCursor.fetchone())
	if (gotIt == None):
		#Insert new member
		newCursor.execute("INSERT INTO blacklist VALUES(?,?)", (user, blacklistUser,))
		newConnection.commit()

	newConnection.close()	#Close connection



#Remove user from blacklist
def removeFromBlacklist(user, blacklistUser):
	
	newConnection = sqlite3.connect('vetterData.db')	#New table
	newCursor = newConnection.cursor()	#New cursor

	#Check if the user already added, if not, do nothing
	newCursor.execute("SELECT * FROM blacklist WHERE user = ? AND blacklistUser = ?", (user, blacklistUser,))
	gotIt = (newCursor.fetchone())
	if (gotIt != None):
		#Delete member
		newCursor.execute("DELETE FROM blacklist WHERE user = ? AND blacklistUser = ?", (user, blacklistUser,))
		newCursor.execute("VACUUM")

	newConnection.close()	#Close connection



#Return the blacklist(for displaying)
def getBlacklist(user):
	
	blacklist =[]
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	for row in newCursor.execute("SELECT * FROM blacklist"):
        	blacklist.append(row[1]) #Add to the list
	newConnection.close()

	return blacklist



#Check if the user is blacklisted by the current user, return True/False
def isBlacklisted(currentUser, checkUser):

	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor

	for row in newCursor.execute("SELECT * FROM blacklist"):
		if (row[0] == currentUser and row[1] == checkUser):
			return True

	newConnection.close()

	return False

	
