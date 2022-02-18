#calculates the parameters for base scores
#saves one line per season per driver

from db import Driver, Race, RaceResult, BaseScore, RefinedScore, Champion, Standing, Lineup, SESSION
from sqlalchemy.sql import func, text
import pandas
import os
import math

crashesStrings = ['accident', 'collision', 'avoiding action', 'crash', 'spun', 'spin', 'handling', 'hit']
points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
drivers = SESSION.query(Driver).order_by(Driver.name, Driver.surname).all()
for driver in drivers:
	print("Filling base scores of "+driver.name+" "+driver.surname+"...")
	driverChampionships = SESSION.query(func.count(Champion.driver_id).label("count")).filter(Champion.driver_id==driver.id).first()
	seasons = SESSION.query(Race.year).join(RaceResult).filter(RaceResult.driver_id==driver.id).group_by(Race.year).all()
	driverCareerRaces = SESSION.query(func.count(RaceResult.driver_id).label("count")).filter(RaceResult.driver_id==driver.id).first()
	seasonCounter = 0
	for season in seasons:
		seasonCounter += 1
		year = season.year
		driverSeasonRaces = SESSION.query(RaceResult).join(Race).filter(Race.year==year, RaceResult.driver_id==driver.id).all()
		racesRecord = SESSION.query(func.count(RaceResult.driver_id).label("count")).join(Race).filter(Race.year<=year).group_by(RaceResult.driver_id).order_by(text("count desc")).first()
		driverRaces = SESSION.query(func.count(RaceResult.driver_id).label("count")).join(Race).filter(Race.year<=year, RaceResult.driver_id==driver.id).group_by(RaceResult.driver_id).order_by(text("count desc")).first()
		seasonRaces = SESSION.query(func.count(Race.id).label("count")).filter(Race.year==year).first()
		seasonChampion = SESSION.query(Champion.driver_id).filter(Champion.year==year).first()
		if seasonChampion.driver_id!=driver.id:
			driverTeam = SESSION.query(Lineup.team).filter(Lineup.year==year, Lineup.driver_id==driver.id).order_by(text("total_races desc")).first()
			driverPoints = SESSION.query(Standing.points).filter(Standing.year==year, Standing.driver_id==driver.id).first()
			teamMates = [teammate.driver_id for teammate in SESSION.query(Lineup.driver_id).filter(Lineup.year==year, Lineup.team==driverTeam.team, Lineup.driver_id!=driver.id).all()]
			teamMatesPoints = SESSION.query(func.sum(Standing.points).label("sum")).filter(Standing.year==year, Standing.driver_id.in_(teamMates)).first()
			if driverPoints==None:
				betterInTeam = 0
			elif teamMatesPoints.sum==None:
				betterInTeam = 1
			else:
				betterInTeam = driverPoints.points>teamMatesPoints.sum
		else:
			betterInTeam = True
		wins = winsNotFromPole = poles = podiums = frontRows = wetRaces = wetWins = wetPodiums = \
		gainedPositions = lostPositions = retirementForCollisions = driverPoints = startingPosition = 0
		for raceResult in driverSeasonRaces:
			if not str(raceResult.starting_position).isnumeric():
				continue
			startingPosition += raceResult.starting_position
			raceDetails = SESSION.query(Race).filter(Race.id==raceResult.race_id).first()
			if raceResult.finishing_position==1:
				wins += 1
				if raceResult.starting_position>1:
					winsNotFromPole += 1
			if raceResult.starting_position==1:
				poles += 1
			if str(raceResult.finishing_position).isnumeric():
				if raceResult.finishing_position>raceResult.starting_position:
					lostPositions += raceResult.finishing_position - raceResult.starting_position
				else:
					gainedPositions += raceResult.starting_position - raceResult.finishing_position
				if raceResult.finishing_position<4:
					podiums += 1
			if raceResult.starting_position<3:
				frontRows += 1
			if raceDetails.rain_affected==True:
				wetRaces += 1
				if raceResult.finishing_position==1:
					wetWins += 1
				if str(raceResult.finishing_position).isnumeric():
					if raceResult.finishing_position<4:
						wetPodiums += 1				
			if any (substr in str(raceResult.retirement_reason).lower() for substr in crashesStrings):
				retirementForCollisions += 1
			if str(raceResult.finishing_position).isnumeric():
				if raceResult.finishing_position<11:
					driverPoints += points[raceResult.finishing_position-1]
		racesCount = len(driverSeasonRaces)

		baseScore = BaseScore(driver_id = driver.id, \
			year=year,\
			races = racesCount, \
			wins = wins, \
			podiums = podiums, \
			poles = poles, \
			front_rows = frontRows, \
			wet_races = wetRaces,\
			wet_wins = wetWins, \
			wet_podiums = wetPodiums, \
			gained_positions = gainedPositions, \
			lost_positions = lostPositions, \
			retirements_for_colisions = retirementForCollisions, \
			points = driverPoints, \
			wins_not_from_pole = winsNotFromPole,\
			starting_position = startingPosition, \
			season_races = seasonRaces.count, \
			driver_races_up_to_this_season = driverRaces.count,\
			races_record_up_to_this_season = racesRecord.count, \
			championships = driverChampionships.count, \
			champion_this_season = seasonChampion.driver_id==driver.id,\
			better_than_teammate = betterInTeam\
		)
		SESSION.add(baseScore)
		SESSION.commit()