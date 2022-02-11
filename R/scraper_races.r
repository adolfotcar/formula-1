#get race results
#source of data: official F1 website

#used to harvest our data
library(rvest)

#creates a directory for our datasets
racesPath = "../datasets/races/"
dir.create("../datasets/", showWarnings = FALSE)
dir.create(racesPath, showWarnings = FALSE)

#first championship was in 1950, iterating through every year up to now
for (year in 1950:2021) {
  #creates a dir for the current year
  dir.create(paste(racesPath, year, sep=""), showWarnings = FALSE)
  
  #link to the page that contains the summary of the season, from this page we'll get all the races
  seasonLink = paste("https://www.formula1.com/en/results.html/", year, "/races.html", sep="")
  seasonPage = read_html(seasonLink)
  
  #creating a dataframe with 2 columns: links for the races & venues names (to be used as a file name)
  raceLinks = html_attr(html_nodes(seasonPage, ".ArchiveLink"), "href")
  raceNames = trimws(html_text(html_nodes(seasonPage, ".ArchiveLink")))
  raceData = data.frame(raceNames, raceLinks, stringsAsFactors = FALSE)
  
  ##iterating our dataframe
  for (raceRow in 1:nrow(raceData)) {
    #generating the filename
    fileName = paste(racesPath, year, "/", raceData[raceRow, "raceNames"], ".csv", sep="")
    #if file already exists, skips to next record
    if (file.exists(fileName))
      next
    
    #reading the page with the race results
    link = paste("https://www.formula1.com", raceData[raceRow, "raceLinks"], sep="")
    page = read_html(link)
  
    ##getting only the values we need
    position = html_text(html_nodes(page, ".limiter+ .dark"))
    driverName = html_text(html_nodes(page, ".bold .hide-for-tablet"))
    driverSurname = html_text(html_nodes(page, ".bold .hide-for-mobile"))
    driverInitials = html_text(html_nodes(page, ".bold .hide-for-desktop"))
    driverTeam = html_text(html_nodes(page, "td+.uppercase "))
    
    #generating a dataframe and saving it
    raceResult = data.frame(position, driverName, driverSurname, driverInitials, driverTeam, stringsAsFactors = FALSE)
    write.table(raceResult, fileName, sep="\t", row.names = FALSE)
  }
  #avoiding getting the connections refused
  Sys.sleep(0.3)
}