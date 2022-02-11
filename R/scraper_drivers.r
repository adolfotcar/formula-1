#loads individual records for each driver
#main usage is to get the reason for retirement for each driver
#source of data: F1 fan site


#used to harvest our data
library(rvest)
#used to remove accentuation from the drivers names
library(stringr)

#sanitizes the string str by removing accentuation
removeAccentuation = function(str){
  sanitized = str
  sanitized = str_replace(sanitized, 'á', 'a')
  sanitized = str_replace(sanitized, 'Á', 'A')
  sanitized = str_replace(sanitized, 'à', 'a')
  sanitized = str_replace(sanitized, 'À', 'A')
  sanitized = str_replace(sanitized, 'ã', 'a')
  sanitized = str_replace(sanitized, 'Ã', 'A')
  sanitized = str_replace(sanitized, 'â', 'a')
  sanitized = str_replace(sanitized, 'Â', 'A')
  sanitized = str_replace(sanitized, 'ä', 'a')
  sanitized = str_replace(sanitized, 'Ä', 'A')
  
  sanitized = str_replace(sanitized, 'é', 'e')
  sanitized = str_replace(sanitized, 'É', 'E')
  sanitized = str_replace(sanitized, 'è', 'e')
  sanitized = str_replace(sanitized, 'È', 'E')
  sanitized = str_replace(sanitized, 'ẽ', 'e')
  sanitized = str_replace(sanitized, 'Ẽ', 'E')
  sanitized = str_replace(sanitized, 'ê', 'e')
  sanitized = str_replace(sanitized, 'Ê', 'E')
  sanitized = str_replace(sanitized, 'ë', 'e')
  sanitized = str_replace(sanitized, 'Ë', 'E')
  
  sanitized = str_replace(sanitized, 'í', 'i')
  sanitized = str_replace(sanitized, 'Í', 'I')
  sanitized = str_replace(sanitized, 'ì', 'i')
  sanitized = str_replace(sanitized, 'Ì', 'I')
  sanitized = str_replace(sanitized, 'ĩ', 'i')
  sanitized = str_replace(sanitized, 'Ĩ', 'I')
  sanitized = str_replace(sanitized, 'î', 'i')
  sanitized = str_replace(sanitized, 'Î', 'I')
  sanitized = str_replace(sanitized, 'ï', 'i')
  sanitized = str_replace(sanitized, 'Ï', 'I')
  
  sanitized = str_replace(sanitized, 'ó', 'o')
  sanitized = str_replace(sanitized, 'Ó', 'O')
  sanitized = str_replace(sanitized, 'ò', 'o')
  sanitized = str_replace(sanitized, 'Ò', 'O')
  sanitized = str_replace(sanitized, 'õ', 'o')
  sanitized = str_replace(sanitized, 'Õ', 'O')
  sanitized = str_replace(sanitized, 'ô', 'o')
  sanitized = str_replace(sanitized, 'Ô', 'O')
  sanitized = str_replace(sanitized, 'ö', 'o')
  sanitized = str_replace(sanitized, 'Ö', 'O')
  
  sanitized = str_replace(sanitized, 'ú', 'u')
  sanitized = str_replace(sanitized, 'Ú', 'U')
  sanitized = str_replace(sanitized, 'ù', 'u')
  sanitized = str_replace(sanitized, 'Ù', 'U')
  sanitized = str_replace(sanitized, 'ũ', 'u')
  sanitized = str_replace(sanitized, 'Ũ', 'U')
  sanitized = str_replace(sanitized, 'û', 'u')
  sanitized = str_replace(sanitized, 'Û', 'U')
  sanitized = str_replace(sanitized, 'ü', 'u')
  sanitized = str_replace(sanitized, 'Ü', 'U')
  
  sanitized = str_replace(sanitized, 'ø', 'o')
  sanitized = str_replace(sanitized, 'Ø', 'o')
  sanitized = str_replace(sanitized, '¢', 'c')
  sanitized = str_replace(sanitized, 'ç', 'c')
  sanitized = str_replace(sanitized, 'Ç', 'c')
  sanitized = str_replace(sanitized, 'š', 's')
  return(sanitized)
}

#creates a directory for our datasets
racesPath = "../datasets/drivers_races/"
dir.create("../datasets/", showWarnings = FALSE)
dir.create(racesPath, showWarnings = FALSE)

#link to the mainpage of our data, from here we'll get the links to the drivers profiles
homeLink = "https://www.f1-fansite.com/f1-drivers/"
homePage = read_html(homeLink)

#creating a dataframe with 2 columns: links for the profile & drivers name (to be used as a file name)
links = html_attr(html_nodes(homePage, ".motor-sport-results a"), "href")
drivers = html_text(html_nodes(homePage, ".motor-sport-results a"))
driverLinksTable = data.frame(links, drivers, stringsAsFactors = FALSE)

#iterating through the dataframe
for (row in 1:nrow(driverLinksTable)){
  #generating the filename
  fileName = removeAccentuation(paste(racesPath, driverLinksTable[row, "drivers"],".csv", sep=""))
  #if file already exists, skips to next record
  if (file.exists(fileName))
    next
  
  #reading the page for the driver profile
  link = driverLinksTable[row, "links"]
  page = read_html(link)
    
  #getting only the values we need
  year = html_text(html_nodes(page, ".msr_driver_races .msr_col2 a"))
  race = html_text(html_nodes(page, ".msr_driver_races .msr_col3 a"))
  team = html_text(html_nodes(page, ".msr_driver_races .msr_col5 a"))
  startingPosition = html_text(html_nodes(page, ".msr_driver_races td.msr_col7"))
  finishingPosition = html_text(html_nodes(page, ".msr_driver_races td.msr_col8"))
  retirementReason = html_text(html_nodes(page, ".msr_driver_races td.msr_col9"))
    
  #generating a dataframe and saving it
  driverData = data.frame(year, race, team, startingPosition, finishingPosition, retirementReason, stringsAsFactors = FALSE)
  write.table(driverData, fileName, sep="\t", row.names = FALSE)
}