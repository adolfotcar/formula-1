#seeds the retirement resons from each driver CSV into the race results table
#also marks the appropriate races as rain affected

from db import Driver, Race, RaceResult, SESSION
import pandas
import os

driversPath = '../datasets/drivers_races/'
driversComplPath = '../datasets/drivers_complement/'

#various datasets uses different names for the races, so we need this dictionary
racesDictionary = { "70th Anniversary" : ['70th Anniversary'] ,"Abu Dhabi" : ['Abu Dhabi'],"Argentina": ['Argentina', 'Argentine', 'argentinian'],"Australia": ['Australia', 'australian'],"Austria": ['Austria', 'austrian'],"Azerbaijan": ['Azerbaijan', 'baku', 'Azerbijan'],"Bahrain": ['Bahrain'],"Belgium": ['Belgium', 'belgian'],"Brazil": ['Brazil', 'brazilian'],"Canada": ['Canada', 'canadian'],"China": ['China', 'chinese'],"Dallas": ['Dallas', 'detroit'],"Detroit": ['Detroit'],"Eifel": ['Eifel'],"Emilia Romagna" : ['Emilia Romagna', 'e. Romagna'],"Europe": ['Europe', 'european'],"France": ['France', 'french'],"Germany": ['Germany', 'german', 'deutsch'],"Great Britain" : ['Great Britain', 'britain', 'british', 'english', 'uk'],"Hungary": ['Hungary', 'hungarian'],"India": ['India', 'indian'],"Indianapolis 500" : ['Indianapolis 500', 'indianapolis', 'indy', 'indy 500'],"Italy": ['Italy', 'italian', 'talian'],"Japan": ['Japan', 'japanese'],"Las Vegas" : ['Las Vegas', 'vegas', 'nevada', 'Caesars Palace', 'Caesar Palace'],"Luxembourg": ['Luxembourg'],"Malaysia": ['Malaysia', 'malaysian'],"Mexico": ['Mexico', 'mexican'],"Monaco": ['Monaco', 'monte carlo', 'montecarlo'],"Morocco": ['Morocco', 'moroccan'],"Netherlands": ['Netherlands', 'dutch', 'the netherlands'],"Pacific": ['Pacific'],"Pescara": ['Pescara'],"Portugal": ['Portugal', 'portuguese'],"Qatar": ['Qatar'],"Russia": ['Russia', 'russian'],"Sakhir": ['Sakhir'],"San Marino" : ['San Marino','imola'],"Saudi Arabia" : ['Saudi Arabia', 'saudi arabian', 'arabian'],"Singapore": ['Singapore', 'singaporian'],"South Africa" : ['South Africa', 'south african'],"South Korea" : ['South Korea', 'korea', 'korean', 'south korean'],"Spain": ['Spain', 'spanish'],"Styria": ['Styria'],"Sweden": ['Sweden', 'swedish'],"Switzerland": ['Switzerland', 'swiss'],"Turkey": ['Turkey', 'turkish'],"Tuscany": ['Tuscany', 'tuscan'],"USA East" : ['USA East', 'usa', 'america', 'american'],"USA West" : ['USA West', 'usa', 'america', 'american'],"United States" : ['United States', 'usa', 'america', 'american']}
driversComplements = os.listdir(driversComplPath)
for driverFile in sorted(os.listdir(driversPath)):
	print("Seeding retirement reasons for "+driverFile[:-4]+"...")
	#files fixed previouly contain an IGNORE, they are files for drivers that didn't actually completed a race
	if "IGNORE" in driverFile:
		continue
	#checking if we're using a complementary dataset or a main one....
	if driverFile in driversComplements:
		driverCsv = pandas.read_csv(driversComplPath+driverFile, sep="\t")
	else:
		driverCsv = pandas.read_csv(driversPath+driverFile, sep="\t")

	#most of drivers have name and surname, but some have 2 or more names, others 2 or more surnames, etc
	#firstname is the first element of the names array, altFirstName is the first two elements and altFirstName2 all elements except the last
	driverNames = driverFile[:-4].split()
	firstName = driverNames[0]
	altFirstName = " ".join(driverNames[0:2])
	altFirstName2 = " ".join(driverNames[:-1])
	#surname is the last element of the names array, altSurname is all except the two first, altSurname2 the last two
	surname = " ".join(driverNames[-1:])
	altSurname = " ".join(driverNames[1:])
	altSurname2 = " ".join(driverNames[2:])
	dbDriver = SESSION.query(Driver).filter((Driver.surname==surname)|(Driver.surname==altSurname)|(Driver.surname==altSurname2)).all()
	#if we found more than one by the surname, then we refine using the name
	if len(dbDriver)>1:
		dbDriver = SESSION.query(Driver).filter(((Driver.surname==surname)|(Driver.surname==altSurname)|(Driver.surname==altSurname2)), ((Driver.name==firstName)|(Driver.name==altFirstName)|(Driver.name==altFirstName2))).all()
		driver = dbDriver[0]
	elif len(dbDriver)==1:
		driver = dbDriver[0]

	#updating driver's races
	for i, driverRace in driverCsv.iterrows():
		year = driverRace[0]
		raceTitle = driverRace[1]
		retirementReason = driverRace[5]
		raceId = None
		seasonRaces = SESSION.query(Race).filter(Race.year==year).all()
		for race in seasonRaces:
			for val in racesDictionary[race.name]:
				if val.lower() in raceTitle.lower():
					raceId = race.id
					break
			if not (raceId is None):
				break

		result = SESSION.query(RaceResult).filter(RaceResult.race_id==raceId, RaceResult.driver_id==driver.id).first()
		if result:
			result.retirement_reason = retirementReason
	SESSION.commit()

#"%accident%" "%collision%" "%avoiding action%" "%crash%" "%spun%" "%handling%" "%hit%"
	

	
#iterrates the rows in the dataset, finds the equivalent DB registry and marks as rain affected
racesCsv = pandas.read_csv('../datasets/wet_races/races.csv', sep="\t")
for i, race in racesCsv.iterrows():
	print("Seeding races weather for "+race[0]+"...")
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
			race.rain_affected = True
			SESSION.commit()
			found = True

	if not found:
		print(year, name)