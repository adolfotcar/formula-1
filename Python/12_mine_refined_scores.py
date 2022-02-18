#compares driver's stats against all their teammates in order to obtain the refined score
#only ran for drivers who won the compaionship or that are still driving(coz they can still becom champions)

from db import Driver, Race, RaceResult, BaseScore, Champion, RefinedScore, SESSION
from sqlalchemy.sql import func, text
from sqlalchemy import case
import pandas
import os
import math

#receives the driver ID and the year to be considered. 
#to obtain the driver score, the year should be 2021 (the latest season)
#to obtain the team mate's score, the year should be the year they raced together
def getBaseScore(driverId, year):

	#reading the values from the base_scores table
	score = SESSION.query(func.sum(BaseScore.races).label("races"),\
							func.sum(BaseScore.wins).label("wins"),\
							func.sum(BaseScore.podiums).label("podiums"),\
							func.sum(BaseScore.poles).label("poles"),\
							func.sum(BaseScore.front_rows).label("front_rows"),\
							func.sum(BaseScore.wet_races).label("wet_races"),\
							func.sum(BaseScore.wet_wins).label("wet_wins"),\
							func.sum(BaseScore.wet_podiums).label("wet_podiums"),\
							func.sum(BaseScore.gained_positions).label("gained_positions"),\
							func.sum(BaseScore.lost_positions).label("lost_positions"),\
							func.sum(BaseScore.starting_position).label("starting_position"),\
							func.sum(BaseScore.retirements_for_collisions).label("retirements_for_colisions"),\
							func.sum(BaseScore.points).label("points"),\
							func.sum(BaseScore.wins_not_from_pole).label("wins_not_from_pole"),\
							func.sum(BaseScore.season_races).label("season_races"),\
							func.max(BaseScore.championships_record_until_now).label("championships_record_until_now"),\
							func.max(BaseScore.races_until_now).label("races_until_now"),\
							func.max(BaseScore.races_record_until_now).label("races_record_until_now"),\
							func.sum(BaseScore.champion_this_season).label("championships"))\
						.filter(BaseScore.driver_id==driverId, BaseScore.year<=year).first()
	
	#calculating the base score
	baseScore = ((score.wins/score.races)*0.231184+\
				(score.podiums/score.races)*0.120778+\
				(score.poles/score.races)*0.139059+\
				(score.front_rows/score.races)*0.048894+\
				(score.wet_wins/score.wet_races if score.wet_races>0 else 0)*0.001676+\
				(score.wet_podiums/score.wet_races if score.wet_races>0 else 0)*0.019313+\
				((score.gained_positions/score.races)-(score.lost_positions/score.races))/(score.starting_position/score.races)*0.026437+\
				((score.races-score.retirements_for_colisions)/score.races)*0.016817+\
				(score.points/score.races/25)*0.130525+\
				(score.wins_not_from_pole/score.wins if score.wins>0 else 0)*0.053239+\
				(score.races/score.season_races)*0.038212+\
				(score.championships/score.championships_record_until_now)*0.118808+\
				(score.races/score.races_record_until_now)*0.055056\
				)

	return baseScore

#points system in F1
points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
#the ids of the champions and the drivers that are still running
championsIds = [champion.driver_id for champion in SESSION.query(Champion.driver_id).group_by(Champion.driver_id).all()]
currentDriverIds = [result.driver_id for result in SESSION.query(RaceResult.driver_id).join(Race).filter(Race.year==2021, RaceResult.driver_id.notin_(championsIds)).group_by(RaceResult.driver_id).all()]
#the program has to run twice: one for the world champions and one for the current drivers
idLists = [championsIds, currentDriverIds]
#after mining the world champions, the next list of ids is of the current drivers
#we have to save it on the DB so it's possible to filter in the future as two separate rankings
miningChampions = True
#reading the drivers list
for ids in idLists:
	drivers = SESSION.query(Driver.id).filter(Driver.id.in_(ids)).order_by(text("drivers.id desc")).all()
	for driver in drivers:
		driverId = driver.id
		#just logging
		print(driverId)
		#reading the score for the driver
		driverScore = getBaseScore(driverId, 2021)
		#all seasons that the driver have competed
		seasons = SESSION.query(RaceResult.team, Race.year).join(Race).filter(RaceResult.driver_id==driverId).group_by(Race.year, RaceResult.team).order_by(Race.year).all()
		refinedScore = 0
		for season in seasons:
			seasonTeamMates = SESSION.query(RaceResult.driver_id).join(Race).filter(Race.year==season.year, RaceResult.team==season.team, RaceResult.driver_id!=driverId).all()
			#some drivers, like Mansel in 1983, raced one race for a testing team...other occasions a team had a single driver
			#in those scenarios there are no teammates to compare so we only use the drivers base sccore
			if len(seasonTeamMates)==0:
				score += driverScore
				continue
			#how many points the driver have scored in the season when comparing against a certain teammate
			driverPoints = 0
			#how many points the team mate have scored in the season
			matePoints = 0
			#the score of the season
			score = 0
			for teamMate in seasonTeamMates:
				#calculate the base score for the team mate in the season, this changes every season even for the same teammate
				mateScore = getBaseScore(teamMate.driver_id, season.year)
				#the races the teammate have raced with the driver in the season
				mateRaces = SESSION.query(RaceResult).join(Race).filter(RaceResult.driver_id==teamMate.driver_id, Race.year==season.year, RaceResult.team==season.team).all()
				#how many races they raced together
				racesTogether = 0
				#how many times the driver finished ahead of the team mate
				finishAheadOfMate = 0
				#how many times the driver started ahead of the team mate
				startAheadOfMate = 0
				for race in mateRaces:
					#reading the drivers result for the specific race
					driverRace = SESSION.query(RaceResult).filter(RaceResult.driver_id==driverId, RaceResult.race_id==race.race_id).first()
					#the driver might not have raced in that race
					if not driverRace:
						continue
					racesTogether += 1
					#establishing points and who finished ahead
					if str(driverRace.finishing_position).isnumeric():
						if str(race.finishing_position).isnumeric():
							if driverRace.finishing_position<=10:
								driverPoints += points[driverRace.finishing_position-1]
							if race.finishing_position<=10:
								matePoints += points[race.finishing_position-1]
							if driverRace.finishing_position<race.finishing_position:
								finishAheadOfMate += 1
						else:
							finishAheadOfMate += 1	
					#establishing who started ahead
					if str(driverRace.starting_position).isnumeric():
						if str(race.starting_position).isnumeric():
							if driverRace.starting_position<race.starting_position:
								startAheadOfMate += 1
						else:
							startAheadOfMate += 1
				teamPoints = driverPoints+matePoints
				#only increments season score, if they actually had at least one race together
				if racesTogether!=0:					
					#if the team didnt score any points, have to avoid division by 0
					if teamPoints==0:
						score += ((math.sqrt(driverScore*mateScore)*14) + (finishAheadOfMate/racesTogether) + (startAheadOfMate/racesTogether))/16
					else:
						if mateScore>0:
							score += ((math.sqrt(driverScore*mateScore)*13) + (finishAheadOfMate/racesTogether) + (driverPoints/teamPoints)+(startAheadOfMate/racesTogether))/16
			#geting the final average of scores against all teammates this season
			refinedScore += score/len(seasonTeamMates)
		#getting the final refined score
		refinedScore = refinedScore/len(seasons)	
		refinedScore =  RefinedScore(driver_id=driverId, base_score=driverScore, refined_score=refinedScore, won_championships=miningChampions)
		SESSION.add(refinedScore)
		SESSION.commit()
	miningChampions = False