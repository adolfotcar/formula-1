from db import RefinedScore, Driver, BaseScoreStats, BaseScore, SESSION
from sqlalchemy import func, case
import pandas
import matplotlib.pyplot as plt

scoresChamps = pandas.read_sql(SESSION.query(func.round(RefinedScore.refined_score, 4).label("score"), Driver.name, Driver.surname).\
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


import plotly.express as px
df = pandas.read_sql(baseScoreQuery.filter(BaseScoreStats.driver_id==722).statement, SESSION.bind)

fig = px.line_polar(df, theta=['wins', 'podiums', 'poles', 'front_rows', 'wet_wins', 'wet_podiums', 'positions', 'collisions', 'points', 'wins not from pole', 'season_races', 'championships', 'career_races'], line_close=True)
fig.show()