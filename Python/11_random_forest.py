from db import Driver, Race, RaceResult, BaseScore, Champion, RefinedScore, SESSION
from sqlalchemy import case
import pandas
from matplotlib import pyplot as plt
import numpy

df = pandas.read_sql(SESSION.query((BaseScore.wins*1.0/BaseScore.races).label("wins"), \
									(BaseScore.podiums*1.0/BaseScore.races).label("podiums"), \
									(BaseScore.poles*1.0/BaseScore.races).label("poles"), \
									(BaseScore.front_rows*1.0/BaseScore.races).label("front_rows"), \
									case([(BaseScore.wet_races>0, BaseScore.wet_wins*1.0/BaseScore.wet_races)], else_=0).label("wet_wins"), \
									case([(BaseScore.wet_races>0, BaseScore.wet_podiums*1.0/BaseScore.wet_races)], else_=0).label("wet_podiums"), \
									(((BaseScore.gained_positions*1.0/BaseScore.races)-(BaseScore.lost_positions*1.0/BaseScore.races))/BaseScore.starting_position*1.0/BaseScore.races).label("positions"), \
									(((BaseScore.races-BaseScore.retirements_for_collisions)*1.0)/BaseScore.races).label("collisions"), \
									(BaseScore.points*1.0/BaseScore.races/25).label("points"), \
									case([(BaseScore.wins>0, BaseScore.wins_not_from_pole*1.0/BaseScore.wins)], else_=0).label("wins_not_from_pole"), \
									(BaseScore.races*1.0/BaseScore.season_races).label("season_races"), \
									(BaseScore.championships_until_now*1.0/BaseScore.championships_record_until_now).label("championships"), \
									(BaseScore.races_until_now*1.0/BaseScore.races_record_until_now).label("career_races"), \
									BaseScore.champion_this_season.label("champion") ).statement, SESSION.bind)

Y = df['champion'].values
Y = Y.astype('int')
X = df.drop(labels=['champion'], axis=1)

from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=20)

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=10, random_state=30)

model.fit(X_train, Y_train)
prediction_test = model.predict(X_test)

from sklearn import metrics
accuracy = metrics.accuracy_score(Y_test, prediction_test)

print(accuracy)

feature_list = list(X.columns)
feature_imp = pandas.Series(model.feature_importances_, index=feature_list).sort_values(ascending=False)

print(feature_imp)