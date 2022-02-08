import requests
import os
import json
import configparser
config = configparser.ConfigParser()
# Set up the cookies needed to get the files
# TODO: Find way to have user log in and  grab the cookies there
config.read('data/settings.ini') 
patron = config['patron']['patron']
api_url = "https://hypno.nimja.com/app"
login_url = "https://hypno.nimja.com/wmyd/"
print(patron)
playlist_url = input("Please enter the playlist URL: \n")
playlist_striped = playlist_url.rsplit('/', 1)[-1]
file_ids = playlist_striped.split("-")



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
        
        
f = open("data/app.json")
data = json.load(f)

#use if not a patreon
def normalDL(file_ids):
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
                
                
def checkCache():
    """[summary]
    """
    
    lastupdated = config(['lastupdated']['time'])


if patron == "True":
    print("yes")
    patreonDL(getLogin(), file_ids)
else:
    print("sex")


