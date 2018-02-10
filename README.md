# Easybank.at parser

## Description

Save transactions from easybank.at to a csv, and generate some plots.

`seleniumParser.py`: Navigates through easybank site via Selenium, stores all transactions to a .csv file. Also categorizes the transactions via IBAN or Regex. Configureable via `data/iban.csv` and `data/text.csv`.

`drawGraphs.py`: Uses data from the csv to generate some plots. E.g. Balance over time, Categorical spendings/income per year, Income/Spendings per month.

## Requirements

* Selenium
* Chromedriver
