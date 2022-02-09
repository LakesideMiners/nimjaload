import requests
import os
import json
import configparser
from os.path import exists
from datetime import datetime
#Read the config file
config = configparser.ConfigParser()
config.read('data/settings.ini') 
# Store a value
patron = config['patron']['patron']
cache_time = config['control']['cacheTime']
# api/app URL
api_url = "https://hypno.nimja.com/app"
# login url
login_url = "https://hypno.nimja.com/wmyd/"



def getLogin():
    """This Returns the cookies for getting patron files

    Returns:
        dict: {'PHPSESSID': 'abc123', 'persist': 'abc123'}
    """   
    with requests.Session() as s:
        email = config['login']['email']
        passcode = config['login']['passcode']
        payload = {
        'email': email,
        'passcode': passcode
        }
        send = s.post("https://hypno.nimja.com/wmyd", data=payload)

        answer = s.post("https://hypno.nimja.com/wmyd")
        cookies = s.cookies
        cookies_dict = cookies.get_dict()
        return cookies_dict
        
        

#use if not a patreon
def normalDL(file_ids):
    f = open("data/app.json")
    data = json.load(f)
    for id in file_ids:
        for i in data['content']['files']:
            if i['id'] == int(id):
                print(i['links']['download'])
                url = (i['links']['download'])
                name = i["name"] + ".mp3"
                # We only need the details for the non patron as that is the only time they are used
                details = i['links']['details']
                # Don't need to use cookies
                r = requests.get(url)
                # This checks if we get html as the content type, if we do, it means its patron only therefoe we skip it
                if r.headers['content-type'] == 'text/html':
                   print("Skipping" + name + " as it is a Patron only file! \n Check below url to see when/if it will be made public\n" + details)
                else:
                    with open(name, "wb") as f:
                        f.write(r.content)
                        print(name + " Is Done Downloading!")
    print("Playlist done downloading!")

# Use if you are a patron            
def patreonDL(cookies, file_ids):
    f = open("data/app.json")
    data = json.load(f)
    for id in file_ids:
        for i in data['content']['files']:
            if i['id'] == int(id):
                print(i['links']['download'])
                url = (i['links']['download'])
                name = i["name"] + ".mp3"
                details = i['links']['details']
                r = requests.get(url, cookies=cookies)
                with open(name, "wb") as f:
                    f.write(r.content)
                    print(name + " Is Done Downloading!")
                    f.close()
    print("Playlist download done!")
                
  
# TODO: Setup Caching and Download app.json         
def checkCache():
    """Checks to see if our stored copy is more then
    """    
    # Check first if the file exists, if it does, we check when it was downloaded
    if exists("data/app.json"):
        f = open("data/app.json")
        data = json.load(f)
        now = datetime.now()    
        nowts = now.timestamp()
        last_updated = data['time']
        print(last_updated)
        difference = float(nowts) - float(last_updated)
        print("app.json last updated " + str(difference)  + " seconds ago!") 
        if difference >= float(cache_time):
            print("Older then " + cache_time + " seconds! Updating!")
            os.remove("data/app.json")
            getApp()
        else:
            print("Not older then " + cache_time + " seconds, so we won't update!")
    else:
        print("We don't have app.json! So we are getting it")
        getApp()


def getApp():
    r = requests.get(api_url)
    with open("data/app.json", "w") as f:
        f.write(r.text)
        print("Done Updating")
        f.close()
        
playlist_url = input("Please enter the playlist URL: \n")
playlist_striped = playlist_url.rsplit('/', 1)[-1]
file_ids = playlist_striped.split("-")


if patron == "True":


    checkCache()
    patreonDL(getLogin(), file_ids)
else:
    checkCache()
    normalDL()