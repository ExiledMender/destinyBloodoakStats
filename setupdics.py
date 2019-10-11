import requests, zipfile, os, pickle, json, sqlite3

if not os.path.exists('Manifest.content'):
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'

    #get the manifest location from the json
    r = requests.get(manifest_url)
    manifest = r.json()
    #print(manifest['Response'].keys())
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

    #Download the file, write it to 'MANZIP'
    r = requests.get(mani_url)
    with open("MANZIP", "wb") as zip:
        zip.write(r.content)
    #print("Download Complete!")

    #Extract the file contents, and rename the extracted file
    # to 'Manifest.content'
    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'Manifest.content')

getNameFromHashRecords = {}
getNameFromHashActivity= {}
getNameFromHashCollectible = {}
#getNameFromHashUnlocks = {}
#
if not os.path.exists('records.json'):
    con = sqlite3.connect('manifest.content')
    cur = con.cursor()


    cur.execute(
    '''SELECT 
        json
    FROM 
        DestinyRecordDefinition
    ''')
    items = cur.fetchall()
    item_jsons = [json.loads(item[0]) for item in items]
    con.close()
    for ijson in item_jsons:
        getNameFromHashRecords[ijson['hash']] = ijson['displayProperties']['name']
    with open('records.json', 'w') as outfile:
        json.dump(getNameFromHashRecords, outfile)
else:
    with open('records.json') as json_file:
        getNameFromHashRecords = json.load(json_file)


if not os.path.exists('collectible.json'):
    con = sqlite3.connect('manifest.content')
    cur = con.cursor()


    cur.execute(
    '''SELECT 
        json
    FROM 
        DestinyCollectibleDefinition
    ''')
    items = cur.fetchall()

    item_jsons = [json.loads(item[0]) for item in items]
    con.close()
    for ijson in item_jsons:
        if 'name' in ijson['displayProperties']:
            getNameFromHashCollectible[str(ijson['hash'])] = ijson['displayProperties']['name']
    
    with open('collectible.json', 'w') as outfile:
        json.dump(getNameFromHashCollectible, outfile)
else:
    with open('collectible.json') as json_file:
        getNameFromHashCollectible = json.load(json_file)


if not os.path.exists('activities.json'):
    con = sqlite3.connect('manifest.content')
    cur = con.cursor()


    cur.execute(
    '''SELECT 
        json
    FROM 
        DestinyActivityDefinition
    ''')
    items = cur.fetchall()

    item_jsons = [json.loads(item[0]) for item in items]
    con.close()
    for ijson in item_jsons:
        if 'name' in ijson['displayProperties']:
            getNameFromHashActivity[str(ijson['hash'])] = ijson['displayProperties']['name']
    
    with open('activities.json', 'w') as outfile:
        json.dump(getNameFromHashActivity, outfile)
else:
    with open('activities.json') as json_file:
        getNameFromHashActivity = json.load(json_file)
#con = sqlite3.connect('manifest.content')
#cur = con.cursor()
#
#cur.execute(
#'''SELECT name FROM sqlite_master WHERE type='table'
#''')
#items = cur.fetchall()
##print(items)