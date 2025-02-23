import os, json, pandas, openpyxl, xlsxwriter

import config
from functions import getNameToHashMapByClanid,getTriumphsJSON, playerHasClears, getClearCount,playerHasFlawless,playerHasCollectible,playerHasTriumph,playerHasRole
from dict import requirementHashes, getNameFromHashActivity,getNameFromHashCollectible,getNameFromHashRecords

# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated

path = os.path.dirname(os.path.abspath(__file__))
writer = pandas.ExcelWriter(path + '\\clanAchievements.xlsx', engine='xlsxwriter') # pylint: disable=W0223

#print(playerHasRole(4611686018468695677,'Levi Master','Y1'))

clanid = 2784110 #Bloodoak I

memberids = getNameToHashMapByClanid(clanid) # memberids['Hali'] is my destinyMembershipID
membersystem = dict()
userRoles = {}
for year,yeardata in requirementHashes.items():
    yearResult = {}
    for username, userid in memberids.items():
        if not username in userRoles.keys():
            userRoles[username] = []
        print('Processing user: ' + username + ' with id ' + userid)
        triumphs = getTriumphsJSON(userid)
        yearResult[username] = {}
        
        for role,roledata in yeardata.items():
            rolestatus = len(roledata) > 0
            if not 'requirements' in roledata:
                print('malformatted requirementHashes')
                continue
            for req in roledata['requirements']:
                if req == 'clears':
                    creq = roledata['clears']
                    for raid in creq:
                        requiredN = raid['count']
                        activityname = getNameFromHashActivity[str(raid['actHashes'][0])]
                        condition = activityname + ' clears (' + str(requiredN) + ')'

                        boolHasClears = playerHasClears(userid, requiredN, raid['actHashes'])
                        cc = getClearCount(userid, raid['actHashes'][0])
                        yearResult[username][condition] = str(boolHasClears) + ' (' + str(cc) + ')'
                        rolestatus &= boolHasClears
                elif req == 'flawless':
                    condition = 'flawless ' + getNameFromHashActivity[roledata['flawless'][0]]
                    if playerHasFlawless(userid, roledata['flawless']):
                            yearResult[username][condition] = 'True'
                            found = True
                    else:
                        rolestatus = False
                        yearResult[username][condition] = 'False'
                elif req == 'collectibles':
                    for collectible in roledata['collectibles']:
                        condition = getNameFromHashCollectible[collectible]
                        if playerHasCollectible(userid, collectible):
                            yearResult[username][condition] = 'True'
                        else:
                            yearResult[username][condition] = 'False'
                            rolestatus = False
                elif req == 'records':
                    for recordHash in roledata['records']:
                        condition = getNameFromHashRecords[recordHash]
                        status = playerHasTriumph(userid, recordHash)
                        yearResult[username][condition] = str(status)
                        rolestatus &= (str(status) == 'True')

            yearResult[username][role] = str(rolestatus)
            if rolestatus:
                userRoles[username].append(role)
            else:
                userRoles[username].append('')

    df = pandas.DataFrame(yearResult)
    df = df.transpose()
    
    df.to_excel(writer, sheet_name = year + ' Roles')

pandas.DataFrame(userRoles).transpose().to_excel(writer, header=None, sheet_name = 'User Roles')
workbook = writer.book
fat = workbook.add_format({'bold': True})

pandas.DataFrame(memberids).transpose().to_excel(writer, header=None, sheet_name = 'Users')

redBG = workbook.add_format({'bg_color': '#FFC7CE'})
greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

importantColumns = {
    'Y1'  : ['A','D','G','J','M','P','W'],
    'Y2'  : ['A','F', 'M','R','X','AE','AK'],
    'Y3'  : ['A']
}

worksheet = writer.sheets['User Roles']
worksheet.set_column('A:A', 15, fat)
worksheet.set_column('B:M', 6, fat)

for year in requirementHashes:
    worksheet = writer.sheets[year + ' Roles']
    worksheet.set_column('A:AK', 2)
    for let in importantColumns[year]:
        worksheet.set_column(let +':'+let, 15, fat)
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'False',
                                                'format': redBG})
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'True',
                                                'format': greenBG})
    worksheet.set_zoom(80)
writer.save()
print('excel file created')