# Easybank.at parser

## Description

Logs in to easybank.at online banking, saves transactions to a csv, and generates some useful plots, which their ebanking-site really lacks.

## Run
`python3 easybankReport.py`

Show parameter help: `python3 easybankReport.py --help` 

## Short description of python files
`seleniumParser.py`: Navigates through easybank site via Selenium, stores all transactions to a .csv file. Also categorizes the transactions via IBAN or Regex. Configureable via `data/iban.csv` and `data/text.csv`.

`drawGraphs.py`: Uses data from the csv to generate some plots. E.g. Balance over time, Categorical spendings/income per year, Income/Spendings per month.

## Requirements

* python3-tk
* Selenium via pip3
* numpy via pip3
* matplotlib via pip3
* [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
