#this script scrapes drivers lineups
#source of data: www.statsf1.com


#used to harvest our data
library(rvest)
#useful for multiple strings manipulation
library(stringr)

#creates a directory for our datasets
lineupsDir = "../datasets/lineups/"
dir.create("../datasets/", showWarnings = FALSE)
dir.create(lineupsDir, showWarnings = FALSE)

#the source of data offers a alphabetical list for the constructors, therefore we need to iterate through the alphabet
alphabet = c("a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z")

for (letter in alphabet){
  #building the link for each letter of the alphabet and reading the table containing the constructors for that letter
  homeLink = paste("https://www.statsf1.com/en/constructeurs-", letter, ".aspx", sep="")
  homePage = read_html(homeLink)
  #this list will contain the links for each constructor page
  links = html_attr(html_nodes(homePage, "td:nth-child(1) a"), "href")
  
  for (link in links){
    #the link is in the format /en/driver-anem.aspx, we need to remove the '/en/' and the '.aspx' to get the driver name
    driverName = substr(link, 5, nchar(link)-5)
    fileName = paste(lineupsDir, driverName, ".csv", sep="")
    
    #skipping files that already exist
    if (file.exists(fileName))
      next
    
    #loading the pages for the detailed lineup over the years 
    teamLink = paste("https://www.statsf1.com", substr(link, 1, nchar(link)-5), "/saison.aspx", sep="")
    teamPage = read_html(teamLink)
    
    lineups = html_text2(html_nodes(teamPage, "#ctl00_CPH_Main_GV_Stats tbody td"))
    
    #final dataset will have two columns: year and driver
    year = c()
    name = c()
    #the table has 15 columnsn year is the first cell and the lneup the second
    cell = 1
    while (cell<length(lineups)){
      currentYear = lineups[cell]
      #the lineup may have more than one row, so we split at the \n
      lineup = str_split(substr(lineups[cell+1], 1, nchar(lineups[cell+1])-1), "\n")
      #iterating through all the drivers
      for (drivers in lineup){
        for (driver in drivers){
          year = c(year, currentYear)
          name = c(name, driver)
        }
      }
      cell = cell+15
    }
    #saving the csv
    lineupData = data.frame(year, name, stringsAsFactors = FALSE)
    write.table(lineupData, fileName, sep="\t", row.names = FALSE)
    
    #sleeping to avoid too many connections error
    Sys.sleep(0.3)
  }
}