#compares driver's stats against all their teammates in order to obtain the refined score
#only ran for drivers who won the compaionship or that are still driving(coz they can still becom champions)

from db import Driver, Race, RaceResult, BaseScoreStats, BaseScore, Champion, RefinedScore, SESSION
from sqlalchemy import case
from sqlalchemy.sql import func, text
import math

def computeScore(score):
	baseScore = ((score.wins/score.races)*0.227474+\
				(score.podiums/score.races)*0.086604+\
				(score.poles/score.races)*0.106152+\
				(score.front_rows/score.races)*0.044463+\
				(score.wet_wins/score.wet_races if score.wet_races>0 else 0)*0.014864+\
				(score.wet_podiums/score.wet_races if score.wet_races>0 else 0)*0.016290+\
				((score.gained_positions/score.races)-(score.lost_positions/score.races))/(score.starting_position/score.races)*0.038639+\
				((score.races-score.retirements_for_collisions)/score.races)*0.017322+\
				(score.points/score.races/25)*0.164522+\
				(score.wins_not_from_pole/score.wins if score.wins>0 else 0)*0.047705+\
				(score.races/score.season_races)*0.030252+\
				(score.championships/score.championships_record_until_now)*0.166374+\
				(score.races/score.races_record_until_now)*0.039338\
				)

	return baseScore

#receives the driver ID and the year to be considered. 
#to obtain the driver score, the year should be 2021 (the latest season)
#to obtain the team mate's score, the year should be the year they raced together
def getBaseScore(driverId, year):

	#reading the values from the base_scores table
	query = SESSION.query(func.sum(BaseScoreStats.races).label("races"),\
							func.sum(BaseScoreStats.wins).label("wins"),\
							func.sum(BaseScoreStats.podiums).label("podiums"),\
							func.sum(BaseScoreStats.poles).label("poles"),\
							func.sum(BaseScoreStats.front_rows).label("front_rows"),\
							func.sum(BaseScoreStats.wet_races).label("wet_races"),\
							func.sum(BaseScoreStats.wet_wins).label("wet_wins"),\
							func.sum(BaseScoreStats.wet_podiums).label("wet_podiums"),\
							func.sum(BaseScoreStats.gained_positions).label("gained_positions"),\
							func.sum(BaseScoreStats.lost_positions).label("lost_positions"),\
							func.sum(BaseScoreStats.starting_position).label("starting_position"),\
							func.sum(BaseScoreStats.retirements_for_collisions).label("retirements_for_collisions"),\
							func.sum(BaseScoreStats.points).label("points"),\
							func.sum(BaseScoreStats.wins_not_from_pole).label("wins_not_from_pole"),\
							func.sum(BaseScoreStats.season_races).label("season_races"),\
							func.max(BaseScoreStats.championships_record_until_now).label("championships_record_until_now"),\
							func.max(BaseScoreStats.races_until_now).label("races_until_now"),\
							func.max(BaseScoreStats.races_record_until_now).label("races_record_until_now"),\
							func.sum(BaseScoreStats.champion_this_season).label("championships"))
	score = query.filter(BaseScoreStats.driver_id==driverId, BaseScoreStats.year==year).first()
	seasonScore = computeScore(score)

	score = query.filter(BaseScoreStats.driver_id==driverId, BaseScoreStats.year<=year).first()
	careerScore = computeScore(score)

	return seasonScore, careerScore

drivers = SESSION.query(Driver).order_by(Driver.name, Driver.surname).all()
for driver in drivers:
	print(driver.name, driver.surname)
	driverId = driver.id
	seasons = SESSION.query(Race.year).join(RaceResult).filter(RaceResult.driver_id==driverId).group_by(Race.year).order_by(Race.year).all()
	for season in seasons:
		year = season.year
		seasonScore, careerScore = getBaseScore(driverId, year)
		baseScore =  BaseScore(driver_id=driverId, year=year, career_score=careerScore,season_score=seasonScore)
		SESSION.add(baseScore)

SESSION.commit()
