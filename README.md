# PokePricing

PokePricing is a Web crawler to grab latest price charting values. The intent of the project is to pull the latest price charting information, so that the user has updated information useful at card shows.


## Input

The initial setup takes the most time, but it will save time as the information is used for multiple events. The information should be stored in an excel file. Use the file `CardList.xlsx` as an example.

- The first column is the general name of card. For example `gyarados`.
- The second column is the set name where the card comes from. For example `Base Set`.
- The third column is the number in the set. For example if the card is 13 of 120 then 13 would appear here.
- The fourth column is the URL to the price charting site where the information is found. This is the most important as this is the only true identifier where the information will be pulled from.

## Custom Args

- The path to the input spreadsheet.
- The column number where the price charting url is located for each row.
