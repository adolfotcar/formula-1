#reads all relevant grids dataset, those which have an equivalent race dataset, and removes special characters from the drivers names and surnames

import pandas
import os
import unidecode

racesPath = '../datasets/races/'
gridsPath = '../datasets/races_grids/'
complPath = '../datasets/races_grids_complement/'

for year in range(1950, 2022):
	for raceFile in os.listdir(racesPath+str(year)):
		#if race file does not have an equivalent grid file, then just continues
		if not os.path.isfile(gridsPath+str(year)+"/"+raceFile):
			continue

		#reads the csv, changes encoding and saves it
		gridCsv = pandas.read_csv(gridsPath+str(year)+"/"+raceFile, sep="\t")
		gridCsv.driverName.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
		gridCsv.driverSurname.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
		gridCsv.to_csv(gridsPath+str(year)+"/"+raceFile, sep="\t", index=False)

for year in range(1950, 2022):
	for raceFile in os.listdir(racesPath+str(year)):
		#if race file does not have an equivalent grid file, then just continues
		if not os.path.isfile(complPath+str(year)+"/"+raceFile):
			continue

		#reads the csv, changes encoding and saves it
		gridCsv = pandas.read_csv(complPath+str(year)+"/"+raceFile, sep="\t")
		gridCsv.names.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
		gridCsv.to_csv(complPath+str(year)+"/"+raceFile, sep="\t", index=False)