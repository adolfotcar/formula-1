import pandas
from matplotlib import pyplot as plt
import numpy

df = pandas.read_csv("ahead.csv");

#sizes = df['champion'].value_counts(sort=1)
#print(sizes)

Y = df['ahead'].values

Y = Y.astype('int')

X = df.drop(labels=['ahead'], axis=1)

from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.05, random_state=20)

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