from ast import literal_eval
import requests
import json


def api_update(user):
    returntext = "Data has been updated. You may continue with other commands."
    with open('users.json') as data:
        userlist = [literal_eval(line) for line in data]
    index = [(i, el.index(user)) for i, el in enumerate(userlist) if user in el]
    line = index[0][0]
    key = userlist[line][1]
    url = "https://lyrania.co.uk/api/accounts.php?search="+key
    try:
        jdata = requests.get(url).json()
        with open(user + ".json", "w+") as data:
            data.write(json.dumps(jdata, sort_keys=True, indent=3))
    except:
        returntext = "An error occurred. Please try again."
    return returntext
