from db import BaseScoreStats, SESSION
from sqlalchemy import case
import pandas
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

#creating the dataframe
df = pandas.read_sql(SESSION.query((BaseScoreStats.wins*1.0/BaseScoreStats.races).label("wins"), \
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
									BaseScoreStats.champion_this_season.label("champion") ).statement, SESSION.bind)

Y = df['champion'].values
Y = Y.astype('int')
X = df.drop(labels=['champion'], axis=1)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=30)

#training and predicting using random forest
rf = RandomForestClassifier(random_state=30)
rf.fit(X_train, Y_train)
rf_prediction = rf.predict(X_test)

features = list(X.columns)
importances = pandas.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
print(importances)