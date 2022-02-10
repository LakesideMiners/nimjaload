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

## TODO: Setup an override.
cache_time = config['control']['cacheTime']
# api/app URL
api_url = "https://hypno.nimja.com/app"

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

# Gets the app
def getApp():
    r = requests.get(api_url)
    with open("data/app.json", "w") as f:
        f.write(r.text)
        print("Done Updating")
        f.close()
        
    
        
# Only runs if user is not a supporter
def formatCookies(): 
    persist_input = input("Please enter the persist cookie: \n")
    persist = {'persist': persist_input}
    print(persist)
    r = requests.get("https://hypno.nimja.com/listen/download/339-loyal_reward.mp3", cookies=persist)
    if r.status_code == requests.codes.ok:
        print("Cookie is VALID! Continuing!")
        return persist

    else:
        print(r.status_code)
        print("Cookie invalid. try again")
        formatCookies()
        
        
        

# Downloaders
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
                
  




playlist_url = input("Please enter the playlist URL: \n")
playlist_striped = playlist_url.rsplit('/', 1)[-1]
file_ids = playlist_striped.split("-")


if patron == "True":
    checkCache()
    patreonDL(formatCookies(), file_ids)
else:
    checkCache()
    normalDL()
