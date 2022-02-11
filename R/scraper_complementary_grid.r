#the main source of data is the official F1 website. But for some reason they are missing the starting grid information on their website
#this script detects races that don't have a starting grid dataset and downloads them from an alternative website
#source of data: www.f1-fansite.com´

#used to harvest our data
library(rvest)
#useful for multiple strings manipulation
library(stringr)

#sanitizes the string str by removing accentuation
removeAccentuation = function(str){
  sanitized = str
  sanitized = str_replace(sanitized, 'á', 'a')
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

racesPath = "../datasets/races/"
gridsPath = "../datasets/races_grids/"
complementaryPath = "../datasets/races_grids_complement/"
dir.create(complementaryPath, showWarnings = FALSE)

#iterating through F1 years
for (year in 1950:2021) {
  #reading each race file for the current year
  for (raceFile in list.files(paste(racesPath, year, sep=""))){
    #if the file does not have an equivalent grid file, an alternative grid has to be sourced
    if (!(raceFile %in% list.files(paste(gridsPath, year, sep="")))){
      #creates a directory for the year
      dir.create(paste(complementaryPath, year, sep=""), showWarnings = FALSE)
      fileName = paste(complementaryPath, year, "/", raceFile, sep="")
      #skipping existent files to improve speed
      if (file.exists(fileName))
        next
      
      #avoiding getting too many connections error
      Sys.sleep(0.3)
      
      url = paste("https://www.f1-fansite.com/f1-result/results-", year,  "-formula-1-grand-prix-of-", sep="")
      raceName = str_replace(tolower(substr(raceFile, 1, nchar(raceFile)-4)), " ", "-")
      
      #USA and netherlands have a 'the' in the URL for some reason
      if (raceName=='united-states')
        raceName = 'the-united-states'
      if (raceName=='netherlands')
        raceName = 'the-netherlands'
      url = paste(url, raceName, sep="")
      
      page = read_html(url)
      
      #getting only the values we need
      #because sometimes two drivers were assigned same starting position, have to do this awful code to split the line in two
      position = str_replace_all(str_replace_all(str_replace_all(as.character(html_nodes(page, "td.msr_col8")), "<td class=\"msr_col8\">", ""), "<br>\n</td>\n", ""), "</td>\n", "")
      driverName = html_text(html_nodes(page, ".msr_col3 a+ a"))
      
      names = c()
      for (n in driverName){
        names = c(names, removeAccentuation(n))
      }
      
      #it means that in the race there were duplicated starting positions
      if (length(position)!=length(names)) {
        positions = c()
        for (p in position){
          for (newPos in str_split(p, "<br>")) {
            positions = c(positions, newPos)
          }
        }
      } else {
        positions = c(position)
      }
      #sometimes have to add empty fields just to match the table
      while(length(positions)>length(names)) {
        names = c(names, "")
      }
      
      #saving dataset
      driverData = data.frame(positions, names, stringsAsFactors = FALSE)
      write.table(driverData, fileName, sep="\t", row.names = FALSE)
    }
  }
}
