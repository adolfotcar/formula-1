#making sure that every driver in the races datasets, have a starting position either from the grid dataset or the complementary grid dataset
#outputs a list of year race - driver name and surname, which have to be investigated individually

import pandas
import os

racesPath = '../datasets/races/'
gridsPath = '../datasets/races_grids/'
complPath = '../datasets/races_grids_complement/'

for year in range(1950, 2022):
	for raceFile in os.listdir(racesPath+str(year)):
		#we have to know if the grid dataset is a standard or complementary, because they have different structures
		usedComplement = False
		raceCsv = pandas.read_csv(racesPath+str(year)+"/"+raceFile, sep="\t")
		if os.path.isfile(gridsPath+str(year)+"/"+raceFile):
			gridCsv = pandas.read_csv(gridsPath+str(year)+"/"+raceFile, sep="\t")
		elif os.path.isfile(complPath+str(year)+"/"+raceFile):
			gridCsv = pandas.read_csv(complPath+str(year)+"/"+raceFile, sep="\t")
			usedComplement = True
		#if can't find either a standard grid or a complementary, outputs as an error
		else:
			print(raceFile)
			continue
		for i, race in raceCsv.iterrows():
			startingPosition = None
			for j, grid in gridCsv.iterrows():
				#the complementary file name and surname are both in the column 1
				if usedComplement:
					if (race[1].strip().lower() in str(grid[1]).strip().lower()) and (race[2].strip().lower() in str(grid[1]).strip().lower()):
						startingPosition = grid[0]
						break
				#in the standard file, name and surname are in different columns
				else:
					if (race[1].strip().lower() in grid[1].strip().lower()) and (race[2].strip().lower() in grid[2].strip().lower()):
						startingPosition = grid[0]
						break
			#if couldn't find the starting position, logs the details to be investigated
			if startingPosition==None:
				print(str(year)+" "+raceFile+" - "+race[1]+" "+race[2])