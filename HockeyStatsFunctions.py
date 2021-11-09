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
    
        teamA_Name = str(gameStats["teams"]["home"]["team"]["name"])
        teamB_Name = str(gameStats["teams"]["away"]["team"]["name"])
        
        teamList["teams"] = updateGamePlayed(gameStats, teamList["teams"], teamA_Name, teamB_Name)
        
        teamList["teams"] = updatePowerRankings(gameStats["teams"], teamList["teams"], teamA_Name, teamB_Name)

    return teamList
    
def updateGamePlayed(gameStats, teamList, teamA_Name, teamB_Name):

    if gameStats["currentPeriod"] < 3:
        print("game between {0} {1} on {2} did not finish.".format(teamList[teamB_Name]["name"],\
        teamList[teamB_Name]["name"], gameStats["period"][0]["startTime"][:10]))
        return teamList
            
    if gameStats["currentPeriod"] == 3:
        if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
            teamList[teamA_Name]["W"] += 1
            teamList[teamA_Name]["Points"] += 2
            teamList[teamB_Name]["L"] += 1
        else:
            teamList[teamB_Name]["W"] += 1
            teamList[teamB_Name]["Points"] += 2
            teamList[teamA_Name]["L"] += 1
            
    elif gameStats["currentPeriod"] > 3:
        if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
            teamList[teamA_Name]["W"] += 1
            teamList[teamA_Name]["Points"] += 2
            teamList[teamB_Name]["L"] += 1
            teamList[teamB_Name]["Points"] += 1
        else:
            teamList[teamB_Name]["W"] += 1
            teamList[teamB_Name]["Points"] += 2
            teamList[teamA_Name]["L"] += 1
            teamList[teamB_Name]["Points"] += 1
    
    teamList[teamA_Name]["GP"] += 1
    teamList[teamB_Name]["GP"] += 1  
    
    return teamList



def updatePowerRankings(gameInfoTeams, teamList, teamA_Name, teamB_Name):

     game_TeamA_gf = gameInfoTeams["home"]["goals"]
     game_TeamA_sf = gameInfoTeams["home"]["shotsOnGoal"]
     game_TeamB_gf = gameInfoTeams["away"]["goals"]
     game_TeamB_sf = gameInfoTeams["away"]["shotsOnGoal"]

     teamA_Modifier = (teamList[teamB_Name]["offPowNum"]*teamList[teamA_Name]["defPowNum"])/\
        (teamList[teamA_Name]["offPowNum"]*teamList[teamB_Name]["defPowNum"])
     teamB_Modifier = (teamList[teamA_Name]["offPowNum"]*teamList[teamB_Name]["defPowNum"])/\
        (teamList[teamB_Name]["offPowNum"]*teamList[teamA_Name]["defPowNum"])

     teamList[teamA_Name]["offPowList"].append(round((game_TeamA_gf/game_TeamA_sf)*teamA_Modifier, 4))
     teamList[teamA_Name]["defPowList"].append(round((game_TeamB_gf/game_TeamB_sf)*teamA_Modifier, 4))

     teamList[teamB_Name]["offPowList"].append(round((game_TeamB_gf/game_TeamB_sf)*teamB_Modifier, 4))
     teamList[teamB_Name]["defPowList"].append(round((game_TeamA_gf/game_TeamA_sf)*teamB_Modifier, 4))


     teamList[teamA_Name] = updateTeamPower(teamList[teamA_Name])
     teamList[teamB_Name] = updateTeamPower(teamList[teamB_Name])

     return (teamList)
    
    
def updateTeamPower(team):

    avg = 0
    for game in team["offPowList"]:
          avg += game
    team["offPowNum"] = round(avg/team["GP"], 4)

    avg = 0
    for game in team["defPowList"]:
          avg += game
    team["defPowNum"] = round(avg/team["GP"], 4)

    team["totalPow"] = round(team["offPowNum"]/team["defPowNum"], 4)
    
    
    return team
    
    
def convertJsonToCSV(teamList):

    teamListCSV = open("teamList.csv", "w")    
        
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
    
    teamListCSV.close()