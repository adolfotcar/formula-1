#detects drivers that have inconsistant data
#for example, if a driver is in a race file for a certain year, may not have that race in his dataset
#in that case it's logged to be investigated manually
#as the source of the drivers dataset is f1fansite and the race file is official F1 website
#a third source is used to settle conflicts: statsf1 or wikipedia

import pandas
import os

racesPath = '../datasets/races/'
complPath = '../datasets/races_grids_complement/'
driversPath = '../datasets/drivers_races/'
driversComplPath = '../datasets/drivers_complement/'

#various datasets uses different names for the races, so we need this dictionary
racesDictionary = { "70th Anniversary" : ['70th Anniversary'] ,"Abu Dhabi" : ['Abu Dhabi'],"Argentina": ['Argentina', 'Argentine', 'argentinian'],"Australia": ['Australia', 'australian'],"Austria": ['Austria', 'austrian'],"Azerbaijan": ['Azerbaijan', 'baku', 'Azerbijan'],"Bahrain": ['Bahrain'],"Belgium": ['Belgium', 'belgian'],"Brazil": ['Brazil', 'brazilian'],"Canada": ['Canada', 'canadian'],"China": ['China', 'chinese'],"Dallas": ['Dallas', 'detroit'],"Detroit": ['Detroit'],"Eifel": ['Eifel'],"Emilia Romagna" : ['Emilia Romagna', 'e. Romagna'],"Europe": ['Europe', 'european'],"France": ['France', 'french'],"Germany": ['Germany', 'german', 'deutsch'],"Great Britain" : ['Great Britain', 'britain', 'british', 'english', 'uk'],"Hungary": ['Hungary', 'hungarian'],"India": ['India', 'indian'],"Indianapolis 500" : ['Indianapolis 500', 'indianapolis', 'indy', 'indy 500'],"Italy": ['Italy', 'italian', 'talian'],"Japan": ['Japan', 'japanese'],"Las Vegas" : ['Las Vegas', 'vegas', 'nevada', 'Caesars Palace', 'Caesar Palace'],"Luxembourg": ['Luxembourg'],"Malaysia": ['Malaysia', 'malaysian'],"Mexico": ['Mexico', 'mexican'],"Monaco": ['Monaco', 'monte carlo', 'montecarlo'],"Morocco": ['Morocco', 'moroccan'],"Netherlands": ['Netherlands', 'dutch', 'the netherlands'],"Pacific": ['Pacific'],"Pescara": ['Pescara'],"Portugal": ['Portugal', 'portuguese'],"Qatar": ['Qatar'],"Russia": ['Russia', 'russian'],"Sakhir": ['Sakhir'],"San Marino" : ['San Marino','imola'],"Saudi Arabia" : ['Saudi Arabia', 'saudi arabian', 'arabian'],"Singapore": ['Singapore', 'singaporian'],"South Africa" : ['South Africa', 'south african'],"South Korea" : ['South Korea', 'korea', 'korean', 'south korean'],"Spain": ['Spain', 'spanish'],"Styria": ['Styria'],"Sweden": ['Sweden', 'swedish'],"Switzerland": ['Switzerland', 'swiss'],"Turkey": ['Turkey', 'turkish'],"Tuscany": ['Tuscany', 'tuscan'],"USA East" : ['USA East', 'usa', 'america', 'american'],"USA West" : ['USA West', 'usa', 'america', 'american'],"United States" : ['United States', 'usa', 'america', 'american']}
driverFiles = os.listdir(driversPath)
for year in range(1950, 2022):
	for raceFile in os.listdir(racesPath+str(year)):
		raceCsv = pandas.read_csv(racesPath+str(year)+"/"+raceFile, sep="\t")
		for i, race in raceCsv.iterrows():
			#when false, has a conflict and needs to be investigated
			found = False
			#for each line in the race dataset, checks if the driver has his own dataset
			for driverFile in driverFiles:
				if (race[1].strip().lower() in driverFile.lower()) and (race[2].strip().lower() in driverFile.lower()):
					driverCsv = pandas.read_csv(driversPath+driverFile, sep="\t")
					#if they have their own dataset, then searches for the current year (if not found, the driver is missing that race in their dataset and needs fixing)
					for i, driverRace in driverCsv.iterrows():
						#all good, just proceed
						if str(driverRace[0]).strip()==str(year):
							country = raceFile[:-4]
							for val in racesDictionary[country]:
								if val.lower() in driverRace[1].lower():
									found = True
									break
							if found:
								break
			#if there is a conflict, does the same check using the complementary drivers datasets
			if not found:
				for driverComp in os.listdir(driversComplPath):
					if (race[1].strip().lower() in driverComp.lower()) and (race[2].strip().lower() in driverComp.lower()):
						driverCsv = pandas.read_csv(driversComplPath+driverComp, sep="\t")
						for i, driverRace in driverCsv.iterrows():
							if str(driverRace[0]).strip()==str(year):
								country = raceFile[:-4]
								for val in racesDictionary[country]:
									if val.lower() in driverRace[1].lower():
										found = True
										break
								if found:
									break
			#logging the conflicts
			if not found:
				print(str(year)+" - "+race[1]+" "+race[2]+"("+raceFile+")")