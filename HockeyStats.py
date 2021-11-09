import os
import sys

import json

from HockeyStatsFunctions import newTeamList
from HockeyStatsFunctions import updateGameRange
from HockeyStatsFunctions import convertJsonToCSV

def main(argv):

    # if teamList.json does not exist, create new file and teamList
    if not os.path.isfile("teamList.json") or os.path.getsize("teamList.json") == 0:
        print("Creating new json file")
        with open("teamList.json", "w") as teamListFile:
            teamList = newTeamList()
            teamListInfo = json.dumps(teamList, indent=4)
            teamListFile.write(teamListInfo)
            teamListFile.close()

    # open teamList.json
    teamListFile = open("teamList.json", "r+")
    teamListInfo = teamListFile.read()
    teamList = json.loads(teamListInfo)
    
    # for team in teamList:
        # print(teamList[team])
        
    teamList = updateGameRange(teamList, int(argv[0]), int(argv[1]))

    convertJsonToCSV(teamList)

    #update teamList and write to teamList.json
    teamListInfo = json.dumps(teamList, indent=4)
    teamListFile.seek(0)
    teamListFile.write(teamListInfo)
    teamListFile.close()

if __name__ == '__main__':
    main(sys.argv[1:])
    
