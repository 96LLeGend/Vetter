"""The function in here is a description of the web design, The description is writen in 
HTML/CSS, and return to cherrypy as a string. In html file, the string with "{}" means replace is needed"""

import messageDBCtrl
import profileDBCtrl
import helper
import blacklistDBCtrl



#When try to load an invalid API, jump to this page
def defaultPage():
	return """
		I don't know where you're trying to go, so have a 404 Error.</br>
		<a href='index'>To Vetter</a>
		"""



#Vetter's login page
def indexPage():

	html = open("loginPage.html","r")
	web = html.read()
	html.close()
	return web

	

#Once login jump to this page, which is the user's home page
def userHome(onlineUsers, currentUser, listOfVee):

	veeBuddyList = profileDBCtrl.allVeeBuddy()	

	#Refresh
	Page = "<head>"
	Page += "<a id='logoffViaClosePage'; href='/logoffViaClosePage'></a>"
	Page += "<meta http-equiv='refresh' content='30'>"
	Page += "Welcome back,  " + currentUser[2] + "!<br/>"
	Page += "<head/>"	
	Page += "</br>"
	
	#Display the list of online user, 
	Page += "==============</br>"
	Page += "People also online: </br>"
	#for i in range(0, len(onlineUsers) - 1, 1): 
	for i in range(0, len(onlineUsers), 1): 
		#Don't display the user himself/herself/itself and don't display the blacklisted user
		if (onlineUsers[i] != currentUser[2] and not(blacklistDBCtrl.isBlacklisted(currentUser[2], onlineUsers[i]))):
			Page += "</br>"
			Page += "<var>" + onlineUsers[i] + "</var>"	
	Page += "</br>" 
	Page += "==============</br>"		

	#Send messagers panel
	Page += """</br>
		<form accept-charset="utf-8" action="/sendMessage" method="post" enctype="multipart/form-data">
		Vee: <input type="text" size="80" name="message"/><br/>
		To user: <input type="text" size="20" name="destination"/>
		<input type="submit" value="Send"/></form>"""

	#Send file panel
	Page += """</br>
		<form accept-charset="utf-8" action="/sendFile" method="post" enctype="multipart/form-data">
		</br>Note: maximum file size should below 5MB</br>
		File: <input type="file" size="20" name="fileToSend"/></br>
		To user: <input type="text" size="20" name="destination"/>
		<input type="submit" value="Send"/></form>
		</br>"""

	#Search profile
	Page += """<table style = 'position: absolute; right:5px; top: 20px'>
		<tr><td style = 'width : 15'>
			<form accept-charset='utf-8' action='/displayProfile' method='post' enctype='multipart/form-data'></br>
				<input type="hidden" name="username" value="""+currentUser[2]+""" /> 
  				<input type="hidden" name="psw" value="""+currentUser[1]+""" /> 
				Enter the user you want to view profile:</br>
				<input type="text" size="5" name="userToDisplay"/></br>
				<input type="submit" value="Search"/>
			</form>
		</td></tr>
		<tr><td>Your VeeBuddy:</td></tr>"""
	
	#List all signed up user
	for i in range(0, len(veeBuddyList) - 1 or 10, 1):
		theLink = "displayProfile?username="+currentUser[2]+"&psw="+currentUser[1]+"&userToDisplay="+veeBuddyList[i]
		Page +="<tr width = '70'><td><a href="+theLink+">"+veeBuddyList[i]+"</a></td></tr>"	
	Page += "</table></br>"

	#Guide to view all message history
	theLink = "searchMessage?username="+currentUser[2]+"&psw="+currentUser[1]
	Page += " <a href='"+theLink+"'>View all history	</a>"
	
	#Display the recent 20 message
	Page += "</br>Recent Vee:</br>"
	for i in range(0, len(listOfVee), 1): 
		Page += """
			</br>
			<table style='width:100%'>
				<tr>
					<td width = '70'>
						From: """+listOfVee[i][0]+"""
					</td>
					<td width = '70'>
						To: """+listOfVee[i][1]+"""
					</td>
					<td width = '350'>
						Sent at: """+helper.epochToReal(listOfVee[i][3])+""" 
					</td>
				</tr>
				<tr width = '450'>"""+listOfVee[i][2]+"""</tr>
			</table>
			"""

	Page += "</br>"
	#To current user's profile
	theLink = "displayProfile?username="+currentUser[2]+"&psw="+currentUser[1]+"&userToDisplay="+currentUser[2]
	Page += "<a href='"+theLink+"'>My Profile Setting  </a>"
	#See blacklist
	theLink = "displayBlacklist?username="+currentUser[2]+"&psw="+currentUser[1]
	Page += "<a href='"+theLink+"'>Blacklist  </a>"
	#Logoff
	Page += "  <a href='logoff'>logoff</a>"

	return Page



#If the username and password is not match the current user's, some page should not be allowed to loaded
def assetErrorPage():
	Page = """</br>
		Oops, something wrong!  :'( </br>
		<a href='index'>Return to Vetter</a>"""
	return Page



#This page display a specific user's profile profile, if display the current user himself/herself, there will 
#be a option for changing the current user to change his/her profile
def displayProfile(currentUser, profile, allowToChange):

	Page = """<head>
		<meta http-equiv='refresh' content='30'>
		Profile<br/>
		<head/>"""
	
	#If the user viewing his/her own profile, a button for change profile should present
	if (allowToChange):
		Page += "<br/>"
		Page += "User name:   "+profile[0]+"</br>" #Not allow to change user name
		Page += "<form accept-charset='utf-8' action='changeProfile' method='post' enctype='multipart/form-data'>"
		Page += "<br/>"

		Page += "Real name:   "+profile[1]+"</br>"
		Page += "New real name:   <input type='text' size='20' name='realName' value=''/><br/>"  
		Page += "<br/>"

		Page += "Job title:   "+profile[2]+"</br>"
		Page += "New job title:   <input type='text' size='20' name='jobTitle' value=''/><br/>"
		Page += "<br/>"

		Page += "Description: "+profile[3]+"</br>"
		Page += "New description: <input type='text' size='20' name='description' value=''/><br/>"
		Page += "<br/>"

		Page += "Location   : "+profile[4]+"</br>"
		Page += "New location:    <input type='text' size='20' name='physicalLocation' value=''/><br/>"
		Page += "<br/>"

		Page += "Profile picture:</br>"
		Page += "<object width='300' height='200' type='html' data="+profile[5]+"></object></br></br>"
		Page += "URL for new picture: <input type='text' size='50' name='picture'/></br>"
		Page += "<input type='submit' value='Upload'/></form>"
		Page += "</br>"

	else:
		#Display all sensible information, no need to display technical profile such as decryptionKey
		Page += "<br/>"
		Page += "User name:   "+profile[0]+"<br/>"
		Page += "Real name:   "+profile[1]+"<br/>"
		Page += "Job title:   "+profile[2]+"<br/>"
		Page += "Description: "+profile[3]+"<br/>"	
		Page += "Location:    "+profile[4]+"<br/>"
		Page += "Profile picture:</br>"
		Page += "<object width='300' height='200' type='html' data="+profile[5]+"></object></br></br>"
		Page += "</br>"

	#Return to home page
	Page += "<br/>"	
	theLink = "userHome?username="+currentUser[2]+"&psw="+currentUser[1]
	Page += " <a href='"+theLink+"'>Home</a>"
	#Logoff
	Page += "  <a href='logoff'>logoff</a>"

	return Page



#The page for displaying the blacklist, it also can let the user to add and remover user from the list
def blacklistPage(currentUser, blacklist):
	
	Page =  """
		<head>
		<meta http-equiv='refresh' content='30'>
		Blacklist<br/>
		<head/>
		<table style='width:100%'>
			<tr>
				<td width = '30'>
					<form accept-charset='utf-8' action='/addUserToBlacklist' method='post' enctype='multipart/form-data'></br>
					Enter the user you want to add to blacklist:</br>
					<input type="hidden" name="username" value="""+currentUser[2]+""" /> 
  					<input type="hidden" name="psw" value="""+currentUser[1]+""" /> 
					<input type="text" size="10" name="userToAdd"/></br>
					<input type="submit" value="Add"/>
					</form>
				</td>
				<td width = '30'>
					<form accept-charset='utf-8' action='/removeUserFromBlacklist' method='post' enctype='multipart/form-data'></br>
					Enter the user you want to remove from blacklist:</br>
					<input type="hidden" name="username" value="""+currentUser[2]+""" /> 
  					<input type="hidden" name="psw" value="""+currentUser[1]+""" /> 
					<input type="text" size="10" name="userToRemove"/></br>
					<input type="submit" value="Remove"/>
				</td>
			</tr>
		</table></br>
		Blacklist: 
		"""

	#Print the list
	if (blacklist != None):
		for i in range(0, len(blacklist), 1):
			Page += blacklist[i]+"  "
	
	theLink = "userHome?username="+currentUser[2]+"&psw="+currentUser[1]
	Page += "</br> <a href='"+theLink+"'>Home</a>"

	return Page



#This page will display all vee, it works also allow the user to search message by username
def messageHistory(currentUser, veeToDisplay):
	#Display the search chart result
	Page =  """
		<head>
		<meta http-equiv='refresh' content='30'>
		Vee history<br/>
		<head/>"""
	
	theLink = "searchMessage?username="+currentUser[2]+"&psw="+currentUser[1]
	Page += """<table style='width:100%'>
			<tr><td>
				<form accept-charset='utf-8' action='/searchMessage' method='post' enctype='multipart/form-data'></br>
					<input type="hidden" name="username" value="""+currentUser[2]+""" /> 
	  				<input type="hidden" name="psw" value="""+currentUser[1]+""" /> 
					Enter the user you want to view profile:</br>
					<input type="text" size="5" name="userToShow"/></br>
					<input type="submit" value="Search"/>
				</form>
			</td>
			<td>
				<a href='"""+theLink+"""'> View all history</a>
			</td></tr>
		</table>"""

	for i in range(0, len(veeToDisplay), 1): 
		#Only display the one relate to the current user
		if (veeToDisplay[i][0] == currentUser[2] or veeToDisplay[i][1] == currentUser[2]):
			Page += """
				</br>
				<table style='width:100%'>
					<tr>
						<td width = '70'>
							From: """+veeToDisplay[i][0]+"""
						</td>
						<td width = '70'>
							To: """+veeToDisplay[i][1]+"""
						</td>
						<td width = '350'>
							Sent at: """+helper.epochToReal(veeToDisplay[i][3])+""" 
						</td>
					</tr>
					<tr width = '450'>"""+veeToDisplay[i][2]+"""</tr>
				</table>
				"""

	#Return to home page
	theLink = "userHome?username="+currentUser[2]+"&psw="+currentUser[1]
	Page += "</br>  <a href='"+theLink+"'>Home</a>"

	return Page
		
