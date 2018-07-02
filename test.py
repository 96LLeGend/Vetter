import string
import random
import cherrypy

#Cherrypy
"""class MainApp(object):

    	@cherrypy.expose
    	def index(self):
		return "hi"
	
	The '8' is default value, so when type:"/generate?length=16" the 16 will over write it, 
	if not specific, you have to give it an input(you can type just "/generate" only)
	@cherrypy.expose
	def generate(self, length=8):	 
		return ''.join(random.sample(string.hexdigits,int(length)))
        
     &     
if __name__ == '__main__':
	cherrypy.quickstart(MainApp())"""
"""
#Hashing
import hashlib
password = "longtermabsorbing"
#hash use sha-256, password+"COMPSYS302-2017" for real password
#hash_object = hashlib.sha256(b'longtermabsorbingCOMPSYS302-2017')
hash_object = hashlib.sha256(password + "COMPSYS302-2017")
hex_dig = hash_object.hexdigest()
print(hex_dig)	

import socket
print(socket.gethostbyname(socket.gethostname()))
#d508d28985b25a689c06e3e2fcb7670fe9c68f036aedde7cc92a86db182efe75


username = ""
password = ""		
data_f = open("data.txt","r")
lines = data_f.readlines()	
data_f.close()	
		
for i in range(0, len(lines[0]), 1):
	if (i < 7):
		username = username + lines[0][i]
	else:
		password = password + lines[0][i]

print(username)
print(password)
"""
"""
import sqlite3

conn = sqlite3.connect('userData.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE stocks
            (date text, trans text, symbol text, qty real, price real)''')

# Insert a row of data
c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

conn.commit()

# Larger example that inserts many records at a time
purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
             ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
             ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
            ]
c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)

# Searching
t = ('RHAT',)
c.execute('SELECT * FROM stocks WHERE symbol=?', t)
print c.fetchone() #Print the current input

#Save (commit) the changes
conn.commit()

for row in c.execute('SELECT * FROM stocks ORDER BY date'):
        print row

#Delete RHAT
c.execute("DELETE FROM stocks WHERE qty=?", ('100',))

conn.commit()

for row in c.execute('SELECT * FROM stocks ORDER BY date'):
        print row

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
"""
"""
import helper
print helper.decode("0, Online user list returned ramo588,2,192.168.1.50,10002,1495672213 jcen902,1,0.0.0.0,10010,1495672251 hsco899,2,174.24.47.200,8080,1495672253")
"""
"""
import socket
#External IP Address
from urllib2 import urlopen
ipAdd = urlopen('http://ip.42.pl/raw').read()
print(ipAdd)
#To get the Hostname
print socket.gethostname()
#To get the IP Address
print socket.gethostbyname(socket.gethostname())
"""
"""
import time
## 24 hour format ##
print (time.strftime("%H:%M:%S"))
## 12 hour format ##
print (time.strftime("%I:%M:%S"))
## dd/mm/yyyy format
print (time.strftime("%d/%m/%Y"))
##UTC##
from datetime import datetime
print(datetime.utcnow())
#epoch time
print time.time()
print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
"""
"""
import base64
image_file = open("nicememe.PNG", "rb")
encoded_string = base64.b64encode(image_file.read())
image_file.close()
print(encoded_string)
"""
"""
@cherrypy.expose
	def sendFile(self, destination, fileToSend):
		size = 0
		data = ""
        	
		data += fileToSend.file.read(8192)
		
		print(data)
		print(fileToSend.filename)
		print(fileToSend.content_type)
		return "0"
"""
"""
import os
if not os.path.exists("myDownload"):
    os.makedirs("myDownload")
f = "myDownload/"+"hello.txt"
localFile = open(f,"w+")
localFile.write("hello")
localFile.close() 
"""
