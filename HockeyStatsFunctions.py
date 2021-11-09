import csv
import json
import urllib.request


def newTeamList():
     
    teamListInfo = urllib.request.urlopen("https://statsapi.web.nhl.com/api/v1/teams").read()
    teamListJson = json.loads(teamListInfo)["teams"]
    teamList = {}
    teamList["gamesRecorded"] = []

    for team in teamListJson:
        teamList[team["id"]] = {"id": team["id"], "name": team["name"], "link": team["link"], "GP": 0, "W": 0, "L": 0, "OTL": 0,\
            "Points": 0, "totalPow": 1, "offPowList": [], "offPowNum": 1, "defPowList": [], "defPowNum": 1}

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
    
        teamA_ID = str(gameStats["teams"]["home"]["team"]["id"])
        teamB_ID = str(gameStats["teams"]["away"]["team"]["id"])
        
        teamList[teamA_ID]["GP"] += 1
        teamList[teamB_ID]["GP"] += 1
        
        if gameStats["currentPeriod"] == 3:
            if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
                teamList[teamA_ID]["W"] += 1
                teamList[teamA_ID]["Points"] += 2
                teamList[teamB_ID]["L"] += 1
            else:
                teamList[teamB_ID]["W"] += 1
                teamList[teamB_ID]["Points"] += 2
                teamList[teamA_ID]["L"] += 1
                
        elif gameStats["currentPeriod"] > 3:
            if gameStats["teams"]["home"]["goals"] > gameStats["teams"]["away"]["goals"]:
                teamList[teamA_ID]["W"] += 1
                teamList[teamA_ID]["Points"] += 2
                teamList[teamB_ID]["L"] += 1
                teamList[teamB_ID]["Points"] += 1
            else:
                teamList[teamB_ID]["W"] += 1
                teamList[teamB_ID]["Points"] += 2
                teamList[teamA_ID]["L"] += 1
                teamList[teamA_ID]["Points"] += 1
                
        else:
            print("game between {0} {1} on {2} did not finish.".format(teamList[teamA_ID]["name"],\
                teamList[teamB_ID]["name"], gameStats["period"][0]["startTime"][:10]))
            continue
            
        
        teamList = updatePowerRankings(gameStats["teams"], teamList, teamA_ID, teamB_ID)

    return teamList
    

def updatePowerRankings(teams, teamList, teamA_ID, teamB_ID):

     game_TeamA_gf = teams["home"]["goals"]
     game_TeamA_sf = teams["home"]["shotsOnGoal"]
     game_TeamB_gf = teams["away"]["goals"]
     game_TeamB_sf = teams["away"]["shotsOnGoal"]

     teamA_Modifier = (teamList[teamB_ID]["offPowNum"]*teamList[teamA_ID]["defPowNum"])/\
        (teamList[teamA_ID]["offPowNum"]*teamList[teamB_ID]["defPowNum"])
     teamB_Modifier = (teamList[teamA_ID]["offPowNum"]*teamList[teamB_ID]["defPowNum"])/\
        (teamList[teamB_ID]["offPowNum"]*teamList[teamA_ID]["defPowNum"])

     teamList[teamA_ID]["offPowList"].append(round((game_TeamA_gf/game_TeamA_sf)*teamA_Modifier, 4))
     teamList[teamA_ID]["defPowList"].append(round((game_TeamB_gf/game_TeamB_sf)*teamA_Modifier, 4))

     teamList[teamB_ID]["offPowList"].append(round((game_TeamB_gf/game_TeamB_sf)*teamB_Modifier, 4))
     teamList[teamB_ID]["defPowList"].append(round((game_TeamA_gf/game_TeamA_sf)*teamB_Modifier, 4))


     teamList[teamA_ID] = updateTeamPower(teamList[teamA_ID])
     teamList[teamB_ID] = updateTeamPower(teamList[teamB_ID])

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
        if count == 0 and team.isnumeric():
     
            # Writing headers of CSV file
            header = teamList[team].keys()
            csv_writer.writerow(header)
            count += 1
     
        if team.isnumeric():
            # Writing data of CSV file
            csv_writer.writerow(teamList[team].values())
    
    teamListCSV.close()