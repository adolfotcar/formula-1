#downloads the starting grid for each race
#source of data: official F1 website

#used to harvest our data
library(rvest)

#creates a directory for our datasets
racesPath = "../datasets/races_grids/"
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
    link = paste(substr(link, 1, nchar(link)-16), "starting-grid.html", sep="")
    page = read_html(link)
    
    archiveLinks = html_text(html_nodes(page, ".ArchiveLink"))
    #some races from the official F1 website don't have the starting grid, we need to skip them
    for (link in archiveLinks){
      #only proceeds if the race has a link for the starting grid (otherwise it opens a 'Not found' page and information is useless)
      if (link=="Starting grid") {
        #getting only the values we need
        position = html_text(html_nodes(page, ".limiter+ .dark"))
        driverName = html_text(html_nodes(page, ".bold .hide-for-tablet"))
        driverSurname = html_text(html_nodes(page, ".bold .hide-for-mobile"))
        driverInitials = html_text(html_nodes(page, ".bold .hide-for-desktop"))
        driverTeam = html_text(html_nodes(page, "td+.uppercase "))
        
        raceResult = data.frame(position, driverName, driverSurname, driverInitials, driverTeam, stringsAsFactors = FALSE)
        write.table(raceResult, fileName, sep="\t", row.names = FALSE)
      }
    }
  }
  #avoiding getting the connections refused
  Sys.sleep(0.3)
}