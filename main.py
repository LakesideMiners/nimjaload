import os
import json
import configparser
from pydub import AudioSegment as aseg
from os.path import exists
from datetime import datetime
import requests


# Read the config file
config = configparser.ConfigParser()
config.read('data/settings.ini')
patron = config['patron']['patron']
cache_time = config['control']['cacheTime']


# api/app URL and test URL for testing cookies
api_url = "https://hypno.nimja.com/app"
test_url = "https://hypno.nimja.com/listen/download/nimja-339-loyal_reward.mp3"


def check_cache():
    """
    Check if cache is too old or if it is too old

    Args: None
    """
    # Check if file exists, if yes, check when it was downloaded
    if exists("data/app.json"):
        f = open("data/app.json")
        data = json.load(f)
        now = datetime.now()
        nowts = now.timestamp()
        last_updated = data['time']
        print(last_updated)
        difference = float(nowts) - float(last_updated)
        print("app.json last updated " + str(difference) + " seconds ago!")
        if difference >= float(cache_time):
            print("Older then " + cache_time + " seconds! Updating!")
            os.remove("data/app.json")
            get_app()
        else:
            print("Not older then " + cache_time +
                  "seconds, so we won't update!")
    else:
        print("We don't have app.json! So we are getting it")
        get_app()


# Gets the app
def get_app():
    """
    Get the app.json from the API.

    Args: None
    """
    r = requests.get(api_url)
    with open("data/app.json", "w") as f:
        f.write(r.text)
        print("Done Updating")
        f.close()


# Only runs if user is a supporter
def format_cookies():
    """
    Returns a dict with the persist cookie`

    Args: None
    """
    persist_input = input("Please enter the persist cookie: \n")
    persist = {'persist': persist_input}
    print(persist)
    r = requests.get(test_url, cookies=persist)
    if r.status_code == requests.codes.ok:
        print("Cookie is VALID! Continuing!")
        return persist

    else:
        print(r.status_code)
        print("Cookie invalid. try again")
        format_cookies()


# Downloaders
# use if not a patreon
def normal_dl(file_ids):
    """
    This function takes a list of file ids and downloads a mp3 file skipping any Patron files for each file

    Args:
        file_ids: an array of file IDs as listed by the app.json, NOT by the file number in the name
    """
    f = open("data/app.json")
    data = json.load(f)
    for ids in file_ids:
        for i in data['content']['files']:
            if i['id'] == int(ids):
                print(i['links']['download'])
                url = i['links']['download']
                name = i["name"] + ".mp3"
                details = i['links']['details']
                # Don't need to use cookies
                r = requests.get(url)
                if r.status_code != requests.codes.ok:
                    print("Skipped" + name + " as it is a Patron file! \n" +
                          "Check url to see when/if it will be made public\n"
                          + details)
                else:
                    with open(name, "wb") as f:
                        f.write(r.content)
                        print(name + " Is Done Downloading!")
    print("Playlist done downloading!")


# Use if you are a patron
def patreon_dl(cookies, file_ids):
    """
    This function takes a list of file ids and downloads them
    
    Args:
        cookies: a dict in the format of
        file_ids: an array of file IDs as listed by the app.json, NOT by the file number in the name
    """
    f = open("data/app.json")
    data = json.load(f)
    for ids in file_ids:
        for i in data['content']['files']:
            if i['id'] == int(ids):
                print(i['links']['download'])
                url = (i['links']['download'])
                name = i["name"] + ".mp3"
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
    check_cache()
    patreon_dl(format_cookies(), file_ids)
else:
    check_cache()
    normal_dl()
