#loads individual records for each driver
#main usage is to get the reason for retirement for each driver
#source of data: F1 fan site


#used to harvest our data
library(rvest)
#used to remove accentuation from the drivers names
library(stringr)

#creates a directory for our datasets
racesPath = "../datasets/wet_races/"
dir.create("../datasets/", showWarnings = FALSE)
dir.create(racesPath, showWarnings = FALSE)

racesWeathers = c()
racesTitles = c()
for (year in 2017:2017){
  print(year)
  #link to the season main page
  homeLink = paste("https://www.statsf1.com/en/", year, ".aspx", sep="")
  homePage = read_html(homeLink)
  links = html_attr(html_nodes(homePage, ".flag a"), "href")
  
  for (link in links){
    raceLink = paste("https://www.statsf1.com", link, sep="")
    racePage = read_html(raceLink)
    
    weather = html_attr(html_nodes(racePage, ".GPmeteo img"), "alt")
    titleAndYear = html_text(html_nodes(racePage, ".navcenter a"))
    raceTitle = ""
    for (titleElement in titleAndYear){
      raceTitle = paste(raceTitle, titleElement) 
    }
    
    racesWeathers = c(racesWeathers, weather)
    racesTitles = c(racesTitles, raceTitle)
  }
}

print(racesTitles)
print(racesWeathers)
races = data.frame(racesTitles, racesWeathers, stringsAsFactors = FALSE)
write.table(races, paste(racesPath, "races.csv", sep=""), sep="\t", row.names = FALSE)

