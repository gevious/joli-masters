-- Calculates the number of active companies in a file based on an indicator
module ActiveCompany (isActive, activeCompanies, indicators) where

import Data.List.Split (splitOn)

indicators = [
    ("BV_MV", 2),
    ("Beta", 3),
    ("Debt equity ratio", 4),
    ("Excess return", 5),
    ("Market value", 6),
    ("Price Sales", 7),
    ("Return monthly", 7)]

type Indicator = String
type DataRow = String
type MonthlyData = String

delimiter = ";"

isActive :: Indicator -> DataRow -> Bool
-- sees if the company in the data row is in fact active
isActive i r = case (lookup i indicators) of
    Just idx -> not $ (splitOn delimiter r) !! idx `elem` ["0","#DIV/0!", "#REF!"]
    Nothing -> error "No indicator found"


activeCompanies :: Indicator -> MonthlyData -> Int
activeCompanies i d = countActive $ map (isActive i) (tail (lines d))

countActive :: [Bool] -> Int
countActive l = length (filter (\x -> x == True) l)
