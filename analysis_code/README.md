# Analysis Code

This code to produce the final values of the data. It no longer transforms the
data, but uses the latest data to produce results for analysis.

## 1. Company count

Produce an output showing the number of active companies in each month. An
active company is one with non-zero values for that month. This should be done
for each of the 4 variables: D/E, MV, PS, BV_MV.  The output will
look something like this:

    Indicator, 2001-Dec, 2002-Jan, 2002-Feb,...
    D/E, 10, 12, 11...
    MV, 12, 8, 9...
    ...


## 2. Total annual return
Calculate the total annual return per company per year. This is done by adding
together each monthly return. This needs to be done for both the *monthly* and
*excess* return values. The range is from Jan - Dec for each year. Included in
the output should be the indicators for last month of the previous year.

    Company name, Annual return, PSR, D/E, MV, BV_MV
    xyz, (sum jan-dec 2002), value for dec 2001, ...

    Company name, Annual excess return, PSR, D/E, MV, BV_MV
    xyz, (sum jan-dec 2002), value for dec 2001, ...

There will only be 2 files, with each of the year's data being included in a
single file. A blank linke should be left to clearly show the separation between
years. The blank line may have the year in the first cell of the line.


## 3. Portfolio returns
