#goes trhough the races files and assembles the history of lineups 

from db import Driver, Lineup, SESSION
import pandas
import os

racesPath = '../datasets/races/'

for year in range(1950, 2022):
	print(year)
	for raceFile in os.listdir(racesPath+str(year)):
		raceCsv = pandas.read_csv(racesPath+str(year)+"/"+raceFile, sep="\t")
		for i, race in raceCsv.iterrows():
			#finds the driver in the DB
			driver = SESSION.query(Driver).filter(Driver.name==race[1].strip(), Driver.surname==race[2].strip()).first()
			if not driver:
				continue

			team = str(race[4]).strip()
			lineup = SESSION.query(Lineup).filter(Lineup.driver_id==driver.id, Lineup.team==team, Lineup.year==year).first()
			#if there's no record yet, creates one with total races of one
			if not lineup:
				newLineup = Lineup(team=team, year=year, driver_id=driver.id, total_races=1)
				SESSION.add(newLineup)
			#if record already exists, increments total races
			else:
				lineup.total_races += 1
			SESSION.commit()