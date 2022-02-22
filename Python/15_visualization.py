from db import RefinedScore, Driver, BaseScoreStats, BaseScore, SESSION
from sqlalchemy import func, case
import pandas
import matplotlib.pyplot as plt
import numpy as np

"""scoresChamps = pandas.read_sql(SESSION.query(func.round(RefinedScore.refined_score, 4).label("score"), Driver.name, Driver.surname).\
								join(Driver).filter(RefinedScore.won_championships==1).order_by(RefinedScore.refined_score).statement, \
								SESSION.bind)
scoresCurrent = pandas.read_sql(SESSION.query(func.round(RefinedScore.refined_score, 4).label("score"), Driver.name, Driver.surname).\
								join(Driver).filter(RefinedScore.won_championships==0).order_by(RefinedScore.refined_score).statement, \
								SESSION.bind)
baseScoreQuery = SESSION.query((BaseScoreStats.wins*1.0/BaseScoreStats.races).label("wins"), \
									(BaseScoreStats.podiums*1.0/BaseScoreStats.races).label("podiums"), \
									(BaseScoreStats.poles*1.0/BaseScoreStats.races).label("poles"), \
									(BaseScoreStats.front_rows*1.0/BaseScoreStats.races).label("front_rows"), \
									case([(BaseScoreStats.wet_races>0, BaseScoreStats.wet_wins*1.0/BaseScoreStats.wet_races)], else_=0).label("wet_wins"), \
									case([(BaseScoreStats.wet_races>0, BaseScoreStats.wet_podiums*1.0/BaseScoreStats.wet_races)], else_=0).label("wet_podiums"), \
									(((BaseScoreStats.gained_positions*1.0/BaseScoreStats.races)-(BaseScoreStats.lost_positions*1.0/BaseScoreStats.races))/BaseScoreStats.starting_position*1.0/BaseScoreStats.races).label("positions"), \
									(((BaseScoreStats.races-BaseScoreStats.retirements_for_collisions)*1.0)/BaseScoreStats.races).label("collisions"), \
									(BaseScoreStats.points*1.0/BaseScoreStats.races/25).label("points"), \
									case([(BaseScoreStats.wins>0, BaseScoreStats.wins_not_from_pole*1.0/BaseScoreStats.wins)], else_=0).label("wins_not_from_pole"), \
									(BaseScoreStats.races*1.0/BaseScoreStats.season_races).label("season_races"), \
									(BaseScoreStats.championships_until_now*1.0/BaseScoreStats.championships_record_until_now).label("championships"), \
									(BaseScoreStats.races_until_now*1.0/BaseScoreStats.races_record_until_now).label("career_races"), \
									BaseScoreStats.champion_this_season.label("champion") )
    
df = pandas.read_sql(baseScoreQuery.statement, SESSION.bind)

plt.matshow(df.corr())
#plt.show()

kimiScores = pandas.read_sql(SESSION.query(BaseScore.season_score, BaseScore.year).filter(BaseScore.driver_id==689).statement, SESSION.bind, index_col="year")
schumacherScores = pandas.read_sql(SESSION.query(BaseScore.season_score, BaseScore.year).filter(BaseScore.driver_id==629).statement, SESSION.bind, index_col="year")
buttonScores = pandas.read_sql(SESSION.query(BaseScore.season_score, BaseScore.year).filter(BaseScore.driver_id==685).statement, SESSION.bind, index_col="year")
sennaScores = pandas.read_sql(SESSION.query(BaseScore.season_score, BaseScore.year).filter(BaseScore.driver_id==587).statement, SESSION.bind, index_col="year")

kimiScores.plot(kind='bar', color={'season_score': ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'orange', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue','blue']})
schumacherScores.plot(kind='bar', color={'season_score': ['blue', 'blue', 'blue', 'orange', 'orange', 'blue', 'blue', 'blue', 'blue', 'orange', 'orange', 'orange', 'orange', 'orange', 'blue', 'blue', 'blue', 'blue','blue']})
buttonScores.plot(kind='bar', color={'season_score': ['blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'orange', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue','blue']})
sennaScores.plot(kind='bar', color={'season_score': ['blue', 'blue', 'blue', 'blue', 'orange', 'blue', 'orange', 'orange', 'blue', 'blue', 'red']})

kimiScores = pandas.read_sql(SESSION.query(BaseScore.career_score, BaseScore.year).filter(BaseScore.driver_id==689).statement, SESSION.bind, index_col="year")
schumacherScores = pandas.read_sql(SESSION.query(BaseScore.career_score, BaseScore.year).filter(BaseScore.driver_id==629).statement, SESSION.bind, index_col="year")
buttonScores = pandas.read_sql(SESSION.query(BaseScore.career_score, BaseScore.year).filter(BaseScore.driver_id==685).statement, SESSION.bind, index_col="year")
sennaScores = pandas.read_sql(SESSION.query(BaseScore.career_score, BaseScore.year).filter(BaseScore.driver_id==587).statement, SESSION.bind, index_col="year")

kimiScores.plot()
schumacherScores.plot()
buttonScores.plot()
sennaScores.plot()

baseScores = pandas.read_sql(SESSION.query(BaseScore.season_score).statement, SESSION.bind)
baseScores.plot(kind='hist', bins=100)

championsScores = pandas.read_sql(SESSION.query(RefinedScore.refined_score).filter(RefinedScore.won_championships==True).statement, SESSION.bind)
championsScores.plot(kind='hist', bins= 10)

"""

parameters = ['Wins', \
            'Podiums', \
            'Poles', \
            'Front Rows', \
            'Wet Wins', \
            'Wet Podiums', \
            'Positioning', \
            'Collision Avoidance', \
            'Points', \
            'Wins Not From Pole', \
            'Season Races', \
            'Championships', \
            'Career Races', '']
    
query = SESSION.query(	func.sum(BaseScoreStats.races).label("races"),\
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
                            func.sum(BaseScoreStats.champion_this_season).label("championships")\
                        )
score =query.filter(BaseScoreStats.driver_id==722).first()
hamilton = [(score.wins/score.races),\
        (score.podiums/score.races),\
        (score.poles/score.races),\
        (score.front_rows/score.races),\
        (score.wet_wins/score.wet_races if score.wet_races>0 else 0),\
        (score.wet_podiums/score.wet_races if score.wet_races>0 else 0),\
        ((score.gained_positions/score.races)-(score.lost_positions/score.races))/(score.starting_position/score.races),\
        ((score.races-score.retirements_for_collisions)/score.races),\
        (score.points/score.races/25),\
        (score.wins_not_from_pole/score.wins if score.wins>0 else 0),\
        (score.races/score.season_races),\
        (score.championships/score.championships_record_until_now),\
        (score.races/score.races_record_until_now)]    
hamilton = np.concatenate((hamilton, [hamilton[0]]))


score =query.filter(BaseScoreStats.driver_id==587).first()
senna = [(score.wins/score.races),\
        (score.podiums/score.races),\
        (score.poles/score.races),\
        (score.front_rows/score.races),\
        (score.wet_wins/score.wet_races if score.wet_races>0 else 0),\
        (score.wet_podiums/score.wet_races if score.wet_races>0 else 0),\
        ((score.gained_positions/score.races)-(score.lost_positions/score.races))/(score.starting_position/score.races),\
        ((score.races-score.retirements_for_collisions)/score.races),\
        (score.points/score.races/25),\
        (score.wins_not_from_pole/score.wins if score.wins>0 else 0),\
        (score.races/score.season_races),\
        (score.championships/score.championships_record_until_now),\
        (score.races/score.races_record_until_now)]    
senna = np.concatenate((senna, [senna[0]]))

score =query.filter(BaseScoreStats.driver_id==555).first()
prost = [(score.wins/score.races),\
        (score.podiums/score.races),\
        (score.poles/score.races),\
        (score.front_rows/score.races),\
        (score.wet_wins/score.wet_races if score.wet_races>0 else 0),\
        (score.wet_podiums/score.wet_races if score.wet_races>0 else 0),\
        ((score.gained_positions/score.races)-(score.lost_positions/score.races))/(score.starting_position/score.races),\
        ((score.races-score.retirements_for_collisions)/score.races),\
        (score.points/score.races/25),\
        (score.wins_not_from_pole/score.wins if score.wins>0 else 0),\
        (score.races/score.season_races),\
        (score.championships/score.championships_record_until_now),\
        (score.races/score.races_record_until_now)]    
prost = np.concatenate((prost, [prost[0]]))

score =query.filter(BaseScoreStats.driver_id==1).first()
fangio = [(score.wins/score.races),\
        (score.podiums/score.races),\
        (score.poles/score.races),\
        (score.front_rows/score.races),\
        (score.wet_wins/score.wet_races if score.wet_races>0 else 0),\
        (score.wet_podiums/score.wet_races if score.wet_races>0 else 0),\
        ((score.gained_positions/score.races)-(score.lost_positions/score.races))/(score.starting_position/score.races),\
        ((score.races-score.retirements_for_collisions)/score.races),\
        (score.points/score.races/25),\
        (score.wins_not_from_pole/score.wins if score.wins>0 else 0),\
        (score.races/score.season_races),\
        (score.championships/score.championships_record_until_now),\
        (score.races/score.races_record_until_now)]    
fangio = np.concatenate((fangio, [fangio[0]]))

label_placement = np.linspace(start=0, stop=2*np.pi, num=len(hamilton))


plt.figure(figsize=(10, 10))
plt.subplot(polar=True)
plt.plot(label_placement, hamilton)
plt.plot(label_placement, prost)
plt.plot(label_placement, fangio)
plt.plot(label_placement, senna)
lines, labels = plt.thetagrids(np.degrees(label_placement), labels=parameters)
plt.title('Driver', y=1.1, fontdict={'fontsize': 18})
plt.legend(labels=['Hamilton', 'Prost', 'Fangio', 'Senna'], loc=(0.95, 0.8))