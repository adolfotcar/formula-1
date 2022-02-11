#seeds the drivers, races and races results using the CSV datasets

from db import Driver, Race, RaceResult, Champion, SESSION
import pandas
import os

racesPath = '../datasets/races/'
gridsPath = '../datasets/races_grids/'
complPath = '../datasets/races_grids_complement/'
champsPath = '../datasets/champions/World_Champions.csv'

#creating one record per racefile
for year in range(1950, 2022):
	print("Seeding drivers and races from "+str(year)+"...")
	for raceFile in os.listdir(racesPath+str(year)):
		raceCsv = pandas.read_csv(racesPath+str(year)+"/"+raceFile, sep="\t")
		#each record in the race CSV is a driver, if they are not in the DB yet have to create
		for i, race in raceCsv.iterrows():
			drivers = SESSION.query(Driver).filter(Driver.name==race[1].strip(), Driver.surname==race[2].strip()).all()
			#if found at least one matching driver record, then addNew would be false
			addNew = len(drivers)==0
			#it's possible that two drivers have the same name and surname, but then they'd have different abbreviations
			for driver in drivers:
				if (driver.abbreviation!=race[3].strip()):
					addNew = True
					break
			
			#adding if it was decided that it doesn't exist yet
			if addNew:
				newDriver = Driver(name=race[1].strip(), surname=race[2].strip(), abbreviation=race[3].strip())
				SESSION.add(newDriver)

		#adding a record for the race
		race = Race(name=raceFile[:-4], year=year)
		SESSION.add(race)
		SESSION.commit()

#the race results we need the grid files to record the starting positions
for year in range(1950, 2022):
	print("Seeding races results from "+str(year)+"...")
	for raceFile in os.listdir(racesPath+str(year)):
		#sometimes we'll use the main datasets, other times the complementary....
		usedComplement = False
		raceCsv = pandas.read_csv(racesPath+str(year)+"/"+raceFile, sep="\t")
		if os.path.isfile(gridsPath+str(year)+"/"+raceFile):
			gridCsv = pandas.read_csv(gridsPath+str(year)+"/"+raceFile, sep="\t")
		elif os.path.isfile(complPath+str(year)+"/"+raceFile):
			gridCsv = pandas.read_csv(complPath+str(year)+"/"+raceFile, sep="\t")
			usedComplement = True
		else:
			#just loging in case can't find the equivalent dataset
			print(raceFile+" - "+str(year))
			continue
		dbRace = SESSION.query(Race).filter(Race.year==year, Race.name==raceFile[:-4]).first()
		for i, race in raceCsv.iterrows():
			startingPosition = None
			for j, grid in gridCsv.iterrows():
				#when used complement the name and surname are in the same cell
				if usedComplement:
					if (race[1].strip().lower() in str(grid[1]).strip().lower()) and (race[2].strip().lower() in str(grid[1]).strip().lower()):
						startingPosition = grid[0]
						break
				else:
					if (race[1].strip().lower() in grid[1].strip().lower()) and (race[2].strip().lower() in grid[2].strip().lower()):
						startingPosition = grid[0]
						break
			if startingPosition==None:
				print(str(year)+" "+raceFile+" - "+race[1]+" "+race[2])
			else:
				dbDriver = SESSION.query(Driver).filter(Driver.name==race[1].strip(), Driver.surname==race[2].strip()).first()
				result = RaceResult(driver_id=dbDriver.id, \
									race_id=dbRace.id, \
									starting_position=startingPosition, \
									finishing_position=race[0], \
									team=str(race[4])) 
				SESSION.add(result)
	SESSION.commit()

print("Seeding champions...")
#creates a table with the world champions, will be used for the refined score
championships = pandas.read_csv(champsPath, sep="\t")
for i, championship in championships.iterrows():
	year = championship[0]
	driverNames = str(championship[1]).strip().split()
	#firstname is the first element of the names array, altFirstName is the first two elements and altFirstName2 all elements except the last
	firstName = driverNames[0]
	altFirstName = " ".join(driverNames[0:2])
	altFirstName2 = " ".join(driverNames[:-1])
	#surname is the last element of the names array, altSurname is all except the two first, altSurname2 the last two
	surname = " ".join(driverNames[-1:])
	altSurname = " ".join(driverNames[1:])
	altSurname2 = " ".join(driverNames[2:])
	drivers = SESSION.query(Driver).filter((Driver.surname==surname)|(Driver.surname==altSurname)|(Driver.surname==altSurname2)).all()
	if len(drivers)==1:
		driver = drivers[0]
	elif len(drivers)>1:
		drivers = SESSION.query(Driver).filter((Driver.surname==surname)|(Driver.surname==altSurname)|(Driver.surname==altSurname2), (Driver.name==firstName)|(Driver.name==altFirstName)|(Driver.name==altFirstName2)).all()
		if len(drivers)==1:
			driver = drivers[0]
		else:
			print(driverNames)
	else:
		print(driverNames)

	champion = Champion(driver_id=driver.id, year=year)
	SESSION.add(champion)
	SESSION.commit()