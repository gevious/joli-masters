import System.IO
import System.Directory (getDirectoryContents)
import Control.Monad
import ActiveCompany
import Data.Map (keys, fromList)
import Data.List (intersperse, find, transpose, sort)
import Data.List.Split (splitOn)

inputDir = "/home/nico/Code/joli_masters/final_transform/by_value/"
filename = "/home/nico/Code/joli_masters/final_transform/by_value/2010-01.csv"
outputfilename = "/tmp/companycount.csv"

main = do
        -- iterate over all the files, and transpose the map
        allFiles <- getDirectoryContents inputDir
        contents <- mapM readFile $ (absFiles allFiles)
        let allContents = transpose $ getIndicators : (map getMonthRow contents)
        let finalContents = concat $ map outputRow allContents
--        print $ getHeader allFiles
--        print finalContents

        -- now that we have our big map, rotate it and write it to file
        writeFile outputfilename ((getHeader allFiles) ++ finalContents)


getMonthRow :: String -> [String]
-- Takes in the file contents and gives the company total for each indicator
getMonthRow contents = map (activeCompanies' contents) (keys $ fromList indicators)

getIndicators :: [String]
getIndicators = keys $ fromList indicators

getHeader :: [String] -> String
-- gets all the files and outputs a 'csv' line
getHeader files = ";" ++ (concat $ intersperse ";" $ map (\t -> take 7 t) $ validFiles files) ++ "\n"

outputRow :: [String] -> String
outputRow d = (concat $ intersperse ";" d) ++ "\n"

activeCompanies' :: String -> String -> String
activeCompanies' c i = show $ activeCompanies i c

validFiles :: [String] -> [String]
-- filter out all filenames starting with '.'
validFiles fs = sort $ filter (\(t:ts) -> t /= '.') fs

absFiles :: [String] -> [String]
absFiles fs = map (\t -> inputDir ++ t) $ validFiles fs
