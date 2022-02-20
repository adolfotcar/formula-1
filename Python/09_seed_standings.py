#reads reace results table and builds the standings according to current ponctuation rules

from db import Race, RaceResult, Standing, SESSION

racesPath = '../datasets/races/'

#this the current points system
points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
for year in range(1950, 2022):
	print(year)
	races = SESSION.query(Race).filter(Race.year==year).all()
	for race in races:
		results = SESSION.query(RaceResult).filter(RaceResult.race_id==race.id).all()
		for result in results:
			#if reult is DNQ, DNF, etc continues
			if not str(result.finishing_position).isnumeric():
				continue
			#if finished higher than 10th, skips...
			if result.finishing_position>10:
				continue

			#finding how many points were scored
			driverPoints = points[result.finishing_position-1]
			standing = SESSION.query(Standing).filter(Standing.year==year, Standing.driver_id==result.driver_id).first()
			#if no registry for the driver and the season, creates one
			if not standing:
				standing = Standing(driver_id=result.driver_id, year=year, points=driverPoints)
				SESSION.add(standing)
			#if there's a registry for the driver and the season, increments points scored
			else:
				standing.points += driverPoints
			SESSION.commit()