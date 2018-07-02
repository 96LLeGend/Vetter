import sqlite3



"""This is the current online user database controller"""



##########Display the user table(for testing)
def printOnlineUserTable():
	newConnection = sqlite3.connect('vetterData.db')	#Go into the table
	newCursor = newConnection.cursor()	#make a cursor
	for row in newCursor.execute("SELECT * FROM onlineUser ORDER BY ID"):
        	print row
	newConnection.close()


	
#Create a database for storing users' id(For indentify who these data for), ip address,  
#port number, frofile, and also the current users' username and hashed password (use later)
def newUserDatabase():

	newConnection = sqlite3.connect('vetterData.db')	#Connect to the database
	newCursor = newConnection.cursor()	#New cursor
	
	try:
		#Create table for saving the online user list
		newCursor.execute('''CREATE TABLE onlineUser(ID, hashedPassword, username, loaction, IP, port, lastLoginTime, publicKey)''')
		#Reserve the first row for the current user
		newCursor.execute("INSERT INTO onlineUser VALUES(?,?,?,?,?,?,?,?)", ("0","-","-","-","-","-","-","-"))
		newConnection.commit()

	except sqlite3.OperationalError as e:
		return 0;	#do nothing
			
	newConnection.close()	#Close connection
	


#Once the user login successfully, store his/her information
def updateCurrentUser(username, password, loaction, IP, port):

	newConnection = sqlite3.connect('vetterData.db')	#Go into the database
	newCursor = newConnection.cursor()	#make a cursor

	# Insert the current user's user name and password	
	newCursor.execute("UPDATE onlineUser SET hashedPassword = ?, username = ?, loaction = ?, IP = ?, port = ? WHERE ID = ?", (password, username, loaction, IP, port, "0"))
	
	#Save and close connection
	newConnection.commit()
	newConnection.close()	

	


#Find who currently login on this locat server
def getCurrentUser():
	
	newConnection = sqlite3.connect('vetterData.db')	#Go into the database
	newCursor = newConnection.cursor()	#make a cursor

	#Return the first row(ID = 0), which is reserve to store the current user on this computer	
	newCursor.execute("SELECT * FROM onlineUser WHERE ID = ?", ("0"))
	gotIt = (newCursor.fetchone())
	newConnection.close()	#Close connection
	#print(gotIt)
	return gotIt



#Search a specific user
def getUser(user):

	newConnection = sqlite3.connect('vetterData.db')	#Go into the database
	newCursor = newConnection.cursor()	#make a cursor

	#Return the first row(ID = 0), which is reserve to store the current user on this computer	
	newCursor.execute("SELECT * FROM onlineUser WHERE username = ?", (user,))
	gotIt = (newCursor.fetchone())

	newConnection.close()	#Close connection

	return gotIt



#Clear the first row, which mean no user is log in with this computer, therefore other 
#all API that required username and password will have no permission to open
def resetCurrentUser():
	
	newConnection = sqlite3.connect('vetterData.db')	#Go into the database
	newCursor = newConnection.cursor()	#make a cursor
	
	#Reset	
	newCursor.execute("UPDATE onlineUser SET hashedPassword = ?, username = ? WHERE ID = ?", ("", "", "0"))
	
	#Save and close connection
	newConnection.commit()
	newConnection.close()	
	


#This function can check get the current online user and save their IP address, port number
#public key and other information to the data base. If the user is not in the list but in the
#database, that mean that user already logoff, so delete him/her from the data base	
def updateOnlineUser(userList):

	newConnection = sqlite3.connect('vetterData.db')	#Go into the database
	newCursor = newConnection.cursor()	#make a cursor

       	#Delete the old data first, ID = 0 reserve for the user that log in to this 
	#computer which only need to update when login and logoff
	newCursor.execute("DELETE FROM onlineUser WHERE ID != ?", ("0"))

	#Insert the new user(Delete all old data + add all new data = "UPDATE")
	for i in range (1, len(userList) - 1, 1):
		newCursor.execute("INSERT INTO onlineUser VALUES(?,?,?,?,?,?,?,?)", (i, "", userList[i][0], userList[i][1], userList[i][2], userList[i][3], userList[i][4], userList[i][5]))

	newCursor.execute("VACUUM")	#Free the space
	#Save and close the database
	newConnection.commit()
	newConnection.close()


#Check the database and put all the usernam into a list, and return the list
def displayOnlineUser():
	newConnection = sqlite3.connect('vetterData.db')	#Go into the database
	newCursor = newConnection.cursor()	#make a cursor
	
	#Form a list to return
	listOfOnlineUser = [];
	for row in newCursor.execute("SELECT * FROM onlineUser ORDER BY ID"):
        	listOfOnlineUser.append(row[2])

	newConnection.close()	

	return listOfOnlineUser;
			
