from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

ENGINE = create_engine("sqlite:///formula1.db")
SESSION = sessionmaker(bind=ENGINE)()

BASE = declarative_base()

class Driver(BASE):
	__tablename__ = "drivers"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String)
	surname = Column(String)
	abbreviation = Column(String)

class Race(BASE):
	__tablename__ = "races"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String)
	year = Column(Integer)
	rain_affected = Column(Boolean)

class RaceResult(BASE):
	__tablename__ = "race_results"

	id = Column(Integer, primary_key=True, autoincrement=True)
	driver_id = Column(Integer, ForeignKey('drivers.id'))
	race_id = Column(Integer, ForeignKey('races.id'))
	starting_position = Column(Integer)
	finishing_position = Column(Integer)
	team = Column(String)
	retirement_reason = Column(String)

class Lineup(BASE):
	__tablename__ = "lineups"

	id = Column(Integer, primary_key=True, autoincrement=True)
	team = Column(String)
	year = Column(Integer)
	driver_id = Column(Integer, ForeignKey('drivers.id'))
	total_races = Column(Integer)

class Standing(BASE):
	__tablename__ = "standings"

	id = Column(Integer, primary_key=True, autoincrement=True)
	year = Column(Integer)
	driver_id = Column(Integer, ForeignKey('drivers.id'))
	points = Column(Integer)

class BaseScore(BASE):
	__tablename__ = "base_scores"

	id = Column(Integer, primary_key=True, autoincrement=True)
	driver_id = Column(Integer, ForeignKey('drivers.id'))	
	year = Column(Integer)
	races = Column(Integer)
	wins = Column(Integer)
	podiums = Column(Integer)
	poles = Column(Integer)
	front_rows = Column(Integer)
	wet_races = Column(Integer)
	wet_wins = Column(Integer)
	wet_podiums = Column(Integer)
	gained_positions = Column(Integer)
	lost_positions = Column(Integer)
	retirements_for_colisions = Column(Integer)
	points = Column(Integer)
	wins_not_from_pole = Column(Integer)
	starting_position = Column(Integer)
	champion_this_season = Column(Boolean)

class RefinedScore(BASE):
	__tablename__ = "refined_scores"

	id = Column(Integer, primary_key=True, autoincrement=True)
	driver_id = Column(Integer, ForeignKey('drivers.id'))
	base_score = Column(Float)
	refined_score = Column(Float)
	won_championships = Column(Boolean)


class Champion(BASE):
	__tablename__ = "champions"
	id = Column(Integer, primary_key=True, autoincrement=True)
	driver_id = Column(Integer, ForeignKey('drivers.id'))
	year = Column(Integer)

BASE.metadata.create_all(ENGINE)