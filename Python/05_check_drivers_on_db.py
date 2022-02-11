#compares the drivers datasets against the drivers inserted into the DB in the previous script
#some drivers they participated only in testing and therefore were not inserted on the DB but have a CSV, this file gives us an output of those cases to be investigated manually

from db import Driver, SESSION
import pandas
import os

driversPath = '../datasets/drivers_races/'
driversComplPath = '../datasets/drivers_complement/'

driversComplements = os.listdir(driversComplPath)
for driverFile in os.listdir(driversPath):
	if "IGNORE" in driverFile:
		continue
	if driverFile in driversComplements:
		driverCsv = pandas.read_csv(driversComplPath+driverFile, sep="\t")
	else:
		driverCsv = pandas.read_csv(driversPath+driverFile, sep="\t")

	driverNames = driverFile[:-4].split()
	#most of drivers have name and surname, but some have 2 or more names, others 2 or more surnames, etc
	#firstname is the first element of the names array, altFirstName is the first two elements and altFirstName2 all elements except the last
	firstName = driverNames[0]
	altFirstName = " ".join(driverNames[0:2])
	altFirstName2 = " ".join(driverNames[:-1])
	#surname is the last element of the names array, altSurname is all except the two first, altSurname2 the last two
	surname = " ".join(driverNames[-1:])
	altSurname = " ".join(driverNames[1:])
	altSurname2 = " ".join(driverNames[2:])
	dbDriver = SESSION.query(Driver).filter((Driver.surname==surname)|(Driver.surname==altSurname)|(Driver.surname==altSurname2)).all()
	#if didn't find the driver in the DB
	if len(dbDriver)==0:
		rows, cols = driverCsv.shape
		#if the CSV has a single row it may be just a DNF, DNQ or absent
		if rows==1:
			for i, driverRace in driverCsv.iterrows():
				#if the value in the finishing position is a number, then there's a problem (it means driver took part in the race)
				if str(driverRace[4]).isnumeric():
					print(driverFile)
					break
		#if has more than one row, there's a problem
		else:
			print(driverFile)
	#even when we find the driver by the surname, have to make sure that the name is the same
	elif len(dbDriver)>1:
		dbDriver = SESSION.query(Driver).filter(((Driver.surname==surname)|(Driver.surname==altSurname)|(Driver.surname==altSurname2)), ((Driver.name==firstName)|(Driver.name==altFirstName)|(Driver.name==altFirstName2))).all()
		#if didn't find, there's a problem
		if len(dbDriver)==0:
			print(driverFile)
		#if found more than one matching, also a problem
		elif len(dbDriver)>1:
			print(driverFile)	