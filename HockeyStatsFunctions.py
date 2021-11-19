import csv
import json
import urllib.request

# function is called to create new team list
# returns a json with the following format:
#{
#    "gamesRecorded": []
#    "teams": {
#        teamName: {
#            "name": teamName
#            "GP: 0
#            "W": 0
#            "L": 0
#            "OTL": 0
#            "Points": 0
#            "totalPow": 1
#            "offPowList": []
#            "offPowNum": 1
#            "defPowList": []
#            "defPowNum": 1
#        },
#        ...
#    }
#}
def newTeamList():
    
    # grab team list from NHL stats webserver API
    # convert team list to json object
    # create new json object, this will be returned
    # add gamesRecorded list to new json
    # add team dict to new json
    teamListInfo = urllib.request.urlopen("https://statsapi.web.nhl.com/api/v1/teams").read()
    teamListJson = json.loads(teamListInfo)["teams"]
    teamList = {}
    teamList["gamesRecorded"] = []
    teamList["teams"] = {}
    
    # for team in team list json from NHL API
    # creats new team in teamList["teams"]
    for team in teamListJson:
        teamList["teams"][team["name"]] = {"name": team["name"], "GP": 0, "W": 0, "L": 0, "OTL": 0, "Points": 0,\
            "totalPow": 1, "offPowList": [], "offPowNum": 1, "defPowList": [], "defPowNum": 1}
    
    #returns new team list
    return teamList
    
# this function updates teams in teamList with games from range gameID1 to gameID2
# returns an updated teamList
def updateGameRange(teamList, gameID1, gameID2):
     
    
    # make a list of strings containing the url for each gameID from NHL API
    # adds game ID to teamList["gamesRecorded"]
    # if game was recorded, does not add to list
    gameList = []
    for i in range(gameID2-gameID1+1):
        if gameID1+i not in teamList["gamesRecorded"]:
            gameList.append("https://statsapi.web.nhl.com/api/v1/game/202102{0:04d}/linescore".format(gameID1+i))
            teamList["gamesRecorded"].append(gameID1+i)
        else:
            print("Game {0} already recorded".format(gameID1+i))
    teamList["gamesRecorded"].sort()

    # for gameID link in list of game urls
    # retrieves game information from url 
    # updates teams in teamList that played in the game
    for gameURL in gameList:
    
        # retrieve game info from game URL
        # convert game info to json object
        gameStatsInfo = urllib.request.urlopen(gameURL).read()
        gameStats = json.loads(gameStatsInfo)
    
        # retrieve team names from game info
        teamA_name = gameStats["teams"]["home"]["team"]["name"]
        teamB_name = gameStats["teams"]["away"]["team"]["name"]
        
        # retrieve teams from teamList
        teamA = teamList["teams"][teamA_name]
        teamB = teamList["teams"][teamB_name]
        
        # if the game is completed, update team stats
        newTeamA, newTeamB = updateGamePlayed(gameStats, teamA, teamB)
        if newTeamA and newTeamB:
            teamA, teamB = updatePowerRankings(gameStats["teams"], teamA, teamB)
        
    return teamList

# this function updates teamA and teamB Games Played, Wins, Loss, OT Loss, and Points
# if the game has not finished, sends none values    
def updateGamePlayed(gameStats, teamA, teamB):

    # check to see if game is finished
    if gameStats["currentPeriod"] < 3:
        print("game between {0} and {1} did not finish.".format(teamA["name"], teamB["name"]))
        return None, None
    
    # check to see if game finished in regulation time
    if gameStats["currentPeriod"] == 3:
        if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
            teamA["W"] += 1
            teamA["Points"] += 2
            teamB["L"] += 1
        else:
            teamB["W"] += 1
            teamB["Points"] += 2
            teamA["L"] += 1
    
    # check to see if game finished in extra time
    elif gameStats["currentPeriod"] > 3:
        if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
            teamA["W"] += 1
            teamA["Points"] += 2
            teamB["L"] += 1
            teamB["Points"] += 1
        else:
            teamB["W"] += 1
            teamB["Points"] += 2
            teamA["L"] += 1
            teamA["Points"] += 1
    
    teamA["GP"] += 1
    teamB["GP"] += 1  
    
    return teamA, teamB

# this function is called if a the game was completed
# updates the offPow Num and List and defPow Num and List
def updatePowerRankings(gameInfoTeams, teamA, teamB):

    teamA, teamB = addToPowerList(gameInfoTeams, teamA, teamB)

    teamA = updatePowerNums(teamA)
    teamB = updatePowerNums(teamB)

    return (teamA, teamB)
    
# adds the game stats to each team's offPowList and defPowList
# offPow number added is goals scored/ shots taken (scoring %)
# defPow number is goals allowed/ shots recevied (goals allowed %)
# a higher offPow number is better, while a lower defPow number is better
def addToPowerList(gameInfoTeams, teamA, teamB):

    # retrieve stats from game
    game_TeamA_gf = gameInfoTeams["home"]["goals"]
    game_TeamA_sf = gameInfoTeams["home"]["shotsOnGoal"]
    game_TeamB_gf = gameInfoTeams["away"]["goals"]
    game_TeamB_sf = gameInfoTeams["away"]["shotsOnGoal"]

    # these modifiers are to be used to realistically adjust stats based on the teams that played
    # cannot get the math correct, so have commented out for now
    # teamA_Modifier = (teamB["offPowNum"]*teamA["defPowNum"])/(teamA["offPowNum"]*teamB["defPowNum"])
    # teamB_Modifier = (teamA["offPowNum"]*teamB["defPowNum"])/(teamB["offPowNum"]*teamA["defPowNum"])

    # add the numbers to list
    teamA["offPowList"].append(round((game_TeamA_gf/game_TeamA_sf), 4))
    teamA["defPowList"].append(round((game_TeamB_gf/game_TeamB_sf), 4))
    teamB["offPowList"].append(round((game_TeamB_gf/game_TeamB_sf), 4))
    teamB["defPowList"].append(round((game_TeamA_gf/game_TeamA_sf), 4))

    return teamA, teamB

# updates totalPow, offPowNum, and defPowNum of team
# totalPow is the inverse relationship of offPowNum and defPowNum
# as offPowNum gets higher (more goals per shot taken), totalPow gets higher
# as defPowNum gets lower (less goals allowed per shot received), totalPow gets higher
def updatePowerNums(team):

    # offPowNum is the average of each number from offPowList
    avg = 0
    for game in team["offPowList"]:
          avg += game
    team["offPowNum"] = avg/team["GP"]

    # defPowNum is the average of each number from defPowList
    avg = 0
    for game in team["defPowList"]:
          avg += game
    team["defPowNum"] = avg/team["GP"]
    
    # totalPow is offPowNum/ defPowNum
    print("{0}, offPowNum: {1}, defPowNum: {2}".format(team["name"], team["offPowNum"], team["defPowNum"]))
    team["totalPow"] = team["offPowNum"]/team["defPowNum"]
    
    return team
    
# creates a new csv file with information from teamList
def convertJsonToCSV(filename, teamList):

    with open(filename, "w", newline = '') as teamListCSV:    
        
        # create the csv writer object
        csv_writer = csv.writer(teamListCSV)
         
        # Counter variable used for writing
        # headers to the CSV file
        count = 0
         
        for team in teamList:
            if count == 0:
         
                # Writing headers of CSV file
                header = teamList[team].keys()
                csv_writer.writerow(header)
                count += 1
         
            else:
                # Writing data of CSV file
                csv_writer.writerow(teamList[team].values())
