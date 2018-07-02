import string
import time

"""This function can turn the list of user online(Sent as a string) form the login server 
and interpret each user's ip, port, etc. return them in a 2D array"""  
def decode(listOfUser):

	#declare variable	
	userInfoList = []	#Note that there is one element in the list now and it is equal to "nothing"
	oneUser = ""
	#Start digit = 29	
	i = 29
	
	while(i < len(listOfUser)):
		checkOneUser = True 

		#Keep adding the letter to "oneUser" string until a blink space is found, that mean this 
		#user's information is complete, sent this string to "decodeOneUser" function for further decoding.
		while (checkOneUser):
			if (listOfUser[i] != "\n"):
				oneUser += listOfUser[i]
			else:	
				
				checkOneUser = False
			i += 1
			if (i == len(listOfUser)):
				checkOneUser = False
		
		#Add to the array
		userInfoList.append(decodeOneUser(oneUser))
		checkOneUser = True
		oneUser = ""
	
	#Remove the first element as it equal to "nothing"
	userInfoList.remove(userInfoList[0])

	return userInfoList
	


#This function can read a single user's information and break it down to an array,
#sort by what kind of the information that it. It only used by "decode" function
def decodeOneUser(userInfo): 
	
	#declare variable
	oneInfo = ""
	oneUser = []
	infoIndex = 0
	i = 0
	
	while(i < len(userInfo)):
		checkOneInfo = True 

		#When a "," is found, that mean this piece of information is complete, add to the "oneUser" array
		#Otherwise just keep adding the letter into the "oneInfo" string
		while (checkOneInfo):
			if ((userInfo[i] != ",") and (userInfo[i] != "\r")):
				oneInfo += userInfo[i]
			else:
				checkOneInfo = False
			i += 1
			if (i == len(userInfo)):
				checkOneInfo = False
			
		oneUser.append(oneInfo)
		oneInfo = ""
		infoIndex += 1

	##If the list missing the public key, just add "n/a" in the end to indicate that 
	if (len(oneUser) < 6):
		oneUser.append("n/a")

	return oneUser



#Get the current epoch time
def getCurrentEpochTime():
	return time.time()



#Translate a epoch time to human readable time and date
def epochToReal(epoch):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(epoch)))


		
	
