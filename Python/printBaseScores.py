#reads reace results table and builds the standings according to current ponctuation rules

from db import Driver, Race, RaceResult, BaseScore, SESSION
from sqlalchemy.sql import func, text
import pandas
import os

record_races = SESSION.query(func.count(RaceResult.driver_id).label("count")).join(Race).filter(Race.year<=2021).group_by(RaceResult.driver_id).order_by(text("count desc")).first()
drivers = SESSION.query(Driver).order_by(Driver.name, Driver.surname).all()
for driver in drivers:
	score = SESSION.query(func.sum(BaseScore.races).label("races"),\
							func.sum(BaseScore.wins).label("wins"),\
							func.sum(BaseScore.pdiums).label("pdiums"),\
							func.sum(BaseScore.poles).label("poles"),\
							func.sum(BaseScore.front_rows).label("front_rows"),\
							func.sum(BaseScore.wet_races).label("wet_races"),\
							func.sum(BaseScore.wet_wins).label("wet_wins"),\
							func.sum(BaseScore.wet_podiums).label("wet_podiums"),\
							func.sum(BaseScore.average_starting_position).label("average_starting_position"),\
							func.sum(BaseScore.average_finishing_position).label("average_finishing_position"),\
							func.sum(BaseScore.retirements_for_colisions).label("retirements_for_colisions"),\
							func.max(BaseScore.f1_race_record_at_retirement).label("f1_race_record_at_retirement"))\
						.filter(BaseScore.driver_id==driver.id).first()

	wetRaces = score.wet_races
	if wetRaces==0:
		wetWinsRatio = 0
		wetPodiumsRatio = 0
	else:
		wetWinsRatio = score.wet_wins/wetRaces
		wetPodiumsRatio = score.wet_podiums/wetRaces
	races = score.races
	base_score = ((score.wins/races)+\
					(score.pdiums/races)+\
					(score.poles/races)+\
					(score.front_rows/races)+\
					(wetWinsRatio)+\
					(wetPodiumsRatio)+\
					((score.average_starting_position-score.average_finishing_position)/score.average_starting_position)+\
					((races-score.retirements_for_colisions)/races)+\
					((score.wins-score.poles)/races)+\
					((score.pdiums-score.front_rows)/races)+\
					(races/score.f1_race_record_at_retirement)+\
					(races/record_races.count))\
					/12

	SESSION.commit()

	print(driver.name, driver.surname, ";"+str(base_score))