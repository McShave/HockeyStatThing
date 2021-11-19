import os
import sys

import json

from HockeyStatsFunctions import *

def main(argv):

    # variables
    jsonFileName = "teamList.json"
    csvFileName = "teamList.csv"

    # if jsonFileName does not exist in current directory,
    # create new file with a basic list of teams
    if not os.path.isfile("teamList.json") or os.path.getsize("teamList.json") == 0:
        
        print("Creating new json file")
        
        # open jsonFileName as teamListFile, if jsonFileName does not exst, create it (with "w")
        # call newTeamList() from HockeyStatsFunctions.py, function returns json object
        # convert json object teamList to string with json.dumps(),
        # write the object to the opened file
        # close the file
        with open(jsonFileName, "w") as teamListFile:
            teamList = newTeamList()
            teamListInfo = json.dumps(teamList, indent=4)
            teamListFile.write(teamListInfo)
            teamListFile.close()

    # open jsonFileName as TeamListFile, opens for read (with "r")
    # read teamListFile to string teamListInfo
    # convert file string to json object
    # close file
    with open(jsonFileName, "r") as teamListFile:
        teamListInfo = teamListFile.read()
        teamList = json.loads(teamListInfo)
        teamListFile.close()    

    # variables
    num1 = int(argv[0])
    num2 = int(argv[1])
    
    # call function updateGameRange() from HockeyStatFunctions.py
    # returns an updated teamList with games with Game IDs from num1 to num2
    teamList = updateGameRange(teamList, num1, num2)

    # call function convertJsonToCSV() from HockeyStatFunctions.py
    # writes teamList["teams"] as a CSV file called csvFileName
    convertJsonToCSV(csvFileName, teamList["teams"])

    # open jsonFileName as TeamListFile, opens for read and write (with "r+")
    # convert json object to string
    # write json string to file
    # close file
    with open(jsonFileName, "r+") as teamListFile:
        teamListInfo = json.dumps(teamList, indent=4)
        teamListFile.write(teamListInfo)
        teamListFile.close()
        
# call main()
if __name__ == '__main__':
    main(sys.argv[1:])
    
