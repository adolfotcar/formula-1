#calculates and saves the parameters for base scores
#saves one line per season per driver

from db import Driver, Race, RaceResult, BaseScore, RefinedScore, Champion, Standing, Lineup, SESSION
from sqlalchemy.sql import func, text
import pandas
import os
import math

#from the retirement reson, detects when it was caused by some form of collision
crashesStrings = ['accident', 'collision', 'avoiding action', 'crash', 'spun', 'spin', 'handling', 'hit']
#current point system, must be used universally for better consistency
points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
#loading all drivers
drivers = SESSION.query(Driver).order_by(Driver.name, Driver.surname).all()
for driver in drivers:
	print("Filling base scores of "+driver.name+" "+driver.surname+"...")
	#loading all seasons
	seasons = SESSION.query(Race.year).join(RaceResult).filter(RaceResult.driver_id==driver.id).group_by(Race.year).all()
	for season in seasons:
		year = season.year
		#how many races were in this season
		seasonRaces = SESSION.query(func.count(Race.id).label("count")).filter(Race.year==year).first()
		#how many races the driver raced in his career up to this year
		driverRaces = SESSION.query(func.count(RaceResult.driver_id).label("count")).join(Race).filter(Race.year<=year, RaceResult.driver_id==driver.id).group_by(RaceResult.driver_id).order_by(text("count desc")).first()
		#record of most raced by a single driver up to this year
		racesRecord = SESSION.query(func.count(RaceResult.driver_id).label("count")).join(Race).filter(Race.year<=year).group_by(RaceResult.driver_id).order_by(text("count desc")).first()
		#how many championships the driver won up to this year
		driverChampionships = SESSION.query(func.count(Champion.driver_id).label("count")).filter(Champion.driver_id==driver.id, Champion.year<=year).first()
		#record of most championships up to this season
		championshipsRecord = SESSION.query(func.count(Champion.driver_id).label("count")).filter(Champion.year<=year).group_by(Champion.driver_id).order_by(text("count desc")).first()
		#who was the champions this season
		seasonChampion = SESSION.query(Champion.driver_id).filter(Champion.year==year).first()

		wins = winsNotFromPole = poles = podiums = frontRows = wetRaces = wetWins = wetPodiums = \
		gainedPositions = lostPositions = retirementForCollisions = driverPoints = startingPosition = 0
		#the races that the driver raced this season
		driverSeasonRaces = SESSION.query(RaceResult).join(Race).filter(Race.year==year, RaceResult.driver_id==driver.id).all()		
		for raceResult in driverSeasonRaces:
			#some drivers were enrolled in the race but never started
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
			retirements_for_collisions = retirementForCollisions, \
			points = driverPoints, \
			wins_not_from_pole = winsNotFromPole,\
			starting_position = startingPosition, \
			season_races = seasonRaces.count, \
			races_until_now = driverRaces.count,\
			races_record_until_now = racesRecord.count, \
			championships_until_now = driverChampionships.count, \
			championships_record_until_now = championshipsRecord.count,\
			champion_this_season = seasonChampion.driver_id==driver.id\
		)
		SESSION.add(baseScore)
		SESSION.commit()