SELECT 
	id, 
	wins*1.0/races AS wins,
	podiums*1.0/races AS podiums,
	poles*1.0/races AS poles,
	front_rows*1.0/races AS front_rows,
	CASE WHEN wet_races>0 THEN wet_wins*1.0/wet_races ELSE 0 END AS wet_wins,
	CASE WHEN wet_races>0 THEN wet_podiums*1.0/wet_races ELSE 0 END AS wet_podiums,
	((gained_positions*1.0/races)-(lost_positions*1.0/races))/starting_position*1.0/races AS positions,
	((races-retirements_for_colisions)*1.0)/races AS collisions,
	points*1.0/races/25 AS points,
	CASE WHEN wins>0 THEN wins_not_from_pole*1.0/wins ELSE 0 END AS wins_not_from_pole,
	races*1.0/season_races AS season_races,
	championships*1.0/7 AS championships,
	driver_races_up_to_this_season*1.0/races_record_up_to_this_season AS total_races,
	champion_this_season
FROM 
	base_scores;


SELECT 
	drivers.name, drivers.surname, refined_score 
FROM 
	refined_scores 
	LEFT JOIN drivers ON drivers.id=refined_scores.driver_id 
WHERE 
	won_championships=1 
ORDER BY refined_score DESC;