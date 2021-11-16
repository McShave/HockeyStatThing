Hockey Stat Thing

to run, enter:
python HockeyStat.py arg1 arg2

arg1, arg2 are the starting and ending Game_ID numbers to add to the teams power ranking calculation.

The games included in the calculation are tracked, so no game can be repeated.

This will generate or update 2 files, teamList.json and teamList.csv.


Future Plans:

- better display option than a .csv file, maybe web app integration (with flask or other similar library)

- better sorting methods.

- tracking stats tracking, including changes over recent days/ games.

- add automation to update the team power ranking after games are played

- view todays games and chances.