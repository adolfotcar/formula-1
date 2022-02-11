#reads the daaset of wet races and makes sure that they exist in our DB
from db import Race, SESSION
import pandas

racesCsv = pandas.read_csv('../datasets/wet_races/races.csv', sep="\t")
for i, race in racesCsv.iterrows():
	weather = race[1].lower().strip()
	if ("sunny" in weather) or ("night" in weather) or ("cloudy" in weather):
		continue
	
	raceDetails = race[0].strip().split()
	name = " ".join(raceDetails[:-1])
	year = "".join(raceDetails[-1:])

	yearRaces =  SESSION.query(Race).filter(Race.year==year).all()
	found = False
	for race in yearRaces:
		if name.lower().strip() in race.name.lower().strip():
			found = True

	if not found:
		print(year, name)