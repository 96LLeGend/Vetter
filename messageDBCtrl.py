import sqlite3
import helper
import blacklistDBCtrl
import userDBCtrl



"""This the message database controller"""



##########Display the message table(for testing)
def printMessageTable():
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	for row in newCursor.execute("SELECT * FROM message"):
        	print row
	newConnection.close()




#Create a database for storing all messages /files sent/receiver from this server. 
#There information it stores are: user, direction, Vee, file, time, date, month, year
def newMessageDatabase():

	newConnection = sqlite3.connect('vetterData.db')	#New table
	newCursor = newConnection.cursor()	#New cursor
	
	try:
		#Create table for saving messages
		newCursor.execute('''CREATE TABLE message(sender, destinaton, message, epochTime, markdown, encoding, encryption, hashing, Hash, decryptionKey)''')
		newConnection.commit()

	except sqlite3.OperationalError as e:
		return 0;	#do nothing	
			
	newConnection.close()	#Close connection



#Save message to the data base, it also save the file's namd as a message when the a filed is received
def addMessage(sender = None, destination = None, message = None, epochTime = None, markdown = None, encoding = None, encryption = None, hashing = None, Hash = None, decryptionKey = None):

	newConnection = sqlite3.connect('vetterData.db')	#New table
	newCursor = newConnection.cursor()	#New cursor

	#Insert new message
	newCursor.execute("INSERT INTO message VALUES(?,?,?,?,?,?,?,?,?,?)", (sender, destination, message, float(epochTime), markdown, encoding, encryption, hashing, Hash, decryptionKey))
	newConnection.commit()

	newConnection.close()	#Close connection



#Save file to the data base
def addFile(sender = None, destination = None, filename = None, content_type = None, epochTime = None, markdown = None, encoding = None, encryption = None, hashing = None, Hash = None, decryptionKey = None):

	newConnection = sqlite3.connect('vetterData.db')	#New table
	newCursor = newConnection.cursor()	#New cursor

	#Insert new file
	newCursor.execute("INSERT INTO message VALUES(?,?,?,?,?,?,?,?,?,?)", (sender, destination, filename, content_type, float(epochTime), markdown, encoding, encryption, hashing, Hash, decryptionKey))
	newConnection.commit()

	newConnection.close()	#Close connection



#In case of the user's memory is runing out of space, a "clear history" can be perform to delete specific 
#amout of chart history. Parameter "periodCover"is for indicate how many history the user want to keep,
#0 means keep no history(delete everything), 1 mean delete the data that older than 1 year(365 days), 2 mean delete 
#the data that older than 1 month(30 days). "Date" is the current date
def clearChartHistory(periodCover, date):

	newConnection = sqlite3.connect('vetterData.db')	#Connect to the database
	newCursor = newConnection.cursor()	#New cursor
	currentTime = helper.getCurrentEpochTime()    #Get current time

	#Delete data accoring to time period
	if (periodCove == 0):
		newCursor.execute("DELETE FROM message")	
	elif (periodCove == 1):
		newCursor.execute("DELETE FROM message WHERE epochTime < ?", (currentTime - (60*60*24*365)))
	else:
		newCursor.execute("DELETE FROM message WHERE epochtime < ?", (currentTime - (60*60*24*30)))
	
	newCursor.execute("VACUUM")	#Free the space
	newConnection.commit() #Save change
	newConnection.close()	#Close connection



#Get messages history, for display on the web
def getMessagesHistory():
	
	#Get current user from the data base
	currentUser = userDBCtrl.getCurrentUser()

	messageList = []
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor

	#Add to list, Only add to the list if the message is belong to the current user and 
	#only if the sender that not in the current user's blacklist
	for row in newCursor.execute("SELECT * FROM message ORDER BY epochTime DESC"):
		
		if ((row[0] == currentUser[2] or row[1] == currentUser[2]) and (not blacklistDBCtrl.isBlacklisted(currentUser[2], row[0]))):
       			messageList.append(row)

	newConnection.close() #Close connection

	return messageList
