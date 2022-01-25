from ast import literal_eval
import requests
import json


def api_update(user):
    returntext = "Data has been updated. You may continue with other commands."
    with open('users.json') as data:
        data_json = json.load(data)
        key = data_json[user]
    url = "https://lyrania.co.uk/api/accounts.php?search="+key
    try:
        jdata = requests.get(url).json()
        with open(user + ".json", "w+") as data:
            data.write(json.dumps(jdata, sort_keys=True, indent=3))
    except:
        returntext = "An error occurred. Please try again."
    return returntext


def fetch(user, *key):
    with open(user+".json") as data:
        data_json = json.load(data)
    for x in key:
        data_json = data_json[x]
    return data_json
