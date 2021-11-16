import csv
import json
import urllib.request


def newTeamList():
     
    teamListInfo = urllib.request.urlopen("https://statsapi.web.nhl.com/api/v1/teams").read()
    teamListJson = json.loads(teamListInfo)["teams"]
    teamList = {}
    teamList["gamesRecorded"] = []
    teamList["teams"] = {}
    
    for team in teamListJson:
        teamList["teams"][team["name"]] = {"name": team["name"], "GP": 0, "W": 0, "L": 0, "OTL": 0, "Points": 0,\
            "totalPow": 1, "offPowList": [], "offPowNum": 1, "defPowList": [], "defPowNum": 1}

    return teamList
    
    
def updateGameRange(teamList, gameID1, gameID2):
     
    
    gameList = []
    for i in range(gameID2-gameID1+1):
        if gameID1+i not in teamList["gamesRecorded"]:
            gameList.append("https://statsapi.web.nhl.com/api/v1/game/202102{0:04d}/linescore".format(gameID1+i))
            teamList["gamesRecorded"].append(gameID1+i)
        else:
            print("Game {0} already recorded".format(gameID1+i))

    teamList["gamesRecorded"].sort()

    for gameURL in gameList:
        gameStatsInfo = urllib.request.urlopen(gameURL).read()
        gameStats = json.loads(gameStatsInfo)
    
        teamA_name = gameStats["teams"]["home"]["team"]["name"]
        teamB_name = gameStats["teams"]["away"]["team"]["name"]
        
        teamA = teamList["teams"][teamA_name]
        teamB = teamList["teams"][teamB_name]
        
        teamA, teamB = updateGamePlayed(gameStats, teamA, teamB)
        teamA, teamB = updatePowerRankings(gameStats["teams"], teamA, teamB)

    return teamList
    
def updateGamePlayed(gameStats, teamA, teamB):

    if gameStats["currentPeriod"] < 3:
        print("game between {0} {1} on {2} did not finish.".format(teamList[teamB_Name]["name"],\
        teamList[teamB_Name]["name"], gameStats["period"][0]["startTime"][:10]))
        return teamList
            
    if gameStats["currentPeriod"] == 3:
        if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
            teamA["W"] += 1
            teamA["Points"] += 2
            teamB["L"] += 1
        else:
            teamB["W"] += 1
            teamB["Points"] += 2
            teamA["L"] += 1
            
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



def updatePowerRankings(gameInfoTeams, teamA, teamB):

    teamA, teamB = addToPowerList(gameInfoTeams, teamA, teamB)


    teamA = updatePowerNums(teamA)
    teamB = updatePowerNums(teamB)

    return (teamA, teamB)
    

def addToPowerList(gameInfoTeams, teamA, teamB):

     game_TeamA_gf = gameInfoTeams["home"]["goals"]
     game_TeamA_sf = gameInfoTeams["home"]["shotsOnGoal"]
     game_TeamB_gf = gameInfoTeams["away"]["goals"]
     game_TeamB_sf = gameInfoTeams["away"]["shotsOnGoal"]

     # teamA_Modifier = (teamB["offPowNum"]*teamA["defPowNum"])/\
        # (teamA["offPowNum"]*teamB["defPowNum"])
     # teamB_Modifier = (teamA["offPowNum"]*teamB["defPowNum"])/\
        # (teamB["offPowNum"]*teamA["defPowNum"])

     teamA["offPowList"].append(round((game_TeamA_gf/game_TeamA_sf), 4))
     teamA["defPowList"].append(round((game_TeamB_gf/game_TeamB_sf), 4))

     teamB["offPowList"].append(round((game_TeamB_gf/game_TeamB_sf), 4))
     teamB["defPowList"].append(round((game_TeamA_gf/game_TeamA_sf), 4))


     teamA = updatePowerNums(teamA)
     teamB = updatePowerNums(teamB)

     return teamA, teamB
    
def updatePowerNums(team):

    avg = 0
    for game in team["offPowList"]:
          avg += game
    team["offPowNum"] = avg/team["GP"]

    avg = 0
    for game in team["defPowList"]:
          avg += game
    team["defPowNum"] = avg/team["GP"]

    team["totalPow"] = team["offPowNum"]/team["defPowNum"]
    
    return team
    
    
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
