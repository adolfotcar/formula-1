#calculates the parameters for base scores
#saves one line per season per driver

from db import Driver, Race, RaceResult, BaseScore, RefinedScore, Champion, SESSION
from sqlalchemy.sql import func, text
import pandas
import os
import math

crashesStrings = ['accident', 'collision', 'avoiding action', 'crash', 'spun', 'spin', 'handling', 'hit']
points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
drivers = SESSION.query(Driver).order_by(Driver.name, Driver.surname).all()
for driver in drivers:
	print("Filling base scores of "+driver.name+" "+driver.surname+"...")
	seasons = SESSION.query(Race.year).join(RaceResult).filter(RaceResult.driver_id==driver.id).group_by(Race.year).all()
	driverCareerRaces = SESSION.query(func.count(RaceResult.driver_id).label("count")).filter(RaceResult.driver_id==driver.id).first()
	seasonCounter = 0
	for season in seasons:
		seasonCounter += 1
		year = season.year
		driverSeasonRaces = SESSION.query(RaceResult).join(Race).filter(Race.year==year, RaceResult.driver_id==driver.id).all()
		maxSeasonFinishingPosition = SESSION.query(func.max(RaceResult.finishing_position).label("max")).join(Race).filter(Race.year==year, RaceResult.finishing_position<35).first()
		seasonRaces = SESSION.query(func.count(Race.id).label("count")).filter(Race.year==year).first()
		seasonChampion = SESSION.query(Champion.driver_id).filter(Champion.year==year).first()
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
			champion_this_season = seasonChampion.driver_id==driver.id,\
		)
		SESSION.add(baseScore)
		SESSION.commit()